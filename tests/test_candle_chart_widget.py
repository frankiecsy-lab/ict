"""CandleChart widget 級單測（offscreen Qt，零真實 OpenD 連線）。

覆蓋：zoom_in()/zoom_out() 按鍵分步縮放（每點擊一階 ×/÷1.25、中心錨定）、
min/max 可見根數 clamp、無數據 no-op；last-price 虛線 + 右軸 tag 回歸測試
（必須跟隨真正最新一根 bar self._bars[-1]，唔係可見視窗最右邊嗰根；最新價超出
當前 Y 範圍 → 整條隱藏）；wheel_notches 正規化由 test_candle_chart.py 純函數單測覆蓋。
"""
from __future__ import annotations

import os
from datetime import datetime

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


class TestTimeWindowApi:
    """time_window()/set_time_window()/view_changed——多 pane 時間軸同步 API。"""

    def test_time_window_right_pinned(self):
        # 30 bars 10:00..10:29（period=1min）；count=10 右 pin → 可見 index 20..29（10:20..10:29）。
        # end = 尾根 start(10:29) + period(1min) = 10:30。
        ch = CandleChart(Config())
        bars = tuple((f"2026-09-30 {10 + i // 60:02d}:{i % 60:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0)
                     for i in range(30))
        ch.update_bars(bars)
        assert ch._period_minutes == 1
        ch._view_count = 10
        ch._right_offset = 0.0
        rng = ch.time_window()
        assert rng == (datetime(2026, 9, 30, 10, 20), datetime(2026, 9, 30, 10, 30))

    def test_time_window_no_bars_returns_none(self):
        ch = CandleChart(Config())
        assert ch.time_window() is None

    def test_set_time_window_aligns_view(self):
        # 30 bars 10:00..10:29（period=1min）；對齊到 (10:05, 10:14) → span-overlap index 5..13。
        ch = CandleChart(Config())
        bars = tuple((f"2026-09-30 {10 + i // 60:02d}:{i % 60:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0)
                     for i in range(30))
        ch.update_bars(bars)
        ok = ch.set_time_window(datetime(2026, 9, 30, 10, 5), datetime(2026, 9, 30, 10, 14))
        assert ok is True
        assert ch._view_count == 9          # index 5..13（含尾）= 9 根
        assert round(ch._right_offset) == 16  # n-1-e = 29-13

    def test_set_time_window_no_match_is_noop(self):
        ch = CandleChart(Config())
        bars = tuple((f"2026-09-30 {10 + i // 60:02d}:{i % 60:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0)
                     for i in range(30))
        ch.update_bars(bars)
        before = (ch._view_count, ch._right_offset)
        ok = ch.set_time_window(datetime(2026, 9, 30, 15, 0), datetime(2026, 9, 30, 15, 5))
        assert ok is False
        assert (ch._view_count, ch._right_offset) == before

    def test_set_time_window_no_bars_is_noop(self):
        ch = CandleChart(Config())
        assert ch.set_time_window(datetime(2026, 9, 30, 10, 5), datetime(2026, 9, 30, 10, 14)) is False

    def test_set_time_window_does_not_emit_view_changed(self):
        """程序化同步唔 emit view_changed（防回授循環）。"""
        ch = CandleChart(Config())
        bars = tuple((f"2026-09-30 {10 + i // 60:02d}:{i % 60:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0)
                     for i in range(30))
        ch.update_bars(bars)
        emitted = []
        ch.view_changed.connect(lambda s, e: emitted.append((s, e)))
        ch.set_time_window(datetime(2026, 9, 30, 10, 5), datetime(2026, 9, 30, 10, 14))
        assert emitted == []

    def test_zoom_in_emits_view_changed(self):
        """用戶 zoom（按鍵）→ emit view_changed。"""
        ch = CandleChart(Config())
        bars = tuple((f"2026-09-30 {10 + i // 60:02d}:{i % 60:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0)
                     for i in range(30))
        ch.update_bars(bars)
        emitted = []
        ch.view_changed.connect(lambda s, e: emitted.append((s, e)))
        ch.zoom_in()
        assert len(emitted) == 1
        start_dt, end_dt = emitted[0]
        # zoom in 後視窗收窄、右 pin → end = 尾根 bar start(10:29) + period(1min) = 10:30
        assert end_dt == datetime(2026, 9, 30, 10, 30)

    def test_reset_view_emits_view_changed(self):
        """reset_view() 重置視窗 → emit view_changed。"""
        ch = CandleChart(Config())
        bars = tuple((f"2026-09-30 {10 + i // 60:02d}:{i % 60:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0)
                     for i in range(30))
        ch.update_bars(bars)
        ch._view_count = 8
        ch._right_offset = 20.0
        emitted = []
        ch.view_changed.connect(lambda s, e: emitted.append((s, e)))
        ch.reset_view()
        assert len(emitted) == 1

    def test_reset_view_no_bars_does_not_emit(self):
        ch = CandleChart(Config())
        emitted = []
        ch.view_changed.connect(lambda s, e: emitted.append((s, e)))
        ch.reset_view()
        assert emitted == []


class TestTimeWindowSyncRoundTrip:
    """跨 pane 同步：pane A 嘅 time_window → pane B set_time_window（不同週期 bar 密度）。"""

    def test_minute_to_day_alignment(self):
        # pane A = 5min bars、pane B = 日線 bars；A 視窗套去 B 應對齊到當日一根。
        ch_a = CandleChart(Config())
        a_bars = tuple((f"2026-09-30 {10 + i // 60:02d}:{i % 60:02d}", 100.0, 101.0, 99.5, 100.5, 1000.0)
                       for i in range(30))  # 10:00..10:29（全喺 09-30）
        ch_a.update_bars(a_bars)
        rng = ch_a.time_window()
        assert rng is not None

        ch_b = CandleChart(Config())
        b_bars = tuple((f"2026-{m:02d}-15", 100.0, 101.0, 99.5, 100.5, 1000.0) for m in (8, 9, 10))
        ch_b.update_bars(b_bars)
        ok = ch_b.set_time_window(rng[0], rng[1])
        assert ok is True
        # B 只匹配到 2026-09-15（當日）一根 → count=1、offset=n-1-e=3-1-1=1
        assert ch_b._view_count == 1
        assert round(ch_b._right_offset) == 1


class TestIndicatorToggles:
    """ICT 指標層（OB / FVG / Confluence）：set_indicator() 立即 recompute + pixel 級驗證。

    crafted 5-bar 序列（手算驗證過嘅 zone 結果）：
      b0 [8.8,9.5] c=9.4↑、b1 [9.3,9.6] c=9.5↑、b2 [10.5,12] c=11.9↑（強陽線）、
      b3 [9.8,10.6] c=9.9↓（pullback）、b4 [9.9,13] c=12.8↑（BOS up trigger）
    → FVG [9.5,10.5]@2 + FVG [9.6,9.8]@3、OB [9.9,10.4]@3（origin=b3 body）、
      confluence = OB ∩ FVG@2 重疊帶 [9.9,10.4]@3。
    """

    @staticmethod
    def _render(ch, w=800, h=600):
        ch.resize(w, h)
        pix = QPixmap(ch.size())
        ch.render(pix)
        return pix.toImage()

    @staticmethod
    def _diff_count(img_a, img_b, threshold: int = 32) -> int:
        """兩張 render 差異像素數（alpha-blended fill 唔可以精確色計數 → 用 diff）。"""
        n = 0
        for y in range(img_a.height()):
            for x in range(img_a.width()):
                ca, cb = img_a.pixelColor(x, y), img_b.pixelColor(x, y)
                if (abs(ca.red() - cb.red()) + abs(ca.green() - cb.green())
                        + abs(ca.blue() - cb.blue())) > threshold:
                    n += 1
        return n

    @staticmethod
    def _count_in(img, color) -> int:
        n = 0
        for y in range(img.height()):
            for x in range(img.width()):
                if img.pixelColor(x, y) == color:
                    n += 1
        return n

    @staticmethod
    def _fvg_bars():
        """3 bars 含已知 bullish FVG [10, 11]@2（c1.high=10 < c3.low=11）。"""
        return (
            ("2026-09-30 09:00", 9.0, 10.0, 8.5, 9.5, 1000.0),
            ("2026-09-30 09:01", 9.5, 10.5, 9.0, 10.4, 1000.0),
            ("2026-09-30 09:02", 10.5, 12.0, 11.0, 11.8, 1000.0),
        )

    @staticmethod
    def _confluence_bars():
        return (
            ("2026-09-30 09:00", 9.0, 9.5, 8.8, 9.4, 1000.0),
            ("2026-09-30 09:01", 9.4, 9.6, 9.3, 9.5, 1000.0),
            ("2026-09-30 09:02", 9.7, 12.0, 10.5, 11.9, 1000.0),
            ("2026-09-30 09:03", 10.4, 10.6, 9.8, 9.9, 1000.0),
            ("2026-09-30 09:04", 10.0, 13.0, 9.9, 12.8, 1000.0),
        )

    def test_default_no_indicators_enabled(self):
        ch = _chart(50)
        assert ch._indicator_enabled == {}
        assert ch._zones == {}

    def test_set_indicator_fvg_recomputes_immediately(self):
        """set_indicator() 同步重算（唔使等 30ms repaint timer）。"""
        from engine.indicators import Zone
        ch = CandleChart(Config())
        ch.update_bars(self._fvg_bars())
        assert ch._zones == {}                       # 預設全 off
        ch.set_indicator("fvg", True)
        assert ch._zones["fvg"] == (Zone("fvg", "bullish", 2, None, 11.0, 10.0),)

    def test_set_indicator_off_clears_zones(self):
        ch = CandleChart(Config())
        ch.update_bars(self._fvg_bars())
        ch.set_indicator("fvg", True)
        assert "fvg" in ch._zones
        ch.set_indicator("fvg", False)
        assert ch._zones == {}

    def test_ob_and_fvg_zone_values_on_crafted_sequence(self):
        """5-bar 序列 → 手算驗證過嘅精確 zone（2 FVG + 1 OB）。"""
        from engine.indicators import Zone
        ch = CandleChart(Config())
        ch.update_bars(self._confluence_bars())
        ch.set_indicator("fvg", True)
        ch.set_indicator("ob", True)
        assert ch._zones["fvg"] == (
            Zone("fvg", "bullish", 2, None, 10.5, 9.5),
            Zone("fvg", "bullish", 3, None, 9.8, 9.6),
        )
        assert ch._zones["ob"] == (Zone("ob", "bullish", 3, None, 10.4, 9.9),)

    def test_confluence_derived_only_when_both_enabled(self):
        """confluence 唔係獨立開關——OB + FVG 同時啟用先自動派生。"""
        from engine.indicators import Zone
        ch = CandleChart(Config())
        ch.update_bars(self._confluence_bars())
        ch.set_indicator("fvg", True)
        assert "confluence" not in ch._zones         # FVG 單開 → 無共鳴層
        ch.set_indicator("ob", True)
        assert ch._zones["confluence"] == (Zone("confluence", "bullish", 3, None, 10.4, 9.9),)

    def test_render_differs_when_fvg_enabled(self):
        """pixel diff：啟用 FVG 後 render 必須有差異（zone fill + 虛線邊框畫入圖）。"""
        ch = CandleChart(Config())
        ch.update_bars(self._fvg_bars())
        img_off = self._render(ch)
        ch.set_indicator("fvg", True)
        img_on = self._render(ch)
        assert self._diff_count(img_off, img_on) > 0

    def test_confluence_border_pixels_only_with_both_enabled(self):
        """confluence 邊框 #B388FF 係 palette 唯一色 → 可以精確計數：
        FVG 單開 = 0、OB+FVG 同開 > 0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._confluence_bars())
        ch.set_indicator("fvg", True)
        assert self._count_in(self._render(ch), QColor("#B388FF")) == 0
        ch.set_indicator("ob", True)
        assert self._count_in(self._render(ch), QColor("#B388FF")) > 0


class TestSecondBatchIndicators:
    """ICT 指標第二批（Breaker / Kill Zones / Daily ref lines）：set_indicator() recompute + pixel 驗證。

    - Breaker：crafted 5-bar 序列 → bearish breaker [10.1,10.4]@3..4；邊框 #4DD0E1 係
      palette 唯一色 → 精確計數（off=0 / on>0）。
    - Kill Zones：HKT intraday bars → EST session bands（zoneinfo DST-aware）；fill 係
      alpha blend → render diff 驗證。
    - Ref lines：兩日 bars → DO×2 + PH/PL/PC 全寬線；PH #FFD54F 唯一色 → 精確計數。
    """

    @staticmethod
    def _render(ch, w=800, h=600):
        ch.resize(w, h)
        pix = QPixmap(ch.size())
        ch.render(pix)
        return pix.toImage()

    @staticmethod
    def _diff_count(img_a, img_b, threshold: int = 32) -> int:
        n = 0
        for y in range(img_a.height()):
            for x in range(img_a.width()):
                ca, cb = img_a.pixelColor(x, y), img_b.pixelColor(x, y)
                if (abs(ca.red() - cb.red()) + abs(ca.green() - cb.green())
                        + abs(ca.blue() - cb.blue())) > threshold:
                    n += 1
        return n

    @staticmethod
    def _count_in(img, color) -> int:
        n = 0
        for y in range(img.height()):
            for x in range(img.width()):
                if img.pixelColor(x, y) == color:
                    n += 1
        return n

    @staticmethod
    def _breaker_bars():
        """5-bar 序列 → bearish breaker [10.1,10.4] start=3 end=4（手算驗證過）。"""
        return (
            ("2026-09-30 09:00", 10.0, 10.5, 9.8, 10.2, 1000.0),
            ("2026-09-30 09:01", 10.4, 10.6, 10.0, 10.1, 1000.0),   # bearish origin body [10.1,10.4]
            ("2026-09-30 09:02", 10.1, 11.2, 10.0, 11.0, 1000.0),   # strong BOS up trigger i=2
            ("2026-09-30 09:03", 10.9, 11.0, 9.5, 9.6, 1000.0),     # close < 10.1 → 失效 k=3
            ("2026-09-30 09:04", 9.7, 10.6, 9.5, 10.5, 1000.0),     # close > 10.4 → mitigation end=4
        )

    @staticmethod
    def _kz_bars():
        """EST（HKT−ET=780min）：asia [0,1] + london [3,4]（純邏輯測試同款數據）。"""
        return tuple((f"2026-01-15 {t}", 100.0, 101.0, 99.5, 100.5, 1000.0) for t in
                     ("09:30", "12:00", "13:00", "15:00", "17:30", "18:00"))

    @staticmethod
    def _ref_bars():
        """兩日 intraday bars → DO×2 + PH/PL/PC（純邏輯測試同款數據）。"""
        return (
            ("2026-09-30 09:30", 10.0, 10.5, 9.8, 10.2, 1000.0),
            ("2026-09-30 10:00", 10.2, 10.6, 10.0, 10.4, 1000.0),
            ("2026-10-01 09:30", 10.5, 10.7, 10.1, 10.6, 1000.0),
        )

    def test_breaker_recomputes_immediately(self):
        """set_indicator("brk") 同步重算 → _zones["breaker"] = 手算驗證過嘅 zone。"""
        from engine.indicators import Zone
        ch = CandleChart(Config())
        ch.update_bars(self._breaker_bars())
        assert ch._zones == {}                       # 預設全 off
        ch.set_indicator("brk", True)
        assert ch._zones["breaker"] == (Zone("breaker", "bearish", 3, 4, 10.4, 10.1),)

    def test_breaker_border_pixels_only_when_enabled(self):
        """Breaker 邊框 #4DD0E1 係 palette 唯一色 → off=0、on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._breaker_bars())
        assert self._count_in(self._render(ch), QColor("#4DD0E1")) == 0
        ch.set_indicator("brk", True)
        assert self._count_in(self._render(ch), QColor("#4DD0E1")) > 0

    def test_kz_bands_recompute_and_render_differs(self):
        """set_indicator("kz") → _kz_bands = EST session bands；alpha fill → render diff > 0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._kz_bars())
        assert ch._kz_bands == ()                    # 預設 off
        img_off = self._render(ch)
        ch.set_indicator("kz", True)
        assert ch._kz_bands == ((0, 1, "asia"), (3, 4, "london"))
        img_on = self._render(ch)
        assert self._diff_count(img_off, img_on) > 0

    def test_kz_off_clears_bands(self):
        """toggle off → _kz_bands 清空（recompute 重置邏輯，唔會殘留舊 band）。"""
        ch = CandleChart(Config())
        ch.update_bars(self._kz_bars())
        ch.set_indicator("kz", True)
        assert len(ch._kz_bands) == 2
        ch.set_indicator("kz", False)
        assert ch._kz_bands == ()

    def test_ref_lines_recompute_and_ph_pixels(self):
        """set_indicator("ref") → _ref_lines = DO×2 + PH/PL/PC；PH #FFD54F 唯一色 → off=0、on>0。"""
        from engine.indicators import RefLine
        ch = CandleChart(Config())
        ch.update_bars(self._ref_bars())
        assert ch._ref_lines == ()                   # 預設 off
        assert self._count_in(self._render(ch), QColor("#FFD54F")) == 0
        ch.set_indicator("ref", True)
        assert ch._ref_lines == (
            RefLine("do", 10.0, 0, 1),
            RefLine("do", 10.5, 2, 2),
            RefLine("ph", 10.6, 0, None),
            RefLine("pl", 9.8, 0, None),
            RefLine("pc", 10.4, 0, None),
        )
        assert self._count_in(self._render(ch), QColor("#FFD54F")) > 0


class TestVOBIndicator:
    """VOB 有效訂單塊圖層（Step 2 · Commit 17）：set_indicator("vob") → detect_valid_order_blocks()
    自含 recompute（獨立於 ob/fvg 開關狀態）；#69F0AE 亮綠係 palette 唯一色 → off=0 / on>0。"""

    @staticmethod
    def _render(ch, w=800, h=600):
        ch.resize(w, h)
        pix = QPixmap(ch.size())
        ch.render(pix)
        return pix.toImage()

    @staticmethod
    def _count_in(img, color) -> int:
        n = 0
        for y in range(img.height()):
            for x in range(img.width()):
                if img.pixelColor(x, y) == color:
                    n += 1
        return n

    @staticmethod
    def _vob_bars():
        """8-bar bullish VOB 序列（同 test_indicators._vob_bullish_bars）：整固 → sweep low 8.9
        （s=3）→ origin 陰線 j=4 body [9.3,9.6] → trigger i=6 BOS up → FVG@7 [9.5,9.8] 重疊。"""
        return (
            ("2026-09-30 09:00", 10.0, 10.2, 9.9, 10.1, 1000.0),   # b0 整固
            ("2026-09-30 09:01", 10.1, 10.3, 10.0, 10.2, 1000.0),  # b1 整固
            ("2026-09-30 09:02", 10.2, 10.4, 9.8, 9.9, 1000.0),    # b2 陰線（prior_high=10.4）
            ("2026-09-30 09:03", 9.9, 10.0, 8.9, 9.5, 1000.0),     # b3 sweep：low 8.9 = 窗口新低
            ("2026-09-30 09:04", 9.6, 9.7, 9.2, 9.3, 1000.0),      # b4 origin 陰線 → OB body [9.3,9.6]
            ("2026-09-30 09:05", 9.3, 9.5, 9.2, 9.4, 1000.0),      # b5 小陽 c1（high 9.5 喺 OB 內）
            ("2026-09-30 09:06", 9.4, 11.2, 9.3, 11.1, 1000.0),    # b6 trigger i=6：BOS up
            ("2026-09-30 09:07", 11.1, 11.5, 9.8, 11.2, 1000.0),   # b7 → FVG@7 [9.5,9.8] 重疊 OB
        )

    def test_vob_recomputes_immediately(self):
        """set_indicator("vob", True) → _zones["vob"] = 完整 OB body（end=None）；toggle off → 清空。"""
        from engine.indicators import Zone
        ch = CandleChart(Config())
        ch.update_bars(self._vob_bars())
        assert ch._zones == {}                       # 預設全 off
        ch.set_indicator("vob", True)
        assert ch._zones["vob"] == (Zone("vob", "bullish", 4, None, 9.6, 9.3),)
        ch.set_indicator("vob", False)
        assert ch._zones == {}

    def test_vob_border_pixels_only_when_enabled(self):
        """#69F0AE（亮綠 VOB 邊框/fill base）palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._vob_bars())
        assert self._count_in(self._render(ch), QColor("#69F0AE")) == 0
        ch.set_indicator("vob", True)
        assert self._count_in(self._render(ch), QColor("#69F0AE")) > 0

