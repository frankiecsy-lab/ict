"""核心引擎包：時間工具 + 蠟燭聚合（純類，零 Qt/futu 依賴）。

FutuEngine（QObject）於 Commit 3 加入後會喺此 export。
"""
from .candle_aggregator import CandleAggregator
from .timeutil import bar_key, floor_to_period, is_up, parse_market_time

__all__ = [
    "CandleAggregator",
    "bar_key",
    "floor_to_period",
    "is_up",
    "parse_market_time",
]
