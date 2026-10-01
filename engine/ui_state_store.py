"""SQLite UI 狀態記憶：持久化主窗口嘅「標的 / pane 佈局 / per-pane 週期 / 指標開關」。

純 stdlib sqlite3，零 Qt/futu 依賴，可獨立單測。DB 檔路徑由呼叫方決定（開發模式 =
專案根目錄；frozen = exe 旁邊——跟 .env / subscriptions.db 同邏輯），本模組只負責
schema + CRUD。

用途：用戶重開 app 時還原上次嘅 UI 狀態——標的編號、1/2/4 pane 佈局、每個 pane 選咗
邊個 K 線週期、邊啲 ICT 指標開關係開緊。設計成**單行 JSON blob**（key='main'）而唔係
拆多欄：(a) schema 演化穩健——加新字段唔使 ALTER TABLE，舊 DB 直接兼容；(b) 原子語義——
一次 save = 一條記錄 INSERT OR REPLACE，唔會寫到一半留低不一致狀態。

Thread safety：每個方法開自己嘅 connection（per-call connect + commit/close）→ 唔共享
connection object，天然 thread-safe。UI 狀態只喺 GUI thread 由用戶操作觸發寫入（低頻、
極小），rollback journal 已足夠（唔需要 WAL）。
"""
from __future__ import annotations

import json
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path


def default_ui_state_path() -> Path:
    """預設 UI 狀態 DB 路徑。

    開發模式 = 專案根目錄（engine/ 上一層）；PyInstaller frozen（onedir）= exe 旁邊——
    跟 .env / subscriptions.db 同邏輯：用戶部署可視、唔放 _MEIPASS temp dir（啟動後即刪）。
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name("ui_state.db")
    return Path(__file__).resolve().parents[1] / "ui_state.db"


class UIStateStore:
    """SQLite UI 狀態記憶（per-call connection，天然 thread-safe）。

    單行表 ui_state(key TEXT PRIMARY KEY, value TEXT NOT NULL)；value = JSON blob。
    save(dict) → INSERT OR REPLACE key='main'；load() → dict | None（無記錄 / 損壞 → None）；
    clear() → 刪全部（測試 / 全量重置用）。
    """

    _KEY = "main"   # 單行記憶：固定 key，value 係完整 UI 狀態 JSON blob

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
                """CREATE TABLE IF NOT EXISTS ui_state (
                       key TEXT PRIMARY KEY,
                       value TEXT NOT NULL
                   )"""
            )

    def save(self, state: dict) -> None:
        """寫入完整 UI 狀態快照（dict → JSON blob，INSERT OR REPLACE key='main'）。"""
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO ui_state (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (self._KEY, json.dumps(state)),
            )

    def load(self) -> dict | None:
        """讀回 UI 狀態快照；無記錄 / JSON 損壞 → None（呼叫方 fallback 預設值）。"""
        with self._tx() as conn:
            row = conn.execute(
                "SELECT value FROM ui_state WHERE key=?", (self._KEY,)
            ).fetchone()
        if row is None:
            return None
        try:
            data = json.loads(row["value"])
        except (ValueError, TypeError):
            return None   # 損壞 blob → 當無記憶（唔應該 crash app）
        return data if isinstance(data, dict) else None

    def clear(self) -> None:
        """清空記憶（測試 / 全量重置用）。"""
        with self._tx() as conn:
            conn.execute("DELETE FROM ui_state")
