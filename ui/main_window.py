"""全屏幕終端主窗口：control bar + CandleChart + FutuEngine 接線 + 狀態列。

- 頂部 control bar：標的編號輸入欄（**只收純編號**——含空白即拒絕；目錄載入後經
  `StockCatalog.canonical_code()` 驗證存在並正規化大小寫，未知編號 → status bar 報錯唔切換）
  + 獨立名稱 LABEL（`name_text()`：中英文名顯示喺輸入欄外，名稱永不入 TEXT FIELD）+
  K 線週期按鍵組（checkable + autoExclusive），returnPressed / 按鍵點擊 →
  engine.switch(code, kline_type) 運行時切換。
- F11 切換全屏幕；Esc 關閉（README Features）。
- Engine signals（callback/setup thread emit）經 Qt auto-queue 過 GUI thread：
  history_ready / bars_changed → chart.update_bars；status / error → status bar；
  catalog_ready → completer model rebuild + 名稱 LABEL 初始化。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QVBoxLayout, QWidget)

from config import KLINE_TYPES
from engine.futu_engine import FutuEngine
from engine.stock_catalog import name_text
from .candle_chart import CandleChart
from .stock_completer import StockCompleter, code_from_completion


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

        self.chart = CandleChart(cfg)

        # Engine（QObject child → 同 window 一齊收）；start() spawn daemon setup thread
        self._engine = FutuEngine(self)
        self._engine.history_ready.connect(self.chart.update_bars)
        self._engine.bars_changed.connect(self.chart.update_bars)
        self._engine.status.connect(lambda m: sb.showMessage(m, 8000))
        self._engine.error.connect(self._on_error)
        self._engine.catalog_ready.connect(self._on_catalog_ready)

        # Central：container + 頂部 control bar + chart（0 margin/spacing，全屏幕感不變）
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_control_bar())
        layout.addWidget(self.chart)
        self.setCentralWidget(central)

        self._engine.start(cfg)

    def _build_control_bar(self):
        """頂部 control bar：標的編號輸入欄 + K 線週期按鍵組（深色主題跟 cfg 配色）。"""
        cfg = self._cfg
        bar = QFrame()
        bar.setFixedHeight(40)
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
        h = QHBoxLayout(bar)
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
        h.addWidget(self.code_edit)

        # 獨立名稱 LABEL：顯示當前標的嘅中英文名（名稱唔入輸入欄）；目錄載入後初始化
        self.name_label = QLabel("")
        self.name_label.setMinimumWidth(200)
        h.addWidget(self.name_label)

        h.addSpacing(16)
        h.addWidget(QLabel("週期"))

        # K 線週期按鍵組（checkable + autoExclusive）：取代 dropdown，一鍵直切
        self._period_group = QButtonGroup(self)
        self._period_group.setExclusive(True)
        for name in KLINE_TYPES:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._period_group.addButton(btn)
            h.addWidget(btn)
            if cfg.kline_type == name:
                btn.setChecked(True)  # 先 set checked 再 connect（避免初始觸發 switch）

        h.addStretch(1)

        self.code_edit.returnPressed.connect(self._do_switch)
        self._period_group.buttonClicked.connect(lambda _btn: self._do_switch())
        return bar

    def current_period(self) -> str:
        """當前選中嘅 K 線週期名（button group checked button text）。"""
        btn = self._period_group.checkedButton()
        return btn.text() if btn else KLINE_TYPES[0]

    def _do_switch(self):
        """ReturnPressed / 週期按鍵 → 驗證輸入欄純編號存在先 switch（名稱唔入輸入欄）。"""
        raw = self.code_edit.text()
        if not raw.strip():
            self.statusBar().showMessage("請輸入股票編號", 8000)
            return
        # 含空白 = 混入咗名稱（例：「HK.00700 騰訊」）→ 拒絕，只收純編號
        if any(ch.isspace() for ch in raw):
            self.statusBar().showMessage("輸入欄只可填純編號（唔好包含股票名稱）", 8000)
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
        self._engine.switch(code=code, kline_type=self.current_period())

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
        self._engine.switch(code=code, kline_type=self.current_period())

    def _update_name_label(self, raw_code: str | None) -> None:
        """獨立 LABEL 顯示當前標的嘅中英文名（`name_text()`）；目錄未載入/未知 code → 清空。"""
        catalog = self._completer.catalog()
        code = catalog.canonical_code(raw_code) if len(catalog) and raw_code else None
        entry = next((e for e in catalog.entries if e.code == code), None)
        self.name_label.setText(name_text(entry) if entry else "")

    def _on_error(self, msg: str) -> None:
        label = QLabel(f"⚠ {msg}")
        self.statusBar().addWidget(label, 1)
        # 保留最後一條 error 喺 status bar（唔會自動消失）；新 status message 會另計

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
