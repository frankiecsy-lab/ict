"""ui_state_store 純邏輯單測：SQLite UI 狀態記憶 CRUD（零 Qt/futu）。

覆蓋：schema 冪等、save/load round-trip、無記錄 → None、損壞 JSON blob → None、
非 dict blob → None、clear()、default_ui_state_path frozen/開發分支。
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from engine.ui_state_store import UIStateStore, default_ui_state_path


@pytest.fixture
def store(tmp_path):
    return UIStateStore(tmp_path / "ui_state.db")


class TestCrud:
    def test_empty_load_returns_none(self, store):
        """無記錄 → load() 返回 None（呼叫方 fallback 預設值）。"""
        assert store.load() is None

    def test_save_and_load_roundtrip(self, store):
        state = {
            "code": "US.AAPL",
            "pane_count": 4,
            "periods": ["K_5M", "K_15M", "K_30M", "K_60M"],
            "indicators": ["ob", "fvg"],
        }
        store.save(state)
        assert store.load() == state

    def test_save_overwrites_single_row(self, store):
        """單行記憶：第二次 save 覆蓋第一次（唔會累積多筆）。"""
        store.save({"code": "HK.HSImain", "pane_count": 1})
        store.save({"code": "US.AAPL", "pane_count": 4})
        assert store.load() == {"code": "US.AAPL", "pane_count": 4}

    def test_save_empty_dict(self, store):
        """空 dict 亦係合法快照（round-trip 保真）。"""
        store.save({})
        assert store.load() == {}

    def test_load_corrupted_json_returns_none(self, store):
        """損壞 JSON blob → load() 返回 None（唔 crash app，當無記憶）。"""
        with sqlite3.connect(str(store.path)) as conn:
            conn.execute(
                "INSERT INTO ui_state (key, value) VALUES (?, ?)",
                ("main", "{not valid json"),
            )
            conn.commit()
        assert store.load() is None

    def test_load_non_dict_json_returns_none(self, store):
        """合法 JSON 但非 dict（例如 list）→ load() 返回 None。"""
        with sqlite3.connect(str(store.path)) as conn:
            conn.execute(
                "INSERT INTO ui_state (key, value) VALUES (?, ?)",
                ("main", json.dumps(["K_1M"])),
            )
            conn.commit()
        assert store.load() is None

    def test_clear(self, store):
        store.save({"code": "US.AAPL"})
        store.clear()
        assert store.load() is None


class TestDefaultUiStatePath:
    def test_dev_mode_is_project_root(self, monkeypatch):
        """非 frozen → DB 喺 engine/ 上一層（專案根目錄）。"""
        monkeypatch.delattr(sys, "frozen", raising=False)
        p = default_ui_state_path()
        assert p.name == "ui_state.db"
        root = Path(__file__).resolve().parents[1]
        assert p.parent == root

    def test_frozen_mode_is_exe_sibling(self, monkeypatch):
        """frozen → DB 喺 exe 旁邊（跟 .env / subscriptions.db 同邏輯）。"""
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        fake_exe = (Path("C:/opt/ICT-Trader-win/ict-trader.exe") if sys.platform == "win32"
                    else Path("/opt/ICT-Trader-win/ict-trader"))
        monkeypatch.setattr(sys, "executable", str(fake_exe))

        p = default_ui_state_path()
        assert p.name == "ui_state.db"
        assert p.parent == fake_exe.parent  # exe 旁邊（同目錄）


class TestThreadSafety:
    def test_concurrent_saves_no_lost_rows(self, store):
        """per-call connection → 多線程併發 save 唔會丟行 / 損壞 blob。"""
        import threading

        n_threads = 8
        errors: list[BaseException] = []

        def worker(i: int) -> None:
            try:
                for j in range(25):
                    store.save({"code": f"CODE-{i}-{j}", "pane_count": i})
            except BaseException as e:  # noqa: BLE001 — 記錄任何異常俾主線程斷言
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        # 最終 load 必須係合法 dict（blob 完整、唔會寫到一半）
        loaded = store.load()
        assert isinstance(loaded, dict)
        assert "code" in loaded and "pane_count" in loaded
