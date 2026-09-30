"""CandleChart widget 級單測（offscreen Qt，零真實 OpenD 連線）。

覆蓋：zoom_in()/zoom_out() 按鍵分步縮放（每點擊一階 ×/÷1.25、中心錨定）、
min/max 可見根數 clamp、無數據 no-op；last-price 虛線 + 右軸 tag 回歸測試
（必須跟隨真正最新一根 bar self._bars[-1]，唔係可見視窗最右邊嗰根；最新價超出
當前 Y 範圍 → 整條隱藏）；wheel_notches 正規化由 test_candle_chart.py 純函數單測覆蓋。
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtGui import QColor, QPixmap  # noqa: E402
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


class TestLastPriceLine:
    """last-price 虛線 + 右軸 tag 回歸測試（offscreen pixel 級驗證）。"""

    @staticmethod
    def _render(ch, w=800, h=600):
        ch.resize(w, h)
        pix = QPixmap(ch.size())
        ch.render(pix)
        return pix.toImage()

    @staticmethod
    def _count_in(img, color, x0, x1, y0, y1):
        n = 0
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if img.pixelColor(x, y) == color:
                    n += 1
        return n

    @staticmethod
    def _mixed_bars(last_close):
        bars = [(f"2026-09-30 09:{i:02d}", 100.0, 101.0, 99.5, 100.0, 1000.0) for i in range(199)]
        bars.append(("2026-09-30 10:00", last_close - 50.0, last_close + 10.0,
                     last_close - 60.0, last_close, 1000.0))
        return tuple(bars)

    def test_tag_follows_true_latest_bar_when_panned_left(self):
        # 200 bars：前 199 根 close=100，真正最新一根（index 199）close=200。
        # pan 左 offset=80 → 可見視窗 = bars[0:120]（全部 close=100）；
        # last-price 線必須畫喺 y_price(200)，唔係可見視窗最右邊嗰根嘅 100。
        ch = CandleChart(Config())
        ch.update_bars(self._mixed_bars(200.0))
        ch._right_offset = 80.0
        ch._y_range = (50.0, 300.0)
        img = self._render(ch)
        lp = QColor("#FFB020")
        # 800×600 → price_r=(12,34,710,411.2)：y(200)=198.48→row 198；y(100)=362.96→row 362
        tag_x = (724, 795)  # 右軸 tag x 範圍（price_r.right()+2 .. +_M_RIGHT-6）
        assert self._count_in(img, lp, *tag_x, 189, 207) > 800   # 真正最新價 200 嘅 tag 喺呢度
        assert self._count_in(img, lp, *tag_x, 353, 371) == 0    # 唔喺可見視窗最右 bar close=100

    def test_line_hidden_when_latest_price_out_of_y_range(self):
        # 最新價 132 超出手動 Y 範圍 (90,130) → y(132)=13.44 喺 price 區頂部之上；
        # 冇 bounds-check 會喺頂 margin 畫出線 + tag，修好後整張圖零 last-price 色像素。
        ch = CandleChart(Config())
        ch.update_bars(self._mixed_bars(132.0))
        ch._right_offset = 80.0
        ch._y_range = (90.0, 130.0)
        img = self._render(ch)
        assert self._count_in(img, QColor("#FFB020"), 0, ch.width() - 1, 0, ch.height() - 1) == 0
