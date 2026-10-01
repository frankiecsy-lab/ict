"""MainWindow control bar 驗證邏輯單測（offscreen Qt + fake engine，零真實 OpenD 連線）。

覆蓋：**onChange guard**（textChanged：欄位出現「code + 名稱」即刻剝離返純 code——
completer setCompletion() 喺 activated 前寫入完整 display_text 嘅路徑）、目錄載入後
`canonical_code()` 驗證存在 + 正規化大小寫、未知編號 → status bar 報錯唔切換、
獨立名稱 LABEL（`name_text()`）顯示、dropdown activated 路徑（code + 名稱同步更新）。
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
    """替身 engine：記錄 switch 呼叫，唔 spawn thread / 唔連 OpenD。

    Signal 簽名跟新多 pane API：history_ready/bars_changed = (period, bars)；
    switch(code=..., periods=[...])——periods 係全 pane combo union（排序 tuple 方便斷言）。
    """

    history_ready = Signal(str, tuple)   # (period, bars) — per-period signal
    bars_changed = Signal(str, tuple)
    status = Signal(str)
    error = Signal(str)
    catalog_ready = Signal(tuple)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.switch_calls: list[tuple[str | None, tuple[str, ...] | None]] = []
        self.start_periods: list[str] | None = None   # start(periods=...) 記錄
        self.state = None                              # _State | None——替身無活躍狀態

    def start(self, cfg, db_path=None, periods=None) -> None:  # noqa: ARG002 — 替身唔連線
        self.start_periods = list(periods) if periods else None

    def stop(self) -> None:
        pass

    def switch(self, code=None, periods=None) -> None:
        self.switch_calls.append((code, tuple(sorted(periods)) if periods is not None else None))


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
    """輸入欄含名稱（空白分隔）→ onChange guard 即刻剝離返純 code，_do_switch 對純 code 正常切換。"""
    win, engine = _make_window(monkeypatch)
    win._on_catalog_ready(_entries())
    win.code_edit.setText("HK.00700 腾讯控股")
    # guard 已將欄位剝離返純 code（名稱唔會殘留）
    assert win.code_edit.text() == "HK.00700"
    win._do_switch()
    assert engine.switch_calls == [("HK.00700", ("K_15M", "K_1M", "K_3M", "K_5M"))]  # sorted() 字典序


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
    assert engine.switch_calls == [("HK.00700", ("K_15M", "K_1M", "K_3M", "K_5M"))]  # sorted() 字典序
    assert win.code_edit.text() == "HK.00700"
    assert win.name_label.text() == name_text(_entries()[1])  # "腾讯控股 TENCENT"


def test_do_switch_before_catalog_passthrough(monkeypatch):
    """目錄未載入（fetch 失敗等）→ 放行俾 engine/OpenD 最終校驗。"""
    win, engine = _make_window(monkeypatch)
    win.code_edit.setText("HK.00700")
    win._do_switch()
    assert engine.switch_calls == [("HK.00700", ("K_15M", "K_1M", "K_3M", "K_5M"))]  # sorted() 字典序


def test_catalog_ready_initializes_name_label(monkeypatch):
    """catalog_ready → 用當前輸入欄 code（預設 HK.HSImain）初始化名稱 LABEL。"""
    win, _engine = _make_window(monkeypatch)
    assert win.name_label.text() == ""  # 目錄未載入前空白
    win._on_catalog_ready(_entries())
    assert win.name_label.text() == "恒指期货主连"


def test_zoom_buttons_wired_to_chart(monkeypatch):
    """control bar 放大/縮小按鍵 → 全部可見 pane 時間視窗 ×/÷1.25（中心錨定）。

    用**真實分鐘 datetime key**：_zoom_all 走 time_window()/set_time_window() 時間空間路徑，
    fake key（bar_key_to_dt parse 唔到）會令 zoom no-op。
    """
    from datetime import datetime, timedelta
    win, _engine = _make_window(monkeypatch)
    base = datetime(2026, 1, 5, 9, 30)
    bars = tuple(((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                  100.0, 101.0, 99.5, 100.5, 1.0) for i in range(200))
    win.chart.update_bars(bars)   # 先餵數據（chart 無 bars 時 zoom no-op）
    assert win.chart._view_count == 120  # Config 預設 visible_bars
    win.zoom_in_btn.click()
    assert win.chart._view_count == 96   # 120min 視窗 ×0.8 → 96 根分鐘 bar
    win.zoom_out_btn.click()
    assert win.chart._view_count == 120  # round-trip 還原（×1.25）


def test_pane_view_changed_broadcasts_time_window(monkeypatch):
    """用戶喺 pane 0 pan/zoom → 時間視窗廣播去其他可見 pane（跨週期 span-overlap 對齊）。"""
    from datetime import datetime, timedelta
    win, _engine = _make_window(monkeypatch)
    base = datetime(2026, 1, 5, 9, 30)
    m_bars = tuple(((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                    100.0, 101.0, 99.5, 100.5, 1.0) for i in range(200))
    w_bars = tuple(((base + timedelta(minutes=3 * j)).strftime("%Y-%m-%d %H:%M"),
                    100.0, 101.0, 99.5, 100.5, 1.0) for j in range(100))
    win._panes[0].update_bars(m_bars)   # pane 0 = K_1M（200 根分鐘 bar）
    win._panes[1].update_bars(w_bars)   # pane 1 = K_3M（100 根 3 分鐘 bar）
    win._set_pane_count(2)              # 顯示 2 pane
    start = base + timedelta(minutes=80)
    end = base + timedelta(minutes=200)
    win._on_pane_view_changed(0, start, end)   # 模擬用戶喺 pane 0 zoom/pan
    assert win._panes[1]._view_count == 41      # [B+80,B+200) ∩ 3min bars = j∈[26..66]
    assert round(win._panes[1]._right_offset) == 33   # 尾根可見 bar = j=66 → offset = 99-66


def test_pane_period_change_pushes_active_snapshot(monkeypatch):
    """combo 換週期 → 目標週期已活躍（其他 pane 用緊）→ 直接推當前 snapshot，唔使等 tick。"""
    from datetime import datetime, timedelta
    win, engine = _make_window(monkeypatch)
    base = datetime(2026, 1, 5, 9, 30)
    five_bars = tuple(((base + timedelta(minutes=5 * j)).strftime("%Y-%m-%d %H:%M"),
                       100.0, 101.0, 99.5, 100.5, 1.0) for j in range(50))

    class _Agg:
        def bars(self): return five_bars

    class _State:
        periods = frozenset({"K_1M", "K_5M", "K_15M"})
        aggregators = {"K_5M": _Agg()}

    engine.state = _State()
    win._pane_combos[1].setCurrentText("K_5M")   # pane 1: K_3M → K_5M（desired == current）
    assert engine.switch_calls == []             # 週期集合未變 → 唔使 fetch
    assert win._panes[1]._bars == five_bars      # 直接推 snapshot


def test_route_period_bars_routes_to_matching_panes(monkeypatch):
    """(period, bars) signal → 路由去所有 combo 顯示該週期嘅 pane（多 pane 同週期都收到）。"""
    from datetime import datetime, timedelta
    win, _engine = _make_window(monkeypatch)
    base = datetime(2026, 1, 5, 9, 30)
    bars = tuple(((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                  1.0, 2.0, 0.5, 1.5, 1.0) for i in range(10))
    win._pane_combos[1].setCurrentText("K_1M")   # pane 1 同 pane 0 一樣 K_1M
    win._on_history_ready("K_1M", bars)
    assert win._panes[0]._bars == bars
    assert win._panes[1]._bars == bars
    assert win._panes[2]._bars == ()             # pane 2 = K_5M → 唔收到


def test_on_code_activated_sets_code_and_name(monkeypatch):
    """Dropdown 選中 → 輸入欄只留 canonical code + switch + 名稱 LABEL 同步。"""
    win, engine = _make_window(monkeypatch)
    entries = _entries()
    win._on_catalog_ready(entries)
    aapl = entries[2]
    win._on_code_activated(display_text(aapl))
    assert win.code_edit.text() == "US.AAPL"  # 名稱唔入輸入欄
    assert engine.switch_calls == [("US.AAPL", ("K_15M", "K_1M", "K_3M", "K_5M"))]  # sorted() 字典序
    assert win.name_label.text() == name_text(aapl)


def test_text_changed_guard_strips_name_on_change(monkeypatch):
    """onChange guard：completer setCompletion() 寫入完整 display_text（code + 名稱）→
    textChanged handler 即刻剝離返純 code，欄位唔會同時持有代碼同名稱。"""
    win, _engine = _make_window(monkeypatch)
    win._on_catalog_ready(_entries())
    # 模擬 popup 開住撳 Enter：setCompletion() 喺 activated 前寫入完整 display_text（雙空格）
    win.code_edit.setText("HK.HSImain  恒指期货主连")
    assert win.code_edit.text() == "HK.HSImain"


def test_text_changed_guard_noop_for_pure_code(monkeypatch):
    """純編號輸入（無空白）→ guard no-op，唔改動欄位。"""
    win, _engine = _make_window(monkeypatch)
    win.code_edit.setText("hk.00700")
    assert win.code_edit.text() == "hk.00700"


def test_text_changed_guard_strips_name_before_catalog(monkeypatch):
    """目錄未載入時 guard 一樣生效（唔依賴 catalog）。"""
    win, _engine = _make_window(monkeypatch)
    win.code_edit.setText("US.AAPL  Apple Inc.")
    assert win.code_edit.text() == "US.AAPL"


def test_indicator_toggle_buttons_exist_and_default_off(monkeypatch):
    """control bar「指標」區：INDICATOR_TOGGLES 每個 entry 一個 checkable 按鍵、預設 off。"""
    win, _engine = _make_window(monkeypatch)
    assert set(win._indicator_btns) == {"ob", "fvg", "vob", "brk", "kz", "ref", "liq"}
    for btn in win._indicator_btns.values():
        assert btn.isCheckable()
        assert not btn.isChecked()


def test_indicator_toggle_applies_to_all_panes(monkeypatch):
    """click 開關 → 全部 4 pane（含隱藏）_indicator_enabled 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    win._indicator_btns["ob"].click()
    assert win._indicator_btns["ob"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("ob") is True
    win._indicator_btns["ob"].click()
    for pane in win._panes:
        assert pane._indicator_enabled.get("ob") is False


def test_indicator_toggles_independent(monkeypatch):
    """兩個開關非 exclusive：OB 同 FVG 可以同時 on（confluence 派生前提）。"""
    win, _engine = _make_window(monkeypatch)
    win._indicator_btns["ob"].click()
    win._indicator_btns["fvg"].click()
    assert win._indicator_btns["ob"].isChecked()
    assert win._indicator_btns["fvg"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("ob") is True
        assert pane._indicator_enabled.get("fvg") is True


def test_second_batch_toggles_apply_to_all_panes(monkeypatch):
    """第二批開關（BRK / KZ / REF）click → 全部 4 pane _indicator_enabled 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    for key in ("brk", "kz", "ref"):
        win._indicator_btns[key].click()
        assert win._indicator_btns[key].isChecked()
        for pane in win._panes:
            assert pane._indicator_enabled.get(key) is True
    for key in ("brk", "kz", "ref"):
        win._indicator_btns[key].click()
        for pane in win._panes:
            assert pane._indicator_enabled.get(key) is False


def test_vob_toggle_applies_to_all_panes(monkeypatch):
    """VOB 開關 click → 全部 4 pane（含隱藏）_indicator_enabled["vob"] 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    win._indicator_btns["vob"].click()
    assert win._indicator_btns["vob"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("vob") is True
    win._indicator_btns["vob"].click()
    for pane in win._panes:
        assert pane._indicator_enabled.get("vob") is False


def test_liq_toggle_applies_to_all_panes(monkeypatch):
    """LIQ 開關 click → 全部 4 pane（含隱藏）_indicator_enabled["liq"] 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    win._indicator_btns["liq"].click()
    assert win._indicator_btns["liq"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("liq") is True
    win._indicator_btns["liq"].click()
    for pane in win._panes:
        assert pane._indicator_enabled.get("liq") is False
