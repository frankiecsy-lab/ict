"""MainWindow control bar 驗證邏輯單測（offscreen Qt + fake engine，零真實 OpenD 連線）。

覆蓋：輸入欄**只收純編號**（含空白/名稱 → 拒絕）、目錄載入後 `canonical_code()` 驗證存在
+ 正規化大小寫、未知編號 → status bar 報錯唔切換、獨立名稱 LABEL（`name_text()`）顯示、
dropdown activated 路徑（code + 名稱同步更新）。
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from config import Config  # noqa: E402
from engine.stock_catalog import StockEntry, display_text, name_text  # noqa: E402
import ui.main_window as mw_module  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402

_app = QApplication.instance() or QApplication([])


class FakeEngine(QObject):
    """替身 engine：記錄 switch 呼叫，唔 spawn thread / 唔連 OpenD。"""

    history_ready = Signal(tuple)
    bars_changed = Signal(tuple)
    status = Signal(str)
    error = Signal(str)
    catalog_ready = Signal(tuple)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.switch_calls: list[tuple[str | None, str | None]] = []

    def start(self, cfg) -> None:  # noqa: ARG002 — 替身唔連線
        pass

    def stop(self) -> None:
        pass

    def switch(self, code=None, kline_type=None) -> None:
        self.switch_calls.append((code, kline_type))


def _entries():
    return [
        StockEntry("HK.HSImain", "恒指期货主连", ""),
        StockEntry("HK.00700", "腾讯控股", "TENCENT"),
        StockEntry("US.AAPL", "苹果", "Apple Inc."),
    ]


def _make_window(monkeypatch) -> tuple[MainWindow, FakeEngine]:
    engine = FakeEngine()
    monkeypatch.setattr(mw_module, "FutuEngine", lambda parent=None: engine)
    win = MainWindow(Config())  # 預設 trading_code=HK.HSImain、kline_type=K_1M
    return win, engine


def test_do_switch_rejects_name_in_field(monkeypatch):
    """輸入欄含名稱（空白分隔）→ 拒絕切換，status bar 提示。"""
    win, engine = _make_window(monkeypatch)
    win._on_catalog_ready(_entries())
    win.code_edit.setText("HK.00700 腾讯控股")
    win._do_switch()
    assert engine.switch_calls == []


def test_do_switch_rejects_empty_field(monkeypatch):
    win, engine = _make_window(monkeypatch)
    win.code_edit.setText("   ")
    win._do_switch()
    assert engine.switch_calls == []


def test_do_switch_unknown_code_rejected_after_catalog(monkeypatch):
    """目錄載入後：未知編號 → 拒絕（唔會打到 OpenD）。"""
    win, engine = _make_window(monkeypatch)
    win._on_catalog_ready(_entries())
    win.code_edit.setText("HK.99999")
    win._do_switch()
    assert engine.switch_calls == []


def test_do_switch_valid_code_normalizes_case_and_updates_name(monkeypatch):
    """小寫輸入 → canonical 大小寫正規化 + switch + 名稱 LABEL 顯示中英文名。"""
    win, engine = _make_window(monkeypatch)
    win._on_catalog_ready(_entries())
    win.code_edit.setText("hk.00700")
    win._do_switch()
    assert engine.switch_calls == [("HK.00700", "K_1M")]
    assert win.code_edit.text() == "HK.00700"
    assert win.name_label.text() == name_text(_entries()[1])  # "腾讯控股 TENCENT"


def test_do_switch_before_catalog_passthrough(monkeypatch):
    """目錄未載入（fetch 失敗等）→ 放行俾 engine/OpenD 最終校驗。"""
    win, engine = _make_window(monkeypatch)
    win.code_edit.setText("HK.00700")
    win._do_switch()
    assert engine.switch_calls == [("HK.00700", "K_1M")]


def test_catalog_ready_initializes_name_label(monkeypatch):
    """catalog_ready → 用當前輸入欄 code（預設 HK.HSImain）初始化名稱 LABEL。"""
    win, _engine = _make_window(monkeypatch)
    assert win.name_label.text() == ""  # 目錄未載入前空白
    win._on_catalog_ready(_entries())
    assert win.name_label.text() == "恒指期货主连"


def test_on_code_activated_sets_code_and_name(monkeypatch):
    """Dropdown 選中 → 輸入欄只留 canonical code + switch + 名稱 LABEL 同步。"""
    win, engine = _make_window(monkeypatch)
    entries = _entries()
    win._on_catalog_ready(entries)
    aapl = entries[2]
    win._on_code_activated(display_text(aapl))
    assert win.code_edit.text() == "US.AAPL"  # 名稱唔入輸入欄
    assert engine.switch_calls == [("US.AAPL", "K_1M")]
    assert win.name_label.text() == name_text(aapl)
