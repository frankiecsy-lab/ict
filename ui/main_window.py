"""全屏幕終端主窗口：CandleChart + FutuEngine 接線 + 狀態列。

- F11 切換全屏幕；Esc 關閉（README Features）。
- Engine signals（callback/setup thread emit）經 Qt auto-queue 過 GUI thread：
  history_ready / bars_changed → chart.update_bars；status / error → status bar。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QMainWindow, QLabel

from engine.futu_engine import FutuEngine
from .candle_chart import CandleChart


class MainWindow(QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self._cfg = cfg
        self.setWindowTitle("ICT Trader")
        self.resize(1280, 800)

        self.chart = CandleChart(cfg)
        self.setCentralWidget(self.chart)

        # 深色主題（status bar / label 跟 .env 配色）
        self.setStyleSheet(
            f"QMainWindow {{ background: {cfg.bg_color}; }}"
            f"QStatusBar {{ background: {cfg.bg_color}; color: {cfg.text_color}; border: none; }}"
            f"QLabel {{ color: {cfg.text_color}; font-family: Consolas; }}"
        )
        sb = self.statusBar()
        sb.showMessage("連線 OpenD 中…", 0)

        # Engine（QObject child → 同 window 一齊收）；start() spawn daemon setup thread
        self._engine = FutuEngine(self)
        self._engine.history_ready.connect(self.chart.update_bars)
        self._engine.bars_changed.connect(self.chart.update_bars)
        self._engine.status.connect(lambda m: sb.showMessage(m, 8000))
        self._engine.error.connect(self._on_error)
        self._engine.start(cfg)

    def _on_error(self, msg: str) -> None:
        label = QLabel(f"⚠ {msg}")
        self.statusBar().addWidget(label, 1)
        # 保留最後一條 error 喺 status bar（唔會自動消失）；新 status message 會另計

    def shutdown(self) -> None:
        """Clean shutdown：close OpenD context + join setup thread（idempotent）。"""
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
