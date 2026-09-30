"""CandleChart widget 級單測（offscreen Qt，零真實 OpenD 連線）。

覆蓋：zoom_in()/zoom_out() 按鍵分步縮放（每點擊一階 ×/÷1.25、中心錨定）、
min/max 可見根數 clamp、無數據 no-op；wheel_notches 正規化由 test_candle_chart.py
純函數單測覆蓋。
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from config import Config  # noqa: E402
from ui.candle_chart import CandleChart, visible_window  # noqa: E402

_app = QApplication.instance() or QApplication([])


def _bars(n: int):
    return tuple((f"2026-09-30 09:{i:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0) for i in range(n))


def _chart(n_bars: int = 500) -> CandleChart:
    ch = CandleChart(Config())
    if n_bars:
        ch.update_bars(_bars(n_bars))
    return ch


class TestZoomButtons:
    def test_zoom_in_one_stage_divides_by_1_25(self):
        ch = _chart()
        assert ch._view_count == 120  # Config 預設 visible_bars
        ch.zoom_in()
        assert ch._view_count == 96   # round(120 / 1.25)

    def test_zoom_out_one_stage_multiplies_by_1_25(self):
        ch = _chart()
        ch.zoom_out()
        assert ch._view_count == 150  # round(120 * 1.25)

    def test_repeated_stages_clamp_at_min_5_bars(self):
        ch = _chart()
        for _ in range(50):
            ch.zoom_in()
        assert ch._view_count == 5

    def test_repeated_stages_clamp_at_max_2000_bars(self):
        ch = _chart(n_bars=1000)
        for _ in range(300):
            ch.zoom_out()
        assert ch._view_count == 2000

    def test_no_bars_is_noop(self):
        ch = _chart(0)
        before = (ch._view_count, ch._right_offset)
        ch.zoom_in()
        ch.zoom_out()
        assert (ch._view_count, ch._right_offset) == before

    def test_zoom_in_center_anchor_keeps_middle_bar(self):
        # total=500、初始 count=120 右 pin → 視窗 [380,500)、中心 bar global index 440。
        # zoom in（count=96）後 440 應保持喺新視窗 f=0.5 位置。
        ch = _chart(500)
        ch.zoom_in()
        assert ch._view_count == 96
        win = visible_window(_bars(500), ch._view_count, ch._right_offset)
        start = len(_bars(500)) - int(round(ch._right_offset)) - len(win)
        assert (440 - start) / ch._view_count == pytest.approx(0.5)

    def test_zoom_in_then_out_round_trips(self):
        # 120 → 96 → round(96*1.25)=120（分步縮放可逆，右 pin 亦還原）
        ch = _chart()
        ch.zoom_in()
        ch.zoom_out()
        assert (ch._view_count, ch._right_offset) == (120, 0.0)
