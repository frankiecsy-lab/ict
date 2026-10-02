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


class TestRightMargin:
    """右側留白 5 bar-slot：slot 寬 = plot 寬 ÷（可見根數 + 5），bar 唔貼住價格軸。"""

    def test_bar_slot_includes_right_margin(self):
        ch = _chart(100)
        ch.resize(800, 600)
        plot, _, _ = ch._panes()
        assert ch._bar_slot(100, plot) == pytest.approx(plot.width() / (100 + 5))

    def test_last_bar_leaves_five_empty_slots(self):
        ch = _chart(100)
        ch.resize(800, 600)
        plot, _, _ = ch._panes()
        slot = ch._bar_slot(100, plot)
        last_slot_right = plot.left() + 100 * slot
        assert plot.right() - last_slot_right == pytest.approx(5 * slot)


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


class TestLiquidityIndicator:
    """Liquidity Levels BSL/SSL 圖層（Step 2 · Commit 18）：set_indicator("liq") →
    detect_liquidity_levels()；#FF80AB（BSL 粉紅）/ #7C4DFF（SSL 深紫）係 palette 唯一色
    → off=0 / on>0。"""

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
    def _liq_bars():
        """16-bar 序列（同 test_indicators._liq_bars）：equal highs @3/@9=12 → BSL；
        equal lows @5/@10=9 → SSL。last_close=10.5。"""
        ohlc = ((9.6, 10, 9.5, 9.8), (9.9, 11, 9.8, 10.4), (10.1, 11.5, 10, 11.2),
                (10.3, 12, 10.2, 11.8), (11.4, 11.5, 10, 10.6), (10.2, 11, 9, 9.3),
                (9.9, 10.5, 9.8, 10.4), (10.1, 11, 10, 10.8), (10.3, 11.5, 10.2, 11.3),
                (10.4, 12, 10, 11.7), (11.4, 11.5, 9, 9.4), (9.9, 11, 9.8, 10.7),
                (10.1, 10.5, 10, 10.4), (10.3, 11, 10.2, 10.9), (10.1, 11.5, 10, 11.3),
                (10.6, 11, 9.6, 10.5))
        return tuple((f"2026-09-30 09:{i:02d}", o, h, l, c, 1000.0)
                     for i, (o, h, l, c) in enumerate(ohlc))

    def test_liquidity_recomputes_immediately(self):
        """set_indicator("liq", True) → _levels = BSL@12 + SSL@9；toggle off → 清空。"""
        from engine.indicators import Level
        ch = CandleChart(Config())
        ch.update_bars(self._liq_bars())
        assert ch._levels == ()                     # 預設全 off
        ch.set_indicator("liq", True)
        assert ch._levels == (Level("bsl", 12.0, 3, None), Level("ssl", 9.0, 5, None))
        ch.set_indicator("liq", False)
        assert ch._levels == ()

    def test_liquidity_pixels_only_when_enabled(self):
        """#FF80AB（BSL）/ #7C4DFF（SSL）palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._liq_bars())
        img_off = self._render(ch)
        assert self._count_in(img_off, QColor("#FF80AB")) == 0
        assert self._count_in(img_off, QColor("#7C4DFF")) == 0
        ch.set_indicator("liq", True)
        img_on = self._render(ch)
        assert self._count_in(img_on, QColor("#FF80AB")) > 0
        assert self._count_in(img_on, QColor("#7C4DFF")) > 0


class TestStructureBreaks:
    """Structure Breaks BOS/CHoCH 圖層（Step 2 · Commit 19）：set_indicator("bos") →
    detect_structure_breaks()；#FF9100（BOS 橙）/ #E040FB（CHoCH 品紅）係 palette 唯一色
    → off=0 / on>0。"""

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
    def _bos_bars():
        """12-bar 序列（同 test_indicators._bos_choch_bars，k=2）：BOS up @5 + CHoCH down @11。"""
        ohlc = ((10.0, 10.5, 9.8, 10.3), (10.3, 11.2, 10.2, 11.0), (11.0, 12.0, 10.9, 11.6),
                (11.6, 11.8, 11.5, 11.7), (11.7, 11.9, 11.6, 11.8), (11.8, 13.0, 11.7, 12.6),
                (12.6, 13.4, 12.5, 13.2), (13.2, 13.8, 12.9, 13.6), (13.6, 13.7, 12.4, 13.0),
                (13.0, 13.9, 12.8, 13.7), (13.7, 14.0, 13.0, 13.9), (13.9, 14.0, 12.2, 12.3))
        return tuple((f"2026-09-30 09:{i:02d}", o, h, l, c, 1000.0)
                     for i, (o, h, l, c) in enumerate(ohlc))

    def test_structure_recomputes_immediately(self):
        """set_indicator("bos", True) → _markers = BOS up @5 + CHoCH down @11；toggle off → 清空。"""
        from engine.indicators import Marker
        ch = CandleChart(Config())
        ch.update_bars(self._bos_bars())
        assert ch._markers == ()                     # 預設全 off
        ch.set_indicator("bos", True)
        assert ch._markers == (Marker("bos", "up", 5), Marker("choch", "down", 11))
        ch.set_indicator("bos", False)
        assert ch._markers == ()

    def test_structure_pixels_only_when_enabled(self):
        """#FF9100（BOS）/ #E040FB（CHoCH）palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._bos_bars())
        img_off = self._render(ch)
        assert self._count_in(img_off, QColor("#FF9100")) == 0
        assert self._count_in(img_off, QColor("#E040FB")) == 0
        ch.set_indicator("bos", True)
        img_on = self._render(ch)
        assert self._count_in(img_on, QColor("#FF9100")) > 0
        assert self._count_in(img_on, QColor("#E040FB")) > 0


class TestPremiumDiscount:
    """Premium/Discount dealing range 圖層（Step 2 · Commit 21）：set_indicator("pd") →
    detect_premium_discount()；EQ 線 #CFD8DC 係 palette 唯一色 → off=0 / on>0
    （premium/discount fill 係 alpha-blend、唔計入 pixel count）。"""

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
    def _pd_bars():
        """6-bar 序列：max high=13（b1）、min low=8（b2）→ equilibrium=(13+8)/2=10.5。"""
        ohlc = ((10.0, 12.0, 9.5, 11.0), (11.0, 13.0, 10.0, 12.0), (12.0, 12.5, 8.0, 9.0),
                (9.0, 11.0, 8.5, 10.5), (10.5, 12.0, 9.5, 11.5), (11.5, 12.2, 10.0, 11.8))
        return tuple((f"2026-09-30 09:{i:02d}", o, h, l, c, 1000.0)
                     for i, (o, h, l, c) in enumerate(ohlc))

    def test_premium_discount_recomputes_immediately(self):
        """set_indicator("pd", True) → _pd_zones = premium[eq,hi] + discount[lo,eq]；toggle off → 清空。"""
        from engine.indicators import Zone
        ch = CandleChart(Config())
        ch.update_bars(self._pd_bars())
        assert ch._pd_zones == ()                     # 預設全 off
        ch.set_indicator("pd", True)
        hi, lo = 13.0, 8.0
        eq = (hi + lo) / 2.0                          # 10.5
        assert ch._pd_zones == (Zone("premium", "bearish", 0, None, hi, eq),
                                Zone("discount", "bullish", 0, None, eq, lo))
        ch.set_indicator("pd", False)
        assert ch._pd_zones == ()

    def test_premium_discount_pixels_only_when_enabled(self):
        """EQ 線 #CFD8DC palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._pd_bars())
        img_off = self._render(ch)
        assert self._count_in(img_off, QColor("#CFD8DC")) == 0
        ch.set_indicator("pd", True)
        img_on = self._render(ch)
        assert self._count_in(img_on, QColor("#CFD8DC")) > 0


class TestOTEIndicator:
    """OTE（Optimal Trade Entry）圖層（Step 2 · Commit 21）：set_indicator("ote") →
    detect_ote_zones()；邊框 #FFC400 係 palette 唯一色 → off=0 / on>0
    （fill alpha-blend、唔計入 pixel count）。"""

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
    def _ote_bars():
        """14-bar（同 test_indicators._ote_both_bars，k=3）：bullish OTE@6 + bearish OTE@10。"""
        ohlc = ((10.0, 10.5, 9.8, 10.3), (10.3, 10.6, 9.5, 9.9), (9.9, 10.0, 9.0, 9.4),
                (9.4, 9.7, 8.5, 9.2), (9.2, 10.2, 9.1, 10.0), (10.0, 11.0, 9.9, 10.8),
                (10.8, 13.0, 10.7, 12.8), (12.8, 12.5, 12.0, 12.2), (12.2, 12.4, 11.8, 12.0),
                (12.0, 12.3, 11.5, 11.7), (11.7, 11.9, 10.5, 11.0), (11.0, 11.6, 10.8, 11.3),
                (11.3, 11.9, 11.0, 11.7), (11.7, 12.2, 11.4, 12.0))
        return tuple((f"2026-09-30 09:{i:02d}", o, h, l, c, 1000.0)
                     for i, (o, h, l, c) in enumerate(ohlc))

    def test_ote_recomputes_immediately(self):
        """set_indicator("ote", True) → _zones["ote"] = bullish@6 + bearish@10；toggle off → 移除。"""
        from engine.indicators import Zone
        ch = CandleChart(Config())
        ch.update_bars(self._ote_bars())
        assert "ote" not in ch._zones                # 預設全 off
        ch.set_indicator("ote", True)
        span_b, span_s = 13.0 - 8.5, 13.0 - 10.5     # bullish H-L1=4.5 / bearish H-L2=2.5
        assert ch._zones["ote"] == (
            Zone("ote", "bullish", 6, None, 13.0 - 0.62 * span_b, 13.0 - 0.79 * span_b),
            Zone("ote", "bearish", 10, None, 10.5 + 0.79 * span_s, 10.5 + 0.62 * span_s),
        )
        ch.set_indicator("ote", False)
        assert "ote" not in ch._zones

    def test_ote_pixels_only_when_enabled(self):
        """OTE 邊框 #FFC400 palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._ote_bars())
        img_off = self._render(ch)
        assert self._count_in(img_off, QColor("#FFC400")) == 0
        ch.set_indicator("ote", True)
        img_on = self._render(ch)
        assert self._count_in(img_on, QColor("#FFC400")) > 0


class TestSessionHighLow:
    """Session High/Low 圖層（Step 2 · Commit 22）：set_indicator("shl") → detect_session_high_low()
    per-day sh/sl 線段；#FF6E40 (SH) / #9CCC65 (SL) 係 palette 唯一色 → off=0 / on>0。"""

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
    def _session_bars():
        """兩日 bars：Day1 (idx0-1) sh=10.5/sl=9.8、Day2 (idx2-3) sh=11.0/sl=9.5。
        Day1 線段喺整體 Y 範圍 [9.5,11.0] 內 → pixel count 可靠（Day2 係邊界極值）。"""
        return (
            ("2026-09-30 09:00", 10.0, 10.5, 9.8, 10.2, 1000.0),
            ("2026-09-30 09:01", 10.2, 10.4, 10.0, 10.3, 1000.0),
            ("2026-10-01 09:00", 10.5, 11.0, 9.5, 10.8, 1000.0),
            ("2026-10-01 09:01", 10.8, 10.9, 9.9, 10.7, 1000.0),
        )

    def test_session_high_low_recomputes_immediately(self):
        """set_indicator("shl", True) → _session_lines = per-day sh/sl；toggle off → 清空。"""
        from engine.indicators import RefLine
        ch = CandleChart(Config())
        ch.update_bars(self._session_bars())
        assert ch._session_lines == ()               # 預設全 off
        ch.set_indicator("shl", True)
        assert ch._session_lines == (
            RefLine("sh", 10.5, 0, 1),
            RefLine("sl", 9.8, 0, 1),
            RefLine("sh", 11.0, 2, 3),
            RefLine("sl", 9.5, 2, 3),
        )
        ch.set_indicator("shl", False)
        assert ch._session_lines == ()

    def test_session_high_low_pixels_only_when_enabled(self):
        """SH #FF6E40 / SL #9CCC65 palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._session_bars())
        img_off = self._render(ch)
        assert self._count_in(img_off, QColor("#FF6E40")) == 0
        assert self._count_in(img_off, QColor("#9CCC65")) == 0
        ch.set_indicator("shl", True)
        img_on = self._render(ch)
        assert self._count_in(img_on, QColor("#FF6E40")) > 0
        assert self._count_in(img_on, QColor("#9CCC65")) > 0


class TestWMRefLines:
    """Weekly/Monthly reference lines 圖層（Step 2 · Commit 24）：set_indicator("wmref") →
    weekly_monthly_reference_lines() Prev Week/Month HLC 全寬線；weekly 青色系
    #00ACC1/#0097A7/#26C6DA + monthly 紫色系 #9575CD/#7E57C2/#B39DDB 係 palette 唯一色 → off=0 / on>0。"""

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
    def _wm_bars():
        """5 ISO 週 + 2 個月；當前週 (b6) 範圍拉闊 → 六條線價全部嚴格喺整體 Y 範圍 [37,58] 內。"""
        return (
            ("2026-08-31 09:30", 45, 50, 40, 47, 1000.0),   # Aug / wk36 → prev month
            ("2026-09-07 09:30", 47, 49, 44, 48, 1000.0),   # wk37
            ("2026-09-14 09:30", 48, 52, 46, 50, 1000.0),   # wk38
            ("2026-09-15 09:30", 50, 51, 47, 49, 1000.0),   # wk38
            ("2026-09-21 09:30", 49, 55, 45, 53, 1000.0),   # wk39 → prev week
            ("2026-09-22 09:30", 53, 54, 48, 52, 1000.0),   # wk39
            ("2026-09-28 09:30", 52, 58, 37, 55, 1000.0),   # wk40 當前（範圍拉闊）
        )

    def test_wm_ref_lines_recomputes_immediately(self):
        """set_indicator("wmref", True) → _wm_lines = Prev Week/Month HLC；toggle off → 清空。"""
        from engine.indicators import RefLine
        ch = CandleChart(Config())
        ch.update_bars(self._wm_bars())
        assert ch._wm_lines == ()                   # 預設全 off
        ch.set_indicator("wmref", True)
        assert ch._wm_lines == (
            RefLine("pwh", 55.0, 0, None),
            RefLine("pwl", 45.0, 0, None),
            RefLine("pwc", 52.0, 0, None),
            RefLine("pmh", 50.0, 0, None),
            RefLine("pml", 40.0, 0, None),
            RefLine("pmc", 47.0, 0, None),
        )
        ch.set_indicator("wmref", False)
        assert ch._wm_lines == ()

    def test_wm_ref_line_pixels_only_when_enabled(self):
        """weekly 青色系 + monthly 紫色系 palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        ch.update_bars(self._wm_bars())
        img_off = self._render(ch)
        for c in ("#00ACC1", "#0097A7", "#26C6DA", "#9575CD", "#7E57C2", "#B39DDB"):
            assert self._count_in(img_off, QColor(c)) == 0
        ch.set_indicator("wmref", True)
        img_on = self._render(ch)
        for c in ("#00ACC1", "#0097A7", "#26C6DA", "#9575CD", "#7E57C2", "#B39DDB"):
            assert self._count_in(img_on, QColor(c)) > 0


class TestSmtDivergence:
    """SMT Divergence 圖層（Step 2 · Commit 25）：set_indicator("smt") + set_smt_bars() →
    detect_smt_divergence(primary, secondary)；#FF4081（bearish 粉紅）/ #18FFFF（bullish 青）
    係 palette 唯一色 → off=0 / on>0。"""

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
    def _smt_pair():
        """Bearish pair（同 test_indicators.test_smt_bearish_divergence）：primary HH 但 secondary
        對應窗口 max 20→15 → bearish marker @7。兩序列 time_key 完全一致（對齊前提）。"""
        pri_h = [10, 11, 12, 15, 12, 11, 12, 16, 12, 11]
        sec_h = [10, 14, 14, 20, 14, 13, 13, 15, 13, 12]

        def _mk(highs):
            return tuple((f"2026-09-30 09:{i:02d}", (h + 1.0) / 2, h, 1.0, (h + 1.0) / 2, 1000.0)
                         for i, h in enumerate(highs))

        return _mk(pri_h), _mk(sec_h)

    @staticmethod
    def _bull_pair():
        """Bullish pair（同 test_indicators.test_smt_bullish_divergence）：primary LL 但 secondary
        對應窗口 min 2→5 → bullish marker @7。"""
        pri_l = [10, 9, 8, 5, 8, 9, 8, 4, 8, 9]
        sec_l = [10, 6, 6, 2, 6, 7, 7, 5, 7, 8]

        def _mk(lows):
            return tuple((f"2026-09-30 09:{i:02d}", (20.0 + l) / 2, 20.0, l, (20.0 + l) / 2, 1000.0)
                         for i, l in enumerate(lows))

        return _mk(pri_l), _mk(sec_l)

    def test_smt_recomputes_immediately(self):
        """set_indicator("smt", True)（set_smt_bars 已先行）→ _smt_markers = bearish @7；toggle off → 清空。"""
        from engine.indicators import Marker
        ch = CandleChart(Config())
        pri, sec = self._smt_pair()
        ch.update_bars(pri)
        ch.set_smt_bars(sec)          # 只存 snapshot（indicator 未啟用 → 無 marker）
        assert ch._smt_markers == ()  # 預設全 off
        ch.set_indicator("smt", True)
        assert ch._smt_markers == (Marker("smt_bearish", "down", 7),)
        ch.set_indicator("smt", False)
        assert ch._smt_markers == ()

    def test_smt_pixels_only_when_enabled(self):
        """#FF4081（bearish）/ #18FFFF（bullish）palette 唯一色 → off=0 / on>0。"""
        ch = CandleChart(Config())
        pri, sec = self._smt_pair()
        ch.update_bars(pri)
        ch.set_smt_bars(sec)
        img_off = self._render(ch)
        assert self._count_in(img_off, QColor("#FF4081")) == 0
        assert self._count_in(img_off, QColor("#18FFFF")) == 0
        ch.set_indicator("smt", True)
        img_on = self._render(ch)
        assert self._count_in(img_on, QColor("#FF4081")) > 0      # bearish 三角 @7
        assert self._count_in(img_on, QColor("#18FFFF")) == 0     # 呢對無 bullish 背離
        pri2, sec2 = self._bull_pair()
        ch.update_bars(pri2)
        ch.set_smt_bars(sec2)
        ch.set_indicator("smt", True)   # 同步 recompute（render 唔會驅動 repaint timer）
        img_bull = self._render(ch)
        assert self._count_in(img_bull, QColor("#18FFFF")) > 0    # bullish 三角 @7

