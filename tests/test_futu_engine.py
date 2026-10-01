"""futu_engine 單測：mock OpenQuoteContext + 真 pandas DataFrame（零真實連線）。

覆蓋：_fetch_history 分頁/tail/NaN skip、on_recv_rsp tick 聚合（含 code filter + SMT 雙標的 routing）、
tick_date / _fallback_date（市場時區）、_setup 編排、switch/_reconfigure 運行時切換
+ rollback、SMT Divergence 配對訂閱（enable/disable/threaded）、start/stop lifecycle。
"""
from __future__ import annotations

import dataclasses
import os
import threading
import time as _time
from datetime import date, datetime, timedelta

import pandas as pd
import pytest
from futu import Market, RET_OK, SubType, StockQuoteHandlerBase

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")   # 必須喺 PySide6 import 前設（同其他 Qt 測試檔一致）

from PySide6.QtWidgets import QApplication  # noqa: E402

import engine.futu_engine as fe
from config import Config, kline_period_minutes
from engine.candle_aggregator import CandleAggregator
from engine.futu_engine import (FutuEngine, _KLTYPE_MAP, _PAGE_SIZE, _QuoteHandler,
                                _State, _fallback_date, _logged_in_flag, _normalize_code)
from engine.stock_catalog import StockEntry

# cross-thread signal（ping thread → test thread）係 queued 到 test thread event loop——
# 需要一個 app instance 先至 processEvents() 有得 pump（同其他 Qt 測試檔共用同一個）。
_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------- fixtures / fakes

def make_cfg(**overrides) -> Config:
    base = dict(trading_code="HK.HSImain", kline_type="K_1M", history_count=300)
    base.update(overrides)
    return Config(**base)


@pytest.fixture(autouse=True)
def _isolate_subscription_db(tmp_path, monkeypatch):
    """每個測試用獨立臨時 SQLite 帳本：避免污染專案根目錄 subscriptions.db + 跨測試隔離。

    engine._ensure_store() 喺 db_path=None（直接呼叫 _setup/_reconfigure，唔經 start()）時
    fallback 去 fe.default_db_path()——呢度 patch 返 tmp_path，令所有 store 寫入都落臨時檔。
    """
    monkeypatch.setattr(fe, "default_db_path", lambda: tmp_path / "subscriptions.db")


_CREATED_ENGINES: list[FutuEngine] = []


@pytest.fixture(autouse=True)
def _stop_engines():
    """Teardown：stop 晒 make_engine 建立嘅 engine（join ping/setup/switch threads，防 daemon 洩漏）。

    connection_state 功能後 _setup() 會 spawn 定時 ping thread——同步跑 _setup 嘅測試唔會自己
    stop() → 呢個 fixture 喺測試結束統一清理。已自行 stop() 過嘅測試 → idempotent no-op。
    """
    yield
    for eng in list(_CREATED_ENGINES):
        try:
            eng.stop()
        finally:
            _CREATED_ENGINES.remove(eng)


class FakeCtx:
    """Mock OpenQuoteContext：scripted request_history_kline 回應 + lifecycle 記錄。"""

    def __init__(self, pages, sub_ret=RET_OK, sub_info=None, basicinfo=None, global_state=None):
        self._pages = list(pages)
        self.kline_calls = []
        self.handler = None
        self.subscribed = None
        self.unsubscribed = None
        self.closed = False
        self.subscribe_event = threading.Event()
        self._sub_ret = sub_ret
        self._sub_info = sub_info
        # market → (ret, df) | Exception；未 script 嘅市場 default 空 DataFrame（catalog fetch 零 entries）
        self._basicinfo = basicinfo or {}
        self.basicinfo_calls = []
        # get_global_state() scripted 回應（ping loop 用）；default = 行情伺服器已登入
        # （proto `required bool qotLogined` → Python True——真實形態，見 futu GetGlobalState.proto）
        self._global_state = global_state if global_state is not None else (RET_OK, {"qot_logined": True})
        self.global_state_calls = []

    def get_global_state(self):
        self.global_state_calls.append(None)
        return self._global_state

    def get_stock_basicinfo(self, market):
        self.basicinfo_calls.append(market)
        resp = self._basicinfo.get(market)
        if isinstance(resp, Exception):
            raise resp
        return resp if resp is not None else (RET_OK, pd.DataFrame())

    def request_history_kline(self, code, ktype=None, autype=None, start=None, end=None,
                              max_count=None, page_req_key=None):
        self.kline_calls.append(dict(code=code, ktype=ktype, start=start, end=end,
                                     max_count=max_count, page_req_key=page_req_key))
        return self._pages.pop(0)

    def set_handler(self, handler):
        self.handler = handler

    def subscribe(self, codes, sub_types):
        self.subscribed = (list(codes), list(sub_types))
        self.subscribe_event.set()
        return self._sub_ret, self._sub_info

    def unsubscribe(self, codes, sub_types):
        self.unsubscribed = (list(codes), list(sub_types))
        return RET_OK, None

    def close(self):
        self.closed = True


class GatedCtx(FakeCtx):
    """subscribe 前 gate 住 → worker thread 保持 alive（測 switch guard / lifecycle）。"""

    def __init__(self, pages, **kw):
        super().__init__(pages, **kw)
        self.gate = threading.Event()
        self.gate_waited = False

    def subscribe(self, codes, sub_types):
        if not self.gate_waited:
            self.gate_waited = True
            self.gate.wait(timeout=10)
        return super().subscribe(codes, sub_types)


def kline_df(rows) -> pd.DataFrame:
    """rows: (time_key, open, high, low, close, volume)。

    欄位順序故意用 futu 實際嘅 open/close/high/low（唔係 OHLC），
    驗證 engine 按欄位名提取而唔係靠位置。
    """
    return pd.DataFrame(
        [dict(time_key=t, open=o, close=c, high=h, low=l, volume=v) for t, o, h, l, c, v in rows]
    )


def quote_df(rows, code="HK.HSImain") -> pd.DataFrame:
    """rows: (data_time, last_price, volume) → QUOTE push DataFrame。"""
    return pd.DataFrame(
        [dict(code=code, data_time=dt, last_price=p, volume=v) for dt, p, v in rows]
    )


def basic_df(rows) -> pd.DataFrame:
    """rows: (code, name, english_name) → get_stock_basicinfo DataFrame（按欄位名提取驗證）。"""
    return pd.DataFrame([dict(code=c, name=n, english_name=e) for c, n, e in rows])


def make_engine(**cfg_overrides) -> FutuEngine:
    """Whitebox：直接注入 cfg + _State，唔行 start()（避免真實連線/線程）。

    新多 pane API：_State(code, anchor_date, periods, aggregators)——單一週期 {kline_type}。
    """
    eng = FutuEngine()
    cfg = make_cfg(**cfg_overrides)
    eng._cfg = cfg
    ktype = cfg.kline_type
    agg = CandleAggregator(kline_period_minutes(ktype) or cfg.period_minutes)
    # 跟 production start() 一致：state.code 永遠係正規化後形式（_setup/_reconfigure 信任輸入、唔再 normalize）
    eng._state = _State(_normalize_code(cfg.trading_code), None, frozenset({ktype}), {ktype: agg})
    _CREATED_ENGINES.append(eng)   # autouse fixture teardown → stop()（清理 ping thread）
    return eng


def set_anchor(eng: FutuEngine, d: date | None) -> FutuEngine:
    """替換 state 嘅 anchor_date（frozen dataclass → replace 出新 reference）。"""
    s = eng.state
    eng._state = dataclasses.replace(s, anchor_date=d)
    return eng


def wait_until(predicate, timeout: float = 5.0) -> bool:
    deadline = _time.monotonic() + timeout
    while _time.monotonic() < deadline:
        if predicate():
            return True
        _time.sleep(0.01)
    return predicate()


def wait_until_pump(predicate, timeout: float = 5.0) -> bool:
    """wait_until + processEvents：cross-thread signal（ping thread emit）→ queued 到 test
    thread event loop，必須 pump events 先至 deliver 到 plain callable receiver。"""
    deadline = _time.monotonic() + timeout
    while _time.monotonic() < deadline:
        if predicate():
            return True
        _app.processEvents()
        _time.sleep(0.01)
    return predicate()


def _patch_now(monkeypatch, hkt_wall: datetime) -> None:
    """Patch `fe.datetime.now(tz)` = 固定 instant（HKT wall clock）轉去傳入 tz。

    模擬真實 `datetime.now(tz)` 語義：同一 instant、不同時區嘅 wall clock 唔同——
    呢個先至測得到「美股喺 HKT 機上今日差一日」嗰種行為。
    """
    from zoneinfo import ZoneInfo

    instant = hkt_wall.replace(tzinfo=ZoneInfo("Asia/Hong_Kong"))

    class _DT:
        @staticmethod
        def now(tz=None):
            return instant.astimezone(tz if tz is not None else ZoneInfo("Asia/Hong_Kong"))

    monkeypatch.setattr(fe, "datetime", _DT)


# ---------------------------------------------------------------- _fetch_history

class TestFetchHistory:
    def test_single_page(self):
        eng = make_engine()
        rows_in = [
            ("2026-09-30 09:30", 100.0, 101.0, 99.5, 100.5, 1000),
            ("2026-09-30 09:31", 100.5, 102.0, 100.0, 101.0, 1200),
        ]
        ctx = FakeCtx([(RET_OK, kline_df(rows_in), None)])
        out = eng._fetch_history(ctx, "HK.HSImain", "K_1M")
        assert out == [
            ("2026-09-30 09:30", 100.0, 101.0, 99.5, 100.5, 1000.0),
            ("2026-09-30 09:31", 100.5, 102.0, 100.0, 101.0, 1200.0),
        ]
        call = ctx.kline_calls[0]
        assert call["code"] == "HK.HSImain"
        assert call["ktype"] is _KLTYPE_MAP["K_1M"]
        assert call["max_count"] == _PAGE_SIZE
        # 明確窗口（實測：no-window 會返回一年前舊數據）
        for s in (call["start"], call["end"]):
            datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    def test_pagination_concatenates(self):
        eng = make_engine()
        base = datetime(2026, 9, 30, 9, 30)
        mk = lambda i: ((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                        100.0 + i, 101.0 + i, 99.0 + i, 100.5 + i, 1000.0 * (i + 1))
        page1 = [mk(i) for i in range(3)]
        page2 = [mk(i) for i in range(3, 6)]
        ctx = FakeCtx([
            (RET_OK, kline_df(page1), "k1"),
            (RET_OK, kline_df(page2), None),
        ])
        out = eng._fetch_history(ctx, "HK.HSImain", "K_1M")
        assert [b[0] for b in out] == [r[0] for r in page1 + page2]
        # 第二頁帶住第一頁返回嘅 page_req_key
        assert ctx.kline_calls[1]["page_req_key"] == "k1"

    def test_tail_to_history_count(self):
        eng = make_engine(history_count=2)
        base = datetime(2026, 9, 30, 9, 30)
        rows = [((base + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M"),
                 100.0, 101.0, 99.0, 100.5, 1000.0) for i in range(5)]
        ctx = FakeCtx([(RET_OK, kline_df(rows), None)])
        out = eng._fetch_history(ctx, "HK.HSImain", "K_1M")
        assert len(out) == 2
        assert [b[0] for b in out] == [rows[-2][0], rows[-1][0]]

    def test_error_raises_with_message(self):
        eng = make_engine()
        ctx = FakeCtx([(-1, "connect timeout", None)])
        with pytest.raises(RuntimeError, match="request_history_kline 失敗"):
            eng._fetch_history(ctx, "HK.HSImain", "K_1M")

    def test_nan_rows_skipped(self):
        eng = make_engine()
        rows = [
            ("2026-09-30 09:30", float("nan"), 101.0, 99.5, 100.5, 1000),   # NaN open → skip
            ("2026-09-30 09:31", 100.5, 102.0, 100.0, float("nan"), 1200),  # NaN close → skip
            ("2026-09-30 09:32", 101.0, 102.5, 100.5, 102.0, 1400),         # 有效
        ]
        ctx = FakeCtx([(RET_OK, kline_df(rows), None)])
        out = eng._fetch_history(ctx, "HK.HSImain", "K_1M")
        assert len(out) == 1 and out[0][0] == "2026-09-30 09:32"

    def test_page_guard_raises(self, monkeypatch):
        monkeypatch.setattr(fe, "_MAX_PAGES", 3)
        eng = make_engine()
        one_row = kline_df([("2026-09-30 09:30", 1.0, 2.0, 0.5, 1.5, 10)])
        ctx = FakeCtx([(RET_OK, one_row, "k")] * 10)  # page_key 永遠 truthy
        with pytest.raises(RuntimeError, match="歷史分頁超過"):
            eng._fetch_history(ctx, "HK.HSImain", "K_1M")
        assert len(ctx.kline_calls) == 3


# ---------------------------------------------------------------- _fetch_catalog（autocomplete 目錄）

class TestFetchCatalog:
    def test_extracts_by_column_name_both_markets(self):
        eng = make_engine()
        ctx = FakeCtx([], basicinfo={
            Market.HK: (RET_OK, basic_df([("HK.HSImain", "恒指期货主连", ""),
                                          ("HK.00700", "腾讯控股", "TENCENT")])),
            Market.US: (RET_OK, basic_df([("US.AAPL", "苹果", "Apple Inc.")])),
        })
        entries = eng._fetch_catalog(ctx)
        assert [e.code for e in entries] == ["HK.HSImain", "HK.HHImain", "HK.MHImain", "HK.00700", "US.AAPL"]  # 3 seeds 先入 + dedup skip API 重複
        by_code = {e.code: e for e in entries}
        assert by_code["HK.00700"].name_cn == "腾讯控股"
        assert by_code["US.AAPL"].name_en == "Apple Inc."

    def test_nan_and_none_cells_cleaned(self):
        eng = make_engine()
        df = pd.DataFrame([dict(code="US.X", name=float("nan"), english_name=None)])
        ctx = FakeCtx([], basicinfo={Market.US: (RET_OK, df)})
        entries = eng._fetch_catalog(ctx)
        assert [e.code for e in entries] == ["HK.HSImain", "HK.HHImain", "HK.MHImain", "US.X"]  # seeds + US row
        by_code = {e.code: e for e in entries}
        assert by_code["US.X"].name_cn == "" and by_code["US.X"].name_en == ""

    def test_empty_code_skipped_and_dedup(self):
        eng = make_engine()
        df = pd.DataFrame([dict(code="", name="x", english_name=""),
                           dict(code="US.AAPL", name="苹果", english_name="Apple Inc."),
                           dict(code="US.AAPL", name="dup", english_name="")])
        ctx = FakeCtx([], basicinfo={Market.US: (RET_OK, df)})
        entries = eng._fetch_catalog(ctx)
        assert [e.code for e in entries] == ["HK.HSImain", "HK.HHImain", "HK.MHImain", "US.AAPL"]  # seeds + dedup 後單一 US row

    def test_one_market_exception_other_still_fetched(self):
        eng = make_engine()
        ctx = FakeCtx([], basicinfo={
            Market.HK: RuntimeError("boom"),
            Market.US: (RET_OK, basic_df([("US.MSFT", "", "Microsoft Corp.")])),
        })
        entries = eng._fetch_catalog(ctx)
        assert [e.code for e in entries] == ["HK.HSImain", "HK.HHImain", "HK.MHImain", "US.MSFT"]  # HK exception 唔阻 US + seeds

    def test_ret_not_ok_skipped_without_crash(self):
        eng = make_engine()
        ctx = FakeCtx([], basicinfo={Market.HK: (-1, "no permission"),
                                     Market.US: (RET_OK, pd.DataFrame())})
        entries = eng._fetch_catalog(ctx)
        assert [e.code for e in entries] == ["HK.HSImain", "HK.HHImain", "HK.MHImain"]  # 兩市場全失敗 → 只剩 seeds

    def test_missing_columns_yield_no_entries(self):
        """df 冇 code/name/english_name 欄（schema 差異）→ getattr None → skip，唔炸。"""
        eng = make_engine()
        df = pd.DataFrame([dict(foo=1, bar=2)])
        ctx = FakeCtx([], basicinfo={Market.US: (RET_OK, df)})
        entries = eng._fetch_catalog(ctx)
        assert [e.code for e in entries] == ["HK.HSImain", "HK.HHImain", "HK.MHImain"]  # schema 差異 → 只剩 seeds

    def test_seed_present_when_api_empty_and_deduped(self):
        """live 實測：get_stock_basicinfo 唔返回主力連續合約（HK 3798 rows 冇 HSImain）
        → _SEED_ENTRIES 補返三隻 HK 指數期貨主連；API 若日後返回同 code 只保留 seed 一份。"""
        eng = make_engine()
        ctx = FakeCtx([], basicinfo={Market.HK: (RET_OK, pd.DataFrame()),
                                     Market.US: (RET_OK, pd.DataFrame())})
        entries = eng._fetch_catalog(ctx)
        assert [e.code for e in entries] == ["HK.HSImain", "HK.HHImain", "HK.MHImain"]

        ctx2 = FakeCtx([], basicinfo={
            Market.HK: (RET_OK, basic_df([("HK.HSImain", "恒指期貨主連(異體)", "")])),
        })
        entries2 = eng._fetch_catalog(ctx2)
        assert [e.code for e in entries2] == ["HK.HSImain", "HK.HHImain", "HK.MHImain"]  # dedup：seeds 先入，API row skip


class TestFetchCatalogBasicInfo:
    """lot_size（每手股數/合約乘數）+ listing_date（上市日期）提取——基本資料行數據源。"""

    def test_extracts_lot_size_and_listing_date(self):
        eng = make_engine()
        df = pd.DataFrame([dict(code="HK.00700", name="腾讯控股", english_name="",
                                lot_size=500, listing_date="2004-06-16"),
                           dict(code="US.AAPL", name="苹果", english_name="Apple Inc.",
                                lot_size=1, listing_date="2016-06-09")])
        ctx = FakeCtx([], basicinfo={Market.US: (RET_OK, df)})
        entries = eng._fetch_catalog(ctx)
        by_code = {e.code: e for e in entries}
        assert by_code["HK.00700"].lot_size == 500
        assert by_code["HK.00700"].listing_date == "2004-06-16"
        assert by_code["US.AAPL"].lot_size == 1

    def test_nan_and_none_basicinfo_cells_cleaned(self):
        """pandas NaN（float）/ None → lot_size=None、listing_date=""（唔會 "nan" 字串混入）。"""
        eng = make_engine()
        df = pd.DataFrame([dict(code="US.X", name="x", english_name="",
                                lot_size=float("nan"), listing_date=None)])
        ctx = FakeCtx([], basicinfo={Market.US: (RET_OK, df)})
        entries = eng._fetch_catalog(ctx)
        by_code = {e.code: e for e in entries}
        assert by_code["US.X"].lot_size is None
        assert by_code["US.X"].listing_date == ""

    def test_non_numeric_lot_size_becomes_none(self):
        eng = make_engine()
        df = pd.DataFrame([dict(code="US.Y", name="y", english_name="",
                                lot_size="abc", listing_date="1990-01-01")])
        ctx = FakeCtx([], basicinfo={Market.US: (RET_OK, df)})
        entries = eng._fetch_catalog(ctx)
        by_code = {e.code: e for e in entries}
        assert by_code["US.Y"].lot_size is None  # 非數字 → None（唔 crash）
        assert by_code["US.Y"].listing_date == "1990-01-01"

    def test_missing_basicinfo_columns_yield_defaults(self):
        """df 冇 lot_size/listing_date 欄（舊 schema）→ getattr None → 預設值，唔炸。"""
        eng = make_engine()
        ctx = FakeCtx([], basicinfo={Market.US: (RET_OK, basic_df([("US.Z", "z", "")]))})
        entries = eng._fetch_catalog(ctx)
        by_code = {e.code: e for e in entries}
        assert by_code["US.Z"].lot_size is None
        assert by_code["US.Z"].listing_date == ""


# ---------------------------------------------------------------- on_recv_rsp

class TestQuoteHandler:
    def _run(self, monkeypatch, eng, df, ret=RET_OK):
        emitted, errors = [], []
        eng.bars_changed.connect(lambda p, b: emitted.append((p, b)))  # (period, bars) per-period signal
        eng.error.connect(errors.append)
        # patch SDK base class 嘅 parse 入口（我哋測自己嘅聚合邏輯，唔係 protobuf 層）
        monkeypatch.setattr(StockQuoteHandlerBase, "on_recv_rsp", lambda self, rsp_pb: (ret, df))
        handler = _QuoteHandler(eng)
        ret_out, data_out = handler.on_recv_rsp(None)
        return emitted, errors, ret_out, data_out

    def test_tick_batch_updates_bar_and_emits(self, monkeypatch):
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))  # future anchor → tick_date 確定性（clock skew 分支）
        df = quote_df([("09:30:45.123", 100.0, 1000), ("09:30:50.456", 101.0, 1500)])
        emitted, errors, ret_out, data_out = self._run(monkeypatch, eng, df)
        assert not errors and ret_out == RET_OK and data_out is df
        assert len(emitted) == 1
        period, snap = emitted[0]   # 新 API：(period, bars) per-period signal
        assert period == "K_1M"
        assert isinstance(snap, tuple)  # immutable snapshot（pyqtSignal 跨線程契約）
        (key, o, h, l, c, v), = snap
        assert key == "2030-01-01 09:30"
        assert (o, h, l, c) == (100.0, 101.0, 100.0, 101.0)
        assert v == 500.0  # 首筆 delta=0（無參考點）+ 第二筆 max(0, 1500-1000)

    def test_updates_seeded_bar(self, monkeypatch):
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))
        eng.state.aggregators["K_1M"].seed_from_history([("2030-01-01 09:30", 99.0, 99.5, 98.5, 99.2, 800)])
        df = quote_df([("09:30:10.000", 100.0, 100)])
        emitted, errors, _, _ = self._run(monkeypatch, eng, df)
        assert not errors and len(emitted) == 1
        _period, snap = emitted[0]   # (period, bars) per-period signal
        (key, o, h, l, c, v), = snap
        # open 保留 seed 值；high=max(99.5,100)=100；low=min(98.5,100)=98.5；volume delta=0（seed 後首筆）
        assert (key, o, h, l, c, v) == ("2030-01-01 09:30", 99.0, 100.0, 98.5, 100.0, 800.0)

    def test_new_bar_after_period_rollover(self, monkeypatch):
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))
        eng.state.aggregators["K_1M"].seed_from_history([("2030-01-01 09:30", 99.0, 99.5, 98.5, 99.2, 800)])
        df = quote_df([("09:30:10.000", 100.0, 100), ("09:31:02.000", 102.0, 500)])
        emitted, errors, _, _ = self._run(monkeypatch, eng, df)
        assert not errors and len(emitted) == 1
        _period, bars = emitted[0]   # (period, bars) per-period signal
        assert len(bars) == 2
        assert bars[0][0] == "2030-01-01 09:30"
        key, o, h, l, c, v = bars[1]
        assert key == "2030-01-01 09:31"
        assert (o, h, l, c) == (102.0, 102.0, 102.0, 102.0)
        assert v == 400.0  # max(0, 500-100)

    def test_error_ret_emits_error(self, monkeypatch):
        eng = make_engine()
        emitted, errors, ret_out, data_out = self._run(monkeypatch, eng, None, ret=-1)
        assert len(errors) == 1 and "QUOTE push" in errors[0]
        assert not emitted and ret_out == -1

    def test_none_data_emits_error(self, monkeypatch):
        eng = make_engine()
        emitted, errors, _, _ = self._run(monkeypatch, eng, None)
        assert len(errors) == 1 and not emitted

    def test_nan_price_row_skipped(self, monkeypatch):
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))
        df = quote_df([("09:30:05.000", float("nan"), 100), ("09:30:06.000", 100.0, 200)])
        emitted, errors, _, _ = self._run(monkeypatch, eng, df)
        assert not errors and len(emitted) == 1
        _period, snap = emitted[0]   # (period, bars) per-period signal
        (key, o, h, l, c, v), = snap
        assert (o, h, l, c) == (100.0, 100.0, 100.0, 100.0) and v == 0.0

    def test_garbage_data_time_row_skipped(self, monkeypatch):
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))
        df = quote_df([("garbage", 100.0, 100), ("09:30:05.000", 101.0, 200)])
        emitted, errors, _, _ = self._run(monkeypatch, eng, df)
        assert not errors and len(emitted) == 1
        _period, snap = emitted[0]   # (period, bars) per-period signal
        (key, o, h, l, c, v), = snap
        assert key == "2030-01-01 09:30" and c == 101.0

    def test_duplicate_tick_no_reemit(self, monkeypatch):
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))
        df = quote_df([("09:30:45.123", 100.0, 1000)])
        emitted, errors, _, _ = self._run(monkeypatch, eng, df)
        assert len(emitted) == 1
        # 重複 tick（同時間同價）→ idempotent no-op → 唔再 emit
        emitted2, _, _, _ = self._run(monkeypatch, eng, df)
        assert not emitted2

    def test_out_of_order_tick_skipped(self, monkeypatch):
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))
        df = quote_df([("09:31:00.000", 100.0, 100), ("09:30:59.000", 99.0, 90)])
        emitted, errors, _, _ = self._run(monkeypatch, eng, df)
        assert not errors and len(emitted) == 1
        _period, bars = emitted[0]   # (period, bars) per-period signal
        assert len(bars) == 1 and bars[0][0] == "2030-01-01 09:31" and bars[0][4] == 100.0

    def test_inflight_old_code_row_skipped(self, monkeypatch):
        """切換後舊標的嘅 in-flight push（unsubscribe 唔係硬停）→ code filter skip。"""
        eng = make_engine()  # state.code = HK.HSImain
        df = quote_df([("09:30:45.123", 100.0, 1000)], code="US.AAPL")
        emitted, errors, ret_out, data_out = self._run(monkeypatch, eng, df)
        assert not errors and not emitted
        assert ret_out == RET_OK and data_out is df

    def test_state_swapped_mid_batch_discards_emit(self, monkeypatch):
        """batch 中途 state 被 swap（identity check）→ 呢批唔 emit。"""
        eng = make_engine()
        set_anchor(eng, date(2030, 1, 1))
        df = quote_df([("09:30:45.123", 100.0, 1000)])
        emitted, errors, _, _ = self._run(monkeypatch, eng, df)
        assert len(emitted) == 1
        # 模擬切換：處理第一筆 tick 時 swap 去新 state（_reconfigure 完成嘅瞬間）
        s = eng.state
        new_state = dataclasses.replace(s, aggregators={"K_1M": CandleAggregator(1)})
        orig_apply = s.aggregators["K_1M"].apply_quote

        def apply_and_swap(self_agg, dt, price, cum):
            eng._state = new_state  # mid-batch switch
            return orig_apply(dt, price, cum)

        monkeypatch.setattr(CandleAggregator, "apply_quote", apply_and_swap)
        emitted2, _, _, _ = self._run(monkeypatch, eng, df)
        assert not emitted2  # handler capture 到嘅 state 已唔係當前 → discard

    def test_no_state_silent_return(self, monkeypatch):
        """start() 前（state None）收到 push → 靜默返回，唔 emit 唔報錯。"""
        eng = FutuEngine()
        eng._cfg = make_cfg()
        df = quote_df([("09:30:45.123", 100.0, 1000)])
        emitted, errors, ret_out, _ = self._run(monkeypatch, eng, df)
        assert not errors and not emitted and ret_out == RET_OK


# ---------------------------------------------------------------- tick_date / _fallback_date

_NOW_HKT = datetime(2026, 9, 30, 15, 0)   # HKT 2026-09-30 15:00（日市收市後）


class TestTickDate:
    def test_no_anchor_uses_market_today(self, monkeypatch):
        _patch_now(monkeypatch, _NOW_HKT)
        assert make_engine().tick_date() == date(2026, 9, 30)

    def test_future_anchor_wins_over_today(self, monkeypatch):
        _patch_now(monkeypatch, _NOW_HKT)
        eng = set_anchor(make_engine(), date(2031, 1, 1))
        assert eng.tick_date() == date(2031, 1, 1)  # clock skew：跟住 seed

    def test_past_anchor_uses_today(self, monkeypatch):
        _patch_now(monkeypatch, _NOW_HKT)
        eng = set_anchor(make_engine(), date(2020, 1, 1))
        assert eng.tick_date() == date(2026, 9, 30)  # 夜期跨午夜 → 用市場今日

    def test_no_state_uses_hk_today(self, monkeypatch):
        """start() 前 tick_date（state None）→ HK fallback，唔炸。"""
        _patch_now(monkeypatch, _NOW_HKT)
        assert FutuEngine().tick_date() == date(2026, 9, 30)


class TestFallbackDate:
    """市場時區 fallback：美股喺 HKT 機上「今日」會同 machine-local 差一日。"""

    def test_hk_code_uses_hk_tz(self, monkeypatch):
        _patch_now(monkeypatch, _NOW_HKT)
        assert _fallback_date(None, "HK.00700") == date(2026, 9, 30)

    def test_us_code_same_day_as_hkt(self, monkeypatch):
        # HKT 15:00 = NY 03:00（EDT）→ 兩邊同日
        _patch_now(monkeypatch, _NOW_HKT)
        assert _fallback_date(None, "US.AAPL") == date(2026, 9, 30)

    def test_us_code_ny_previous_day(self, monkeypatch):
        # HKT 2026-10-01 02:00 = NY 2026-09-30 14:00 → NY「今日」係前一日
        # （machine-local HKT 今日會係 10-01——呢個 test 就係驗證用咗市場時區）
        _patch_now(monkeypatch, datetime(2026, 10, 1, 2, 0))
        assert _fallback_date(None, "US.AAPL") == date(2026, 9, 30)

    def test_unknown_prefix_falls_back_to_hk(self, monkeypatch):
        _patch_now(monkeypatch, _NOW_HKT)
        assert _fallback_date(None, "SG.D05") == date(2026, 9, 30)

    def test_no_dot_defaults_hk(self, monkeypatch):
        _patch_now(monkeypatch, _NOW_HKT)
        assert _fallback_date(None, "HSImain") == date(2026, 9, 30)

    def test_anchor_wins_when_after_today(self, monkeypatch):
        _patch_now(monkeypatch, _NOW_HKT)
        assert _fallback_date(date(2027, 1, 1), "US.AAPL") == date(2027, 1, 1)

    def test_tzdata_missing_falls_back_machine_local(self, monkeypatch):
        """ZoneInfo 炸（tzdata 缺失）→ 回落 machine-local，唔 propagate。"""
        def boom(_name):
            raise KeyError("no such timezone")

        monkeypatch.setattr(fe, "ZoneInfo", boom)
        assert _fallback_date(None, "HK.00700") == date.today()


# ---------------------------------------------------------------- _setup 編排（test thread 同步行）

HIST_ROWS = [
    ("2026-09-30 09:30", 100.0, 101.0, 99.5, 100.5, 1000),
    ("2026-09-30 09:31", 100.5, 102.0, 100.0, 101.0, 1200),
]


class TestSetup:
    def test_happy_path(self, monkeypatch):
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        created = {}

        def fake_connect(host, port):
            created.update(host=host, port=port)
            return ctx

        monkeypatch.setattr(fe, "OpenQuoteContext", fake_connect)
        statuses, errors, history = [], [], []
        eng.status.connect(statuses.append)
        eng.error.connect(errors.append)
        eng.history_ready.connect(lambda p, b: history.append((p, b)))  # (period, bars) per-period signal
        eng._setup()  # test thread 同步行 → signal 直接遞送

        assert created == {"host": "127.0.0.1", "port": 11111}
        assert not errors
        assert len(history) == 1   # per-period signal：(period, bars)
        _p, bars = history[0]
        assert _p == "K_1M" and len(bars) == 2
        assert ctx.handler is not None  # set_handler 已呼叫
        assert ctx.subscribed == (["HK.HSImain"], [SubType.QUOTE])
        assert eng._ctx is ctx
        # seed 完成先 swap state：anchor = seed 最後一根 bar 嘅日期
        assert eng.state.anchor_date == date(2026, 9, 30)
        assert eng.state.code == "HK.HSImain"
        assert eng.state.periods == frozenset({"K_1M"})
        assert any(s.startswith("訂閱成功") for s in statuses)  # catalog status 會喺跟住 emit

    def test_env_lowercase_hsimain_normalized(self, monkeypatch):
        """.env 小寫 hk.hsimain → fetch/subscribe/state 全部用正規形式 HK.HSImain。"""
        eng = make_engine(history_count=2, trading_code="hk.hsimain")
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        errors = []
        eng.error.connect(errors.append)
        eng._setup()

        assert not errors
        assert ctx.kline_calls[0]["code"] == "HK.HSImain"
        assert ctx.subscribed == (["HK.HSImain"], [SubType.QUOTE])
        assert eng.state.code == "HK.HSImain"

    def test_connect_failure_emits_error(self, monkeypatch):
        eng = make_engine()

        def boom(host, port):
            raise ConnectionRefusedError("OpenD not running")

        monkeypatch.setattr(fe, "OpenQuoteContext", boom)
        errors = []
        eng.error.connect(errors.append)
        eng._setup()
        assert len(errors) == 1 and "連唔到 OpenD" in errors[0]
        assert eng._ctx is None

    def test_subscribe_failure_closes_ctx(self, monkeypatch):
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)], sub_ret=-1, sub_info="no permission")
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        errors = []
        eng.error.connect(errors.append)
        eng._setup()
        assert any("subscribe 失敗" in e for e in errors)
        assert ctx.closed is True and eng._ctx is None

    def test_kline_error_closes_ctx(self, monkeypatch):
        eng = make_engine()
        ctx = FakeCtx([(-1, "kline err", None)])
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        errors = []
        eng.error.connect(errors.append)
        eng._setup()
        assert any("request_history_kline" in e for e in errors)
        assert ctx.closed is True and eng._ctx is None

    def test_setup_emits_catalog_ready_and_registers_aliases(self, monkeypatch):
        """catalog fetch 成功 → catalog_ready emit + status；mixed-case code 自動註冊 alias。"""
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)], basicinfo={
            Market.HK: (RET_OK, basic_df([("HK.FUTmain", "富途控股", "")])),
        })
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        statuses, catalogs = [], []
        eng.status.connect(statuses.append)
        eng.catalog_ready.connect(catalogs.append)
        eng._setup()

        assert len(catalogs) == 1 and all(isinstance(e, StockEntry) for e in catalogs[0])
        assert any("股票目錄已載入" in s for s in statuses)
        # alias auto-registration：upper form → canonical（_normalize_code 即刻生效）
        assert fe._CODE_ALIASES.get("HK.FUTMAIN") == "HK.FUTmain"
        assert _normalize_code("hk.futmain") == "HK.FUTmain"
        monkeypatch.delitem(fe._CODE_ALIASES, "HK.FUTMAIN", raising=False)

    def test_catalog_failure_does_not_break_setup(self, monkeypatch):
        """catalog fetch 炸 → log + continue：主流程完成、ctx 唔 close、無 error signal。"""
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)

        def boom(_ctx):
            raise RuntimeError("catalog boom")

        monkeypatch.setattr(eng, "_fetch_catalog", boom)
        statuses, errors = [], []
        eng.status.connect(statuses.append)
        eng.error.connect(errors.append)
        eng._setup()

        assert not errors
        assert ctx.closed is False and eng._ctx is ctx  # 主流程 intact
        assert any("訂閱成功" in s for s in statuses)
        assert not any("股票目錄已載入" in s for s in statuses)


# ---------------------------------------------------------------- _normalize_code（大小寫敏感特例）

class TestNormalizeCode:
    def test_hsimain_case_sensitive_alias(self):
        # Futu 主力連續合約代碼大小寫敏感：OpenD 拒收 HSIMAIN（實測「未知股票 HSIMAIN」）
        assert _normalize_code("hk.hsimain") == "HK.HSImain"
        assert _normalize_code("HK.HSIMAIN") == "HK.HSImain"

    def test_strip_and_upper(self):
        assert _normalize_code("  hk.00700 ") == "HK.00700"

    def test_us_ticker_unchanged(self):
        assert _normalize_code("us.aapl") == "US.AAPL"


# ---------------------------------------------------------------- switch 校驗（test thread 同步行）

class TestSwitchValidation:
    def _connected(self) -> FutuEngine:
        eng = make_engine()
        eng._ctx = FakeCtx([])  # 模擬已連線（switch 只檢查 ctx is not None）
        return eng

    def test_bad_code_format_emits_error(self):
        eng = self._connected()
        errors, statuses = [], []
        eng.error.connect(errors.append)
        eng.status.connect(statuses.append)
        eng.switch(code="AAPL", periods=["K_1M"])  # 缺市場 prefix
        assert len(errors) == 1 and "格式錯誤" in errors[0]
        assert not statuses and not eng._switching

    def test_bad_ktype_emits_error(self):
        eng = self._connected()
        errors = []
        eng.error.connect(errors.append)
        eng.switch(code="HK.00700", periods=["K_2M"])
        assert len(errors) == 1 and "未知 K 線週期" in errors[0]

    def test_not_connected_silent_return(self):
        eng = make_engine()  # 無 ctx（start 未行過）
        errors, statuses = [], []
        eng.error.connect(errors.append)
        eng.status.connect(statuses.append)
        eng.switch(code="US.AAPL", periods=["K_5M"])
        assert not errors and not statuses and not eng._switching

    def test_closed_rejects_silently(self):
        eng = self._connected()
        eng.stop()  # _closed=True + ctx close
        errors, statuses = [], []
        eng.error.connect(errors.append)
        eng.status.connect(statuses.append)
        eng.switch(code="US.AAPL", periods=["K_5M"])
        assert not errors and not statuses


# ---------------------------------------------------------------- _reconfigure 運行時切換（test thread 同步行）

class TestReconfigure:
    def _setup_eng(self, pages, sub_ret=RET_OK, sub_info=None):
        eng = make_engine(history_count=2)
        ctx = FakeCtx(pages, sub_ret=sub_ret, sub_info=sub_info)
        eng._ctx = ctx
        return eng, ctx

    def test_happy_path_swaps_state(self):
        eng, ctx = self._setup_eng([(RET_OK, kline_df(HIST_ROWS), None)])
        statuses, errors, history = [], [], []
        eng.status.connect(statuses.append)
        eng.error.connect(errors.append)
        eng.history_ready.connect(lambda p, b: history.append((p, b)))  # (period, bars) per-period signal
        old_state = eng.state

        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))

        # 1) unsubscribe 舊 → 2) fetch 新 code/ktype → 3) subscribe 新
        assert ctx.unsubscribed == (["HK.HSImain"], [SubType.QUOTE])
        call = ctx.kline_calls[0]
        assert call["code"] == "US.AAPL" and call["ktype"] is _KLTYPE_MAP["K_5M"]
        assert ctx.subscribed == (["US.AAPL"], [SubType.QUOTE])
        # state swap：新 aggregator + anchor（seed 最後一根 bar 日期）
        st = eng.state
        assert st is not old_state
        assert st.code == "US.AAPL"
        assert st.periods == frozenset({"K_5M"})
        assert st.anchor_date == date(2026, 9, 30)
        assert len(st.aggregators["K_5M"].bars()) == 2
        # signals：history_ready 新 snapshot (period, bars) + status 切換成功（test thread → 同步遞送）
        _p, bars = history[0]
        assert not errors and len(history) == 1 and _p == "K_5M" and len(bars) == 2
        assert any("切換成功" in s for s in statuses)

    def test_no_history_rolls_back(self):
        eng, ctx = self._setup_eng([(RET_OK, kline_df([]), None)])
        errors, history = [], []
        eng.error.connect(errors.append)
        eng.history_ready.connect(lambda p, b: history.append((p, b)))  # (period, bars) per-period signal
        old_state = eng.state

        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))

        assert any("冇歷史數據" in e for e in errors)
        assert not history
        assert eng.state is old_state  # state 未 swap，圖表保持 live
        assert ctx.subscribed == (["HK.HSImain"], [SubType.QUOTE])  # rollback resubscribe 舊

    def test_fetch_failure_rolls_back(self):
        eng, ctx = self._setup_eng([(-1, "kline err", None)])
        errors = []
        eng.error.connect(errors.append)
        old_state = eng.state

        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))

        assert any("切換失敗" in e and "request_history_kline" in e for e in errors)
        assert eng.state is old_state
        assert ctx.subscribed == (["HK.HSImain"], [SubType.QUOTE])  # resubscribe 舊

    def test_subscribe_failure_rolls_back(self):
        eng, ctx = self._setup_eng(
            [(RET_OK, kline_df(HIST_ROWS), None)], sub_ret=-1, sub_info="no permission")
        errors = []
        eng.error.connect(errors.append)
        old_state = eng.state

        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))

        assert any("subscribe US.AAPL 失敗" in e for e in errors)
        assert eng.state is old_state  # subscribe 失敗 → 唔 swap
        assert ctx.subscribed == (["HK.HSImain"], [SubType.QUOTE])  # 最後一次係 rollback

    def test_unsubscribe_failure_does_not_block(self):
        """unsubscribe 失敗唔阻切換（in-flight push 由 handler code filter 兜底）。"""
        eng, ctx = self._setup_eng([(RET_OK, kline_df(HIST_ROWS), None)])

        def bad_unsub(codes, sub_types):
            return -1, "err"

        ctx.unsubscribe = bad_unsub
        errors = []
        eng.error.connect(errors.append)
        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))
        assert not errors and eng.state.code == "US.AAPL"

    def test_closed_suppresses_signals(self):
        """stop() 後（_closed）worker 完成 → swap 照做但唔 emit。"""
        eng, ctx = self._setup_eng([(RET_OK, kline_df(HIST_ROWS), None)])
        eng._closed = True
        statuses, history = [], []
        eng.status.connect(statuses.append)
        eng.history_ready.connect(lambda p, b: history.append((p, b)))  # (period, bars) per-period signal

        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))

        assert not statuses and not history


# ---------------------------------------------------------------- SMT Divergence（雙標的配對訂閱）

class TestSmt:
    def test_enable_smt_same_code(self):
        """smt_on=True + cfg.smt_code → fetch+seed 副標的 + subscribe；primary aggregator 沿用（唔重新 fetch）。"""
        eng = make_engine(history_count=2, smt_code="US.QQQ")
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])   # 1 page：淨係 secondary fetch 用
        eng._ctx = ctx
        history, smt_history = [], []
        eng.history_ready.connect(lambda p, b: history.append((p, len(b))))
        eng.smt_history_ready.connect(lambda p, b: smt_history.append((p, len(b))))

        eng._reconfigure("HK.HSImain", frozenset({"K_1M"}), smt_on=True)

        assert ctx.unsubscribed is None                          # 同 code → primary 唔會 unsub
        assert [c["code"] for c in ctx.kline_calls] == ["US.QQQ"]   # 淨係 secondary fetch（primary 沿用）
        assert ctx.subscribed == (["US.QQQ"], [SubType.QUOTE])
        st = eng.state
        assert st.code == "HK.HSImain" and st.smt_code == "US.QQQ"
        assert set(st.aggregators) == {"K_1M"} and set(st.smt_aggregators) == {"K_1M"}
        assert st.aggregators["K_1M"].bars() == ()               # primary aggregator 沿用（make_engine 未 seed）
        assert len(st.smt_aggregators["K_1M"].bars()) == 2       # secondary seed from HIST_ROWS
        assert history == [("K_1M", 0)] and smt_history == [("K_1M", 2)]

    def test_disable_smt_unsubscribes_secondary(self):
        """smt_on=False（舊 state 有 SMT）→ unsubscribe 副標的；aggregator 全部沿用、零 fetch。"""
        eng = make_engine(history_count=2, smt_code="US.QQQ")
        ctx1 = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        eng._ctx = ctx1
        eng._reconfigure("HK.HSImain", frozenset({"K_1M"}), smt_on=True)   # 先啟用

        ctx2 = FakeCtx([])                                                # 停用：唔應該有任何 fetch
        eng._ctx = ctx2
        history, smt_history = [], []
        eng.history_ready.connect(lambda p, b: history.append((p, len(b))))
        eng.smt_history_ready.connect(lambda p, b: smt_history.append((p, len(b))))

        eng._reconfigure("HK.HSImain", frozenset({"K_1M"}), smt_on=False)

        assert not ctx2.kline_calls                                       # 全部 aggregator 沿用
        assert ctx2.unsubscribed == (["US.QQQ"], [SubType.QUOTE])         # 副標的 unsub
        st = eng.state
        assert st.smt_code is None and st.smt_aggregators == {}
        assert history == [("K_1M", 0)] and not smt_history               # 停用後唔再 emit SMT

    def test_smt_code_rows_route_to_smt_aggregator(self, monkeypatch):
        """QUOTE push row code == state.smt_code → smt aggregator + smt_bars_changed（primary 唔受影響）。"""
        eng = make_engine(smt_code="US.QQQ")
        smt_agg = CandleAggregator(1)
        eng._state = dataclasses.replace(eng.state, smt_code="US.QQQ", smt_aggregators={"K_1M": smt_agg})
        set_anchor(eng, date(2030, 1, 1))
        primary, smt_bars, errors = [], [], []
        eng.bars_changed.connect(lambda p, b: primary.append((p, len(b))))
        eng.smt_bars_changed.connect(lambda p, b: smt_bars.append((p, len(b))))
        eng.error.connect(errors.append)

        df = quote_df([("09:30:45.123", 200.0, 100)], code="US.QQQ")
        monkeypatch.setattr(StockQuoteHandlerBase, "on_recv_rsp", lambda self, rsp_pb: (RET_OK, df))
        _QuoteHandler(eng).on_recv_rsp(None)

        assert not primary and not errors                                # primary aggregator 冇收到呢筆 tick
        assert smt_bars == [("K_1M", 1)]                                 # secondary tick → smt aggregator
        assert len(smt_agg.bars()) == 1

    def test_mixed_code_rows_route_by_code(self, monkeypatch):
        """同一 push 混合 primary + SMT code rows → 各入自己 aggregator（dual emit）；未知 code skip。"""
        eng = make_engine(smt_code="US.QQQ")
        smt_agg = CandleAggregator(1)
        eng._state = dataclasses.replace(eng.state, smt_code="US.QQQ", smt_aggregators={"K_1M": smt_agg})
        set_anchor(eng, date(2030, 1, 1))
        primary, smt_bars, errors = [], [], []
        eng.bars_changed.connect(lambda p, b: primary.append((p, len(b))))
        eng.smt_bars_changed.connect(lambda p, b: smt_bars.append((p, len(b))))
        eng.error.connect(errors.append)

        df = pd.concat([quote_df([("09:30:45.123", 100.0, 100)]),
                        quote_df([("09:30:46.123", 200.0, 200)], code="US.QQQ"),
                        quote_df([("09:30:47.123", 300.0, 300)], code="US.TSLA")], ignore_index=True)
        monkeypatch.setattr(StockQuoteHandlerBase, "on_recv_rsp", lambda self, rsp_pb: (RET_OK, df))
        _QuoteHandler(eng).on_recv_rsp(None)

        assert not errors
        assert primary == [("K_1M", 1)] and smt_bars == [("K_1M", 1)]    # 各入自己 aggregator；US.TSLA skip

    def test_switch_smt_requires_cfg(self):
        """switch(smt=True) 但 .env 未設 SMT_CODE → error reject（唔會打到 OpenD）。"""
        eng = make_engine(history_count=2)   # cfg.smt_code=None
        eng._ctx = FakeCtx([])               # switch() 要求 ctx 非 None 先至行到校驗
        errors = []
        eng.error.connect(errors.append)

        eng.switch(smt=True)

        assert any("SMT_CODE" in e for e in errors)

    def test_switch_smt_same_as_primary_rejected(self):
        """SMT 配對同主標的一樣 → error reject（背離偵測無意義）。"""
        eng = make_engine(history_count=2, smt_code="HK.HSImain")   # == trading_code
        eng._ctx = FakeCtx([])               # switch() 要求 ctx 非 None 先至行到校驗
        errors = []
        eng.error.connect(errors.append)

        eng.switch(smt=True)

        assert any("唔可以同主標的一樣" in e for e in errors)

    def test_switch_smt_threaded_enable(self):
        """switch(smt=True) 真線程路徑：worker 行 _reconfigure(smt_on=True) → subscribe 副標的 + state swap。"""
        eng = make_engine(history_count=2, smt_code="US.QQQ")
        ctx = GatedCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        eng._ctx = ctx

        eng.switch(smt=True)   # code=None → 沿用 HK.HSImain；periods=None → 沿用 K_1M
        assert wait_until(lambda: ctx.gate_waited)  # worker 行到 subscribe（gate 住）
        ctx.gate.set()
        assert wait_until(lambda: not eng._switching)

        assert [c["code"] for c in ctx.kline_calls] == ["US.QQQ"]
        assert ctx.subscribed == (["US.QQQ"], [SubType.QUOTE])
        st = eng.state
        assert st.code == "HK.HSImain" and st.smt_code == "US.QQQ"
        assert len(st.smt_aggregators["K_1M"].bars()) == 2
        eng.stop()


# ---------------------------------------------------------------- switch 真線程（guard / lifecycle）

class TestSwitchThreaded:
    def test_guard_rejects_concurrent_switch(self):
        """第一單切換進行中 → 第二單 reject；完成後 state 已 swap。"""
        eng = make_engine(history_count=2)
        ctx = GatedCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        eng._ctx = ctx
        statuses = []
        eng.status.connect(statuses.append)

        eng.switch(code="US.AAPL", periods=["K_5M"])
        assert wait_until(lambda: ctx.gate_waited)  # worker 行到 subscribe（gate 住）
        eng.switch(code="HK.00700", periods=["K_1M"])  # → reject
        assert any("切換進行中" in s for s in statuses)  # switch() 喺 test thread → 同步遞送

        ctx.gate.set()
        assert wait_until(lambda: not eng._switching)
        assert eng.state.code == "US.AAPL" and eng.state.periods == frozenset({"K_5M"})
        eng.stop()

    def test_code_normalized_to_upper(self):
        """小寫輸入 → upper 後 fetch/subscribe/state 全部用正規格式。"""
        eng = make_engine(history_count=2)
        ctx = GatedCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        eng._ctx = ctx

        eng.switch(code="hk.00700", periods=["k_5m"])  # 小寫 → upper() 正規化
        assert wait_until(lambda: ctx.gate_waited)
        ctx.gate.set()
        assert wait_until(lambda: not eng._switching)
        assert eng.state.code == "HK.00700" and eng.state.periods == frozenset({"K_5M"})
        assert ctx.subscribed == (["HK.00700"], [SubType.QUOTE])
        eng.stop()

    def test_hsimain_alias_flows_through_switch(self):
        """小寫 hk.hsimain → 正規形式 HK.HSImain（fetch/subscribe/state 全部用 alias）。

        當前標的設做另一隻（HK.00700）→ 行 code-change 路徑先至有 fetch/subscribe 可斷言
        （同 code 切換喺新 engine 係 no-op：沿用 aggregator、唔重新 subscribe）。
        """
        eng = make_engine(history_count=2, trading_code="HK.00700")
        ctx = GatedCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        eng._ctx = ctx

        eng.switch(code="hk.hsimain", periods=["K_1M"])
        assert wait_until(lambda: ctx.gate_waited)
        ctx.gate.set()
        assert wait_until(lambda: not eng._switching)
        assert eng.state.code == "HK.HSImain"
        assert ctx.kline_calls[0]["code"] == "HK.HSImain"
        assert ctx.subscribed == (["HK.HSImain"], [SubType.QUOTE])
        eng.stop()

    def test_switch_rejected_while_setup_running(self, monkeypatch):
        """setup thread 未收工（alive）→ switch reject + status 提示。"""
        eng = FutuEngine()
        ctx = GatedCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        eng.start(make_cfg(history_count=2))
        assert wait_until(lambda: ctx.gate_waited)  # setup thread 阻塞喺 subscribe（alive）

        statuses = []
        eng.status.connect(statuses.append)
        eng.switch(code="US.AAPL", periods=["K_5M"])
        assert any("連線中" in s for s in statuses)
        assert not eng._switching  # 冇 spawn worker

        ctx.gate.set()
        eng.stop()


# ---------------------------------------------------------------- start/stop lifecycle（真線程 + Event 同步）

class TestStartStop:
    def test_start_stop_lifecycle(self, monkeypatch):
        eng = FutuEngine()
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        eng.start(make_cfg(history_count=2))
        assert ctx.subscribe_event.wait(5)  # setup thread 行到 subscribe
        eng.stop()
        assert ctx.closed is True
        assert not (eng._thread and eng._thread.is_alive())
        eng.stop()  # idempotent

    def test_start_twice_noop(self, monkeypatch):
        connected = threading.Event()
        calls = []

        gated = GatedCtx([(RET_OK, kline_df(HIST_ROWS), None)])  # subscribe gate 住令 setup thread alive

        def factory(h, p):
            connected.set()
            calls.append((h, p))
            return gated

        monkeypatch.setattr(fe, "OpenQuoteContext", factory)
        eng = FutuEngine()
        eng.start(make_cfg(history_count=2))
        assert connected.wait(5)  # worker thread 已入 _setup（alive）
        eng.start(make_cfg())     # 第二次 → early return
        gated.gate.set()          # 釋放 subscribe
        assert gated.subscribe_event.wait(5)
        eng.stop()
        assert len(calls) == 1

    def test_start_connect_failure_thread_exits(self, monkeypatch):
        eng = FutuEngine()

        def boom(h, p):
            raise ConnectionRefusedError("no OpenD")

        monkeypatch.setattr(fe, "OpenQuoteContext", boom)
        eng.start(make_cfg())
        thread = eng._thread
        assert wait_until(lambda: not thread.is_alive())
        assert eng._ctx is None

    def test_stop_without_start_is_safe(self):
        FutuEngine().stop()  # 唔好炸

    def test_aggregators_before_start_raises(self):
        with pytest.raises(RuntimeError, match="start"):
            FutuEngine().aggregators


# ---------------------------------------------------------------- 訂閱帳本 reconcile（自動清理洩漏）

class ReconcileCtx:
    """Mock OpenQuoteContext：query_subscription + unsubscribe 記錄（reconcile 測試用）。"""

    def __init__(self, open_codes=(), unsub_ret=RET_OK):
        self._open = set(open_codes)
        self.unsub_calls = []          # list[list[code]]——每次 unsubscribe 嘅 code 列表
        self._unsub_ret = unsub_ret

    def query_subscription(self, is_all_conn=True):
        return RET_OK, {
            "total_used": len(self._open), "own_used": len(self._open), "remain": 900,
            "sub_list": {"QUOTE": sorted(self._open)},
        }

    def unsubscribe(self, codes, sub_types):
        self.unsub_calls.append(list(codes))
        return self._unsub_ret, None

    def close(self):
        self.closed = True


def _reconcile_eng(active_code: str = "US.AAPL") -> FutuEngine:
    """make_engine 後將 state.code 設為 active_code（reconcile 以呢個做「要保留」基準）。"""
    eng = make_engine(history_count=2)
    if active_code != "HK.HSImain":
        eng._state = dataclasses.replace(eng.state, code=active_code)
    return eng


class TestReconcile:
    def test_cleans_stale_leaked_subscriptions(self):
        """帳本入面「唔係當前 state 且 age>=閾值」嘅洩漏訂閱 → unsubscribe + remove。"""
        import time as _t
        eng = _reconcile_eng("US.AAPL")
        store = eng._ensure_store()
        old = _t.time() - 120  # > MIN_SUBSCRIBE_SECONDS(75)
        store.add("HK.HSImain", ts=old)
        store.add("US.BBBL", ts=old)
        ctx = ReconcileCtx(open_codes={"US.AAPL", "HK.HSImain", "US.BBBL"})
        eng._ctx = ctx

        eng._reconcile_subscriptions()

        # 兩筆洩漏訂閱被清理；當前 state US.AAPL 唔會 unsub
        assert sorted(c for call in ctx.unsub_calls for c in call) == ["HK.HSImain", "US.BBBL"]
        assert all("US.AAPL" not in call for call in ctx.unsub_calls)
        # 帳本只剩當前活躍 code（其實 US.AAPL 從來唔喺帳本——reconcile 只清 due）
        remaining = {c for c, _s, _ts in store.list_active()}
        assert "HK.HSImain" not in remaining and "US.BBBL" not in remaining

    def test_skips_recent_subscriptions(self):
        """age < MIN_SUBSCRIBE_SECONDS → 未到期，唔會 unsubscribe（避免又撞「訂閱時間過短」）。"""
        import time as _t
        eng = _reconcile_eng("US.AAPL")
        store = eng._ensure_store()
        store.add("HK.HSImain", ts=_t.time())  # 剛訂閱
        ctx = ReconcileCtx(open_codes={"US.AAPL", "HK.HSImain"})
        eng._ctx = ctx

        eng._reconcile_subscriptions()

        assert not ctx.unsub_calls  # 未滿 1min → 唔清，留待下輪
        assert any(c == "HK.HSImain" for c, _s, _ts in store.list_active())

    def test_query_failure_is_noop(self):
        """query_subscription 失敗 → 跳過呢輪（唔改帳本、唔 unsubscribe），避免誤刪。"""
        import time as _t
        eng = _reconcile_eng("US.AAPL")
        store = eng._ensure_store()
        store.add("HK.HSImain", ts=_t.time() - 120)

        def bad_query(is_all_conn=True):
            return -1, "query err"

        ctx = ReconcileCtx(open_codes={"US.AAPL"})
        ctx.query_subscription = bad_query
        eng._ctx = ctx

        eng._reconcile_subscriptions()

        assert not ctx.unsub_calls  # query 失敗 → 完全唔動
        assert any(c == "HK.HSImain" for c, _s, _ts in store.list_active())  # 帳本 intact

    def test_cleans_residual_not_in_ledger(self):
        """OpenD 端有、帳本冇、且唔係當前 state → 直接 unsubscribe（上次 crash 殘留自癒）。"""
        eng = _reconcile_eng("US.AAPL")
        eng._ensure_store()  # 空帳本
        ctx = ReconcileCtx(open_codes={"US.AAPL", "US.CCCC"})  # US.CCCC 係殘留
        eng._ctx = ctx

        eng._reconcile_subscriptions()

        assert ["US.CCCC"] in ctx.unsub_calls  # 殘留被清
        assert all("US.AAPL" not in call for call in ctx.unsub_calls)

    def test_unsubscribe_failure_keeps_entry_for_retry(self):
        """unsubscribe 仍失敗（例如仲未滿 1min）→ 保留帳本條目，下輪再試。"""
        import time as _t
        eng = _reconcile_eng("US.AAPL")
        store = eng._ensure_store()
        store.add("HK.HSImain", ts=_t.time() - 120)
        ctx = ReconcileCtx(open_codes={"US.AAPL", "HK.HSImain"}, unsub_ret=-1)
        eng._ctx = ctx

        eng._reconcile_subscriptions()

        assert ["HK.HSImain"] in ctx.unsub_calls  # 有試過
        assert any(c == "HK.HSImain" for c, _s, _ts in store.list_active())  # 失敗 → 保留待重試

    def test_schedule_reconcile_idempotent(self):
        """_schedule_reconcile：排一次 timer；重複呼叫唔會再排（冪等）。"""
        eng = _reconcile_eng("US.AAPL")
        eng._ctx = ReconcileCtx(open_codes={"US.AAPL"})

        eng._schedule_reconcile()
        first = eng._reconcile_timer
        assert first is not None and first.is_alive()
        eng._schedule_reconcile()  # 第二次 → no-op（同一 timer）
        assert eng._reconcile_timer is first
        first.cancel()

    def test_schedule_reconcile_noop_when_closed(self):
        """_closed=True → _schedule_reconcile 唔排 timer。"""
        eng = _reconcile_eng("US.AAPL")
        eng._ctx = ReconcileCtx(open_codes={"US.AAPL"})
        eng._closed = True

        eng._schedule_reconcile()

        assert eng._reconcile_timer is None


class TestSubscriptionLedgerIntegration:
    """_setup / _reconfigure 同 SQLite 帳本嘅整合（autouse fixture 已隔離 DB 去 tmp_path）。"""

    def test_setup_records_initial_subscription(self, monkeypatch):
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        eng._setup()

        assert any(c == "HK.HSImain" for c, _s, _ts in eng._store.list_active())
        # 訂閱成功 → 排程咗 reconcile timer（開機對帳）
        assert eng._reconcile_timer is not None and eng._reconcile_timer.is_alive()
        eng._reconcile_timer.cancel()

    def test_reconfigure_unsubscribe_failure_keeps_pending(self):
        """unsubscribe 舊失敗（訂閱未滿 1min）→ 舊 code 保留喺帳本（pending），新 code 入帳。"""
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        store = eng._ensure_store()
        store.add("HK.HSImain", ts=_time.time())  # 模擬初始訂閱已入帳

        def short_unsub(codes, sub_types):
            return -1, "Basic訂閱時間過短"  # OpenD 拒收（未滿 1min）

        ctx.unsubscribe = short_unsub
        eng._ctx = ctx

        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))

        # 舊 code unsubscribe 失敗 → 保留 pending；新 code subscribe 成功 → 入帳
        remaining = {c for c, _s, _ts in store.list_active()}
        assert "HK.HSImain" in remaining and "US.AAPL" in remaining
        assert eng.state.code == "US.AAPL"
        # reconcile timer 已排程（稍後重試清 HK.HSImain）
        assert eng._reconcile_timer is not None and eng._reconcile_timer.is_alive()
        eng._reconcile_timer.cancel()

    def test_reconfigure_unsubscribe_success_removes_old(self):
        """unsubscribe 舊成功 → 帳本移除舊 code，只留新 code。"""
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])  # unsubscribe default RET_OK
        store = eng._ensure_store()
        store.add("HK.HSImain", ts=_time.time())
        eng._ctx = ctx

        eng._reconfigure("US.AAPL", frozenset({"K_5M"}))

        remaining = {c for c, _s, _ts in store.list_active()}
        assert "HK.HSImain" not in remaining and "US.AAPL" in remaining


# ---------------------------------------------------------------- start(code=...)（UI-state 記憶還原標的）

class TestStartCodeParam:
    """start(code=...) → state.code = 正規化後嘅 code；None → fallback cfg.trading_code。

    patch `_setup` 做 no-op（唔 spawn 真實 OpenD 連線），只驗證 start() **同步**設定 state 嗰段邏輯
    （line: `self._state = _State(code, ...)` 喺 thread.start() 之前，所以 start() 返回後 state 已定）。
    """

    def test_start_with_explicit_code_normalizes(self, monkeypatch):
        eng = FutuEngine()
        monkeypatch.setattr(eng, "_setup", lambda: None)   # no-op：唔連 OpenD
        cfg = make_cfg(trading_code="HK.HSImain")
        eng.start(cfg, periods=["K_1M"], code="us.aapl")
        assert eng.state.code == "US.AAPL"   # 小寫 → canonical upper

    def test_start_without_code_falls_back_to_env(self, monkeypatch):
        """code=None（GUI 無記憶）→ fallback cfg.trading_code（.env）。"""
        eng = FutuEngine()
        monkeypatch.setattr(eng, "_setup", lambda: None)
        cfg = make_cfg(trading_code="hk.hsimain")   # .env 小寫 → normalize
        eng.start(cfg, periods=["K_1M"])            # code=None（預設）
        assert eng.state.code == "HK.HSImain"

    def test_start_respects_saved_periods(self, monkeypatch):
        """start(periods=[...]) → state.periods = 傳入 union（多 pane，upper + dedup）。"""
        eng = FutuEngine()
        monkeypatch.setattr(eng, "_setup", lambda: None)
        cfg = make_cfg(trading_code="HK.HSImain")
        eng.start(cfg, periods=["K_5M", "k_15m"], code="US.AAPL")
        assert eng.state.periods == frozenset({"K_5M", "K_15M"})


# ---------------------------------------------------------------- OpenD 定時 ping（連線狀態 + RTT）

class TestLoggedInFlag:
    """_logged_in_flag：qot_logined / trd_logined 雙形態判定（proto bool + docstring str）。"""

    @pytest.mark.parametrize("value", [True, "1", "true", "TRUE", " True ", 1])
    def test_logged_in_forms(self, value):
        assert _logged_in_flag(value) is True

    @pytest.mark.parametrize("value", [False, "0", "false", None, "", 0])
    def test_not_logged_in_forms(self, value):
        assert _logged_in_flag(value) is False


class TestPingOnce:
    """_ping_once：get_global_state() RTT → (connected, latency_ms)——純邏輯、零線程。"""

    def test_connected_when_qot_logined(self):
        eng = make_engine()
        ctx = FakeCtx([])   # default global_state = (RET_OK, {"qot_logined": True})（proto bool 真實形態）
        connected, latency_ms = eng._ping_once(ctx)
        assert connected is True
        assert latency_ms >= 0.0   # perf_counter RTT（本地 mock ≈ 0ms）
        assert len(ctx.global_state_calls) == 1

    def test_disconnected_when_qot_not_logged_in_bool(self):
        """qot_logined=False（proto bool 形態、行情伺服器未登入）→ 斷線。"""
        eng = make_engine()
        ctx = FakeCtx([], global_state=(RET_OK, {"qot_logined": False}))
        connected, _latency = eng._ping_once(ctx)
        assert connected is False

    def test_connected_when_qot_logined_string_one(self):
        """兼容形態：字串 '1'（官方 docstring 聲稱嘅 str 返回）→ 已連線。"""
        eng = make_engine()
        ctx = FakeCtx([], global_state=(RET_OK, {"qot_logined": "1"}))
        connected, _latency = eng._ping_once(ctx)
        assert connected is True

    def test_disconnected_when_qot_not_logged_in(self):
        """兼容形態：字串 '0'（行情伺服器未登入）→ 斷線。"""
        eng = make_engine()
        ctx = FakeCtx([], global_state=(RET_OK, {"qot_logined": "0"}))
        connected, _latency = eng._ping_once(ctx)
        assert connected is False

    def test_disconnected_when_qot_key_missing(self):
        """data 缺 qot_logined key（None）→ 斷線（唔 crash）。"""
        eng = make_engine()
        ctx = FakeCtx([], global_state=(RET_OK, {}))
        connected, _latency = eng._ping_once(ctx)
        assert connected is False

    def test_disconnected_when_ret_not_ok(self):
        """ret != RET_OK（data 係錯誤字串）→ 斷線。"""
        eng = make_engine()
        ctx = FakeCtx([], global_state=(-1, "F3CNN返回错误"))
        connected, _latency = eng._ping_once(ctx)
        assert connected is False

    def test_exception_returns_disconnected_sentinel(self):
        """get_global_state 拋 exception（OpenD 斷線）→ (False, -1.0)。"""
        class BoomCtx:
            def get_global_state(self):
                raise ConnectionError("OpenD down")

        eng = make_engine()
        assert eng._ping_once(BoomCtx()) == (False, -1.0)


class TestPingLoopLifecycle:
    """_start_ping_loop / _ping_loop thread lifecycle + connection_state signal 遞送。"""

    def test_setup_starts_ping_and_emits_connected(self, monkeypatch):
        """_setup() 連線成功 → ping thread 啟動並 emit (True, RTT)。"""
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        monkeypatch.setattr(fe, "OpenQuoteContext", lambda h, p: ctx)
        states = []
        eng.connection_state.connect(lambda c, l: states.append((c, l)))   # 2-arg signal → tuple record
        eng._setup()   # test thread 同步行 → ping thread spawn

        assert wait_until_pump(lambda: len(ctx.global_state_calls) >= 1)
        assert wait_until_pump(
            lambda: any(c is True and lat >= 0 for c, lat in states))   # connected + RTT（cross-thread queued）
        eng.stop()
        assert not (eng._ping_thread and eng._ping_thread.is_alive())

    def test_ping_loop_exits_when_stopped(self):
        """stop() → _ping_stop set + ctx=None → ping thread 退出（唔再 ping）。"""
        eng = make_engine(history_count=2)
        ctx = FakeCtx([(RET_OK, kline_df(HIST_ROWS), None)])
        eng._ctx = ctx
        eng._start_ping_loop()
        assert wait_until(lambda: len(ctx.global_state_calls) >= 1)   # ping 運行中
        eng.stop()
        n_after_stop = len(ctx.global_state_calls)
        _time.sleep(0.3)   # 留一段間隔 → thread 應已退出、冇新 ping
        assert len(ctx.global_state_calls) == n_after_stop

    def test_ping_loop_superseded_by_new_generation(self):
        """_start_ping_loop 重啟（setup retry）→ 舊 thread 偵測 gen mismatch 自然退出（唔重複 ping）。"""
        eng = make_engine()
        ctx = FakeCtx([])
        eng._ctx = ctx
        eng._start_ping_loop()
        first_thread = eng._ping_thread
        assert wait_until(lambda: len(ctx.global_state_calls) >= 1)
        eng._start_ping_loop()   # 重啟 → gen+1、新 thread
        second_thread = eng._ping_thread
        assert second_thread is not first_thread
        assert wait_until(lambda: not first_thread.is_alive())   # 舊 thread 退出（≤2s）

    def test_disconnected_emitted_when_open_d_drops(self):
        """運行時 OpenD 斷線（get_global_state 拋 exception）→ connection_state(False, -1.0)。"""
        class DropCtx(FakeCtx):
            def __init__(self):
                super().__init__([], global_state=(RET_OK, {"qot_logined": "1"}))
                self.drop = threading.Event()

            def get_global_state(self):
                if self.drop.is_set():
                    raise ConnectionError("OpenD down")
                return super().get_global_state()

        eng = make_engine()
        ctx = DropCtx()
        eng._ctx = ctx
        states = []
        eng.connection_state.connect(lambda c, l: states.append((c, l)))   # 2-arg signal → tuple record
        eng._start_ping_loop()
        assert wait_until_pump(lambda: any(c is True for c, _l in states))   # 先 connected（cross-thread queued）
        ctx.drop.set()
        assert wait_until_pump(lambda: (False, -1.0) in states)              # 再報斷線
        eng.stop()
