"""Futu 行情引擎：OpenD 連線 + 歷史 K 線 seed + QUOTE 訂閱實時回調聚合。

Threading model（見 README Architecture）:
- start() spawn daemon setup thread 跑 OpenQuoteContext / request_history_kline 等阻塞操作；
- futu-api 每個 context 只有一條 callback thread → on_recv_rsp 必須快：parse + aggregate + emit，唔做重活；
- 跨線程傳 immutable tuple-of-tuples snapshot（pyqtSignal queued），GUI 負責 render。

實測驗證嘅 OpenD 行為（2026-09-29/30, HK.HSImain）:
1. no-window request_history_kline 返回一年前舊數據 → 必須用 now() 計算嘅明確 start/end 窗口；
2. window + max_count 返回時間序**頭 N 根**（唔係最近 N 根）→ page_req_key 分頁攞晒再 tail(history_count)；
3. DataFrame 欄位順序係 open/close/high/low（唔係 OHLC）→ 按欄位名提取；
4. subscribe 成功時第二個返回值係 None → 只檢查 ret code；
5. live tick data_time 係 time-only 'HH:mm:ss.SSS' → 補 date = max(anchor, today)。
"""
from __future__ import annotations

import logging
import math
import threading
from datetime import date, datetime

from PySide6.QtCore import QObject, Signal

from futu import (
    AuType,
    KLType,
    RET_OK,
    OpenQuoteContext,
    StockQuoteHandlerBase,
    SubType,
)

from .candle_aggregator import CandleAggregator
from .timeutil import history_window, parse_market_time, resolve_tick_datetime

logger = logging.getLogger(__name__)

_KLTYPE_MAP: dict[str, KLType] = {
    "K_1M": KLType.K_1M,
    "K_3M": KLType.K_3M,
    "K_5M": KLType.K_5M,
    "K_15M": KLType.K_15M,
    "K_30M": KLType.K_30M,
    "K_60M": KLType.K_60M,
    "K_DAY": KLType.K_DAY,
    "K_WEEK": KLType.K_WEEK,
    "K_MON": KLType.K_MON,
}

_PAGE_SIZE = 1000          # request_history_kline 單次上限（見 API_LIMITS）
_MAX_PAGES = 200           # 防禦上限：防 page_req_key 永遠唔係 None 時死循環


class _QuoteHandler(StockQuoteHandlerBase):
    """QUOTE push 回調：parse tick → 聚合入蠟燭 → emit bars_changed 新 snapshot。"""

    def __init__(self, engine: "FutuEngine") -> None:
        super().__init__()
        self._engine = engine

    def on_recv_rsp(self, rsp_pb):  # noqa: N802 (SDK naming)
        ret_code, data = super().on_recv_rsp(rsp_pb)
        eng = self._engine
        if ret_code != RET_OK or data is None:
            eng.error.emit(f"QUOTE push 異常: ret={ret_code}")
            return ret_code, data
        tick_date = eng.tick_date()  # time-only tick 補 date，每 batch 一次
        changed = False
        for row in data.itertuples(index=False):
            dt = resolve_tick_datetime(row.data_time, tick_date)
            if dt is None:
                continue
            try:
                price = float(row.last_price)
                cum_vol = float(row.volume)
            except (TypeError, ValueError):
                continue
            if not price > 0:  # NaN guard：nan > 0 係 False → skip
                continue
            changed |= eng.aggregator.apply_quote(dt, price, cum_vol)
        if eng.cfg.debug and len(data):
            logger.debug("tick batch rows=%d", len(data))
        if changed:
            eng.bars_changed.emit(eng.aggregator.bars())
        return ret_code, data


class FutuEngine(QObject):
    """futu 行情 pipeline 嘅 QObject 包裝。

    Signals（全部喺非 GUI thread emit；Qt auto-queue 去 GUI thread）:
    - history_ready(tuple[Bar]): seed 完成後嘅完整 snapshot
    - bars_changed(tuple[Bar]): tick 聚合後嘅新 snapshot
    - status(str) / error(str)
    """

    history_ready = Signal(tuple)
    bars_changed = Signal(tuple)
    status = Signal(str)
    error = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cfg = None
        self._aggregator: CandleAggregator | None = None
        self._ctx: OpenQuoteContext | None = None
        self._thread: threading.Thread | None = None
        self._anchor_date: date | None = None  # seed 最後一根歷史 bar 嘅日期（tick time-only → full datetime）
        self._lock = threading.Lock()

    @property
    def cfg(self):
        return self._cfg

    @property
    def aggregator(self) -> CandleAggregator:
        if self._aggregator is None:
            raise RuntimeError("FutuEngine.start() 未呼叫")
        return self._aggregator

    def tick_date(self) -> date:
        """time-only tick 要補嘅日期：max(anchor, today)。

        處理夜期跨午夜（00:00 後 today > anchor → 用 today）同 clock skew
        （anchor > today → 保持 anchor，跟住 seed）。
        """
        today = date.today()
        return self._anchor_date if (self._anchor_date is not None and self._anchor_date > today) else today

    def start(self, cfg) -> None:
        """啟動連線 + 歷史 fetch + 訂閱（背景 daemon thread，立即返回）。"""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return  # 已經 starting/started
            self._cfg = cfg
            self._aggregator = CandleAggregator(cfg.period_minutes)
            self._anchor_date = None
            thread = threading.Thread(target=self._setup, name="futu-setup", daemon=True)
            self._thread = thread
        thread.start()

    def stop(self) -> None:
        """Idempotent 關閉：close ctx（停 callback thread）、等 setup thread 結束。"""
        with self._lock:
            thread = self._thread
            self._thread = None
        self._close_ctx()
        if thread is not None and thread.is_alive():
            thread.join(timeout=10)

    def _close_ctx(self) -> None:
        """Close 本 engine 持有嘅 context（idempotent、thread-safe）。"""
        with self._lock:
            ctx = self._ctx
            self._ctx = None
        if ctx is not None:
            try:
                ctx.close()
            except Exception:  # noqa: BLE001 — close 唔好 propagate 去 GUI shutdown path
                logger.exception("OpenQuoteContext.close() failed")

    def _fetch_history(self, ctx) -> list[tuple]:
        """明確窗口 + page_req_key 分頁 → 最近 history_count 根（時間序 tuple）。"""
        cfg = self._cfg
        ktype = _KLTYPE_MAP[cfg.kline_type]
        start_str, end_str = history_window(cfg.period_minutes, cfg.history_count)
        rows: list[tuple] = []
        page_key = None
        for _ in range(_MAX_PAGES):
            ret, df, page_key = ctx.request_history_kline(
                cfg.trading_code, ktype=ktype, autype=AuType.QFQ,
                start=start_str, end=end_str, max_count=_PAGE_SIZE, page_req_key=page_key,
            )
            if ret != RET_OK or df is None:
                raise RuntimeError(f"request_history_kline 失敗: {df}")  # 錯誤時第二返回值係 err str
            if len(df):
                sub = df[["time_key", "open", "high", "low", "close", "volume"]]
                for r in sub.itertuples(index=False, name=None):
                    try:
                        vals = (r[0],) + tuple(float(v) for v in r[1:])
                    except (TypeError, ValueError):
                        continue
                    if not all(math.isfinite(v) for v in vals[1:]):
                        continue  # NaN/None 價格行 skip（外部數據邊界驗證）
                    rows.append(vals)
            if not page_key:
                break  # 最後一頁（key None/falsy）
        else:
            raise RuntimeError(f"歷史分頁超過 {_MAX_PAGES} 頁")
        return rows[-cfg.history_count:]

    def _setup(self) -> None:
        cfg = self._cfg
        try:
            ctx = OpenQuoteContext(cfg.opend_host, cfg.opend_port)
        except Exception as exc:  # noqa: BLE001 — 連線失敗（OpenD 未開等）→ 回報 GUI
            logger.exception("OpenQuoteContext connect failed")
            self.error.emit(f"連唔到 OpenD {cfg.opend_host}:{cfg.opend_port}: {exc}")
            return
        with self._lock:
            if self._ctx is not None:  # stop() 已行過 / 重複 start → close 自己嘅連線退出
                ctx.close()
                return
            self._ctx = ctx
        try:
            self.status.emit("OpenD 連線成功")

            rows = self._fetch_history(ctx)
            n = self.aggregator.seed_from_history(rows)
            if rows:
                last_dt = parse_market_time(rows[-1][0])
                if last_dt is not None:
                    self._anchor_date = last_dt.date()
            self.history_ready.emit(self.aggregator.bars())

            ctx.set_handler(_QuoteHandler(self))
            self.status.emit(f"訂閱 {cfg.trading_code} QUOTE 中…")
            ret, sub_info = ctx.subscribe([cfg.trading_code], [SubType.QUOTE])
            if ret != RET_OK:
                raise RuntimeError(f"subscribe 失敗: {sub_info}")  # 成功時第二返回值係 None（實測）
            self.status.emit(f"訂閱成功 · 歷史 {n} 根 · 等待實時報價")
        except Exception as exc:  # noqa: BLE001 — setup 任何失敗 → 回報 + 確保 ctx close
            logger.exception("FutuEngine setup failed")
            self.error.emit(str(exc))
            self._close_ctx()
