"""SQLite 訂閱帳本：記錄每筆活躍 QUOTE 訂閱（code / subtype / 訂閱時間）。

純 stdlib sqlite3，零 Qt/futu 依賴，可獨立單測。DB 檔路徑由呼叫方決定
（開發模式 = 專案根目錄；frozen = exe 旁邊——跟 .env 同邏輯），本模組只負責
schema + CRUD + 「到期清理」查詢。

用途：FutuEngine 切換標的時 unsubscribe 舊 code，但 OpenD 規則「同一 code 訂閱未滿
1 分鐘就 unsubscribe 會被拒」（實測錯誤訊息「Basic訂閱時間過短」）→ 舊訂閱實際未移除、
持續佔用額度（洩漏）。帳本記錄每筆訂閱嘅 subscribed_at；engine 定時 reconcile() 對
「已不活躍且 >MIN_SUBSCRIBE_SECONDS」的條目重試 unsubscribe → 杜絕洩漏。開機再用
query_subscription() 對帳自癒上次殘留（見 futu_engine）。

Thread safety：每個方法開自己嘅 connection（per-call connect + commit/close）→ 唔共享
connection object，天然 thread-safe；SQLite file locking 處理 reconcile worker 同 switch
worker 嘅低頻併發寫入。DB 極小、操作稀疏，rollback journal 已足夠（唔需要 WAL）。
"""
from __future__ import annotations

import sqlite3
import sys
import time
from contextlib import contextmanager
from pathlib import Path

# OpenD 要求「訂閱滿 1 分鐘先可以 unsubscribe」；+15s 緩衝避免邊界重試又失敗（OpenD 內部
# 計時可能略遲於我哋記錄嘅 subscribed_at）。reconcile 只對 age >= 呢個值嘅條目重試。
MIN_SUBSCRIBE_SECONDS = 75


def default_db_path() -> Path:
    """預設訂閱帳本 DB 路徑。

    開發模式 = 專案根目錄（engine/ 上一層）；PyInstaller frozen（onedir）= exe 旁邊——
    跟 .env 同邏輯：用戶部署可視、唔放 _MEIPASS temp dir（啟動後即刪）。
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name("subscriptions.db")
    return Path(__file__).resolve().parents[1] / "subscriptions.db"


class SubscriptionStore:
    """SQLite 訂閱帳本（per-call connection，天然 thread-safe）。

    每筆訂閱 = (code, subtype) 主鍵 + subscribed_at（epoch seconds）。re-subscribe 同 code
    → INSERT OR REPLACE 更新時間戳（重新計時）。
    """

    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._ensure_schema()

    @property
    def path(self) -> Path:
        return self._path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._path))
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _tx(self):
        """開 connection → yield → commit（失敗 rollback）→ 確保 close。"""
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self._tx() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS subscriptions (
                       code TEXT NOT NULL,
                       subtype TEXT NOT NULL,
                       subscribed_at REAL NOT NULL,
                       PRIMARY KEY (code, subtype)
                   )"""
            )

    def add(self, code: str, subtype: str = "QUOTE", ts: float | None = None) -> None:
        """記錄一筆訂閱；re-subscribe 同 (code, subtype) → 更新 subscribed_at（重新計時）。"""
        if ts is None:
            ts = time.time()
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO subscriptions (code, subtype, subscribed_at) VALUES (?, ?, ?) "
                "ON CONFLICT(code, subtype) DO UPDATE SET subscribed_at=excluded.subscribed_at",
                (code, subtype, ts),
            )

    def remove(self, code: str, subtype: str = "QUOTE") -> None:
        """移除一筆訂閱（unsubscribe 成功後呼叫）。"""
        with self._tx() as conn:
            conn.execute(
                "DELETE FROM subscriptions WHERE code=? AND subtype=?", (code, subtype)
            )

    def list_active(self) -> list[tuple[str, str, float]]:
        """全部帳本條目（code, subtype, subscribed_at），訂閱時間序。"""
        with self._tx() as conn:
            rows = conn.execute(
                "SELECT code, subtype, subscribed_at FROM subscriptions ORDER BY subscribed_at"
            ).fetchall()
        return [(r["code"], r["subtype"], r["subscribed_at"]) for r in rows]

    def due_for_cleanup(self, active_codes: set[str], now: float | None = None) -> list[tuple[str, str, float]]:
        """「已不活躍且訂閱滿 MIN_SUBSCRIBE_SECONDS」的條目——reconcile 重試 unsubscribe 目標。

        active_codes = 要保留嘅 code（當前 state.code）；其餘 age >= 閾值嘅條目即係洩漏候選。
        """
        if now is None:
            now = time.time()
        cutoff = now - MIN_SUBSCRIBE_SECONDS
        with self._tx() as conn:
            if active_codes:
                ph = ",".join("?" * len(active_codes))
                rows = conn.execute(
                    f"SELECT code, subtype, subscribed_at FROM subscriptions "
                    f"WHERE subscribed_at <= ? AND code NOT IN ({ph}) ORDER BY subscribed_at",
                    (cutoff, *active_codes),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT code, subtype, subscribed_at FROM subscriptions "
                    "WHERE subscribed_at <= ? ORDER BY subscribed_at",
                    (cutoff,),
                ).fetchall()
        return [(r["code"], r["subtype"], r["subscribed_at"]) for r in rows]

    def clear(self) -> None:
        """清空帳本（測試 / 全量重置用）。"""
        with self._tx() as conn:
            conn.execute("DELETE FROM subscriptions")
