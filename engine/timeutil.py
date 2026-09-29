"""市場時間工具（純 stdlib，零依賴）。

時區鐵律：富途 quote `data_time` 同 kline `time_key` 對 HK.HSImain 都係 HKT naive
string → 一律 parse naive、floor 到週期邊界，**永遠唔好 astimezone / 加 tzinfo**。
呢個係 live bar key 同歷史 bar key 對得上嘅前提。
"""
from __future__ import annotations

from datetime import datetime, timedelta

_MINUTES_PER_DAY = 24 * 60


def parse_market_time(value) -> datetime | None:
    """解析市場時間為 naive datetime；失敗返回 None。

    接受 'yyyy-MM-dd HH:mm:ss'（futu push / kline 格式）同 'yyyy-MM-dd HH:mm'，
    以及已經係 datetime 嘅輸入（若有 tzinfo 只係 strip 掉，唔做轉換）。
    """
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        s = value.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None
    else:
        return None
    if dt.tzinfo is not None:
        # 時區鐵律：唔做 astimezone，只 strip tzinfo（futu 數據本應 naive）
        dt = dt.replace(tzinfo=None)
    return dt


def floor_to_period(dt: datetime, period_minutes: int) -> datetime:
    """將時間向下取整到週期邊界。

    intraday → 分鐘邊界；K_DAY → 日曆日 00:00；K_WEEK → 該週星期一 00:00；
    K_MON（config 以 30 天近似）→ 該月 1 號 00:00。
    """
    if period_minutes >= 30 * _MINUTES_PER_DAY:
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period_minutes >= 7 * _MINUTES_PER_DAY:
        monday = dt - timedelta(days=dt.weekday())
        return monday.replace(hour=0, minute=0, second=0, microsecond=0)
    if period_minutes >= _MINUTES_PER_DAY:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    total = dt.hour * 60 + dt.minute
    floored = (total // period_minutes) * period_minutes
    h, m = divmod(floored, 60)
    return dt.replace(hour=h, minute=m, second=0, microsecond=0)


def bar_key(dt: datetime, period_minutes: int) -> str:
    """bar 嘅正規化 key：intraday='yyyy-MM-dd HH:mm' / K_DAY|K_WEEK='yyyy-MM-dd' / K_MON='yyyy-MM'。

    歷史 seed 同 live tick 一律經 floor_to_period + bar_key 產生 key，確保兩者一致。
    """
    if period_minutes >= 30 * _MINUTES_PER_DAY:
        return dt.strftime("%Y-%m")
    if period_minutes >= _MINUTES_PER_DAY:
        return dt.strftime("%Y-%m-%d")
    return dt.strftime("%Y-%m-%d %H:%M")


def is_up(open_: float, close: float) -> bool:
    """蠟燭方向：close >= open 視為漲（doji 畫作漲色）。"""
    return close >= open_
