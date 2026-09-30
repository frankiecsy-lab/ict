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
6. 代碼大小寫敏感：HK.HSImain 等主力連續合約必須保留原 casing，upper 做 HSIMAIN OpenD 報「未知股票」
   → _normalize_code() upper 後經 _CODE_ALIASES 映返正規形式。
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
    Market,
    RET_OK,
    OpenQuoteContext,
    StockQuoteHandlerBase,
    SubType,
)

from config import kline_period_minutes
from .candle_aggregator import CandleAggregator
from .stock_catalog import StockEntry, register_code_aliases
from .subscription_store import SubscriptionStore, default_db_path
from .timeutil import history_window, parse_market_time, resolve_tick_datetime

logger = logging.getLogger(__name__)

# 定時 reconcile 間隔（秒）：對「已不活躍且訂閱滿 MIN_SUBSCRIBE_SECONDS」的洩漏訂閱重試 unsubscribe。
_RECONCILE_INTERVAL = 30.0

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

# Futu 代碼大小寫敏感特例（主力連續合約）：OpenD 拒收全 upper 形式（實測「未知股票 HSIMAIN」）
_CODE_ALIASES = {
    "HK.HSIMAIN": "HK.HSImain",   # 恒指期貨主連
    "HK.HHIMAIN": "HK.HHImain",   # 國指期貨主連
    "HK.MHIMAIN": "HK.MHImain",   # 小恒指期貨主連
}

# get_stock_basicinfo 唔包含主力連續合約（2026-09-30 live 實測：HK 3798 rows 冇 HSImain）
# → seed 補返，確保預設 TRADING_CODE 一定有 autocomplete；API 日後若返回同 code 會 dedup skip。
# 三隻 HK 指數期貨主連均經 get_market_snapshot live 驗證（2026-09-30）；US/SG 指數期貨本帳號
# 行情權限不足、官方名稱無法核實 → 暫唔 seed（避免 seed-first dedup 用錯名 shadow API 正確名）。
_SEED_ENTRIES = (
    StockEntry("HK.HSImain", "恒指期货主连", ""),
    StockEntry("HK.HHImain", "国指期货主连", ""),
    StockEntry("HK.MHImain", "小恒指期货主连", ""),
)


def _normalize_code(raw: str) -> str:
    """strip + uppercase，再將大小寫敏感特例映返正規形式。"""
    code = raw.strip().upper()
    return _CODE_ALIASES.get(code, code)


def _cell_str(value) -> str:
    """DataFrame cell → 乾淨 string（None/NaN 空欄位 → ""，防 "nan" 字串混入目錄）。"""
    if value is None:
        return ""
    try:
        if value != value:  # NaN guard（pandas 空欄位）
            return ""
    except TypeError:
        pass
    s = str(value).strip()
    return "" if s.lower() == "nan" else s

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
    catalog_ready = Signal(tuple)   # tuple[StockEntry]：HK+US 股票目錄（fuzzy autocomplete 用）

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
        # SQLite 訂閱帳本：記錄每筆活躍 QUOTE 訂閱（code/subtype/時間）→ reconcile 清理洩漏。
        # db_path=None → default_db_path()（開發=專案根目錄、frozen=exe 旁邊）。
        self._store: SubscriptionStore | None = None
        self._reconcile_timer: threading.Timer | None = None   # 定時重試 unsubscribe 洩漏訂閱

    def _ensure_store(self) -> SubscriptionStore:
        """惰性建立訂閱帳本（首次 subscribe/reconcile 前）；db_path 由 start() 注入或預設。"""
        if self._store is None:
            path = getattr(self, "_db_path", None) or default_db_path()
            self._store = SubscriptionStore(path)
        return self._store

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

    def start(self, cfg, db_path: str | Path | None = None) -> None:
        """啟動連線 + 歷史 fetch + 訂閱（背景 daemon thread，立即返回）。

        db_path：SQLite 訂閱帳本路徑；None → default_db_path()。
        """
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return  # 已經 starting/started
            self._closed = False
            self._cfg = cfg
            self._db_path = db_path
            self._state = _State(CandleAggregator(cfg.period_minutes),
                                 _normalize_code(cfg.trading_code), cfg.kline_type, None)
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
            timer = self._reconcile_timer
            self._reconcile_timer = None
        if timer is not None:
            timer.cancel()  # 阻止未觸發嘅 reconcile；已運行中嘅會因 _closed 快速返回
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
        new_code = _normalize_code(code) if code else (cur.code if cur else None)
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
                else:
                    self._ensure_store().add(code)  # re-subscribe 成功 → 帳本重新計時
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
                    # 「訂閱未滿 1 分鐘」→ OpenD 拒收；帳本保留呢筆（pending），reconcile 稍後重試
                else:
                    self._ensure_store().remove(old_state.code)
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
            self._ensure_store().add(new_code)   # 新訂閱入帳本（re-subscribe 同 code → 重新計時）
            self._schedule_reconcile()           # 排程清理：舊 code 若 unsubscribe 失敗（pending）稍後重試
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

    # ------------------------------------------------------------- 訂閱帳本 reconcile（自動清理洩漏）

    def _schedule_reconcile(self) -> None:
        """排程一次定時 reconcile（_RECONCILE_INTERVAL 後）。

        冪等：已有 pending timer → 唔重複排。reconcile 喺獨立 daemon thread 跑（unsubscribe
        係同步阻塞，唔好占 switch worker / callback thread）。
        """
        with self._lock:
            if self._closed or self._ctx is None:
                return
            if self._reconcile_timer is not None and self._reconcile_timer.is_alive():
                return  # 已經排程咗
            timer = threading.Timer(_RECONCILE_INTERVAL, self._reconcile_subscriptions)
            timer.daemon = True
            timer.name = "futu-reconcile"
            self._reconcile_timer = timer
        timer.start()

    def _query_open_subscriptions(self, ctx) -> set[str] | None:
        """query_subscription() → OpenD 端實際訂閱緊嘅 code 集合；失敗/異常 → None（對帳跳過）。"""
        try:
            ret, data = ctx.query_subscription(is_all_conn=False)
        except Exception:  # noqa: BLE001 — query 唔好 propagate 去 reconcile worker
            logger.exception("query_subscription exception")
            return None
        if ret != RET_OK or not isinstance(data, dict):
            logger.warning("query_subscription 失敗: %s", data)
            return None
        codes: set[str] = set()
        for sub_list in (data.get("sub_list") or {}).values():
            codes.update(sub_list or [])
        return codes

    def _reconcile_subscriptions(self) -> None:
        """定時清理：對「已不活躍且訂閱滿 MIN_SUBSCRIBE_SECONDS」的洩漏訂閱重試 unsubscribe。

        流程（獨立 daemon thread）：
        1. query_subscription() 攞 OpenD 端實際訂閱 code；失敗 → 跳過呢輪（下輪再試）。
        2. store.due_for_cleanup(active_codes) = 帳本入面「唔係當前 state.code 且 age>=閾值」嘅條目。
        3. 逐筆 unsubscribe：成功 → remove；失敗（例如仲未滿 1min）→ 保留，下輪再試。
        4. query 到但帳本冇記錄嘅 code（上次 crash 殘留、唔係當前 state）→ 直接 unsubscribe + 唔入帳本。

        冪等：每輪重讀 store；無 due → no-op。stop() 後 _closed=True → 快速返回。
        """
        with self._lock:
            if self._closed or self._ctx is None:
                return
            ctx = self._ctx
        state = self._state
        active_codes = {state.code} if state else set()

        open_codes = self._query_open_subscriptions(ctx)
        if open_codes is None:
            return  # query 失敗 → 唔改帳本，下輪再試（避免誤刪）

        store = self._ensure_store()
        ledger_codes = {c for c, _s, _ts in store.list_active()}  # loop 前 snapshot（residual 判斷用）
        for code, subtype, _ts in store.due_for_cleanup(active_codes):
            try:
                ret, info = ctx.unsubscribe([code], [SubType.QUOTE])
            except Exception:  # noqa: BLE001 — 單筆 unsubscribe exception 唔阻其餘清理
                logger.exception("reconcile unsubscribe %s exception", code)
                continue
            if ret == RET_OK:
                store.remove(code, subtype)
                logger.info("reconcile：已清理洩漏訂閱 %s", code)
            else:
                logger.warning("reconcile：unsubscribe %s 仍失敗（稍後重試）: %s", code, info)

        # 殘留自癒：OpenD 端有、但帳本完全冇記錄（上次 crash 前嘅訂閱）、且唔係當前 state →
        # unsubscribe。用 loop 前 ledger snapshot 排除「已喺帳本」嘅 code——避免同 due-loop 重複 unsub。
        for code in open_codes - active_codes - ledger_codes:
            try:
                ret, info = ctx.unsubscribe([code], [SubType.QUOTE])
            except Exception:  # noqa: BLE001 — 同上
                logger.exception("reconcile unsubscribe residual %s exception", code)
                continue
            if ret == RET_OK:
                logger.info("reconcile：已清理殘留訂閱 %s（帳本無記錄）", code)
            else:
                logger.warning("reconcile：unsubscribe 殘留 %s 失敗: %s", code, info)

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

    def _fetch_catalog(self, ctx) -> list[StockEntry]:
        """Fetch HK+US 股票基本資料（code/name/english_name）→ StockEntry list。

        Per-market try/except：單一市場失敗唔阻另一邊；重覆 code dedup。
        `code` 保留 API 返回嘅嚴格大小寫正規形式（autocomplete + alias 註冊用）。
        """
        entries: list[StockEntry] = []
        seen: set[str] = set()
        for e in _SEED_ENTRIES:  # seed 先入（API 返回同 code 時 dedup skip）
            if e.code not in seen:
                seen.add(e.code)
                entries.append(e)
        for market in (Market.HK, Market.US):
            try:
                ret, df = ctx.get_stock_basicinfo(market)
            except Exception:  # noqa: BLE001 — 單市場 exception 唔阻另一邊
                logger.exception("get_stock_basicinfo(%s) exception", market)
                continue
            if ret != RET_OK or df is None:
                logger.warning("get_stock_basicinfo(%s) 失敗: %s", market, df)
                continue
            for row in df.itertuples(index=False):
                code = _cell_str(getattr(row, "code", None))
                if not code or code in seen:
                    continue
                seen.add(code)
                entries.append(StockEntry(
                    code=code,
                    name_cn=_cell_str(getattr(row, "name", None)),
                    name_en=_cell_str(getattr(row, "english_name", None)),
                ))
        return entries

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

            code = _normalize_code(cfg.trading_code)  # .env 小寫/全 upper 輸入都映返正規形式
            rows = self._fetch_history(ctx, code, cfg.kline_type)
            cur_state = self._state
            n = cur_state.aggregator.seed_from_history(rows)
            anchor = None
            if rows:
                last_dt = parse_market_time(rows[-1][0])
                if last_dt is not None:
                    anchor = last_dt.date()
            # seed 完成先 swap state（anchor 一齊入，無 None window）
            self._state = _State(cur_state.aggregator, code, cfg.kline_type, anchor)
            if not self._closed:
                self.history_ready.emit(self._state.aggregator.bars())

            ctx.set_handler(_QuoteHandler(self))
            self.status.emit(f"訂閱 {code} QUOTE 中…")
            ret, sub_info = ctx.subscribe([code], [SubType.QUOTE])
            if ret != RET_OK:
                raise RuntimeError(f"subscribe 失敗: {sub_info}")  # 成功時第二返回值係 None（實測）
            self._ensure_store().add(code)   # 初始訂閱入帳本
            self._schedule_reconcile()       # 開機對帳：query_subscription 清理上次殘留訂閱
            self.status.emit(f"訂閱成功 · 歷史 {n} 根 · 等待實時報價")

            # 股票目錄 fetch（autocomplete 輔助功能）：獨立 try/except——失敗唔影響主流程、唔 close ctx
            try:
                entries = self._fetch_catalog(ctx)
                if entries and not self._closed:
                    register_code_aliases(entries, _CODE_ALIASES)
                    self.catalog_ready.emit(tuple(entries))
                    self.status.emit(f"股票目錄已載入 · {len(entries)} 隻")
            except Exception:  # noqa: BLE001 — catalog failure must not break startup
                logger.exception("stock catalog fetch failed")
        except Exception as exc:  # noqa: BLE001 — setup 任何失敗 → 回報 + 確保 ctx close
            logger.exception("FutuEngine setup failed")
            self.error.emit(str(exc))
            self._close_ctx()
