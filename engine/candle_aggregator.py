"""蠟燭聚合引擎：將實時報價 tick 聚合入 K 線。

純類，零 Qt / futu / pandas 依賴 → 可獨立單測。喺 futu callback thread 上調用，
所以 apply_quote 必須 O(1)/tick、唔好阻塞。

Bar = immutable tuple `(time_key, open, high, low, close, volume)`；
`bars()` 每次返回新 tuple snapshot（pyqtSignal 傳 reference，snapshot 不可變 → 無鎖）。

已知近似：
- seed / 日 rollover 後第一筆 tick 嘅 volume delta 記 0（累計成交量參考點重置），
  之後每筆都精確；最多影響一根 bar 嘅開頭幾秒。
- 期貨夜期「交易日」界線未必等於日曆午夜，rollover reset 係合理近似。
"""
from __future__ import annotations

from datetime import datetime

from .timeutil import bar_key, floor_to_period, parse_market_time

# (time_key, open, high, low, close, volume)
Bar = tuple[str, float, float, float, float, float]


class CandleAggregator:
    """由 tick 聚合出 K 線序列；歷史 seed + live append/update。"""

    def __init__(self, period_minutes: int):
        if period_minutes < 1:
            raise ValueError(f"period_minutes 必須 >= 1，收到 {period_minutes!r}")
        self._period = period_minutes
        self._bars: list[Bar] = []
        self._last_tick_dt: datetime | None = None
        self._last_cum_vol: float | None = None

    @property
    def period_minutes(self) -> int:
        return self._period

    def seed_from_history(self, rows) -> int:
        """以歷史 K 線 seed。rows：(time_key, open, high, low, close, volume)，
        time_key 接受 'yyyy-MM-dd HH:mm[:ss]' string 或 datetime；非法行跳過。
        返回實際 seed 嘅 bar 數。重複調用會取代舊 bars（重連 re-seed 安全）。
        """
        normalized: list[Bar] = []
        last_floored: datetime | None = None
        for row in rows:
            t = parse_market_time(row[0])
            if t is None:
                continue
            try:
                o, h, l, c, v = (float(x) for x in row[1:6])
            except (TypeError, ValueError):
                continue
            f = floor_to_period(t, self._period)
            normalized.append((bar_key(f, self._period), o, h, l, c, v))
            last_floored = f
        if not normalized:
            return 0
        normalized.sort(key=lambda b: b[0])
        self._bars = normalized
        # 以最後一根歷史 bar 嘅週期邊界做 out-of-order 參考：早於 snapshot 嘅延遲 push 會被 skip
        self._last_tick_dt = last_floored
        self._last_cum_vol = None
        return len(normalized)

    def apply_quote(self, data_time, last_price, cum_volume) -> bool:
        """處理一筆 QUOTE tick；返回 bars 有冇變動。

        - close = last_price；high/low = max/min(舊值, last_price)（quote 嘅日級
          open/high/low 係當日累計、尺度錯，唔好用）。
        - volume = 累計日成交量 delta：max(0, cum_now − 上一筆 cum)。
        """
        dt = parse_market_time(data_time)
        if dt is None:
            return False
        try:
            price = float(last_price)
            cum = float(cum_volume)
        except (TypeError, ValueError):
            return False
        if price <= 0:
            return False

        # Out-of-order guard：早於上一筆已處理 tick → 整筆 skip；重複 tick（==）自然 idempotent no-op
        if self._last_tick_dt is not None and dt < self._last_tick_dt:
            return False

        # 日界 rollover：date 變咗 → 累計成交量參考重置（新交易日 counter 由 0 起算）
        if self._last_tick_dt is not None and dt.date() != self._last_tick_dt.date():
            self._last_cum_vol = None

        key = bar_key(floor_to_period(dt, self._period), self._period)
        delta = max(0.0, cum - self._last_cum_vol) if self._last_cum_vol is not None else 0.0

        changed = False
        if self._bars and self._bars[-1][0] == key:
            last = self._bars[-1]
            cand = (key, last[1], max(last[2], price), min(last[3], price), price, last[5] + delta)
            if cand != last:
                self._bars[-1] = cand
                changed = True
        else:
            self._bars.append((key, price, price, price, price, delta))
            changed = True

        self._last_tick_dt = dt
        self._last_cum_vol = cum
        return changed

    def bars(self) -> tuple[Bar, ...]:
        """返回 immutable snapshot（每次新 tuple），供 pyqtSignal 跨線程傳遞。"""
        return tuple(self._bars)
