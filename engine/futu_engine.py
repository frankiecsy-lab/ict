"""Futu 行情引擎：OpenD 連線 + 歷史 K 線 seed + QUOTE 訂閱實時回調聚合。

Threading model（見 README Architecture）:
- start() spawn daemon setup thread 跑 OpenQuoteContext / request_history_kline 等阻塞操作；
- switch() 每次 spawn 一個 daemon worker thread 做運行時改標的/週期（_workers list，stop() join 晒）；
- futu-api 每個 context 只有一條 callback thread → on_recv_rsp 必須快：parse + aggregate + emit，唔做重活；
- 跨線程傳 immutable tuple-of-tuples snapshot（pyqtSignal queued），GUI 負責 render。

運行時切換一致性：engine 只持一個 immutable `_State(agg, code, kline_type, anchor_date)` reference；
handler 每 batch load 一次 + per-row `row.code != state.code → skip`（unsubscribe 唔係硬停，
in-flight push 會喺 swap 後先至到）+ emit 前確認 `state is eng._state`。

實測驗證嘅 OpenD 行為（2026-09-29/30, HK.HSImain）:
1. no-window request_history_kline 返回一年前舊數據 → 必須用 now() 計算嘅明確 start/end 窗口；
2. window + max_count 返回時間序**頭 N 根**（唔係最近 N 根）→ page_req_key 分頁攞晒再 tail(history_count)；
3. DataFrame 欄位順序係 open/close/high/low（唔係 OHLC）→ 按欄位名提取；
4. subscribe 成功時第二個返回值係 None → 只檢查 ret code；
5. live tick data_time 係 time-only 'HH:mm:ss.SSS' → 補 date = max(anchor, market_today)；
   market_today 用市場自己時區（zoneinfo）計算——美股喺 HKT 機上「今日」會同 machine-local 差一日。
"""
from __future__ import annotations

import logging
import math
import re
import threading
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import QObject, Signal

from futu import (
    AuType,
    KLType,
    RET_OK,
    OpenQuoteContext,
    StockQuoteHandlerBase,
    SubType,
)

from config import kline_period_minutes
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

# 股票編號格式（Step 2 支持美港股；futu 原生 code 格式）
_CODE_RE = re.compile(r"^(HK|US)\.\w+$", re.IGNORECASE)

# time-only tick 補 fallback date 用嘅市場時區（只影響日曆日期推斷，永遠唔轉換數據 timestamp——時區鐵律不變）
_MARKET_TZ: dict[str, str] = {
    "HK": "Asia/Hong_Kong",
    "US": "America/New_York",
}


@dataclass(frozen=True)
class _State:
    """當前行情狀態（immutable reference；切換時一次過 swap，handler 靠 identity check）。"""

    aggregator: CandleAggregator
    code: str
    kline_type: str
    anchor_date: date | None = None


def _fallback_date(anchor: date | None, code: str) -> date:
    """time-only tick 要補嘅日期：max(anchor, 市場時區今日)。

    處理夜期跨午夜（00:00 後 today > anchor → 用 today）同 clock skew
    （anchor > today → 保持 anchor，跟住 seed）。市場時區由 code prefix 決定。
    """
    prefix = code.split(".", 1)[0].upper() if "." in code else "HK"
    try:
        tz = ZoneInfo(_MARKET_TZ.get(prefix, _MARKET_TZ["HK"]))
        today = datetime.now(tz).date()
    except Exception:  # noqa: BLE001 — tzdata 缺失等 → 回落 machine-local
        today = date.today()
    return anchor if (anchor is not None and anchor > today) else today


class _QuoteHandler(StockQuoteHandlerBase):
    """QUOTE push 回調：parse tick → 聚合入蠟燭 → emit bars_changed 新 snapshot。"""

    def __init__(self, engine: "FutuEngine") -> None:
        super().__init__()
        self._engine = engine

    def on_recv_rsp(self, rsp_pb):  # noqa: N802 (SDK naming)
        ret_code, data = super().on_recv_rsp(rsp_pb)
        eng = self._engine
        if ret_code != RET_OK or data is None:
            if not eng._closed:
                eng.error.emit(f"QUOTE push 異常: ret={ret_code}")
            return ret_code, data
        state = eng._state  # 每 batch load 一次（GIL-atomic reference）
        if state is None:
            return ret_code, data
        fallback = _fallback_date(state.anchor_date, state.code)
        changed = False
        for row in data.itertuples(index=False):
            # code filter：切換後舊標的嘅 in-flight push（unsubscribe 唔係硬停）一律 skip
            if getattr(row, "code", state.code) != state.code:
                continue
            dt = resolve_tick_datetime(row.data_time, fallback)
            if dt is None:
                continue
            try:
                price = float(row.last_price)
                cum_vol = float(row.volume)
            except (TypeError, ValueError):
                continue
            if not price > 0:  # NaN guard：nan > 0 係 False → skip
                continue
            changed |= state.aggregator.apply_quote(dt, price, cum_vol)
        if eng.cfg.debug and len(data):
            logger.debug("tick batch rows=%d", len(data))
        if changed and state is eng._state:  # batch 中途 state 被 swap → 呢批 discard
            eng.bars_changed.emit(state.aggregator.bars())
        return ret_code, data


class FutuEngine(QObject):
    """futu 行情 pipeline 嘅 QObject 包裝。

    Signals（全部喺非 GUI thread emit；Qt auto-queue 去 GUI thread）:
    - history_ready(tuple[Bar]): seed / 切換完成後嘅完整 snapshot
    - bars_changed(tuple[Bar]): tick 聚合後嘅新 snapshot
    - status(str) / error(str)

    運行時切換：switch(code, kline_type) spawn worker thread 做 unsubscribe → fetch →
    seed → subscribe，全部驗證通過先 swap `_State`；任何失敗 rollback（resubscribe 舊標的）。
    """

    history_ready = Signal(tuple)
    bars_changed = Signal(tuple)
    status = Signal(str)
    error = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cfg = None
        self._state: _State | None = None
        self._ctx: OpenQuoteContext | None = None
        self._thread: threading.Thread | None = None      # 初始 setup thread
        self._workers: list[threading.Thread] = []       # switch worker threads（stop() join 晒）
        self._switching = False                          # switch guard flag
        self._closed = False                             # stop() 後抑制 emit / reject switch
        self._lock = threading.Lock()

    @property
    def cfg(self):
        return self._cfg

    @property
    def state(self) -> _State | None:
        return self._state

    @property
    def aggregator(self) -> CandleAggregator:
        if self._state is None:
            raise RuntimeError("FutuEngine.start() 未呼叫")
        return self._state.aggregator

    def tick_date(self) -> date:
        """time-only tick 要補嘅日期（讀當前 state；handler 用 _fallback_date(captured state)）。"""
        if self._state is None:
            return _fallback_date(None, "HK")
        return _fallback_date(self._state.anchor_date, self._state.code)

    def start(self, cfg) -> None:
        """啟動連線 + 歷史 fetch + 訂閱（背景 daemon thread，立即返回）。"""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return  # 已經 starting/started
            self._closed = False
            self._cfg = cfg
            self._state = _State(CandleAggregator(cfg.period_minutes),
                                 cfg.trading_code, cfg.kline_type, None)
            thread = threading.Thread(target=self._setup, name="futu-setup", daemon=True)
            self._thread = thread
        thread.start()

    def stop(self) -> None:
        """Idempotent 關閉：close ctx（停 callback thread）、join setup + switch worker threads。"""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            workers = list(self._workers)
            self._workers.clear()
            thread = self._thread
            self._thread = None
        self._close_ctx()
        for t in (thread, *workers):
            if t is not None and t.is_alive():
                t.join(timeout=10)

    def switch(self, code: str | None = None, kline_type: str | None = None) -> None:
        """運行時改標的/週期（worker thread，立即返回）。

        校驗失敗 → error signal；setup/switch 進行中 → status 提示並 reject。
        任一參數為 None → 沿用當前值（UI 一律傳齊兩個）。
        """
        with self._lock:
            if self._closed or self._ctx is None:
                return
            cur = self._state
        new_code = code.strip().upper() if code else (cur.code if cur else None)
        new_ktype = kline_type.strip().upper() if kline_type else (cur.kline_type if cur else None)
        if new_code is None or new_ktype is None:
            return  # start() 未行過 / 無當前狀態 → 冇嘢可以切
        if code and not _CODE_RE.match(new_code):
            self.error.emit(f"股票編號格式錯誤：{code!r}（例：HK.00700 / US.AAPL）")
            return
        if kline_type and new_ktype not in _KLTYPE_MAP:
            valid = ", ".join(_KLTYPE_MAP)
            self.error.emit(f"未知 K 線週期 {kline_type!r}，可選：{valid}")
            return
        with self._lock:
            if self._closed or self._ctx is None:
                self.error.emit("未連線 OpenD，無法切換")
                return
            if self._thread is not None and self._thread.is_alive():
                self.status.emit("連線中，請稍後再試")
                return
            if self._switching:
                self.status.emit("切換進行中，請稍候")
                return
            self._switching = True
            thread = threading.Thread(target=self._reconfigure, args=(new_code, new_ktype),
                                      name="futu-switch", daemon=True)
            self._workers.append(thread)
        thread.start()

    def _rollback(self, code: str, msg: str) -> None:
        """切換失敗 → resubscribe 舊標的（state 未 swap，圖表保持 live）。"""
        ctx = self._ctx
        if ctx is not None and not self._closed:
            try:
                ret, info = ctx.subscribe([code], [SubType.QUOTE])
                if ret != RET_OK:
                    logger.error("rollback resubscribe %s 失敗: %s", code, info)
            except Exception:  # noqa: BLE001 — rollback 唔好 propagate
                logger.exception("rollback resubscribe exception")
        if not self._closed:
            self.error.emit(f"切換失敗：{msg}")

    def _reconfigure(self, new_code: str, new_ktype: str) -> None:
        """Worker thread：unsubscribe 舊 → fetch+seed 新 → subscribe 新 → swap state。"""
        old_state = self._state
        try:
            if not self._closed and old_state is not None:
                self.status.emit(f"切換中 {new_code} {new_ktype}…")
            ctx = self._ctx
            if ctx is None or old_state is None:
                return
            # 1) unsubscribe 舊（唔係硬停——in-flight push 由 handler code filter 兜底）
            try:
                ret, info = ctx.unsubscribe([old_state.code], [SubType.QUOTE])
                if ret != RET_OK:
                    logger.warning("unsubscribe %s 失敗: %s", old_state.code, info)
            except Exception:  # noqa: BLE001 — unsubscribe 失敗唔阻切換（code filter 兜底）
                logger.exception("unsubscribe exception")
            # 2) fetch 新歷史（明確窗口 + 分頁；失敗 raise → rollback）
            rows = self._fetch_history(ctx, new_code, new_ktype)
            # 3) build + seed 新 aggregator
            period = kline_period_minutes(new_ktype)
            agg = CandleAggregator(period)
            n = agg.seed_from_history(rows)
            if n == 0:
                self._rollback(old_state.code, f"{new_code} {new_ktype} 冇歷史數據")
                return
            anchor = None
            last_dt = parse_market_time(rows[-1][0])
            if last_dt is not None:
                anchor = last_dt.date()
            # 4) subscribe 新（全部驗證通過先 swap）
            ret, sub_info = ctx.subscribe([new_code], [SubType.QUOTE])
            if ret != RET_OK:
                self._rollback(old_state.code, f"subscribe {new_code} 失敗: {sub_info}")
                return
            # 5) atomic swap + notify
            new_state = _State(agg, new_code, new_ktype, anchor)
            self._state = new_state
            if not self._closed:
                self.history_ready.emit(new_state.aggregator.bars())
                self.status.emit(f"切換成功 · {new_code} {new_ktype} · {n} 根")
        except Exception as exc:  # noqa: BLE001 — fetch 等任何失敗 → rollback + 回報
            logger.exception("FutuEngine reconfigure failed")
            if old_state is not None and not self._closed:
                self._rollback(old_state.code, str(exc))
        finally:
            self._switching = False

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

    def _fetch_history(self, ctx, code: str, kline_type: str) -> list[tuple]:
        """明確窗口 + page_req_key 分頁 → 最近 history_count 根（時間序 tuple）。"""
        cfg = self._cfg
        period = kline_period_minutes(kline_type) or cfg.period_minutes
        ktype = _KLTYPE_MAP[kline_type]
        start_str, end_str = history_window(period, cfg.history_count)
        rows: list[tuple] = []
        page_key = None
        for _ in range(_MAX_PAGES):
            ret, df, page_key = ctx.request_history_kline(
                code, ktype=ktype, autype=AuType.QFQ,
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
            if not self._closed:
                self.error.emit(f"連唔到 OpenD {cfg.opend_host}:{cfg.opend_port}: {exc}")
            return
        with self._lock:
            if self._ctx is not None:  # stop() 已行過 / 重複 start → close 自己嘅連線退出
                ctx.close()
                return
            self._ctx = ctx
        try:
            self.status.emit("OpenD 連線成功")

            rows = self._fetch_history(ctx, cfg.trading_code, cfg.kline_type)
            cur_state = self._state
            n = cur_state.aggregator.seed_from_history(rows)
            anchor = None
            if rows:
                last_dt = parse_market_time(rows[-1][0])
                if last_dt is not None:
                    anchor = last_dt.date()
            # seed 完成先 swap state（anchor 一齊入，無 None window）
            self._state = _State(cur_state.aggregator, cfg.trading_code, cfg.kline_type, anchor)
            if not self._closed:
                self.history_ready.emit(self._state.aggregator.bars())

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
