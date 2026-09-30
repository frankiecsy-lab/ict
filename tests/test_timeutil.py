"""timeutil 單測：時間解析、週期 floor、bar key、方向判定、tick 時間補全、歷史窗口。"""
import math
from datetime import date, datetime, time as dtime, timedelta

import pytest

from engine.timeutil import (
    _MAX_WINDOW_DAYS,
    bar_key,
    floor_to_period,
    history_window,
    is_up,
    parse_market_time,
    parse_time_only,
    resolve_tick_datetime,
)


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


class TestParseTimeOnly:
    """futu live tick data_time 係 time-only string（實測 'HH:mm:ss.SSS'）。"""

    def test_millis(self):
        assert parse_time_only("14:30:45.123") == dtime(14, 30, 45, 123000)

    def test_seconds(self):
        assert parse_time_only("14:30:45") == dtime(14, 30, 45)

    def test_minutes(self):
        assert parse_time_only("14:30") == dtime(14, 30)

    @pytest.mark.parametrize(
        "bad", ["", "   ", "abc", "99:99", "25:00:00", "14:61:00", "14:30:45.1234567"]
    )
    def test_garbage_returns_none(self, bad):
        assert parse_time_only(bad) is None

    @pytest.mark.parametrize("bad", [None, 12345, dtime(14, 30)])
    def test_non_string_returns_none(self, bad):
        assert parse_time_only(bad) is None


class TestResolveTickDatetime:
    def test_datetime_passthrough_naive(self):
        dt = resolve_tick_datetime(datetime(2026, 9, 28, 14, 30, 45))
        assert dt == datetime(2026, 9, 28, 14, 30, 45) and dt.tzinfo is None

    def test_full_string_ignores_fallback(self):
        # 含日期部分 → 直接 parse，fallback 唔使理
        assert resolve_tick_datetime("2026-09-28 14:30:45", date(2030, 1, 1)) == datetime(2026, 9, 28, 14, 30, 45)

    def test_time_only_uses_fallback_date(self):
        assert resolve_tick_datetime("09:30:05.500", date(2026, 9, 28)) == datetime(2026, 9, 28, 9, 30, 5, 500000)

    def test_time_only_no_fallback_uses_today(self):
        dt = resolve_tick_datetime("14:30:45")
        assert dt.date() == date.today()
        assert (dt.hour, dt.minute, dt.second) == (14, 30, 45)

    @pytest.mark.parametrize("bad", [None, 12345, "not-a-time"])
    def test_garbage_returns_none(self, bad):
        assert resolve_tick_datetime(bad) is None


class TestHistoryWindow:
    """明確 start/end 窗口（實測：no-window 會返回一年前舊數據）。"""

    NOW = datetime(2026, 9, 30, 15, 0, 0)

    def test_1m_window(self):
        # days = ceil(300*1/360)+2 = 3
        start, end = history_window(1, 300, now=self.NOW)
        assert end == "2026-09-30 15:00:00"
        assert start == (self.NOW - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")

    def test_5m_window(self):
        # days = ceil(300*5/360)+2 = 7
        start, _ = history_window(5, 300, now=self.NOW)
        assert start == (self.NOW - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    def test_day_period_wider(self):
        # K_DAY: days = int(ceil(300*1.5))+7 = 457（日線要覆蓋更多自然日）
        start, _ = history_window(24 * 60, 300, now=self.NOW)
        assert start == (self.NOW - timedelta(days=457)).strftime("%Y-%m-%d %H:%M:%S")

    def test_mon_period_clamped_to_max_window(self):
        # K_MON(43200min) × 1000 → raw days ≈ 45007（>123 年）→ OpenD 拒收過長窗口。
        # clamp 到 _MAX_WINDOW_DAYS：start = NOW − max_window，唔會算出百多年跨度。
        start, end = history_window(30 * 24 * 60, 1000, now=self.NOW)
        assert start == (self.NOW - timedelta(days=_MAX_WINDOW_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
        assert end == "2026-09-30 15:00:00"

    def test_week_period_not_clamped(self):
        # K_WEEK(10080min) × 300 → raw days ≈ 10577（< max）→ 唔受 clamp 影響。
        start, _ = history_window(7 * 24 * 60, 300, now=self.NOW)
        expected_days = int(math.ceil(300 * (7 * 24 * 60 / (24 * 60)) * 1.5)) + 7
        assert start == (self.NOW - timedelta(days=expected_days)).strftime("%Y-%m-%d %H:%M:%S")

    def test_format_is_futu_compatible(self):
        start, end = history_window(1, 10, now=self.NOW)
        for s in (start, end):
            assert datetime.strptime(s, "%Y-%m-%d %H:%M:%S") is not None

    @pytest.mark.parametrize("period,count", [(0, 300), (-1, 300), (1, 0), (1, -5)])
    def test_invalid_raises(self, period, count):
        with pytest.raises(ValueError):
            history_window(period, count)
