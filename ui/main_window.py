"""全屏幕終端主窗口：control bar + CandleChart + FutuEngine 接線 + 狀態列。

- 頂部 control bar：標的編號輸入欄（**只收純編號**——onChange guard `textChanged` 即刻剝離
  「code + 名稱」，目錄載入後經 `StockCatalog.canonical_code()` 驗證存在並正規化大小寫，
  未知編號 → status bar 報錯唔切換）
  + **onChange guard**（`textChanged`：completer `setCompletion()` 會喺 activated 前將完整
    display_text「code + 名稱」寫入欄位 → handler 即刻剝離返純 code，欄位永不同時持有代碼同名稱）
  + 獨立名稱 LABEL（`name_text()`：中英文名顯示喺輸入欄外，名稱永不入 TEXT FIELD）+
  K 線週期按鍵組（checkable + autoExclusive）+ 右側**放大/縮小按鍵**（每點擊 = 一階 ×/÷1.25
  分步 X 軸縮放，多段式唔再直跳 min/max 極限），returnPressed / 按鍵點擊 →
  engine.switch(code, kline_type) 運行時切換。
- F11 切換全屏幕；Esc 關閉（README Features）。
- Engine signals（callback/setup thread emit）經 Qt auto-queue 過 GUI thread：
  history_ready / bars_changed → chart.update_bars；status / error → status bar；
  smt_history_ready / smt_bars_changed → chart.set_smt_bars（SMT Divergence 配對副標的 snapshot，
  同週期路由去各 pane）；catalog_ready → completer model rebuild + 名稱 LABEL 初始化；
  connection_state(bool, float) → **右下角**連線狀態 + 反應速度（µs/ms，addPermanentWidget）。
"""
from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (QButtonGroup, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget)

from config import KLINE_TYPES
from engine.futu_engine import FutuEngine
from engine.stock_catalog import basic_info_text, name_text
from engine.ui_state_store import UIStateStore, default_ui_state_path
from .candle_chart import CandleChart
from .stock_completer import StockCompleter, code_from_completion

logger = logging.getLogger(__name__)

# 指標開關註冊表（模組化擴展點）：加新指標 = 喺呢度加一行 → control bar 自動生成對應 checkable 按鍵。
# 偵測邏輯喺 engine/indicators.py、繪製層喺 candle_chart._recompute_zones() / paintEvent；
# key 必須同 CandleChart.set_indicator() 認得嘅 key 一致（"ob"/"fvg"/"vob"/"brk"/"kz"/"ref"/"liq"/"bos"/"pd"/"ote"/"shl"/"wmref"/"smt"）。
# "smt" 條件顯示：.env 未設 SMT_CODE（無配對副標的）→ control bar 唔生成該按鍵。
INDICATOR_TOGGLES: tuple[tuple[str, str], ...] = (
    ("ob", "OB"), ("fvg", "FVG"), ("vob", "VOB"), ("brk", "BRK"), ("kz", "KZ"),
    ("ref", "REF"), ("liq", "LIQ"), ("bos", "BOS"), ("pd", "PD"), ("ote", "OTE"),
    ("shl", "SHL"), ("wmref", "W/M"), ("smt", "SMT")
)

# OpenD 連線狀態指示色（獨立於市場慣例漲跌色——已連線恆綠、斷線恆紅，唔隨 convention 翻轉）
_CONN_OK_COLOR = "#089981"    # teal green（= HK down_color）
_CONN_BAD_COLOR = "#F23645"   # red（= HK up_color）


def format_latency(ms: float | None) -> str:
    """延遲顯示：<1ms → µs 精度、≥1ms → ms；負數/None → "—"（斷線 / 未知）。

    「反應速度微秒ms」：本地 OpenD RTT 通常 sub-millisecond，<1ms 顯示 µs（例 320µs）、
    否則 ms（例 4.2ms）——一個函數兩種單位自適應。
    """
    if ms is None or ms < 0:
        return "—"
    if ms < 1.0:
        return f"{ms * 1000:.0f}µs"
    return f"{ms:.1f}ms"


class MainWindow(QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self._cfg = cfg
        self.setWindowTitle("ICT Trader")
        self.resize(1280, 800)

        # 深色主題（status bar / label 跟 .env 配色）
        self.setStyleSheet(
            f"QMainWindow {{ background: {cfg.bg_color}; }}"
            f"QStatusBar {{ background: {cfg.bg_color}; color: {cfg.text_color}; border: none; }}"
            f"QLabel {{ color: {cfg.text_color}; font-family: Consolas; }}"
        )
        sb = self.statusBar()
        sb.showMessage("連線 OpenD 中…", 0)

        self._syncing = False   # Defensive 保留：移除跨 pane 同步後已無 reader；仍包住會 emit view_changed 嘅 reset_view()，防日後重接 listener 誤廣播

        self.chart = CandleChart(cfg)
        # 多 pane 圖表區：pane 0 = self.chart（兼容既有測試）；panes 1..3 預建、由 1/2/4 layout 按鍵顯示。
        # 每個 pane = 頂部週期 combo + 獨立放大/縮小按鍵 + CandleChart（各 pane 獨立選週期、異步縮放）。
        self._panes: list[CandleChart] = []
        self._pane_combos: list[QComboBox] = []
        self._pane_widgets: list[QWidget] = []
        self._pane_zoom_in: list[QPushButton] = []
        self._pane_zoom_out: list[QPushButton] = []
        for i in range(4):
            widget, combo, pane = self._build_pane_widget(i)
            self._pane_widgets.append(widget)
            self._pane_combos.append(combo)
            self._panes.append(pane)

        # Engine（QObject child → 同 window 一齊收）；start() spawn daemon setup thread。
        # per-period signals (period, bars) → 按週期路由去對應 pane。
        self._engine = FutuEngine(self)
        self._engine.history_ready.connect(self._on_history_ready)
        self._engine.bars_changed.connect(self._on_bars_changed)
        self._engine.smt_history_ready.connect(self._on_smt_bars)   # SMT 配對副標的 snapshot（seed/switch 完成）
        self._engine.smt_bars_changed.connect(self._on_smt_bars)    # SMT tick 聚合更新
        self._engine.status.connect(lambda m: sb.showMessage(m, 8000))
        self._engine.error.connect(self._on_error)
        self._engine.catalog_ready.connect(self._on_catalog_ready)
        # 右下角：OpenD 連線狀態 + 反應速度（µs/ms）——addPermanentWidget = status bar 右側永久 widget。
        self._conn_label = QLabel("● OpenD 未連線")
        self._conn_ok: bool | None = None   # 上次連線狀態（只在翻轉時改色，避免每 ping 重寫 stylesheet）
        self._conn_label.setStyleSheet(f"color: {_CONN_BAD_COLOR}; font-family: Consolas;")
        sb.addPermanentWidget(self._conn_label)
        self._engine.connection_state.connect(self._on_connection_state)

        # Central：container + 頂部 control bar + pane grid（0 margin/spacing，全屏幕感不變）
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_control_bar())
        self._pane_grid = QGridLayout()
        self._pane_grid.setContentsMargins(2, 2, 2, 2)
        self._pane_grid.setHorizontalSpacing(4)
        self._pane_grid.setVerticalSpacing(4)
        layout.addLayout(self._pane_grid, 1)
        self.setCentralWidget(central)

        self._pane_count = 1
        self._set_pane_count(1)   # 初始單 pane（self.chart）
        self._layout_panes()      # grid 初始排布（pane 0 @ (0,0)）
        # UI 狀態記憶：開機還原上次嘅 code / layout / periods / indicators。喺 engine.start()
        # **之前**——set combos/layout/indicators 時 engine 未 start，唔會觸發 switch；start()
        # 讀 _desired_periods() + code= 一次到位（saved_code=None → cfg.trading_code）。
        self._state_store = UIStateStore(default_ui_state_path())
        saved_code = self._load_ui_state()
        # SMT Divergence：還原後嘅按鍵 checked 狀態（.env 無 SMT_CODE → 冇按鍵 → False）→ start() 一次到位
        smt_btn = self._indicator_btns.get("smt")
        smt_on = bool(smt_btn.isChecked()) if smt_btn is not None else False
        # 開機即 fetch 全部 pane 週期（setup thread 內逐個 seed；GUI 唔使事後重試 switch）
        self._engine.start(cfg, periods=list(self._desired_periods()), code=saved_code, smt=smt_on)

    def _build_pane_widget(self, index: int) -> tuple[QWidget, QComboBox, CandleChart]:
        """單一 pane：頂部週期 combo + 獨立放大/縮小按鍵 + CandleChart。返回 (container, combo, chart)。"""
        cfg = self._cfg
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)

        combo = QComboBox()
        for name in KLINE_TYPES:
            combo.addItem(name)
        if index == 0 and cfg.kline_type in KLINE_TYPES:
            combo.setCurrentText(cfg.kline_type)   # pane 0 預設跟 .env kline_type
        else:
            combo.setCurrentIndex(min(index, len(KLINE_TYPES) - 1))  # 其餘 pane 錯開週期
        combo.setStyleSheet(
            f"QComboBox {{ background: {cfg.bg_color}; color: {cfg.text_color};"
            f" border: 1px solid {cfg.axis_text_color}; border-radius: 3px; padding: 0 6px;"
            f" font-family: Consolas; min-height: 20px; }}"
        )
        combo.currentTextChanged.connect(lambda _t, i=index: self._on_pane_period_changed(i))

        chart = CandleChart(cfg) if index else self.chart
        # 異步縮放：每個 pane 完全獨立（wheel/drag/按鍵都只影響本 pane），無跨 pane 時間同步。
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(combo)
        header.addStretch(1)
        zin = QPushButton("放大")
        zout = QPushButton("縮小")
        for _b in (zin, zout):
            _b.setCursor(Qt.CursorShape.PointingHandCursor)
        # lambda 包零參數調用：PySide6 clicked 有 (bool checked) 重載，直接 connect zoom_in(steps=1)
        # 會靜默綁定 bool 版 → no-op（踩坑記錄見 AGENTS.md 附錄）；closure 捕獲本 pane chart、天然獨立。
        zin.clicked.connect(lambda: chart.zoom_in())
        zout.clicked.connect(lambda: chart.zoom_out())
        header.addWidget(zin)
        header.addWidget(zout)
        v.addLayout(header)
        self._pane_zoom_in.append(zin)
        self._pane_zoom_out.append(zout)
        v.addWidget(chart, 1)
        return container, combo, chart

    def _set_pane_count(self, count: int) -> None:
        """切換 1/2/4 pane layout：顯示對應 pane、隱藏其餘（pane 數據保留，唔重建）。"""
        self._pane_count = count
        for i in range(4):
            self._pane_widgets[i].setVisible(i < count)

    def _layout_panes(self) -> None:
        """按當前 pane 數重排 grid：1=單格 / 2=左右 / 4=2x2。"""
        n = self._pane_count
        for i in range(4):
            w = self._pane_widgets[i]
            if i >= n:
                continue
            if n == 1:
                r, c = 0, 0
            elif n == 2:
                r, c = 0, i
            else:
                r, c = divmod(i, 2)
            self._pane_grid.addWidget(w, r, c)

    def _build_control_bar(self):
        """頂部 control bar（兩行）：第一行 = 標的編號輸入欄 + K 線週期按鍵組；
        第二行 = 當前標的基本資料 LABEL（每手股數 / 上市日期，深色主題跟 cfg 配色）。"""
        cfg = self._cfg
        bar = QFrame()
        bar.setStyleSheet(
            f"QFrame {{ background: {cfg.grid_color}; border-bottom: 1px solid {cfg.axis_text_color}; }}"
            f"QLabel {{ color: {cfg.text_color}; font-family: Consolas; padding-left: 8px; }}"
            f"QLineEdit {{"
            f" background: {cfg.bg_color}; color: {cfg.text_color};"
            f" border: 1px solid {cfg.axis_text_color}; border-radius: 4px;"
            f" padding: 2px 8px; font-family: Consolas; }}"
            f"QPushButton {{"
            f" background: {cfg.bg_color}; color: {cfg.text_color};"
            f" border: 1px solid {cfg.axis_text_color}; border-radius: 4px;"
            f" padding: 2px 8px; font-family: Consolas; }}"
            f"QPushButton:hover {{ background: {cfg.grid_color}; }}"
            f"QPushButton:checked {{"
            f" background: {cfg.last_price_color}; color: {cfg.bg_color};"
            f" border-color: {cfg.last_price_color}; font-weight: bold; }}"
        )
        v = QVBoxLayout(bar)
        v.setContentsMargins(0, 2, 0, 2)
        v.setSpacing(2)
        h = QHBoxLayout()
        h.setContentsMargins(8, 0, 8, 0)
        h.addWidget(QLabel("標的"))

        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("純編號（例：HK.00700 / US.AAPL）")
        self.code_edit.setText(cfg.trading_code)
        self.code_edit.setFixedWidth(240)
        # Fuzzy autocomplete：目錄由 engine catalog_ready 載入；activated → 用 canonical code switch
        self._completer = StockCompleter(self)
        self._code_by_text: dict[str, str] = {}
        self._completer.activated.connect(self._on_code_activated)
        self.code_edit.setCompleter(self._completer)
        # onChange (textChanged) guard：completer setCompletion() 會喺 activated 前將完整
        # display_text（code + 名稱）寫入輸入欄 → 即刻剝離返純 code
        self.code_edit.textChanged.connect(self._on_code_text_changed)
        h.addWidget(self.code_edit)

        # 獨立名稱 LABEL：顯示當前標的嘅中英文名（名稱唔入輸入欄）；目錄載入後初始化
        self.name_label = QLabel("")
        self.name_label.setMinimumWidth(200)
        h.addWidget(self.name_label)

        h.addSpacing(16)
        h.addWidget(QLabel("佈局"))

        # 1/2/4 pane layout 按鍵組（checkable + autoExclusive）：週期選擇已下放各 pane combo
        self._layout_group = QButtonGroup(self)
        self._layout_group.setExclusive(True)
        for n in (1, 2, 4):
            btn = QPushButton(str(n))
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._layout_group.addButton(btn)
            h.addWidget(btn)
            if n == 1:
                btn.setChecked(True)  # 先 set checked 再 connect（避免初始觸發 layout）
        self._layout_group.buttonClicked.connect(lambda _btn: self._on_layout_clicked())

        # 指標開關（checkable、非 exclusive）：每個 INDICATOR_TOGGLES entry 一個按鍵；
        # toggled → 全部 pane 同步（含隱藏——狀態同 pane 數據一樣保留）
        h.addSpacing(16)
        h.addWidget(QLabel("指標"))
        self._indicator_btns: dict[str, QPushButton] = {}
        for key, label in INDICATOR_TOGGLES:
            if key == "smt" and not self._cfg.smt_code:
                continue   # .env 未設 SMT_CODE（無配對副標的）→ 唔生成 SMT 按鍵
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # lambda 包參數：避開 signal overload 綁定陷阱（踩坑記錄見 AGENTS.md 附錄）；
            # 預設 off → setChecked 唔會觸發，無初始觸發問題
            btn.toggled.connect(lambda on, k=key: self._on_indicator_toggled(k, bool(on)))
            h.addWidget(btn)
            self._indicator_btns[key] = btn

        h.addStretch(1)

        self.code_edit.returnPressed.connect(self._do_switch)
        # 放大/縮小按鍵已移去各 pane header row（異步縮放、每 pane 獨立，見 _build_pane_widget）。
        v.addLayout(h)

        # 第二行：當前標的基本資料（每手股數 / 上市日期）——目錄載入後由 _update_name_label() 填充；
        # widget-level stylesheet 覆蓋 bar 級 QLabel 顏色 → 較暗色區分主控制行
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(
            f"color: {cfg.axis_text_color}; font-family: Consolas; padding-left: 8px;"
        )
        h2 = QHBoxLayout()
        h2.setContentsMargins(0, 0, 8, 0)
        h2.addWidget(self.info_label)
        h2.addStretch(1)
        v.addLayout(h2)
        return bar

    def _desired_periods(self) -> frozenset[str]:
        """全部 4 pane combo 週期 union = engine 目標活躍週期集合。

        與可見性無關（隱藏 pane 嘅週期都保持活躍）：layout 切換即時有數據、唔會 stale；
        OpenD 訂閱額度零額外成本（單一 QUOTE 訂閱 → N aggregator fan-out）。
        """
        return frozenset(c.currentText() for c in self._pane_combos)

    # ------------------------------------------------------------- UI state persistence（SQLite 記憶）

    def _load_ui_state(self) -> str | None:
        """開機還原上次 UI 狀態：code / pane count / per-pane periods / indicator toggles。

        喺 engine.start() **之前**呼叫——set combos/layout/indicators 時 engine 未 start，
        唔會觸發 switch；start() 讀 _desired_periods() + code= 一次到位。返回 saved code
        （None → engine fallback cfg.trading_code）。任何字段缺失 / 損壞 → 靜默跳過該字段
        （記憶係輔助功能，唔應該阻斷啟動）。
        """
        state = self._state_store.load()
        if not isinstance(state, dict):
            return None

        # pane count / layout（1/2/4）：set + relayout（同 _on_layout_clicked 一樣搬位）
        n = state.get("pane_count")
        if n in (1, 2, 4) and n != self._pane_count:
            self._set_pane_count(n)
            for i in range(4):   # removeWidget 先至 addWidget 會真正搬位（Qt grid 唔會自動 move）
                self._pane_grid.removeWidget(self._pane_widgets[i])
            self._layout_panes()
            # 同步 layout 按鍵 checked 狀態：構造時 default「1」checked，還原 pane count 後要將
            # 對應按鍵 setChecked(True)（exclusive group 自動 uncheck 其餘）。programmatic
            # setChecked 唔會 emit clicked → 唔觸發 _on_layout_clicked / save。
            for btn in self._layout_group.buttons():
                if btn.text() == str(n):
                    btn.blockSignals(True)
                    try:
                        btn.setChecked(True)
                    finally:
                        btn.blockSignals(False)

        # per-pane periods：blockSignals——engine 未 start，setCurrentText 唔會觸發 switch
        periods = state.get("periods")
        if isinstance(periods, list) and len(periods) == len(self._pane_combos):
            for i, combo in enumerate(self._pane_combos):
                p = periods[i]
                if p in KLINE_TYPES:
                    combo.blockSignals(True)
                    try:
                        combo.setCurrentText(p)
                    finally:
                        combo.blockSignals(False)

        # indicator toggles：setChecked（blockSignals 避免觸發 handler）+ 直接同步 pane
        indicators = state.get("indicators")
        if isinstance(indicators, list):
            want_set = set(indicators)
            for key, btn in self._indicator_btns.items():
                want = key in want_set
                if btn.isChecked() != want:
                    btn.blockSignals(True)
                    try:
                        btn.setChecked(want)
                    finally:
                        btn.blockSignals(False)
                # 直接同步 pane（唔經 handler → load 期間唔會觸發 save）；pane 預設全 off
                for pane in self._panes:
                    pane.set_indicator(key, want)

        # code：set 輸入欄（blockSignals 避免觸發 textChanged guard）+ 返回俾 start()
        code = state.get("code")
        if isinstance(code, str) and code.strip():
            self.code_edit.blockSignals(True)
            try:
                self.code_edit.setText(code)
            finally:
                self.code_edit.blockSignals(False)
            return code
        return None

    def _save_ui_state(self) -> None:
        """寫入當前 UI 狀態快照（code / pane count / per-pane periods / indicator toggles）。

        由四個 change handler 呼叫（用戶操作、低頻、極小寫入）→ on-change save，唔需要 debounce。
        store 失敗 → 靜默忽略（記憶係輔助功能，唔應該阻斷主流程）。
        """
        try:
            state = {
                "pane_count": self._pane_count,
                "periods": [c.currentText() for c in self._pane_combos],
                "indicators": [k for k, b in self._indicator_btns.items() if b.isChecked()],
            }
            code = self.code_edit.text().strip()
            if code:
                state["code"] = code
            self._state_store.save(state)
        except Exception:  # noqa: BLE001 — persistence is best-effort，唔阻斷主流程
            logger.exception("UI state save failed")

    def _do_switch(self):
        """ReturnPressed / 週期按鍵 → 驗證輸入欄純編號存在先 switch（名稱唔入輸入欄）。

        onChange guard（`_on_code_text_changed`）已確保欄位永遠無空白，呢度只需處理空欄。
        """
        raw = self.code_edit.text()
        if not raw.strip():
            self.statusBar().showMessage("請輸入股票編號", 8000)
            return
        catalog = self._completer.catalog()
        code = None
        if len(catalog):
            # 目錄已載入 → 驗證存在 + 正規化嚴格大小寫（例：hk.00700 → HK.00700）
            code = catalog.canonical_code(raw)
            if code is None:
                self.statusBar().showMessage(f"股票編號唔存在：{raw.strip()}", 8000)
                return
        else:
            # 目錄未載入（catalog fetch 失敗等）→ 放行俾 engine/OpenD 最終校驗
            code = raw.strip()
        self.code_edit.setText(code)
        self._update_name_label(code)
        self._apply_code_switch(code)

    def _apply_code_switch(self, code: str) -> None:
        """標的驗證通過 → 重置全部 pane 視圖 + engine switch（periods = 全 pane combo union）。

        舊 Y range / pan offset 對新數據無意義；_syncing guard 阻 reset_view emit view_changed
        廣播去其他 pane（切換標的唔應該連帶移動其他 pane 時間視窗——新數據到齊後各 pane 右 pin）。
        """
        self._syncing = True
        try:
            for pane in self._panes:
                pane.reset_view()
        finally:
            self._syncing = False
        self._engine.switch(code=code, periods=list(self._desired_periods()))
        self._save_ui_state()   # 標的改變 → 記憶（code + 當前 layout/periods/indicators）

    def _on_code_text_changed(self, text: str) -> None:
        """onChange guard：欄位出現「code + 名稱」（含空白）→ 即刻剝離返純 code。

        QCompleter `setCompletion()` 會喺 `activated` signal 之前將完整 display_text
        （例「HK.HSImain 恒指期货主连」）寫入輸入欄——呢度確保任何路徑下欄位都唔會
        同時持有代碼同名稱。剝離後無空白 → 再觸發嘅 textChanged 自然 no-op，唔死循環；
        blockSignals 避免多餘 signal round-trip。
        """
        if not any(ch.isspace() for ch in text):
            return
        tokens = [t for t in text.split() if t]
        code = tokens[0] if tokens else ""
        self.code_edit.blockSignals(True)
        try:
            self.code_edit.setText(code)
        finally:
            self.code_edit.blockSignals(False)

    def _on_catalog_ready(self, entries) -> None:
        """Engine setup thread fetch 完 HK+US 目錄 → rebuild completer model（GUI thread）。"""
        self._code_by_text = self._completer.set_catalog(tuple(entries))
        # 目錄到手 → 用當前輸入欄 code 初始化名稱 LABEL
        self._update_name_label(self.code_edit.text())

    def _on_code_activated(self, text: str) -> None:
        """Dropdown 選中一行 → 輸入欄只留 code（名稱唔入 TEXT FIELD）→ switch。

        `code_from_completion()` 由 mapping 還原嚴格大小寫 canonical code；mapping miss 時取
        display_text 第一 token（code 永遠係第一 whitespace token）兜底——確保任何路徑下輸入欄
        都只出現 code，唔會殘留 dropdown 顯示嘅中英文名。
        """
        code = code_from_completion(text, self._code_by_text)
        if not code:
            return
        self.code_edit.setText(code)
        self._update_name_label(code)
        self._apply_code_switch(code)

    def _update_name_label(self, raw_code: str | None) -> None:
        """獨立 LABEL 顯示當前標的嘅中英文名（`name_text()`）+ 基本資料行（`basic_info_text()`：
        每手股數 / 上市日期）；目錄未載入/未知 code → 兩個 LABEL 都清空。"""
        catalog = self._completer.catalog()
        code = catalog.canonical_code(raw_code) if len(catalog) and raw_code else None
        entry = next((e for e in catalog.entries if e.code == code), None)
        self.name_label.setText(name_text(entry) if entry else "")
        self.info_label.setText(basic_info_text(entry) if entry else "")

    def _on_error(self, msg: str) -> None:
        label = QLabel(f"⚠ {msg}")
        self.statusBar().addWidget(label, 1)
        # 保留最後一條 error 喺 status bar（唔會自動消失）；新 status message 會另計

    def _on_connection_state(self, connected: bool, latency_ms: float) -> None:
        """connection_state signal → 右下角 label：● OpenD 已連線 · 320µs / ● OpenD 未連線。"""
        if self._conn_ok is not connected:   # 只在狀態翻轉時改色（避免每 ping 重寫 stylesheet）
            color = _CONN_OK_COLOR if connected else _CONN_BAD_COLOR
            self._conn_label.setStyleSheet(f"color: {color}; font-family: Consolas;")
            self._conn_ok = connected
        if connected:
            self._conn_label.setText(f"● OpenD 已連線 · {format_latency(latency_ms)}")
        else:
            self._conn_label.setText("● OpenD 未連線")

    # ------------------------------------------------------------- panes / time sync

    def _route_period_bars(self, period: str, bars) -> None:
        """(period, bars) → 所有 combo 顯示該週期嘅 pane（可多 pane 同週期）。"""
        for i in range(len(self._panes)):
            if self._pane_combos[i].currentText() == period:
                self._panes[i].update_bars(bars)

    def _on_history_ready(self, period: str, bars) -> None:
        """Engine seed/switch 完成 → 路由完整 snapshot 去對應 pane（per-period signal）。"""
        self._route_period_bars(period, bars)

    def _on_bars_changed(self, period: str, bars) -> None:
        """Tick 聚合更新 → 路由新 snapshot 去對應 pane。"""
        self._route_period_bars(period, bars)

    def _on_smt_bars(self, period: str, bars) -> None:
        """SMT 配對副標的 snapshot（seed/switch/tick）→ 同週期路由去各 pane（set_smt_bars 只存 + coalesce repaint）。"""
        for i in range(len(self._panes)):
            if self._pane_combos[i].currentText() == period:
                self._panes[i].set_smt_bars(bars)

    def _on_pane_period_changed(self, i: int) -> None:
        """某 pane combo 換週期 → reset 該 pane 視圖 + engine switch（periods = 全 pane union）。

        新週期 → 舊 Y range / pan offset 無意義；_syncing guard 阻 reset_view broadcast。
        若目標週期已活躍（其他 pane 用緊）→ 直接推當前 snapshot，唔使等下一筆 tick。
        """
        new_period = self._pane_combos[i].currentText()
        desired = self._desired_periods()
        state = self._engine.state
        current = state.periods if state is not None else frozenset()
        self._syncing = True
        try:
            self._panes[i].reset_view()
        finally:
            self._syncing = False
        if desired != current:
            # 週期集合改變 → worker thread fetch+seed 差集；history_ready 會路由返去各 pane
            self._engine.switch(periods=list(desired))
        elif state is not None and new_period in state.aggregators:
            # 該週期已活躍（其他 pane 用緊）→ 直接推當前 snapshot，唔使等下一筆 tick
            self._panes[i].update_bars(state.aggregators[new_period].bars())
        self._save_ui_state()   # per-pane 週期改變 → 記憶

    def _on_layout_clicked(self) -> None:
        """1/2/4 layout 按鍵 → 顯示/隱藏 pane + grid 重排（pane 數據保留、唔重建）。"""
        btn = self._layout_group.checkedButton()
        if btn is None:
            return
        n = int(btn.text())
        if n == self._pane_count:
            return
        self._set_pane_count(n)
        for i in range(4):   # removeWidget 先至 addWidget 會真正搬位（Qt grid 唔會自動 move）
            self._pane_grid.removeWidget(self._pane_widgets[i])
        self._layout_panes()
        self._save_ui_state()   # layout 改變 → 記憶（early return 已確保只喺真改變時 save）

    def _on_indicator_toggled(self, key: str, on: bool) -> None:
        """指標開關 → 同步全部 4 pane（含隱藏——狀態同 pane 數據一樣保留）。

        "smt" 特殊：除圖層外仲要 engine 端訂閱配對副標的（雙訂閱）→ switch(smt=on/off)。
        setup/switch 進行中時 engine 會 status 提示並 reject（pane 圖層狀態照樣翻轉，
        下輪 toggle 或重開 app 會再同步）。
        """
        for pane in self._panes:
            pane.set_indicator(key, on)
        if key == "smt":
            self._engine.switch(smt=on)   # 啟用/停用 SMT 配對副標的訂閱（worker thread）
        self._save_ui_state()   # 指標開關改變 → 記憶

    def shutdown(self) -> None:
        """Clean shutdown：close OpenD context + join setup/switch threads（idempotent）。"""
        self._engine.stop()

    # ------------------------------------------------------------- keys

    def keyPressEvent(self, event: QKeyEvent):  # noqa: N802 (Qt naming)
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
