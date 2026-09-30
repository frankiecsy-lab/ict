"""subscription_store 純邏輯單測：SQLite 訂閱帳本 CRUD + due_for_cleanup（零 Qt/futu）。

覆蓋：schema 冪等、add/remove/list_active、re-subscribe 重新計時、due_for_cleanup
（active_codes 過濾 + MIN_SUBSCRIBE_SECONDS 閾值）、default_db_path frozen/開發分支。
"""
from __future__ import annotations

import sys
import time as _t

import pytest

from engine.subscription_store import (MIN_SUBSCRIBE_SECONDS, SubscriptionStore,
                                       default_db_path)


@pytest.fixture
def store(tmp_path):
    return SubscriptionStore(tmp_path / "subs.db")


class TestCrud:
    def test_empty_ledger(self, store):
        assert store.list_active() == []

    def test_add_and_list(self, store):
        ts = 1000.0
        store.add("HK.HSImain", ts=ts)
        rows = store.list_active()
        assert len(rows) == 1
        code, subtype, at = rows[0]
        assert (code, subtype, at) == ("HK.HSImain", "QUOTE", ts)

    def test_add_multiple_ordered_by_time(self, store):
        store.add("US.AAPL", ts=2000.0)
        store.add("HK.HSImain", ts=1000.0)  # 較早 → 排前
        codes = [c for c, _s, _ts in store.list_active()]
        assert codes == ["HK.HSImain", "US.AAPL"]

    def test_remove(self, store):
        store.add("HK.HSImain")
        store.remove("HK.HSImain")
        assert store.list_active() == []

    def test_remove_missing_is_noop(self, store):
        store.remove("US.NOSUCH")  # 唔好炸
        assert store.list_active() == []

    def test_resubscribe_updates_timestamp(self, store):
        """re-subscribe 同 (code, subtype) → INSERT OR REPLACE 更新 subscribed_at（重新計時）。"""
        store.add("HK.HSImain", ts=1000.0)
        store.add("HK.HSImain", ts=2000.0)  # re-subscribe
        rows = store.list_active()
        assert len(rows) == 1  # 唔會重複
        assert rows[0][2] == 2000.0

    def test_distinct_subtypes_coexist(self, store):
        """同 code 唔同 subtype → 兩筆獨立條目（主鍵 = (code, subtype)）。"""
        store.add("HK.HSImain", subtype="QUOTE", ts=1000.0)
        store.add("HK.HSImain", subtype="K_1M", ts=1500.0)
        assert len(store.list_active()) == 2

    def test_clear(self, store):
        store.add("US.AAPL")
        store.add("HK.HSImain")
        store.clear()
        assert store.list_active() == []


class TestDueForCleanup:
    def test_due_excludes_recent_and_active(self, store):
        now = 10_000.0
        old = now - (MIN_SUBSCRIBE_SECONDS + 1)   # 已滿閾值
        recent = now - 5                          # 未滿閾值
        active = now - (MIN_SUBSCRIBE_SECONDS + 1)  # 已滿但係當前活躍 → 保留
        store.add("STALE", ts=old)                # due（不活躍 + 夠舊）
        store.add("RECENT", ts=recent)            # 唔 due（太新）
        store.add("ACTIVE", ts=active)            # 唔 due（係 active_codes）

        due = {c for c, _s, _ts in store.due_for_cleanup({"ACTIVE"}, now=now)}
        assert due == {"STALE"}

    def test_due_empty_active_codes(self, store):
        """active_codes 空 → 所有 age>=閾值嘅條目都係 due（例如 state 未建立）。"""
        now = 10_000.0
        old = now - (MIN_SUBSCRIBE_SECONDS + 1)
        recent = now - 5
        store.add("STALE", ts=old)
        store.add("RECENT", ts=recent)

        due = {c for c, _s, _ts in store.due_for_cleanup(set(), now=now)}
        assert due == {"STALE"}

    def test_due_boundary_at_threshold(self, store):
        """age 恰好 = MIN_SUBSCRIBE_SECONDS → subscribed_at <= cutoff → due（含邊界）。"""
        now = 10_000.0
        at_cutoff = now - MIN_SUBSCRIBE_SECONDS
        store.add("EDGE", ts=at_cutoff)

        due = {c for c, _s, _ts in store.due_for_cleanup(set(), now=now)}
        assert "EDGE" in due

    def test_due_none_when_all_recent(self, store):
        store.add("RECENT", ts=_t.time())  # 剛訂閱
        assert store.due_for_cleanup({"OTHER"}) == []


class TestDefaultDbPath:
    def test_dev_mode_is_project_root(self, monkeypatch):
        """非 frozen → DB 喺 engine/ 上一層（專案根目錄）。"""
        monkeypatch.delattr(sys, "frozen", raising=False)
        p = default_db_path()
        assert p.name == "subscriptions.db"
        # parents[1] of engine/subscription_store.py = 專案根
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        assert p.parent == root

    def test_frozen_mode_is_exe_sibling(self, monkeypatch):
        """frozen → DB 喺 exe 旁邊（跟 .env 同邏輯）。平台無關：驗證 name + parent。"""
        from pathlib import Path

        monkeypatch.setattr(sys, "frozen", True, raising=False)
        fake_exe = (Path("C:/opt/ICT-Trader-win/ict-trader.exe") if sys.platform == "win32"
                    else Path("/opt/ICT-Trader-win/ict-trader"))
        monkeypatch.setattr(sys, "executable", str(fake_exe))

        p = default_db_path()
        assert p.name == "subscriptions.db"
        assert p.parent == fake_exe.parent  # exe 旁邊（同目錄）


class TestThreadSafety:
    def test_concurrent_adds_no_lost_rows(self, store):
        """per-call connection → 多線程併發 add 唔會丟行（SQLite file locking 兜底）。"""
        import threading

        n_threads, per_thread = 8, 25

        def worker(i):
            for j in range(per_thread):
                store.add(f"CODE_{i}_{j}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(store.list_active()) == n_threads * per_thread


def test_min_subscribe_seconds_is_sane():
    """閾值必須 > 60s（OpenD「訂閱滿 1 分鐘」規則）+ 留緩衝。"""
    assert MIN_SUBSCRIBE_SECONDS >= 75
