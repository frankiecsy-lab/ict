"""市場時間工具（純 stdlib，零依賴）。

時區鐵律：富途 quote `data_time` 同 kline `time_key` 對 HK.HSImain 都係 HKT naive
string → 一律 parse naive、floor 到週期邊界，**永遠唔好 astimezone / 加 tzinfo**。
呢個係 live bar key 同歷史 bar key 對得上嘅前提。
"""
from __future__ import annotations

import math
from datetime import date, datetime, time as dtime, timedelta

_MINUTES_PER_DAY = 24 * 60
# request_history_kline 窗口寬度上限（天）：OpenD 對過長窗口會拒收（實測 K_MON 跨度 >~55 年 → ret=-1
# F3CNN返回错误）。大週期 × 大 count 算出嘅理論窗口可達百多年（K_MON×1000 ≈ 123 年）→ 必須 clamp。
# 40 年遠低於臨界點（留 ~15 年安全餘量），且已覆蓋 HK.HSImain 全部可用歷史（~21 年）。
_MAX_WINDOW_DAYS = 40 * 365


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


def parse_time_only(value) -> dtime | None:
    """解析時間-only string（futu live tick data_time 格式 'HH:mm:ss.SSS'）。失敗返回 None。"""
    if not isinstance(value, str):
        return None
    s = value.strip()
    for fmt in ("%H:%M:%S.%f", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    return None


def resolve_tick_datetime(value, fallback_date=None) -> datetime | None:
    """將 tick 時間解析為 naive datetime。

    futu live QUOTE push 嘅 data_time 實際係 **time-only** string 'HH:mm:ss.SSS'（無日期），
    需要由 engine 傳入 date（max(anchor, today)）補齊；完整 datetime string / datetime 對象直接經 parse_market_time。
    """
    if isinstance(value, datetime):
        return parse_market_time(value)
    if not isinstance(value, str):
        return None
    s = value.strip()
    if "-" in s or "T" in s:  # 含日期部分 → 完整格式
        return parse_market_time(s)
    t = parse_time_only(s)
    if t is None:
        return None
    if fallback_date is None:
        fallback_date = datetime.now().date()
    return datetime.combine(fallback_date, t)


def history_window(period_minutes: int, count: int, now=None) -> tuple[str, str]:
    """計算 request_history_kline 嘅明確 start/end 窗口（返回 'yyyy-MM-dd HH:mm:ss' string）。

    實測：no-window 請求對 HK.HSImain 返回一年前舊數據 → 必須用明確窗口；
    且 window + max_count 返回時間序**頭 N 根**而非最近 N 根 → engine 端 page_req_key 分頁攞晒再 tail(count)。
    窗口寬度保守估計（假設每日最少 360 分鐘交易），覆蓋港股（~375 min/日）同恒指期貨夜期（~834 min/日）。
    """
    if period_minutes <= 0 or count <= 0:
        raise ValueError("period_minutes/count must be > 0")
    now = now or datetime.now()
    if period_minutes < _MINUTES_PER_DAY:
        days = math.ceil(count * period_minutes / 360.0) + 2
    else:
        days = int(math.ceil(count * (period_minutes / _MINUTES_PER_DAY) * 1.5)) + 7
    days = min(days, _MAX_WINDOW_DAYS)  # 大週期 × 大 count → clamp，防 OpenD 拒收過長窗口
    start = now - timedelta(days=days)
    return start.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S")
