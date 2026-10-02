"""Futu 行情引擎：OpenD 連線 + 歷史 K 線 seed + QUOTE 訂閱實時回調聚合。

Threading model（見 README Architecture）:
- start() spawn daemon setup thread 跑 OpenQuoteContext / request_history_kline 等阻塞操作；
- switch() 每次 spawn 一個 daemon worker thread 做運行時改標的/週期（_workers list，stop() join 晒）；
- futu-api 每個 context 只有一條 callback thread → on_recv_rsp 必須快：parse + aggregate + emit，唔做重活；
- 跨線程傳 immutable tuple-of-tuples snapshot（pyqtSignal queued），GUI 負責 render。

運行時切換一致性：engine 只持一個 immutable `_State(code, anchor_date, periods, aggregators)`
reference——**單一 QUOTE 訂閱 → N 個 aggregator（每週期一個）**，多 pane 同時看同一標的嘅
多個週期。handler 每 batch load 一次 state + per-row `row.code != state.code → skip`
（unsubscribe 唔係硬停，in-flight push 會喺 swap 後先至到）+ emit 前確認 `state is eng._state`；
tick fan-out 入所有 aggregator，各週期獨立 emit `(period, bars)`。

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
import time
from dataclasses import dataclass, field
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
    TickerDirect,
    TickerHandlerBase,
)

from config import kline_period_minutes
from .candle_aggregator import CandleAggregator
from .connection_test import CONNECT_RETRY_INTERVAL_S, tcp_reachable
from .stock_catalog import StockEntry, register_code_aliases
from .subscription_store import SubscriptionStore, default_db_path
from .timeutil import history_window, parse_market_time, resolve_tick_datetime

logger = logging.getLogger(__name__)

# 定時 reconcile 間隔（秒）：對「已不活躍且訂閱滿 MIN_SUBSCRIBE_SECONDS」的洩漏訂閱重試 unsubscribe。
_RECONCILE_INTERVAL = 30.0

# OpenD 定時 ping 間隔（秒）：get_global_state() RTT → connection_state signal（右下角連線狀態 + 延遲）。
_PING_INTERVAL = 2.0

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


def _cell_int(value) -> int | None:
    """DataFrame cell → int（lot_size 等整數欄位；None/NaN/非數字 → None）。"""
    if value is None:
        return None
    try:
        if value != value:  # NaN guard（pandas 空欄位）
            return None
    except TypeError:
        pass
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None

# time-only tick 補 fallback date 用嘅市場時區（只影響日曆日期推斷，永遠唔轉換數據 timestamp——時區鐵律不變）
_MARKET_TZ: dict[str, str] = {
    "HK": "Asia/Hong_Kong",
    "US": "America/New_York",
}


@dataclass(frozen=True)
class _State:
    """當前行情狀態（immutable reference；切換時一次過 swap，handler 靠 identity check）。

    **單一 QUOTE 訂閱 → N 個 aggregator**：`periods` = 活躍週期集合、`aggregators` =
    {週期名 → CandleAggregator}。多 pane 同時看同一標的嘅多個週期——tick fan-out 入所有
    aggregator，各週期獨立 emit `(period, bars)`。
    """

    code: str
    anchor_date: date | None
    periods: frozenset[str]
    aggregators: dict[str, CandleAggregator]
    smt_code: str | None = None   # SMT Divergence 配對副標的（None = 功能關閉）
    smt_aggregators: dict[str, CandleAggregator] = field(default_factory=dict)

    def bar_count(self) -> int:
        return sum(len(a.bars()) for a in self.aggregators.values()) + \
            sum(len(a.bars()) for a in self.smt_aggregators.values())


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


def _logged_in_flag(value) -> bool:
    """get_global_state() 嘅 qot_logined / trd_logined 判定。

    **proto 實測係 bool**（`GetGlobalState.proto`: `required bool qotLogined`）→ Python True/False；
    官方 docstring 話 str '1'/'0'——兩種形態都兜底：`str(value).strip().lower() in ("1","true")`。
    唔好靠 truthiness（字串 '0' 係 truthy → 會誤判已登入）。
    """
    return str(value).strip().lower() in ("1", "true")


def _subtype_enum(name: str):
    """訂閱帳本 / query_subscription 嘅 subtype 名（"QUOTE"/"TICKER"…）→ SubType 常數。

    SDK 實測 SubType 常數係純字串（SubType.QUOTE == "QUOTE"），但經 getattr 映射兜底
    未來 SDK 改 enum；未知名 → QUOTE fallback（reconcile 清理用，唔會誤清其他 subtype）。
    """
    st = getattr(SubType, str(name).upper(), None)
    return st if isinstance(st, str) else SubType.QUOTE


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
        changed: set[str] = set()
        smt_changed: set[str] = set()
        for row in data.itertuples(index=False):
            # code routing：primary → aggregators；SMT 配對副標的 → smt_aggregators；
            # 其他 code（切換後舊標的嘅 in-flight push，unsubscribe 唔係硬停）一律 skip
            row_code = getattr(row, "code", None)
            if row_code == state.code:
                aggs, target = state.aggregators, changed
            elif state.smt_code is not None and row_code == state.smt_code:
                aggs, target = state.smt_aggregators, smt_changed
            else:
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
            for period, agg in aggs.items():  # fan-out 入該 code 嘅所有週期 aggregator
                if agg.apply_quote(dt, price, cum_vol):
                    target.add(period)
        if eng.cfg.debug and len(data):
            logger.debug("tick batch rows=%d", len(data))
        if state is eng._state:  # batch 中途 state 被 swap → 呢批 discard
            for period in sorted(changed):
                eng.bars_changed.emit(period, state.aggregators[period].bars())
            for period in sorted(smt_changed):
                eng.smt_bars_changed.emit(period, state.smt_aggregators[period].bars())
        return ret_code, data


class _TickerHandler(TickerHandlerBase):
    """TICKER push 回調（Commit 31）：parse 逐筆成交 → emit tick_data snapshot。

    SDK `TickerHandlerBase.on_recv_rsp` 返回 `(ret, DataFrame)`，欄位 = code/name/time/price/volume/
    turnover/ticker_direction/sequence/type/push_data_type——**ticker_direction 同 type 已係字串**
    （SDK 內部經 TickerDirect.to_string2 / TickerType.to_string2 映射：'BUY'/'SELL'/'NEUTRAL'、
    'AUTO_MATCH'/'LATE'/…；無值 → 'N/A'）。`time` = 完整成交時間字串（唔似 QUOTE 嘅 time-only）。

    只保留當前主標的（state.code）——SMT 副標的 / 切換後舊標的 in-flight push 一律 skip
    （同 _QuoteHandler code routing 一致；unsubscribe 唔係硬停）。
    """

    def __init__(self, engine: "FutuEngine") -> None:
        super().__init__()
        self._engine = engine

    def on_recv_rsp(self, rsp_pb):  # noqa: N802 (SDK naming)
        ret_code, data = super().on_recv_rsp(rsp_pb)
        eng = self._engine
        if ret_code != RET_OK or data is None:
            if not eng._closed:
                eng.error.emit(f"TICKER push 異常: ret={ret_code}")
            return ret_code, data
        state = eng._state  # 每 batch load 一次（GIL-atomic reference）
        if state is None:
            return ret_code, data
        rows: list[tuple[str, float, float, str, str]] = []
        for row in data.itertuples(index=False):
            if getattr(row, "code", None) != state.code:   # 只主標的（副標的 / 舊 push → skip）
                continue
            try:
                price = float(getattr(row, "price", 0.0))
                volume = float(getattr(row, "volume", 0.0))
            except (TypeError, ValueError):
                continue
            if not price > 0:   # NaN guard：nan > 0 係 False → skip
                continue
            rows.append((
                str(getattr(row, "time", "") or ""),                    # 成交時間（完整字串）
                price,                                                 # 成交價
                volume,                                                # 成交量
                str(getattr(row, "ticker_direction", "") or ""),       # BUY/SELL/NEUTRAL/N/A
                str(getattr(row, "type", "") or ""),                   # AUTO_MATCH/LATE/…/N/A
            ))
        if rows and state is eng._state:   # batch 中途 state 被 swap → 呢批 discard
            eng.tick_data.emit(tuple(rows))
        return ret_code, data


class FutuEngine(QObject):
    """futu 行情 pipeline 嘅 QObject 包裝。

    Signals（全部喺非 GUI thread emit；Qt auto-queue 去 GUI thread）:
    - history_ready(str, tuple[Bar]): seed / 切換完成後嘅完整 snapshot，(period, bars)
    - bars_changed(str, tuple[Bar]): tick 聚合後嘅新 snapshot，(period, bars)
    - smt_history_ready / smt_bars_changed: SMT Divergence 配對副標的嘅 seed / tick snapshot（同 (period, bars)）
    - status(str) / error(str)
    - connection_state(bool, float): (connected, latency_ms) 定時 ping get_global_state RTT（右下角狀態）
    - tick_data(tuple[(str,float,float,str,str)]): 主標的逐筆成交 batch——(time, price, volume, direction, type)
      （Commit 31：報價頁左側全高逐筆面板；direction = BUY/SELL/NEUTRAL → 主買/主賣背景色）

    運行時切換：switch(code=None, periods=None, smt=None) spawn worker thread——code 變先 unsubscribe/subscribe、
    periods 變先 fetch+seed 差集；smt=True/False 啟用/停用 SMT 配對副標的（雙訂閱）。全部驗證通過先 swap
    `_State`（單一 QUOTE 訂閱 → N aggregator；SMT 活躍時 +1 訂閱 → M aggregator）。
    """

    history_ready = Signal(str, tuple)   # (period, bars)：多 pane 各週期獨立 seed snapshot
    bars_changed = Signal(str, tuple)    # (period, bars)：tick fan-out 後各週期新 snapshot
    smt_history_ready = Signal(str, tuple)   # (period, bars)：SMT 配對副標的 seed snapshot
    smt_bars_changed = Signal(str, tuple)    # (period, bars)：SMT 配對副標的 tick 新 snapshot
    status = Signal(str)
    error = Signal(str)
    catalog_ready = Signal(tuple)   # tuple[StockEntry]：HK+US 股票目錄（fuzzy autocomplete 用）
    connection_state = Signal(bool, float)   # (connected, latency_ms)：定時 ping RTT（右下角連線狀態 + 延遲）
    tick_data = Signal(tuple)   # tuple[(time_str, price, volume, direction, type)]：主標的逐筆成交 batch（Commit 31）

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
        self._ping_thread: threading.Thread | None = None      # OpenD 定時 ping thread（連線狀態 + RTT）
        self._ping_stop = threading.Event()                    # stop()/supersede → 喚醒 ping loop 退出
        self._ping_gen = 0                                     # generation counter：重啟後舊 thread 偵測 mismatch 自然退出

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
    def aggregators(self) -> dict[str, CandleAggregator]:
        """{週期名 → aggregator}；start() 未呼叫 → RuntimeError。"""
        if self._state is None:
            raise RuntimeError("FutuEngine.start() 未呼叫")
        return self._state.aggregators

    def tick_date(self) -> date:
        """time-only tick 要補嘅日期（讀當前 state；handler 用 _fallback_date(captured state)）。"""
        if self._state is None:
            return _fallback_date(None, "HK")
        return _fallback_date(self._state.anchor_date, self._state.code)

    def start(self, cfg, db_path: str | Path | None = None, periods=None,
              code: str | None = None, smt: bool = False) -> None:
        """啟動連線 + 歷史 fetch + 訂閱（背景 daemon thread，立即返回）。

        db_path：SQLite 訂閱帳本路徑；None → default_db_path()。
        periods：初始活躍週期集合（多 pane）；None → 只 cfg.kline_type。setup thread 喺 subscribe
        前逐個 fetch+seed——開機一次到位，GUI 唔使事後重試 switch（setup thread alive 期間會被 reject）。
        code：初始標的編號；None → cfg.trading_code（.env）。GUI UI-state 記憶還原上次標的時傳入。
        smt：SMT Divergence 開機即啟用（需 cfg.smt_code）→ setup thread 一併 fetch+seed+訂閱副標的。
        """
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return  # 已經 starting/started
            self._closed = False
            self._cfg = cfg
            self._db_path = db_path
            code = _normalize_code(code if code is not None else cfg.trading_code)
            initial = frozenset(p.strip().upper() for p in periods) if periods else frozenset({cfg.kline_type})
            aggregators = {p: CandleAggregator(kline_period_minutes(p) or cfg.period_minutes)
                           for p in sorted(initial)}
            smt_code = _normalize_code(cfg.smt_code) if (smt and cfg.smt_code) else None
            smt_aggregators = ({p: CandleAggregator(kline_period_minutes(p) or cfg.period_minutes)
                                for p in sorted(initial)} if smt_code else {})
            self._state = _State(code, None, initial, aggregators, smt_code, smt_aggregators)
            thread = threading.Thread(target=self._setup, name="futu-setup", daemon=True)
            self._thread = thread
        thread.start()

    def stop(self) -> None:
        """Idempotent 關閉：close ctx（停 callback thread）、join setup + switch worker + ping threads。"""
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
            ping_thread = self._ping_thread
            self._ping_thread = None
        if timer is not None:
            timer.cancel()  # 阻止未觸發嘅 reconcile；已運行中嘅會因 _closed 快速返回
        self._ping_stop.set()   # 喚醒 ping loop（若喺 wait）→ 下輪偵測退出
        self._close_ctx()       # ctx=None → ping loop 偵測到即退出
        for t in (thread, *workers):
            if t is not None and t.is_alive():
                t.join(timeout=10)
        if ping_thread is not None and ping_thread.is_alive():
            ping_thread.join(timeout=5)

    def switch(self, code: str | None = None, periods=None, smt: bool | None = None) -> None:
        """運行時改標的 / 週期集合 / SMT 配對開關（worker thread，立即返回）。

        `periods` = 活躍週期名 list（多 pane 各週期）；None → 沿用當前。code 變先 unsubscribe/subscribe、
        periods 變先 fetch+seed 差集。`smt`：True=啟用 SMT Divergence（需 cfg.smt_code）、False=停用、
        None=沿用當前。校驗失敗 → error signal；setup/switch 進行中 → status 提示並 reject。
        """
        with self._lock:
            if self._closed or self._ctx is None:
                return
            cur = self._state
        new_code = _normalize_code(code) if code else (cur.code if cur else None)
        if periods is not None:
            new_periods = frozenset(p.strip().upper() for p in periods)
        else:
            new_periods = cur.periods if cur else frozenset()
        if new_code is None or not new_periods:
            return  # start() 未行過 / 無當前狀態 → 冇嘢可以切
        if code and not _CODE_RE.match(new_code):
            self.error.emit(f"股票編號格式錯誤：{code!r}（例：HK.00700 / US.AAPL）")
            return
        bad = [p for p in new_periods if p not in _KLTYPE_MAP]
        if bad:
            valid = ", ".join(_KLTYPE_MAP)
            self.error.emit(f"未知 K 線週期 {bad}，可選：{valid}")
            return
        # SMT 啟用校驗：.env 未設 SMT_CODE / 配對同主標的一樣 → reject（唔會打到 OpenD）
        if smt is True:
            if not self._cfg.smt_code:
                self.error.emit("SMT Divergence 需要 .env 設定 SMT_CODE（配對副標的）")
                return
            if _normalize_code(self._cfg.smt_code) == new_code:
                self.error.emit(f"SMT 配對唔可以同主標的一樣：{new_code}")
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
            thread = threading.Thread(target=self._reconfigure, args=(new_code, new_periods, smt),
                                      name="futu-switch", daemon=True)
            self._workers.append(thread)
        thread.start()

    def _rollback(self, code: str, msg: str, smt_code: str | None = None) -> None:
        """切換失敗 → resubscribe 舊標的（state 未 swap，圖表保持 live）；SMT 配對活躍時一併 resubscribe。"""
        ctx = self._ctx
        if ctx is not None and not self._closed:
            codes = [code] + ([smt_code] if smt_code else [])
            try:
                ret, info = ctx.subscribe(codes, [SubType.QUOTE])
                if ret != RET_OK:
                    logger.error("rollback resubscribe %s 失敗: %s", code, info)
                else:
                    for c in codes:
                        self._ensure_store().add(c)  # re-subscribe 成功 → 帳本重新計時
            except Exception:  # noqa: BLE001 — rollback 唔好 propagate
                logger.exception("rollback resubscribe exception")
            # TICKER（Commit 31）：主標的一併 resubscribe（非致命——失敗只係逐筆面板暫停，reconcile 兜底）
            try:
                ret_tk, info_tk = ctx.subscribe([code], [SubType.TICKER])
                if ret_tk == RET_OK:
                    self._ensure_store().add(code, "TICKER")
                else:
                    logger.warning("rollback TICKER resubscribe %s 失敗（非致命）: %s", code, info_tk)
            except Exception:  # noqa: BLE001 — 同上
                logger.exception("rollback TICKER resubscribe exception")
        if not self._closed:
            self.error.emit(f"切換失敗：{msg}")

    def _reconfigure(self, new_code: str, new_periods: frozenset[str], smt_on: bool | None = None) -> None:
        """Worker thread：（code 變先）unsubscribe 舊 → fetch+seed 各週期 → （code 變先）subscribe 新 → swap。

        **單一 QUOTE 訂閱 → N aggregator**：只 subscribe `new_code` 一次；tick fan-out 入所有週期
        aggregator。periods 差集處理——同 code 下未變嘅週期直接沿用舊 aggregator（保留 live bars，
        唔使重新 fetch）；code 變時全部重建（舊標的 bars 無意義）。

        SMT 配對：`smt_on` True=啟用 / False=停用 / None=沿用當前。啟用 → 副標的逐週期
        fetch+seed（同 primary 窗口）+ subscribe；停用 → unsubscribe 舊副標的。任何失敗 →
        rollback resubscribe 切換前狀態（state 未 swap，訂閱集合保持一致）。
        """
        old_state = self._state
        try:
            if not self._closed and old_state is not None:
                self.status.emit(f"切換中 {new_code} · {len(new_periods)} 週期…")
            ctx = self._ctx
            if ctx is None or old_state is None:
                return
            code_changed = old_state.code != new_code
            # SMT 目標：smt_on=None → 沿用當前；True → cfg.smt_code（switch() 已校驗）；False → 關閉
            if smt_on is None:
                smt_target = old_state.smt_code
            elif smt_on and self._cfg.smt_code:
                smt_target = _normalize_code(self._cfg.smt_code)
            else:
                smt_target = None
            # 1) code 變 → unsubscribe 舊主標的；SMT 停用 → unsubscribe 舊副標的（唔係硬停——in-flight push 由 handler code filter 兜底）
            if code_changed:
                try:
                    ret, info = ctx.unsubscribe([old_state.code], [SubType.QUOTE])
                    if ret != RET_OK:
                        logger.warning("unsubscribe %s 失敗: %s", old_state.code, info)
                        # 「訂閱未滿 1 分鐘」→ OpenD 拒收；帳本保留呢筆（pending），reconcile 稍後重試
                    else:
                        self._ensure_store().remove(old_state.code)
                except Exception:  # noqa: BLE001 — unsubscribe 失敗唔阻切換（code filter 兜底）
                    logger.exception("unsubscribe exception")
                # TICKER（Commit 31）：舊主標的一併 unsub（非致命——失敗保留 pending，reconcile 稍後重試）
                try:
                    ret_tk, info_tk = ctx.unsubscribe([old_state.code], [SubType.TICKER])
                    if ret_tk == RET_OK:
                        self._ensure_store().remove(old_state.code, "TICKER")
                    else:
                        logger.warning("unsubscribe TICKER %s 失敗（pending）: %s", old_state.code, info_tk)
                except Exception:  # noqa: BLE001 — 同上
                    logger.exception("unsubscribe TICKER exception")
            if old_state.smt_code is not None and smt_target is None:
                try:
                    ret, info = ctx.unsubscribe([old_state.smt_code], [SubType.QUOTE])
                    if ret != RET_OK:
                        logger.warning("unsubscribe SMT %s 失敗: %s", old_state.smt_code, info)
                        # 「訂閱未滿 1 分鐘」→ OpenD 拒收；帳本保留呢筆（pending），reconcile 稍後重試
                    else:
                        self._ensure_store().remove(old_state.smt_code)
                except Exception:  # noqa: BLE001 — unsubscribe 失敗唔阻切換（code filter 兜底）
                    logger.exception("SMT unsubscribe exception")
            # 2) build + seed 各週期 aggregator（同 code 未變嘅週期沿用舊 aggregator）
            anchor = old_state.anchor_date if not code_changed else None
            aggregators: dict[str, CandleAggregator] = {}
            total = 0
            for p in sorted(new_periods):
                period_min = kline_period_minutes(p) or self._cfg.period_minutes
                if not code_changed and p in old_state.aggregators:
                    agg = old_state.aggregators[p]   # 保留 live bars，唔重新 fetch
                    aggregators[p] = agg
                    total += len(agg.bars())
                    continue
                rows = self._fetch_history(ctx, new_code, p)   # 明確窗口 + 分頁；失敗 raise → rollback
                agg = CandleAggregator(period_min)
                n = agg.seed_from_history(rows)
                if n == 0:
                    self._rollback(old_state.code, f"{new_code} {p} 冇歷史數據", old_state.smt_code)
                    return
                aggregators[p] = agg
                total += n
                last_dt = parse_market_time(rows[-1][0])
                if last_dt is not None and (anchor is None or last_dt.date() > anchor):
                    anchor = last_dt.date()
            # 2b) SMT 配對副標的 aggregator（同 primary 週期集合；同 code 未變嘅週期沿用舊 aggregator）
            smt_aggregators: dict[str, CandleAggregator] = {}
            if smt_target is not None:
                for p in sorted(new_periods):
                    period_min = kline_period_minutes(p) or self._cfg.period_minutes
                    if not code_changed and p in old_state.smt_aggregators:
                        agg = old_state.smt_aggregators[p]   # 保留 live bars，唔重新 fetch
                        smt_aggregators[p] = agg
                        total += len(agg.bars())
                        continue
                    rows = self._fetch_history(ctx, smt_target, p)
                    agg = CandleAggregator(period_min)
                    n = agg.seed_from_history(rows)
                    if n == 0:
                        self._rollback(old_state.code, f"{smt_target} {p} 冇歷史數據", old_state.smt_code)
                        return
                    smt_aggregators[p] = agg
                    total += n
                    last_dt = parse_market_time(rows[-1][0])
                    if last_dt is not None and (anchor is None or last_dt.date() > anchor):
                        anchor = last_dt.date()
            # 3) code 變 → subscribe 新主標的；SMT 新啟用/換配對 → subscribe 副標的（全部驗證通過先 swap）
            if code_changed:
                ret, sub_info = ctx.subscribe([new_code], [SubType.QUOTE])
                if ret != RET_OK:
                    self._rollback(old_state.code, f"subscribe {new_code} 失敗: {sub_info}", old_state.smt_code)
                    return
                self._ensure_store().add(new_code)   # 新訂閱入帳本（re-subscribe 同 code → 重新計時）
                # TICKER（Commit 31）：新主標的逐筆訂閱（非致命——失敗只係逐筆面板空，K 線照常）
                try:
                    ret_tk, info_tk = ctx.subscribe([new_code], [SubType.TICKER])
                    if ret_tk == RET_OK:
                        self._ensure_store().add(new_code, "TICKER")
                    else:
                        logger.warning("subscribe TICKER %s 失敗（非致命）: %s", new_code, info_tk)
                        if not self._closed:   # Commit 32：visible warning——切換後逐筆面板空白原因要見到
                            self.error.emit(f"TICKER 逐筆訂閱失敗（非致命）：{new_code} — 逐筆面板將無數據")
                except Exception:  # noqa: BLE001 — TICKER 失敗唔阻切換
                    logger.exception("subscribe TICKER exception")
            if smt_target is not None and old_state.smt_code != smt_target:
                ret, sub_info = ctx.subscribe([smt_target], [SubType.QUOTE])
                if ret != RET_OK:
                    self._rollback(old_state.code, f"subscribe SMT {smt_target} 失敗: {sub_info}", old_state.smt_code)
                    return
                self._ensure_store().add(smt_target)   # 新訂閱入帳本（re-subscribe 同 code → 重新計時）
            self._schedule_reconcile()               # 排程清理：舊 code 若 unsubscribe 失敗（pending）稍後重試
            # 4) atomic swap + per-period notify
            new_state = _State(new_code, anchor, new_periods, aggregators, smt_target, smt_aggregators)
            self._state = new_state
            if not self._closed:
                for p in sorted(new_periods):
                    self.history_ready.emit(p, aggregators[p].bars())
                    if smt_target is not None:
                        self.smt_history_ready.emit(p, smt_aggregators[p].bars())
                self.status.emit(f"切換成功 · {new_code} · {len(new_periods)} 週期 · {total} 根")
        except Exception as exc:  # noqa: BLE001 — fetch 等任何失敗 → rollback + 回報
            logger.exception("FutuEngine reconfigure failed")
            if old_state is not None and not self._closed:
                self._rollback(old_state.code, str(exc), old_state.smt_code)
        finally:
            self._switching = False

    # ------------------------------------------------------------- 訂閱帳本 reconcile（自動清理洩漏）

    def _start_ping_loop(self) -> None:
        """啟動定時 ping thread（每 _PING_INTERVAL 秒 get_global_state RTT → connection_state signal）。

        Generation counter（_ping_gen）：重啟時舊 thread 偵測 gen mismatch 自然退出——唔會重複 ping / 洩漏。
        _setup() OpenD 連線成功後呼叫；switch() 唔改連線（同一 ctx）→ 唔使重啟。
        """
        with self._lock:
            if self._closed:
                return
            self._ping_gen += 1
            gen = self._ping_gen
            self._ping_stop.clear()
            thread = threading.Thread(target=self._ping_loop, args=(gen,), name="futu-ping", daemon=True)
            self._ping_thread = thread
        thread.start()

    def _ping_once(self, ctx) -> tuple[bool, float]:
        """單次 ping：get_global_state() RTT → (connected, latency_ms)；exception → (False, -1.0)。

        connected = ret OK + data 係 dict + qot_logined 已登入（行情伺服器——連線狀態權威來源）。
        latency_ms 用 perf_counter（高精度 monotonic clock）量 RTT——本地 OpenD 通常 sub-millisecond，
        UI 端 <1ms 顯示 µs、否則 ms。
        """
        try:
            t0 = time.perf_counter()
            ret, data = ctx.get_global_state()
            latency_ms = (time.perf_counter() - t0) * 1000.0
        except Exception:  # noqa: BLE001 — ping exception → 當斷線，唔 propagate 去 GUI shutdown path
            logger.exception("OpenD ping failed")
            return False, -1.0
        connected = ret == RET_OK and isinstance(data, dict) and _logged_in_flag(data.get("qot_logined"))
        return connected, latency_ms

    def _ping_loop(self, gen: int) -> None:
        """定時 ping loop：每輪 get_global_state RTT → connection_state(connected, latency_ms)。

        退出條件：stop()（_ping_stop set / ctx=None）或被新 ping loop supersede（gen mismatch）。
        """
        while not self._ping_stop.is_set():
            if gen != self._ping_gen or self._closed:
                break   # engine 已關閉 / 被取代 → 自然退出
            ctx = self._ctx
            if ctx is None:
                break   # stop()/setup 失敗 close 咗 ctx → 退出（UI 保持初始「未連線」狀態）
            connected, latency_ms = self._ping_once(ctx)
            if not self._closed and gen == self._ping_gen:
                self.connection_state.emit(connected, latency_ms)
            self._ping_stop.wait(_PING_INTERVAL)

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

    def _query_open_subscriptions(self, ctx) -> dict[str, list[str]] | None:
        """query_subscription() → OpenD 端實際訂閱緊嘅 code→[subtypes] 映射；失敗/異常 → None（對帳跳過）。

        Commit 31：由 set[codes] 升級做 per-code subtype 列表——reconcile unsubscribe 要帶正確
        SubType（TICKER 洩漏唔可以淨係 unsub QUOTE）。sub_list key = subtype 名（"QUOTE"/"TICKER"…）。
        """
        try:
            ret, data = ctx.query_subscription(is_all_conn=False)
        except Exception:  # noqa: BLE001 — query 唔好 propagate 去 reconcile worker
            logger.exception("query_subscription exception")
            return None
        if ret != RET_OK or not isinstance(data, dict):
            logger.warning("query_subscription 失敗: %s", data)
            return None
        code_subs: dict[str, list[str]] = {}
        for subtype, sub_list in (data.get("sub_list") or {}).items():
            for c in sub_list or []:
                code_subs.setdefault(c, []).append(str(subtype))
        return code_subs

    def _reconcile_subscriptions(self) -> None:
        """定時清理：對「已不活躍且訂閱滿 MIN_SUBSCRIBE_SECONDS」的洩漏訂閱重試 unsubscribe。

        流程（獨立 daemon thread）：
        1. query_subscription() 攞 OpenD 端實際訂閱 code；失敗 → 跳過呢輪（下輪再試）。
        2. store.due_for_cleanup(active_codes) = 帳本入面「唔喺 active codes（主標的 + SMT 配對）且 age>=閾值」嘅條目。
        3. 逐筆 unsubscribe：成功 → remove；失敗（例如仲未滿 1min）→ 保留，下輪再試。
        4. query 到但帳本冇記錄嘅 code（上次 crash 殘留、唔係當前 state）→ 直接 unsubscribe + 唔入帳本。

        冪等：每輪重讀 store；無 due → no-op。stop() 後 _closed=True → 快速返回。
        """
        with self._lock:
            if self._closed or self._ctx is None:
                return
            ctx = self._ctx
        state = self._state
        active_codes = {state.code} if state else set()   # SMT 配對副標的亦係活躍訂閱（唔好當洩漏清走）
        if state is not None and state.smt_code:
            active_codes.add(state.smt_code)

        open_map = self._query_open_subscriptions(ctx)   # code → [subtypes]（Commit 31）
        if open_map is None:
            return  # query 失敗 → 唔改帳本，下輪再試（避免誤刪）
        open_codes = set(open_map)

        store = self._ensure_store()
        ledger_codes = {c for c, _s, _ts in store.list_active()}  # loop 前 snapshot（residual 判斷用）
        for code, subtype, _ts in store.due_for_cleanup(active_codes):
            try:
                ret, info = ctx.unsubscribe([code], [_subtype_enum(subtype)])   # 帶正確 SubType（TICKER/QUOTE）
            except Exception:  # noqa: BLE001 — 單筆 unsubscribe exception 唔阻其餘清理
                logger.exception("reconcile unsubscribe %s exception", code)
                continue
            if ret == RET_OK:
                store.remove(code, subtype)
                logger.info("reconcile：已清理洩漏訂閱 %s [%s]", code, subtype)
            else:
                logger.warning("reconcile：unsubscribe %s [%s] 仍失敗（稍後重試）: %s", code, subtype, info)

        # 殘留自癒：OpenD 端有、但帳本完全冇記錄（上次 crash 前嘅訂閱）、且唔係當前 state →
        # unsubscribe。用 loop 前 ledger snapshot 排除「已喺帳本」嘅 code——避免同 due-loop 重複 unsub。
        for code in open_codes - active_codes - ledger_codes:
            subtypes = list(dict.fromkeys(_subtype_enum(s) for s in open_map.get(code, []))) or [SubType.QUOTE]
            try:
                ret, info = ctx.unsubscribe([code], subtypes)   # 清晒該 code 全部殘留 subtype
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
        """Fetch HK+US 股票基本資料（code/name/english_name/lot_size/listing_date）→ StockEntry list。

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
                    lot_size=_cell_int(getattr(row, "lot_size", None)),
                    listing_date=_cell_str(getattr(row, "listing_date", None)),
                ))
        return entries

    def _setup(self) -> None:
        cfg = self._cfg
        # Commit 36：TCP pre-check + 自動重試——sync constructor 對死端點會入 while True 無限重試永久阻塞（AGENTS.md #20），
        # 之前 K 線永遠「等待行情數據」零回饋；而家 fast-fail 後每 CONNECT_RETRY_INTERVAL_S 自動重試到 OpenD 起或 stop()
        warned = False
        while not self._closed:
            ok, msg = tcp_reachable(cfg.quote_host, cfg.quote_port)
            if ok:
                break
            if not warned and not self._closed:
                self.error.emit(
                    f"連唔到報價 OpenD {cfg.quote_host}:{cfg.quote_port}（{msg}）——每 {CONNECT_RETRY_INTERVAL_S:.0f}s 自動重試中…")
                warned = True
            time.sleep(CONNECT_RETRY_INTERVAL_S)
        if self._closed:
            return
        try:
            ctx = OpenQuoteContext(cfg.quote_host, cfg.quote_port)   # Commit 35：報價 OpenD 獨立端點
        except Exception as exc:  # noqa: BLE001 — 連線失敗（OpenD 未開等）→ 回報 GUI
            logger.exception("OpenQuoteContext connect failed")
            if not self._closed:
                self.error.emit(f"連唔到報價 OpenD {cfg.quote_host}:{cfg.quote_port}: {exc}")
            return
        with self._lock:
            if self._ctx is not None:  # stop() 已行過 / 重複 start → close 自己嘅連線退出
                ctx.close()
                return
            self._ctx = ctx
        try:
            self.status.emit("OpenD 連線成功")
            self._start_ping_loop()   # 定時 ping：get_global_state RTT → 右下角連線狀態 + 延遲顯示

            cur_state = self._state
            code = cur_state.code   # start() 已正規化（cfg.trading_code 或 GUI UI-state 記憶還原嘅 code）
            anchor = None
            total = 0
            for ktype in sorted(cur_state.periods):   # 多 pane：逐週期 fetch+seed（單一 QUOTE 訂閱共用）
                rows = self._fetch_history(ctx, code, ktype)
                agg = cur_state.aggregators[ktype]
                n = agg.seed_from_history(rows)
                total += n
                if rows:
                    last_dt = parse_market_time(rows[-1][0])
                    if last_dt is not None and (anchor is None or last_dt.date() > anchor):
                        anchor = last_dt.date()
            # SMT 配對副標的：逐週期 fetch+seed（同 primary 窗口；失敗 → raise → 回報 + close ctx）
            if cur_state.smt_code is not None:
                for ktype in sorted(cur_state.periods):
                    rows = self._fetch_history(ctx, cur_state.smt_code, ktype)
                    agg = cur_state.smt_aggregators[ktype]
                    n = agg.seed_from_history(rows)
                    total += n
                    if rows:
                        last_dt = parse_market_time(rows[-1][0])
                        if last_dt is not None and (anchor is None or last_dt.date() > anchor):
                            anchor = last_dt.date()
            # seed 完成先 swap state（anchor 一齊入，無 None window）；per-period emit
            self._state = _State(code, anchor, cur_state.periods, dict(cur_state.aggregators),
                                 cur_state.smt_code, dict(cur_state.smt_aggregators))
            if not self._closed:
                for p in sorted(self._state.periods):
                    self.history_ready.emit(p, self._state.aggregators[p].bars())
                    if self._state.smt_code is not None:
                        self.smt_history_ready.emit(p, self._state.smt_aggregators[p].bars())

            ctx.set_handler(_QuoteHandler(self))
            ctx.set_handler(_TickerHandler(self))   # Commit 31：TICKER push handler（獨立 proto_id slot，同 QUOTE 共存）
            codes = [code] + ([cur_state.smt_code] if cur_state.smt_code else [])   # SMT 配對一併訂閱
            self.status.emit(f"訂閱 {code} QUOTE 中…")
            ret, sub_info = ctx.subscribe(codes, [SubType.QUOTE])
            if ret != RET_OK:
                raise RuntimeError(f"subscribe 失敗: {sub_info}")  # 成功時第二返回值係 None（實測）
            for c in codes:
                self._ensure_store().add(c)   # 初始訂閱入帳本
            # TICKER 訂閱（Commit 31）：只主標的；失敗非致命——逐筆面板空 + warning，唔影響 K 線主流程
            try:
                ret_tk, info_tk = ctx.subscribe([code], [SubType.TICKER])
                if ret_tk == RET_OK:
                    self._ensure_store().add(code, "TICKER")   # 入帳本（PK=(code, subtype)，同 QUOTE 獨立行）
                else:
                    logger.warning("TICKER subscribe %s 失敗（非致命）: %s", code, info_tk)
                    if not self._closed:   # Commit 32：visible warning——逐筆面板空白原因要喺 status bar ⚠ 見到
                        self.error.emit(f"TICKER 逐筆訂閱失敗（非致命）：{code} — 逐筆面板將無數據")
            except Exception:  # noqa: BLE001 — TICKER 失敗唔阻開機
                logger.exception("TICKER subscribe exception")
            self._schedule_reconcile()       # 開機對帳：query_subscription 清理上次殘留訂閱
            self.status.emit(f"訂閱成功 · {len(cur_state.periods)} 週期 · 歷史 {total} 根 · 等待實時報價")

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
