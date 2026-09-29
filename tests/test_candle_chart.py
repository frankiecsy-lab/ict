"""candle_chart 純 layout 函數單測（零 Qt app 依賴）。"""
import math

import pytest

from ui.candle_chart import (
    fmt_price,
    nice_step,
    price_range,
    time_label,
    visible_slice,
    volume_max,
)


def _bar(key="2026-09-30 09:30", o=100.0, h=101.0, l=99.5, c=100.5, v=1000.0):
    return (key, o, h, l, c, v)


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
