"""candle_chart 純 layout 函數單測（零 Qt app 依賴）。"""
import math
from datetime import datetime

import pytest

from ui.candle_chart import (
    fmt_price,
    infer_period_minutes,
    nice_step,
    pan_x,
    pan_y,
    price_range,
    time_label,
    time_window_indices,
    visible_slice,
    visible_window,
    volume_max,
    wheel_notches,
    window_time_range,
    zoom_x,
    zoom_y,
)


def _bar(key="2026-09-30 09:30", o=100.0, h=101.0, l=99.5, c=100.5, v=1000.0):
    return (key, o, h, l, c, v)


def _bars(n: int) -> tuple:
    """n 根連續 bar，key = '2026-09-30 09:{i:02d}'（方便斷言邊界）。"""
    return tuple(_bar(f"2026-09-30 09:{i:02d}") for i in range(n))


class TestVisibleWindow:
    def test_offset_zero_equals_visible_slice(self):
        bars = _bars(10)
        assert visible_window(bars, 4, 0) == visible_slice(bars, 4)

    def test_positive_offset_shifts_toward_older(self):
        # 10 根、count=4、off=2 → end=8, start=4 → bars[4:8]（09:04..09:07）
        out = visible_window(_bars(10), 4, 2)
        assert len(out) == 4 and out[0][0].endswith("09:04") and out[-1][0].endswith("09:07")

    def test_offset_clamped_to_oldest(self):
        # off=100 → clamp 到 n-count=6 → end=4, start=0 → bars[0:4]
        assert visible_window(_bars(10), 4, 100) == _bars(10)[:4]

    def test_negative_offset_clamped_to_zero(self):
        assert visible_window(_bars(10), 4, -5) == visible_slice(_bars(10), 4)

    def test_count_larger_than_available_returns_all(self):
        # count=20 > n=10 → offset clamp 到 0、視窗收窄到全部 10 根（唔會繞圈）
        out = visible_window(_bars(10), 20, 5)
        assert len(out) == 10 and out[0][0].endswith("09:00") and out[-1][0].endswith("09:09")

    def test_fractional_offset_rounds_to_whole_bar(self):
        # off=2.6 → round→3；off=2.4 → round→2
        assert visible_window(_bars(10), 4, 2.6) == visible_window(_bars(10), 4, 3)
        assert visible_window(_bars(10), 4, 2.4) == visible_window(_bars(10), 4, 2)

    @pytest.mark.parametrize("count", [0, -5])
    def test_invalid_count_returns_empty(self, count):
        assert visible_window(_bars(10), count, 0) == ()

    def test_empty_bars(self):
        assert visible_window((), 4, 0) == ()


class TestZoomX:
    def test_zoom_in_reduces_count_by_1_25(self):
        new_count, _off = zoom_x(100, 0.0, 1000, 0.5, 1)
        assert new_count == 80  # round(100 / 1.25)

    def test_zoom_out_increases_count_by_1_25(self):
        new_count, _off = zoom_x(80, 0.0, 1000, 0.5, -1)
        assert new_count == 100  # round(80 * 1.25)

    def test_cursor_anchor_keeps_bar_under_cursor(self):
        # total=100、count=100（全顯示）、游標 f=0.5 → global index 50。
        # zoom in delta=1 → count=80；global 50 應保持喺新視窗 f=0.5 位置。
        new_count, off = zoom_x(100, 0.0, 100, 0.5, 1)
        assert new_count == 80
        win = visible_window(_bars(100), new_count, off)
        # global index 50 喺視窗內嘅 local position：(g − start)/count
        start = len(_bars(100)) - int(round(off)) - len(win)
        assert (50 - start) / new_count == pytest.approx(0.5)

    def test_zoom_in_clamped_to_min_5_bars(self):
        new_count, _off = zoom_x(5, 0.0, 1000, 0.5, 10)
        assert new_count == 5

    def test_zoom_out_clamped_to_max_2000(self):
        new_count, _off = zoom_x(2000, 0.0, 100000, 0.5, -1)
        assert new_count == 2000

    def test_zero_delta_no_change(self):
        assert zoom_x(120, 30.0, 1000, 0.7, 0) == (120, 30.0)

    def test_fractional_half_stage_zoom_in(self):
        # delta=0.5 → count × 1.25^-0.5 ≈ ×0.8944 → round(89.44)=89（多段式小數 notch）
        new_count, _off = zoom_x(100, 0.0, 1000, 0.5, 0.5)
        assert new_count == 89

    def test_fractional_half_stage_zoom_out(self):
        # delta=-0.5 → count × 1.25^0.5 ≈ ×1.1180 → round(111.80)=112
        new_count, _off = zoom_x(100, 0.0, 1000, 0.5, -0.5)
        assert new_count == 112


class TestWheelNotches:
    def test_one_windows_notch_up_is_plus_one_stage(self):
        # Windows 單 notch = +120° → +1 階（唔再係 1.25**120 直跳極限）
        assert wheel_notches(120) == pytest.approx(1.0)

    def test_one_windows_notch_down_is_minus_one_stage(self):
        assert wheel_notches(-120) == pytest.approx(-1.0)

    def test_fractional_delta_preserved(self):
        # 部分裝置報半 notch（±60°）→ ±0.5 階，保留小數精度
        assert wheel_notches(60) == pytest.approx(0.5)
        assert wheel_notches(-240) == pytest.approx(-2.0)

    def test_zero_angle_is_noop(self):
        assert wheel_notches(0) == 0.0


class TestPanX:
    def test_pan_toward_older_increases_offset(self):
        _c, off = pan_x(4, 0.0, 100, +10)
        assert off == 10.0

    def test_pan_toward_newer_decreases_offset(self):
        _c, off = pan_x(4, 20.0, 100, -5)
        assert off == 15.0

    def test_clamped_at_zero(self):
        _c, off = pan_x(4, 0.0, 100, -5)
        assert off == 0.0

    def test_clamped_at_oldest_boundary(self):
        # max offset = total-count = 80；off=75 + 10 → clamp 到 80
        _c, off = pan_x(20, 75.0, 100, +10)
        assert off == 80.0

    def test_count_unchanged(self):
        c, _off = pan_x(42, 0.0, 100, 3)
        assert c == 42


class TestZoomY:
    def test_zoom_in_shrinks_span_by_1_25(self):
        lo, hi = zoom_y(100.0, 110.0, 0.5, 1)
        assert (hi - lo) == pytest.approx(8.0)  # 10 / 1.25

    def test_cursor_anchor_keeps_price_under_cursor(self):
        # span=10、f=0.5 → 游標價 p = hi - f*span = 105。zoom in 後 105 應保持喺 f=0.5。
        lo, hi = zoom_y(100.0, 110.0, 0.5, 1)
        assert (hi - 105.0) / (hi - lo) == pytest.approx(0.5)

    def test_zoom_out_grows_span(self):
        lo, hi = zoom_y(100.0, 110.0, 0.5, -1)
        assert (hi - lo) == pytest.approx(12.5)  # 10 * 1.25

    def test_anchor_at_top(self):
        # f=0（頂部）→ 游標價 = hi；縮放後 hi 側保持。
        lo, hi = zoom_y(100.0, 110.0, 0.0, 1)
        assert (hi - 110.0) / (hi - lo) == pytest.approx(0.0)

    def test_span_floor_prevents_degenerate_range(self):
        # delta=100 → 1.25^-100 極小 → span clamp 到 10 * 1e-4 = 0.001
        lo, hi = zoom_y(100.0, 110.0, 0.5, 100)
        assert (hi - lo) == pytest.approx(0.001)

    def test_zero_delta_no_change(self):
        assert zoom_y(100.0, 110.0, 0.3, 0) == (100.0, 110.0)

    def test_invalid_range_returns_unchanged(self):
        assert zoom_y(110.0, 100.0, 0.5, 1) == (110.0, 100.0)


class TestPanY:
    def test_shift_up_positive_delta(self):
        lo, hi = pan_y(100.0, 110.0, +5.0)
        assert (lo, hi) == (105.0, 115.0)

    def test_shift_down_negative_delta(self):
        lo, hi = pan_y(100.0, 110.0, -3.0)
        assert (lo, hi) == (97.0, 107.0)

    def test_span_preserved(self):
        lo, hi = pan_y(25340.0, 25400.0, 123.456)
        assert (hi - lo) == pytest.approx(60.0)


class TestVisibleSlice:
    def test_takes_last_n(self):
        bars = tuple(_bar(f"2026-09-30 09:{i:02d}") for i in range(10))
        out = visible_slice(bars, 4)
        assert len(out) == 4 and out[0][0].endswith("09:06") and out[-1][0].endswith("09:09")

    def test_count_larger_than_bars(self):
        bars = (_bar(), _bar())
        assert visible_slice(bars, 120) == bars

    @pytest.mark.parametrize("count", [0, -5])
    def test_invalid_count_returns_empty(self, count):
        assert visible_slice((_bar(),), count) == ()

    def test_empty_bars(self):
        assert visible_slice((), 120) == ()


class TestPriceRange:
    def test_padding_5_percent(self):
        bars = (_bar(l=100.0, h=110.0), _bar(l=101.0, h=109.0))
        assert price_range(bars) == (99.5, 110.5)

    def test_flat_bars_fallback_1_percent(self):
        bars = (_bar(o=25340.5, h=25340.5, l=25340.5, c=25340.5),)
        lo, hi = price_range(bars)
        assert (lo, hi) == pytest.approx((25340.5 - 253.405, 25340.5 + 253.405))

    def test_empty_returns_none(self):
        assert price_range(()) is None


class TestVolumeMax:
    def test_max(self):
        bars = (_bar(v=100), _bar(v=900), _bar(v=400))
        assert volume_max(bars) == 900.0

    def test_all_zero_fallback_one(self):
        assert volume_max((_bar(v=0.0), _bar(v=0.0))) == 1.0

    def test_empty(self):
        assert volume_max(()) == 1.0


class TestNiceStep:
    @pytest.mark.parametrize("span,expected", [
        (100.0, 20.0),   # raw≈16.7 → 2×10
        (10.0, 2.0),     # raw≈1.67 → 2×1
        (5.0, 1.0),      # raw≈0.83 → 10×0.1
        (0.0, 1.0),      # 退化
    ])
    def test_steps(self, span, expected):
        assert nice_step(span) == expected

    def test_step_is_1_2_25_5_times_power_of_ten(self):
        for span in (3.7, 42.0, 834.0, 9999.0):
            s = nice_step(span)
            mantissa = round(s / 10 ** math.floor(math.log10(s)), 6)
            assert mantissa in (1.0, 2.0, 2.5, 5.0, 10.0)


class TestTimeLabel:
    def test_intraday_shows_hh_mm(self):
        assert time_label("2026-09-30 09:30") == "09:30"

    @pytest.mark.parametrize("key", ["2026-09-30", "2026-09"])
    def test_day_week_month_unchanged(self, key):
        assert time_label(key) == key


class TestFmtPrice:
    def test_two_decimals(self):
        assert fmt_price(25340.5) == "25340.50"


class TestWindowTimeRange:
    """window_time_range：可見視窗 → (start_dt, end_dt)，end = 尾根 bar **結束**（含 period）。"""

    def test_right_pinned_window(self):
        bars = _bars(10)  # keys 09:00..09:09，period=1min
        rng = window_time_range(bars, 4, 0.0, 1)
        assert rng == (datetime(2026, 9, 30, 9, 6), datetime(2026, 9, 30, 9, 10))

    def test_panned_window(self):
        bars = _bars(10)
        # offset=4 → 可見 09:00..09:05（尾根 start 09:05）→ end = 09:06
        rng = window_time_range(bars, 6, 4.0, 1)
        assert rng == (datetime(2026, 9, 30, 9, 0), datetime(2026, 9, 30, 9, 6))

    def test_end_includes_period(self):
        # period=5min：尾根 start 09:09 → end = 09:14（完整覆蓋視窗）
        bars = _bars(10)
        rng = window_time_range(bars, 2, 0.0, 5)
        assert rng == (datetime(2026, 9, 30, 9, 8), datetime(2026, 9, 30, 9, 14))

    def test_empty_bars_returns_none(self):
        assert window_time_range((), 10, 0.0, 1) is None

    def test_invalid_count_returns_none(self):
        assert window_time_range(_bars(5), 0, 0.0, 1) is None

    def test_unparseable_key_returns_none(self):
        bars = tuple(_bar("not-a-date") for _ in range(3))
        assert window_time_range(bars, 3, 0.0, 1) is None


class TestTimeWindowIndices:
    """time_window_indices：span-overlap → [s, e]（含尾）；無 overlap → None。"""

    def test_exact_match(self):
        bars = _bars(10)  # keys 09:00..09:09，period=1min
        # span-overlap：bar [09:02,09:03)..[09:06,09:07) overlap 視窗 [09:02,09:07)；
        # bar 09:01（end=09:02）只觸及邊界點 → 半開區間唔算 overlap。
        idx = time_window_indices(bars, datetime(2026, 9, 30, 9, 2), datetime(2026, 9, 30, 9, 7), 1)
        assert idx == (2, 6)

    def test_partial_overlap_clips_to_bars(self):
        bars = _bars(10)
        # start 喺 bar 中間（09:01）→ 首根 overlap 係 09:01；end 越尾 → 最後一根 09:09
        idx = time_window_indices(bars, datetime(2026, 9, 30, 9, 1), datetime(2026, 9, 30, 9, 59), 1)
        assert idx == (1, 9)

    def test_no_overlap_returns_none(self):
        bars = _bars(10)
        assert time_window_indices(bars, datetime(2026, 9, 30, 10, 0), datetime(2026, 9, 30, 10, 5), 1) is None

    def test_empty_bars_returns_none(self):
        assert time_window_indices((), datetime(2026, 9, 30, 9, 0), datetime(2026, 9, 30, 9, 5), 1) is None

    def test_none_bounds_return_none(self):
        bars = _bars(10)
        assert time_window_indices(bars, None, datetime(2026, 9, 30, 9, 5), 1) is None
        assert time_window_indices(bars, datetime(2026, 9, 30, 9, 0), None, 1) is None

    def test_single_bar_match(self):
        bars = _bars(10)
        idx = time_window_indices(bars, datetime(2026, 9, 30, 9, 4), datetime(2026, 9, 30, 9, 5), 1)
        assert idx == (4, 4)

    def test_cross_period_alignment(self):
        """跨週期對齊：intraday pane 視窗套去日線 bars → 只匹配當日一根（span-overlap）。"""
        day_bars = tuple(_bar("2026-09-30") for _ in range(1)) + tuple(_bar(f"2026-10-{d:02d}") for d in (1, 2, 3))
        # intraday pane 視窗：2026-09-30 09:30 → 14:56（全喺 09-30 當日）；日線 period=1440min
        idx = time_window_indices(day_bars, datetime(2026, 9, 30, 9, 30), datetime(2026, 9, 30, 14, 56), 1440)
        assert idx == (0, 0)

    def test_coarser_bar_starting_before_window_still_overlaps(self):
        """較粗 pane bar start 早於視窗 start（日線 09-30 00:00 < intraday 視窗 10:00）→ 仍 overlap。"""
        day_bars = tuple(_bar(f"2026-09-{d:02d}") for d in (28, 29, 30))
        idx = time_window_indices(day_bars, datetime(2026, 9, 30, 10, 0), datetime(2026, 9, 30, 10, 30), 1440)
        assert idx == (2, 2)


class TestInferPeriodMinutes:
    """infer_period_minutes：由 bar key 間隔推斷本 pane 週期。"""

    def test_minute_bars(self):
        bars = tuple(_bar(f"2026-09-30 09:{i:02d}") for i in range(10))
        assert infer_period_minutes(bars) == 1

    def test_five_minute_bars(self):
        bars = tuple(_bar(f"2026-09-30 {9 + (i * 5) // 60:02d}:{(i * 5) % 60:02d}") for i in range(10))
        assert infer_period_minutes(bars) == 5

    def test_daily_bars(self):
        bars = tuple(_bar(f"2026-09-{d:02d}") for d in (24, 25, 28, 29, 30))
        assert infer_period_minutes(bars) == 1440

    def test_fewer_than_two_bars_defaults_to_one(self):
        assert infer_period_minutes(()) == 1
        assert infer_period_minutes((_bar("2026-09-30"),)) == 1

    def test_unparseable_keys_default_to_one(self):
        bars = tuple(_bar("not-a-date") for _ in range(5))
        assert infer_period_minutes(bars) == 1

