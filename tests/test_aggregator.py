"""CandleAggregator 核心單測：合成 tick 序列驗證聚合邏輯。

覆蓋：seed、同分鐘 OHLC 更新、新分鐘 append、volume delta 累計 + 跨 bar 邊界歸屬、
日 rollover reset、out-of-order skip、duplicate no-op、非法輸入 skip、
live key == seeded history key（時區不變量）、多週期 floor。
"""
from datetime import datetime

import pytest

from engine.candle_aggregator import CandleAggregator


def _bar(key, o=100.0, h=101.0, l=99.0, c=100.5, v=50.0):
    return (key, o, h, l, c, v)


class TestSeed:
    def test_seed_normalizes_history_rows(self):
        agg = CandleAggregator(1)
        n = agg.seed_from_history([
            ("2026-09-28 14:28:00", 98.0, 99.0, 97.5, 98.5, 10),
            ("2026-09-28 14:29:00", 98.5, 100.0, 98.0, 99.5, 20),
            ("2026-09-28 14:30:00", 99.5, 101.0, 99.0, 100.0, 30),
        ])
        assert n == 3
        bars = agg.bars()
        assert isinstance(bars, tuple)
        assert bars[0] == ("2026-09-28 14:28", 98.0, 99.0, 97.5, 98.5, 10.0)
        assert bars[-1][0] == "2026-09-28 14:30"

    def test_seed_skips_bad_rows(self):
        agg = CandleAggregator(1)
        n = agg.seed_from_history([
            ("garbage", 1, 2, 3, 4, 5),
            (None, 1, 2, 3, 4, 5),
            ("2026-09-28 14:30:00", "bad", 2, 3, 4, 5),
            ("2026-09-28 14:31:00", 1, 2, 3, 4, 5),
        ])
        assert n == 1
        assert agg.bars()[0][0] == "2026-09-28 14:31"

    def test_seed_empty_returns_zero(self):
        agg = CandleAggregator(1)
        assert agg.seed_from_history([]) == 0
        assert agg.bars() == ()

    def test_reseed_replaces(self):
        agg = CandleAggregator(1)
        agg.seed_from_history([("2026-09-28 14:30:00", 1, 2, 3, 4, 5)])
        n = agg.seed_from_history([("2026-09-28 15:00:00", 1, 2, 3, 4, 5)])
        assert n == 1
        assert len(agg.bars()) == 1
        assert agg.bars()[0][0] == "2026-09-28 15:00"

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError, match="period_minutes"):
            CandleAggregator(0)


class TestLiveUpdate:
    def setup_method(self):
        self.agg = CandleAggregator(1)
        self.agg.seed_from_history([("2026-09-28 14:30:00", 100.0, 101.0, 99.0, 100.5, 50.0)])

    def test_same_minute_updates_ohlc(self):
        assert self.agg.apply_quote("2026-09-28 14:30:05", 102.0, 100.0)
        last = self.agg.bars()[-1]
        assert (last[2], last[3], last[4]) == (102.0, 99.0, 102.0), "high/close 應更新，low 不變"

        assert self.agg.apply_quote("2026-09-28 14:30:20", 98.5, 107.0)
        last = self.agg.bars()[-1]
        assert (last[2], last[3], last[4]) == (102.0, 98.5, 98.5), "low/close 應更新，high 不變"

    def test_new_minute_appends_bar(self):
        before = len(self.agg.bars())
        assert self.agg.apply_quote("2026-09-28 14:31:02", 103.0, 110.0)
        bars = self.agg.bars()
        assert len(bars) == before + 1
        new = bars[-1]
        assert new[0] == "2026-09-28 14:31"
        # 新 bar：open=high=low=close=第一筆 last_price
        assert (new[1], new[2], new[3], new[4]) == (103.0, 103.0, 103.0, 103.0)

    def test_volume_delta_accumulation_and_boundary_attribution(self):
        # seed 後 _last_cum_vol=None → 第一筆 delta=0（已知近似，bar 保留歷史 volume）
        assert self.agg.apply_quote("2026-09-28 14:30:05", 100.0, 100.0)
        assert self.agg.bars()[-1][5] == 50.0

        # 同分鐘第二筆：delta = 107 - 100 = 7
        assert self.agg.apply_quote("2026-09-28 14:30:20", 100.5, 107.0)
        assert self.agg.bars()[-1][5] == 57.0

        # 跨 bar 邊界：新 bar 只計自己嘅 delta = 110 - 107 = 3
        assert self.agg.apply_quote("2026-09-28 14:31:01", 101.0, 110.0)
        bars = self.agg.bars()
        assert bars[-2][5] == 57.0, "舊 bar volume 唔應被新 tick 影響"
        assert bars[-1][5] == 3.0

    def test_negative_cum_delta_clamped_to_zero(self):
        self.agg.apply_quote("2026-09-28 14:30:05", 100.0, 100.0)
        # cum 倒退（異常數據）→ delta clamp 到 0，唔會負數
        assert self.agg.apply_quote("2026-09-28 14:30:10", 100.5, 90.0)
        assert self.agg.bars()[-1][5] == 50.0

    def test_day_rollover_resets_volume_reference(self):
        agg = CandleAggregator(1)
        agg.seed_from_history([("2026-09-28 23:59:00", 100, 101, 99, 100.5, 50)])
        assert agg.apply_quote("2026-09-28 23:59:30", 100.2, 5000.0)

        # 跨日曆午夜：date 變咗 → _last_cum_vol reset → 新 bar 第一筆 delta=0
        assert agg.apply_quote("2026-09-29 00:00:10", 100.8, 8.0)
        bars = agg.bars()
        assert bars[-1][0] == "2026-09-29 00:00"
        assert bars[-1][5] == 0.0

        # 之後 delta 正常累計：13 - 8 = 5
        assert agg.apply_quote("2026-09-29 00:00:40", 101.0, 13.0)
        assert agg.bars()[-1][5] == 5.0

    def test_out_of_order_tick_skipped(self):
        self.agg.apply_quote("2026-09-28 14:30:20", 100.5, 107.0)
        snapshot = self.agg.bars()
        # 早於已處理 tick → 整筆 skip，bars 完全唔變
        assert not self.agg.apply_quote("2026-09-28 14:30:10", 999.0, 999.0)
        assert self.agg.bars() == snapshot

    def test_delayed_tick_before_snapshot_skipped(self):
        # seed 後 _last_tick_dt = 最後歷史 bar 邊界（14:30）→ 早於呢個嘅延遲 push skip
        assert not self.agg.apply_quote("2026-09-28 14:29:58", 999.0, 999.0)
        assert len(self.agg.bars()) == 1

    def test_duplicate_tick_is_noop(self):
        self.agg.apply_quote("2026-09-28 14:30:05", 100.0, 100.0)
        snapshot = self.agg.bars()
        assert not self.agg.apply_quote("2026-09-28 14:30:05", 100.0, 100.0), "重複 tick 應 idempotent no-op"
        assert self.agg.bars() == snapshot

    @pytest.mark.parametrize(
        "dt,price,cum", [
            ("garbage", 100.0, 10.0),
            (None, 100.0, 10.0),
            ("2026-09-28 14:30:05", 0.0, 10.0),
            ("2026-09-28 14:30:05", -5.0, 10.0),
            ("2026-09-28 14:30:05", None, 10.0),
            ("2026-09-28 14:30:05", "abc", 10.0),
        ]
    )
    def test_invalid_inputs_skipped(self, dt, price, cum):
        snapshot = self.agg.bars()
        assert not self.agg.apply_quote(dt, price, cum)
        assert self.agg.bars() == snapshot


class TestTimezoneInvariant:
    """live bar key 必須同 seeded history key 對得上（naive parse + floor，零 astimezone）。"""

    def test_live_tick_updates_seeded_forming_bar(self):
        agg = CandleAggregator(1)
        # futu kline time_key 格式 'yyyy-MM-dd HH:mm:ss'；quote data_time 同格式
        agg.seed_from_history([("2026-09-28 14:30:00", 100.0, 101.0, 99.0, 100.5, 50.0)])
        assert agg.apply_quote("2026-09-28 14:30:45", 100.9, 60.0)
        bars = agg.bars()
        assert len(bars) == 1, "tick 應更新已 seed 嘅 forming bar，唔好 append 新 bar"
        assert bars[0][0] == "2026-09-28 14:30"
        assert bars[0][4] == 100.9

    def test_history_minute_precision_key_matches(self):
        agg = CandleAggregator(1)
        agg.seed_from_history([("2026-09-28 14:30", 100.0, 101.0, 99.0, 100.5, 50.0)])
        assert agg.apply_quote("2026-09-28 14:30:59", 100.1, 55.0)
        assert len(agg.bars()) == 1


class TestMultiPeriod:
    def test_5m_flooring(self):
        agg = CandleAggregator(5)
        agg.seed_from_history([("2026-09-28 14:30:00", 100, 101, 99, 100.5, 50)])
        # 14:32 仍屬 14:30 bar
        assert agg.apply_quote("2026-09-28 14:32:10", 100.7, 60.0)
        assert len(agg.bars()) == 1
        # 14:35 → 新 bar
        assert agg.apply_quote("2026-09-28 14:35:01", 101.2, 70.0)
        bars = agg.bars()
        assert len(bars) == 2
        assert bars[-1][0] == "2026-09-28 14:35"

    def test_60m_flooring(self):
        agg = CandleAggregator(60)
        agg.seed_from_history([("2026-09-28 14:00:00", 100, 101, 99, 100.5, 50)])
        assert agg.apply_quote("2026-09-28 14:59:59", 100.3, 60.0)
        assert len(agg.bars()) == 1
        assert agg.apply_quote("2026-09-28 15:00:00", 100.4, 70.0)
        assert agg.bars()[-1][0] == "2026-09-28 15:00"
