"""全屏幕終端主窗口：control bar + CandleChart + FutuEngine 接線 + 狀態列。

- 頂部 control bar：標的編號輸入欄（fuzzy autocomplete：編號 / 中英文名、簡繁兼容，
  目錄由 engine `catalog_ready` 一次性載入）+ K 線週期 combo，
  returnPressed / dropdown activated → engine.switch(code, kline_type) 運行時切換。
- F11 切換全屏幕；Esc 關閉（README Features）。
- Engine signals（callback/setup thread emit）經 Qt auto-queue 過 GUI thread：
  history_ready / bars_changed → chart.update_bars；status / error → status bar；
  catalog_ready → completer model rebuild。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QVBoxLayout, QWidget)

from config import KLINE_TYPES
from engine.futu_engine import FutuEngine
from .candle_chart import CandleChart
from .stock_completer import StockCompleter


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
        """頂部 control bar：標的編號輸入欄 + K 線週期 combo（深色主題跟 cfg 配色）。"""
        cfg = self._cfg
        bar = QFrame()
        bar.setFixedHeight(40)
        bar.setStyleSheet(
            f"QFrame {{ background: {cfg.grid_color}; border-bottom: 1px solid {cfg.axis_text_color}; }}"
            f"QLabel {{ color: {cfg.text_color}; font-family: Consolas; padding-left: 8px; }}"
            f"QLineEdit, QComboBox {{"
            f" background: {cfg.bg_color}; color: {cfg.text_color};"
            f" border: 1px solid {cfg.axis_text_color}; border-radius: 4px;"
            f" padding: 2px 8px; font-family: Consolas; }}"
        )
        h = QHBoxLayout(bar)
        h.setContentsMargins(8, 0, 8, 0)
        h.addWidget(QLabel("標的"))

        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("編號 / 中英文名（模糊匹配，例：騰訊、AAPL、hsimain）")
        self.code_edit.setText(cfg.trading_code)
        self.code_edit.setFixedWidth(340)
        # Fuzzy autocomplete：目錄由 engine catalog_ready 載入；activated → 用 canonical code switch
        self._completer = StockCompleter(self)
        self._code_by_text: dict[str, str] = {}
        self._completer.activated.connect(self._on_code_activated)
        self.code_edit.setCompleter(self._completer)
        h.addWidget(self.code_edit)

        h.addSpacing(16)
        h.addWidget(QLabel("週期"))

        self.period_combo = QComboBox()
        # 先 set items/index 再 connect（避免初始設定觸發 activated → switch）
        self.period_combo.addItems(list(KLINE_TYPES))
        idx = KLINE_TYPES.index(cfg.kline_type) if cfg.kline_type in KLINE_TYPES else 0
        self.period_combo.setCurrentIndex(idx)
        h.addWidget(self.period_combo)

        h.addStretch(1)

        def _do_switch():
            # 一次 action 傳齊兩個值（避免連續兩次 switch）
            self._engine.switch(code=self.code_edit.text(),
                                kline_type=self.period_combo.currentText())

        self.code_edit.returnPressed.connect(_do_switch)
        self.period_combo.activated.connect(lambda _idx: _do_switch())
        return bar

    def _on_catalog_ready(self, entries) -> None:
        """Engine setup thread fetch 完 HK+US 目錄 → rebuild completer model（GUI thread）。"""
        self._code_by_text = self._completer.set_catalog(tuple(entries))

    def _on_code_activated(self, text: str) -> None:
        """Dropdown 選中一行 → 用嚴格大小寫 canonical code switch（保留當前週期）。"""
        code = self._code_by_text.get(text)
        if not code:
            return
        self.code_edit.setText(code)
        self._engine.switch(code=code, kline_type=self.period_combo.currentText())

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
