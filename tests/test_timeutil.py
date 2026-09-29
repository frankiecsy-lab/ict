"""timeutil 單測：時間解析、週期 floor、bar key、方向判定。"""
from datetime import datetime

import pytest

from engine.timeutil import bar_key, floor_to_period, is_up, parse_market_time


class TestParseMarketTime:
    def test_full_seconds(self):
        assert parse_market_time("2026-09-28 14:30:45") == datetime(2026, 9, 28, 14, 30, 45)

    def test_minute_precision(self):
        assert parse_market_time("2026-09-28 14:30") == datetime(2026, 9, 28, 14, 30)

    def test_result_is_naive(self):
        dt = parse_market_time("2026-09-28 14:30:45")
        assert dt.tzinfo is None

    @pytest.mark.parametrize(
        "bad", ["", "   ", "not-a-date", "2026/09/28 14:30:45", "2026-13-45 99:99:99", "28-09-2026 14:30"]
    )
    def test_garbage_returns_none(self, bad):
        assert parse_market_time(bad) is None

    @pytest.mark.parametrize("bad", [None, 12345, ["2026-09-28 14:30:45"]])
    def test_non_string_returns_none(self, bad):
        assert parse_market_time(bad) is None

    def test_datetime_passthrough_strips_tzinfo_without_conversion(self):
        from datetime import timezone

        aware = datetime(2026, 9, 28, 14, 30, 45, tzinfo=timezone.utc)
        dt = parse_market_time(aware)
        assert dt == datetime(2026, 9, 28, 14, 30, 45)
        assert dt.tzinfo is None


class TestFloorToPeriod:
    def test_1m_is_noop_on_minutes(self):
        assert floor_to_period(datetime(2026, 9, 28, 14, 37, 45), 1) == datetime(2026, 9, 28, 14, 37)

    def test_5m(self):
        assert floor_to_period(datetime(2026, 9, 28, 14, 37, 59), 5) == datetime(2026, 9, 28, 14, 35)

    def test_15m_across_hour(self):
        assert floor_to_period(datetime(2026, 9, 28, 14, 50), 15) == datetime(2026, 9, 28, 14, 45)

    def test_30m(self):
        assert floor_to_period(datetime(2026, 9, 28, 9, 31), 30) == datetime(2026, 9, 28, 9, 30)

    def test_60m(self):
        assert floor_to_period(datetime(2026, 9, 28, 23, 58), 60) == datetime(2026, 9, 28, 23, 0)

    def test_day(self):
        assert floor_to_period(datetime(2026, 9, 28, 14, 37, 45), 1440) == datetime(2026, 9, 28)

    def test_week_floors_to_monday(self):
        # 2026-09-28 係星期一；2026-10-03 係星期六 → floor 到 2026-09-28
        assert datetime(2026, 9, 28).weekday() == 0
        assert floor_to_period(datetime(2026, 10, 3, 15, 0), 7 * 1440) == datetime(2026, 9, 28)

    def test_month_floors_to_first(self):
        assert floor_to_period(datetime(2026, 9, 28, 15, 0), 30 * 1440) == datetime(2026, 9, 1)


class TestBarKey:
    def test_intraday(self):
        assert bar_key(datetime(2026, 9, 28, 14, 35), 5) == "2026-09-28 14:35"

    def test_day_and_week_same_format(self):
        assert bar_key(datetime(2026, 9, 28), 1440) == "2026-09-28"
        assert bar_key(datetime(2026, 9, 28), 7 * 1440) == "2026-09-28"

    def test_month(self):
        assert bar_key(datetime(2026, 9, 1), 30 * 1440) == "2026-09"


class TestIsUp:
    def test_up(self):
        assert is_up(100.0, 101.0)

    def test_down(self):
        assert not is_up(100.0, 99.0)

    def test_doji_counts_as_up(self):
        assert is_up(100.0, 100.0)
