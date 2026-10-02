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
from engine.stock_catalog import (StockEntry, basic_info_text, display_text, name_text)  # noqa: E402
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
    connection_state = Signal(bool, float)   # (connected, latency_ms) — 右下角連線狀態 + 延遲
    smt_history_ready = Signal(str, tuple)   # (period, bars) — SMT Divergence 配對副標的 seed snapshot
    smt_bars_changed = Signal(str, tuple)    # (period, bars) — SMT tick 聚合更新

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.switch_calls: list[tuple[str | None, tuple[str, ...] | None]] = []
        self.start_periods: list[str] | None = None   # start(periods=...) 記錄
        self.start_code: str | None = None            # start(code=...) 記錄（UI-state 記憶還原）
        self.start_smt: bool = False                  # start(smt=...) 記錄（SMT Divergence 開機啟用）
        self.smt_switches: list[bool] = []            # switch(smt=on/off) 記錄（運行時啟用/停用副標的訂閱）
        self.state = None                              # _State | None——替身無活躍狀態

    def start(self, cfg, db_path=None, periods=None, code=None, smt=False) -> None:  # noqa: ARG002 — 替身唔連線
        self.start_periods = list(periods) if periods else None
        self.start_code = code
        self.start_smt = bool(smt)

    def stop(self) -> None:
        pass

    def switch(self, code=None, periods=None, smt=None) -> None:
        # switch_calls 保持 (code, periods) 2-tuple（既有斷言格式）；smt 另計
        self.switch_calls.append((code, tuple(sorted(periods)) if periods is not None else None))
        if smt is not None:
            self.smt_switches.append(bool(smt))


class FakeStateStore:
    """替身 UI state store：記錄 save 呼叫、返回預設 load（唔觸碰真實 SQLite）。

    `_load_value` 預設 None = 無記憶（startup fallback 預設值）；測試可喺構造 window **前**
    set `store._load_value = {...}` 模擬「上次有保存過嘅狀態」。save() 每次記錄一份快照。
    """

    def __init__(self, path=None) -> None:   # noqa: ARG002 — 替身唔開 DB
        self.path = path
        self.saved: list[dict] = []          # 每次 save() 記錄一份 dict 快照
        self._load_value: dict | None = None

    def save(self, state: dict) -> None:
        self.saved.append(dict(state))

    def load(self):
        return self._load_value

    def clear(self) -> None:
        self._load_value = None


def _entries():
    # HK.HSImain 無基本資料（seed 主力連續合約唔喺 API 列表——真實行為）；其餘兩隻有 lot_size/listing_date
    return [
        StockEntry("HK.HSImain", "恒指期货主连", ""),
        StockEntry("HK.00700", "腾讯控股", "TENCENT", lot_size=500, listing_date="2004-06-16"),
        StockEntry("US.AAPL", "苹果", "Apple Inc.", lot_size=1, listing_date="2016-06-09"),
    ]


def _make_window(monkeypatch, saved_state: dict | None = None) -> tuple[MainWindow, FakeEngine]:
    """構造 MainWindow（fake engine + fake UI state store）。

    `saved_state` 預設 None = 無記憶（startup fallback 預設值）；傳入 dict → 模擬「上次保存過」
    嘅狀態俾 `_load_ui_state()` 還原。fake store 可經 `win._state_store` 存取（斷言 save）。
    """
    engine = FakeEngine()
    monkeypatch.setattr(mw_module, "FutuEngine", lambda parent=None: engine)
    store = FakeStateStore()
    if saved_state is not None:
        store._load_value = dict(saved_state)
    monkeypatch.setattr(mw_module, "UIStateStore", lambda path=None: store)
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


def test_catalog_ready_initializes_info_label_empty_for_seed(monkeypatch):
    """catalog_ready → 基本資料行：seed 主力連續合約無 lot_size/listing_date → 空白。"""
    win, _engine = _make_window(monkeypatch)
    assert win.info_label.text() == ""  # 目錄未載入前空白
    win._on_catalog_ready(_entries())
    assert win.info_label.text() == ""  # HK.HSImain seed 無基本資料


def test_do_switch_updates_info_label(monkeypatch):
    """切換標的 → 基本資料行同步更新（每手股數 · 上市日期）。"""
    win, _engine = _make_window(monkeypatch)
    win._on_catalog_ready(_entries())
    win.code_edit.setText("HK.00700")
    win._do_switch()
    assert win.info_label.text() == basic_info_text(_entries()[1])  # "每手 500 · 上市 2004-06-16"


def test_unknown_code_clears_name_and_info_labels(monkeypatch):
    """未知 code → 名稱 + 基本資料兩個 LABEL 都清空。"""
    win, _engine = _make_window(monkeypatch)
    win._on_catalog_ready(_entries())
    win.code_edit.setText("HK.00700")
    win._do_switch()
    assert win.info_label.text() == "每手 500 · 上市 2004-06-16"
    win._update_name_label("HK.NOSUCH")
    assert win.name_label.text() == ""
    assert win.info_label.text() == ""


def test_pane_zoom_button_affects_only_own_pane(monkeypatch):
    """每 pane 獨立縮放按鍵（異步縮放）：click pane 0「放大」只改 pane 0，其他 pane 不受影響。

    按鍵接線用零參數 lambda——PySide6 clicked 有 (bool checked) 重載，直接 connect
    zoom_in(steps=1) 會靜默綁定 bool 版 → no-op（踩坑記錄見 AGENTS.md 附錄 #4）。
    """
    from datetime import datetime, timedelta
    win, _engine = _make_window(monkeypatch)
    base = datetime(2026, 1, 5, 9, 30)
    m_bars = tuple(((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                    100.0, 101.0, 99.5, 100.5, 1.0) for i in range(200))
    w_bars = tuple(((base + timedelta(minutes=3 * j)).strftime("%Y-%m-%d %H:%M"),
                    100.0, 101.0, 99.5, 100.5, 1.0) for j in range(200))
    win._panes[0].update_bars(m_bars)   # pane 0（200 根分鐘 bar）
    win._panes[1].update_bars(w_bars)   # pane 1（200 根 3 分鐘 bar）
    win._set_pane_count(2)              # 顯示 2 pane
    assert win._panes[0]._view_count == 120
    assert win._panes[1]._view_count == 120
    win._pane_zoom_in[0].click()        # click pane 0 嘅「放大」按鍵
    assert win._panes[0]._view_count == 96   # 120 / 1.25 → 96（中心錨定）
    assert win._panes[1]._view_count == 120  # pane 1 不受影響——無跨 pane 同步


def test_no_cross_pane_sync_on_zoom(monkeypatch):
    """異步縮放：用戶喺 pane 0 zoom/pan（wheel/drag/按鍵路徑 → emit view_changed）唔會廣播去其他 pane。"""
    from datetime import datetime, timedelta
    win, _engine = _make_window(monkeypatch)
    base = datetime(2026, 1, 5, 9, 30)
    m_bars = tuple(((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                    100.0, 101.0, 99.5, 100.5, 1.0) for i in range(200))
    w_bars = tuple(((base + timedelta(minutes=3 * j)).strftime("%Y-%m-%d %H:%M"),
                    100.0, 101.0, 99.5, 100.5, 1.0) for j in range(200))
    win._panes[0].update_bars(m_bars)   # pane 0 = K_1M（200 根分鐘 bar）
    win._panes[1].update_bars(w_bars)   # pane 1 = K_3M（200 根 3 分鐘 bar）
    win._set_pane_count(2)              # 顯示 2 pane
    before = (win._panes[1]._view_count, win._panes[1]._right_offset)
    win._panes[0].zoom_in()             # 模擬用戶喺 pane 0 zoom（emit view_changed）
    start = base + timedelta(minutes=80)
    end = base + timedelta(minutes=200)
    assert win._panes[0].set_time_window(start, end)   # 模擬用戶 pan/zoom 時間視窗改變
    assert (win._panes[1]._view_count, win._panes[1]._right_offset) == before  # pane 1 完全不變


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
    assert win.info_label.text() == basic_info_text(aapl)  # "每手 1 · 上市 2016-06-09"


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
    assert set(win._indicator_btns) == {"ob", "fvg", "vob", "brk", "kz", "ref", "liq", "bos", "pd", "ote", "shl", "wmref"}
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


def test_bos_toggle_applies_to_all_panes(monkeypatch):
    """BOS 開關 click → 全部 4 pane（含隱藏）_indicator_enabled["bos"] 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    win._indicator_btns["bos"].click()
    assert win._indicator_btns["bos"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("bos") is True
    win._indicator_btns["bos"].click()
    for pane in win._panes:
        assert pane._indicator_enabled.get("bos") is False


def test_pd_ote_toggles_apply_to_all_panes(monkeypatch):
    """PD / OTE 開關 click → 全部 4 pane（含隱藏）_indicator_enabled 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    for key in ("pd", "ote"):
        win._indicator_btns[key].click()
        assert win._indicator_btns[key].isChecked()
        for pane in win._panes:
            assert pane._indicator_enabled.get(key) is True
    for key in ("pd", "ote"):
        win._indicator_btns[key].click()
        for pane in win._panes:
            assert pane._indicator_enabled.get(key) is False


def test_shl_toggle_applies_to_all_panes(monkeypatch):
    """SHL（Session High/Low）開關 click → 全部 4 pane _indicator_enabled["shl"] 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    win._indicator_btns["shl"].click()
    assert win._indicator_btns["shl"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("shl") is True
    win._indicator_btns["shl"].click()
    for pane in win._panes:
        assert pane._indicator_enabled.get("shl") is False


def test_wmref_toggle_applies_to_all_panes(monkeypatch):
    """W/M（Weekly/Monthly ref lines）開關 click → 全部 4 pane _indicator_enabled["wmref"] 同步翻轉；再 click 還原。"""
    win, _engine = _make_window(monkeypatch)
    win._indicator_btns["wmref"].click()
    assert win._indicator_btns["wmref"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("wmref") is True
    win._indicator_btns["wmref"].click()
    for pane in win._panes:
        assert pane._indicator_enabled.get("wmref") is False


# ---------------------------------------------------------------- UI state persistence（SQLite 記憶）

def test_startup_loads_saved_state(monkeypatch):
    """開機還原上次 UI 狀態：code / pane count / per-pane periods / indicator toggles。"""
    saved = {
        "code": "US.AAPL",
        "pane_count": 4,
        "periods": ["K_5M", "K_15M", "K_30M", "K_60M"],
        "indicators": ["ob", "fvg"],
    }
    win, engine = _make_window(monkeypatch, saved_state=saved)
    # code → 輸入欄 + start(code=...)（engine 用還原嘅標的，唔係 cfg.trading_code）
    assert win.code_edit.text() == "US.AAPL"
    assert engine.start_code == "US.AAPL"
    # pane count / layout：_pane_count 還原 + layout 按鍵 checked 狀態同步（「4」checked、「1」uncheck）
    assert win._pane_count == 4
    btn4 = next(b for b in win._layout_group.buttons() if b.text() == "4")
    btn1 = next(b for b in win._layout_group.buttons() if b.text() == "1")
    assert btn4.isChecked()
    assert not btn1.isChecked()
    # load 期間唔觸發 save（setChecked 唔 emit clicked → 唔經 _on_layout_clicked）
    assert win._state_store.saved == []
    # per-pane periods（combo 還原）+ start(periods=...) = 全 pane union
    assert [c.currentText() for c in win._pane_combos] == ["K_5M", "K_15M", "K_30M", "K_60M"]
    assert sorted(engine.start_periods) == ["K_15M", "K_30M", "K_5M", "K_60M"]
    # indicator toggles（button checked + 全部 pane enabled）
    assert win._indicator_btns["ob"].isChecked()
    assert win._indicator_btns["fvg"].isChecked()
    assert not win._indicator_btns["vob"].isChecked()
    for pane in win._panes:
        assert pane._indicator_enabled.get("ob") is True
        assert pane._indicator_enabled.get("fvg") is True
        assert pane._indicator_enabled.get("vob") is False


def test_startup_no_saved_state_uses_defaults(monkeypatch):
    """無記憶（load → None）→ 全部 fallback 預設值：cfg.trading_code / 單 pane / indicators off。"""
    win, engine = _make_window(monkeypatch)   # saved_state=None
    assert win.code_edit.text() == "HK.HSImain"   # cfg.trading_code 預設
    assert engine.start_code is None              # → engine fallback cfg.trading_code
    assert win._pane_count == 1
    # layout 按鍵 default「1」checked（無記憶 → 構造時預設）
    btn1 = next(b for b in win._layout_group.buttons() if b.text() == "1")
    assert btn1.isChecked()
    for btn in win._indicator_btns.values():
        assert not btn.isChecked()


def test_startup_ignores_malformed_saved_state(monkeypatch):
    """損壞 / 缺字段嘅 saved state → 靜默跳過該字段（唔 crash、fallback 預設）。"""
    # code 有效；pane_count=3 非法、periods 長度錯配、indicators 非 list → 全部忽略
    win, engine = _make_window(monkeypatch, saved_state={
        "code": "US.AAPL",
        "pane_count": 3,
        "periods": ["K_5M"],
        "indicators": "ob",
    })
    assert win.code_edit.text() == "US.AAPL"      # code 有效 → 還原
    assert engine.start_code == "US.AAPL"
    assert win._pane_count == 1                   # pane_count=3 非法 → 保持預設 1
    for btn in win._indicator_btns.values():
        assert not btn.isChecked()                # indicators 非 list → 全 off


def test_save_on_indicator_toggle(monkeypatch):
    """click 指標開關 → _save_ui_state 寫入快照（indicators 含該 key）；startup load 唔會 save。"""
    win, _engine = _make_window(monkeypatch)
    assert win._state_store.saved == []   # startup load（無記憶）唔觸發 save
    win._indicator_btns["ob"].click()
    assert len(win._state_store.saved) == 1
    snap = win._state_store.saved[-1]
    assert "ob" in snap["indicators"]
    assert snap["pane_count"] == 1


def test_save_on_layout_change(monkeypatch):
    """click layout「4」→ _save_ui_state 寫入 pane_count=4。"""
    win, _engine = _make_window(monkeypatch)
    btn4 = next(b for b in win._layout_group.buttons() if b.text() == "4")
    btn4.click()
    assert win._pane_count == 4
    snap = win._state_store.saved[-1]
    assert snap["pane_count"] == 4


def test_save_on_pane_period_change(monkeypatch):
    """換某 pane combo 週期 → _save_ui_state 寫入新 periods。"""
    win, engine = _make_window(monkeypatch)
    win._pane_combos[0].setCurrentText("K_5M")   # currentTextChanged → _on_pane_period_changed(0)
    assert len(win._state_store.saved) == 1
    snap = win._state_store.saved[-1]
    assert snap["periods"][0] == "K_5M"
    # engine switch 收到新 union（含 K_5M）
    assert any("K_5M" in (p or ()) for _c, p in engine.switch_calls)


def test_save_on_code_switch(monkeypatch):
    """切換標的 → _save_ui_state 寫入新 code。"""
    win, engine = _make_window(monkeypatch)
    win.code_edit.setText("US.AAPL")   # textChanged guard：無空白 → no-op
    win._do_switch()                    # catalog 空 → 放行 → _apply_code_switch → switch + save
    assert len(win._state_store.saved) == 1
    snap = win._state_store.saved[-1]
    assert snap["code"] == "US.AAPL"
    assert engine.switch_calls and engine.switch_calls[-1][0] == "US.AAPL"


# ---------------------------------------------------------------- OpenD 連線狀態顯示（右下角）

def test_format_latency_units():
    """format_latency：<1ms → µs；≥1ms → ms；負數/None → "—"。"""
    assert mw_module.format_latency(0.32) == "320µs"
    assert mw_module.format_latency(0.999) == "999µs"    # 邊界：<1ms 仍用 µs（0.999ms = 999µs）
    assert mw_module.format_latency(1.0) == "1.0ms"      # 邊界：≥1ms 轉 ms
    assert mw_module.format_latency(4.256) == "4.3ms"
    assert mw_module.format_latency(-1.0) == "—"         # 斷線 / 未知
    assert mw_module.format_latency(None) == "—"


def test_connection_label_initial_disconnected(monkeypatch):
    """右下角 label 初始 = ● OpenD 未連線（紅），且掛喺 status bar（addPermanentWidget → 右側）。"""
    win, _engine = _make_window(monkeypatch)
    assert win._conn_label.text() == "● OpenD 未連線"
    assert "#F23645" in win._conn_label.styleSheet()     # 初始斷線色（紅）
    assert win._conn_label.parent() is win.statusBar()   # status bar permanent widget（右下角）


def test_connection_state_updates_label(monkeypatch):
    """connection_state signal → label 文字 + 顏色：已連線（綠 + µs/ms 自適應）/ 斷線（紅）。"""
    win, engine = _make_window(monkeypatch)
    engine.connection_state.emit(True, 0.32)
    assert "已連線" in win._conn_label.text() and "320µs" in win._conn_label.text()
    assert "#089981" in win._conn_label.styleSheet()     # 已連線 → 綠
    engine.connection_state.emit(True, 4.256)            # ≥1ms → ms 單位（顏色唔重寫）
    assert "4.3ms" in win._conn_label.text()
    assert "#089981" in win._conn_label.styleSheet()
    engine.connection_state.emit(False, -1.0)
    assert win._conn_label.text() == "● OpenD 未連線"
    assert "#F23645" in win._conn_label.styleSheet()     # 斷線 → 紅


# ------------------------------------------------------------- 跨視窗同步 signals（code_changed / last_price）

def _bars_with_close(close: float = 1.5):
    """(time_key, o, h, l, c, v) bar tuple——close = index 4。"""
    from datetime import datetime, timedelta
    base = datetime(2026, 1, 5, 9, 30)
    return tuple(((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                  1.0, 2.0, 0.5, close, 1.0) for i in range(3))


def test_code_changed_emitted_on_apply_code_switch(monkeypatch):
    """_apply_code_switch → code_changed emit（所有入口：returnPressed / dropdown activated）。"""
    win, _engine = _make_window(monkeypatch)
    events: list[str] = []
    win.code_changed.connect(events.append)

    win._apply_code_switch("US.AAPL")
    assert events == ["US.AAPL"]


def test_last_price_emitted_from_primary_handlers(monkeypatch):
    """_on_history_ready / _on_bars_changed → last_price = bars[-1][4]（收市價）。"""
    win, _engine = _make_window(monkeypatch)
    prices: list[float] = []
    win.last_price.connect(prices.append)

    win._on_history_ready("K_1M", _bars_with_close(320.75))
    assert prices == [320.75]

    win._on_bars_changed("K_1M", _bars_with_close(321.5))
    assert prices == [320.75, 321.5]


def test_last_price_not_emitted_on_empty_or_smt(monkeypatch):
    """空 bars → 唔 emit；SMT 副標的 handler → 唔 emit（副標的價唔應該驅動主下單欄）。"""
    win, _engine = _make_window(monkeypatch)
    prices: list[float] = []
    win.last_price.connect(prices.append)

    win._on_history_ready("K_1M", ())      # 空 snapshot → 唔 emit
    win._on_bars_changed("K_1M", ())       # 同上
    assert prices == []

    win._on_smt_bars("K_1M", _bars_with_close(99.0))   # SMT handler → 無 last_price emit
    assert prices == []
