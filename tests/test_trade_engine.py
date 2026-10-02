"""TradeEngine 單測（offscreen Qt + FakeTradeCtx）。

策略：
- monkeypatch `engine.trade_engine.OpenSecTradeContext` → 按 filter_trdmarket 返回 fake；
- poll/query 邏輯直接喺 main thread 同步調用 `_setup()` / `_poll_once()`——
  同線程 emit = Qt direct connection，唔使 pump event loop；
- place_order 真係 spawn worker thread（跨線程 auto-queue）→ `_pump_until()` pump。
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")   # 必須喺 PySide6 import 前

import time
from types import SimpleNamespace

import pandas as pd
import pytest
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication

from futu import RET_OK, TrdEnv, TrdSide

import engine.trade_engine as te
from engine.trade_engine import TradeEngine, _f, _needs_unlock


@pytest.fixture(autouse=True, scope="module")
def _app():
    """跨線程 auto-queue signal 交付需要 QCoreApplication 存在。"""
    return QApplication.instance() or QApplication([])


def _pump_until(predicate, timeout: float = 5.0) -> bool:
    """Pump Qt event loop 直到 predicate() 為真（跨線程 auto-queue signal 交付）。"""
    deadline = time.time() + timeout
    while not predicate():
        if time.time() > deadline:
            return False
        QCoreApplication.processEvents()
        time.sleep(0.01)
    return True


class FakeTradeCtx:
    """Scripted OpenSecTradeContext fake：call recording + 可編排 responses。"""

    def __init__(self):
        self.acc_list = (RET_OK, pd.DataFrame())      # 預設無帳戶
        self.positions = (RET_OK, [])
        self.funds = (RET_OK, [])
        self.place_results: list[tuple] = []          # [(ret, msg), ...]；最後一個重複使用
        self.unlock_result = (RET_OK, "ok")
        self.closed = False
        self.last_place_kwargs: dict | None = None
        self.calls = {
            "get_acc_list": 0, "position_list_query": 0, "accinfo_query": 0,
            "place_order": 0, "unlock_trade": 0,
        }

    def get_acc_list(self):
        self.calls["get_acc_list"] += 1
        return self.acc_list

    def position_list_query(self, **kwargs):
        self.calls["position_list_query"] += 1
        return self.positions

    def accinfo_query(self, **kwargs):
        self.calls["accinfo_query"] += 1
        return self.funds

    def place_order(self, **kwargs):
        self.calls["place_order"] += 1
        self.last_place_kwargs = kwargs
        if len(self.place_results) > 1:
            return self.place_results.pop(0)
        return self.place_results[0]

    def unlock_trade(self, password=None, **kwargs):
        self.calls["unlock_trade"] += 1
        self.last_unlock_password = password
        return self.unlock_result

    def close(self):
        self.closed = True


def _install_ctx_factory(monkeypatch, ctxs_by_market: dict[str, FakeTradeCtx]):
    """monkeypatch OpenSecTradeContext → 按 filter_trdmarket.name 返回對應 fake。"""
    def factory(filter_trdmarket=None, host="127.0.0.1", port=11111, **kw):
        name = getattr(filter_trdmarket, "name", None) or str(filter_trdmarket)
        return ctxs_by_market[name]

    monkeypatch.setattr(te, "OpenSecTradeContext", factory)


def _cfg(markets=("HK",)):
    return SimpleNamespace(trd_markets=markets, opend_host="127.0.0.1", opend_port=11111)


def _acc_df(rows: list[dict]) -> pd.DataFrame:
    """get_acc_list 返回 DataFrame（trd_env 係字串：TrdEnv.REAL == "REAL"）。"""
    return pd.DataFrame(rows)


@pytest.fixture(autouse=True)
def _engine():
    engine = TradeEngine()
    yield engine
    engine.stop()   # idempotent——所有測試後都 clean shutdown


# ------------------------------------------------------------- 純函數

def test_needs_unlock_variants():
    assert _needs_unlock("請先解鎖交易") is True
    assert _needs_unlock("trade not unlocked, please unlock first") is True
    assert _needs_unlock("insufficient balance") is False
    assert _needs_unlock("") is False


def test_f_handles_invalid_values():
    assert _f("N/A") == 0.0          # NoneDataValue
    assert _f(None) == 0.0
    assert _f(float("nan")) == 0.0
    assert _f(3) == 3.0
    assert _f(2.5, default=1.0) == 2.5
    assert _f(True, default=-1.0) == -1.0   # bool 唔算有效數


# ------------------------------------------------------------- lifecycle / setup

def test_start_spawns_setup_and_poll_threads(monkeypatch):
    ctx = FakeTradeCtx()
    ctx.acc_list = (RET_OK, _acc_df([{"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1"}]))
    _install_ctx_factory(monkeypatch, {"HK": ctx})

    pos_events: list = []
    engine = TradeEngine()
    engine.positions_updated.connect(lambda rows: pos_events.append(rows))
    try:
        engine.start(_cfg(("HK",)))
        assert _pump_until(lambda: len(pos_events) >= 1), "首輪 poll 應 emit positions"
        assert ctx.calls["position_list_query"] >= 1
        assert engine._poll_thread is not None and engine._poll_thread.is_alive()
    finally:
        engine.stop()


def test_stop_is_idempotent_and_joins_threads(monkeypatch):
    ctx = FakeTradeCtx()
    ctx.acc_list = (RET_OK, _acc_df([{"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1"}]))
    _install_ctx_factory(monkeypatch, {"HK": ctx})

    pos_events: list = []
    engine = TradeEngine()
    engine.positions_updated.connect(lambda rows: pos_events.append(rows))
    engine.start(_cfg(("HK",)))
    assert _pump_until(lambda: len(pos_events) >= 1)

    engine.stop()
    engine.stop()   # idempotent：第二次唔 crash
    assert ctx.closed is True, "stop() 應 close 所有 contexts"


def test_no_real_account_status_message(monkeypatch):
    """只有 SIMULATE 帳戶 → status「未找到實倉」+ poll loop 唔啟動。"""
    ctx = FakeTradeCtx()
    ctx.acc_list = (RET_OK, _acc_df([{"acc_id": 1, "trd_env": "SIMULATE", "card_num": "C1"}]))
    _install_ctx_factory(monkeypatch, {"HK": ctx})

    engine = TradeEngine()
    status_events: list[str] = []
    engine.status.connect(status_events.append)
    engine._cfg = _cfg(("HK",))   # 直接同步跑 setup（main thread，唔 spawn thread）
    engine._setup()
    assert any("未找到實倉" in m for m in status_events), f"status={status_events}"
    assert engine._poll_thread is None, "無 REAL 帳戶唔應啟動 poll loop"


def test_market_ctx_failure_continues_other_markets(monkeypatch):
    """HK context 建立失敗 → error emit + US 照常連線。"""
    us = FakeTradeCtx()
    us.acc_list = (RET_OK, _acc_df([{"acc_id": 2, "trd_env": TrdEnv.REAL, "card_num": "C2"}]))

    def factory(filter_trdmarket=None, **kw):
        name = getattr(filter_trdmarket, "name", None) or str(filter_trdmarket)
        if name == "HK":
            raise RuntimeError("connection refused")
        return us

    monkeypatch.setattr(te, "OpenSecTradeContext", factory)

    engine = TradeEngine()
    status_events: list[str] = []
    error_events: list[str] = []
    engine.status.connect(status_events.append)
    engine.error.connect(error_events.append)
    engine._cfg = _cfg(("HK", "US"))
    engine._setup()
    assert any("HK" in m and "連線失敗" in m for m in error_events), f"errors={error_events}"
    assert list(engine._ctxs) == ["US"], "HK 失敗唔應影響 US context"
    assert any("已連線：1 個實倉帳戶" in m for m in status_events), f"status={status_events}"


# ------------------------------------------------------------- poll / queries

def _wire_poll_state(engine: TradeEngine, ctx: FakeTradeCtx, acc_id: int = 7) -> None:
    engine._ctxs["HK"] = ctx
    engine._accounts["HK"] = [(acc_id, "card")]


def test_positions_signal_emits_mapped_rows():
    """position_list_query dict → PositionRow 映射（pl_ratio 已是百分數、'N/A'→0.0）。"""
    ctx = FakeTradeCtx()
    ctx.positions = (RET_OK, [{
        "code": "HK.00700", "stock_name": "騰訊控股", "position_market": "HK",
        "qty": 100, "can_sell_qty": 50, "cost_price": 300.0, "nominal_price": 320.0,
        "market_val": 32000.0, "pl_ratio": 6.67, "pl_val": 2000.0,
    }])
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    pos_events: list = []
    engine.positions_updated.connect(pos_events.append)
    engine._poll_once()   # main thread 同步 → direct connection

    assert len(pos_events) == 1 and len(pos_events[0]) == 1
    row = pos_events[0][0]
    assert (row.code, row.name, row.market) == ("HK.00700", "騰訊控股", "HK")
    assert row.qty == 100.0 and row.can_sell_qty == 50.0
    assert row.cost_price == 300.0 and row.last_price == 320.0
    assert row.market_value == 32000.0 and row.pl_val == 2000.0
    assert row.pl_ratio_pct == 6.67, "pl_ratio 已是百分數數字，唔好再 ×100"


def test_positions_query_failure_returns_empty():
    ctx = FakeTradeCtx()
    ctx.positions = (-1, "query failed")
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    pos_events: list = []
    engine.positions_updated.connect(pos_events.append)
    engine._poll_once()
    assert pos_events == [()], "查詢失敗 → 空 tuple（唔 crash）"


def test_funds_signal_emits_snapshot_totals():
    """多帳戶 accinfo_query → 跨帳戶加總成一個 FundsSnapshot。"""
    ctx = FakeTradeCtx()
    base = {
        "total_assets": 1_000_000.0, "hk_cash": 500_000.0, "us_cash": 10_000.0,
        "hk_avl_withdrawal_cash": 400_000.0, "us_avl_withdrawal_cash": 8_000.0,
        "power": 2_000_000.0, "initial_margin": 50_000.0, "maintenance_margin": 30_000.0,
    }
    ctx.funds = (RET_OK, [base])
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)
    # 第二個帳戶：加總驗證
    engine._accounts["HK"] = [(7, "c1"), (8, "c2")]

    funds_events: list = []
    engine.funds_updated.connect(funds_events.append)
    engine._poll_once()

    assert len(funds_events) == 1
    f = funds_events[0]
    assert f.total_assets == 2_000_000.0, "兩帳戶加總"
    assert f.cash_hkd == 1_000_000.0 and f.cash_usd == 20_000.0
    assert f.withdraw_hkd == 800_000.0 and f.withdraw_usd == 16_000.0
    assert f.buying_power == 4_000_000.0
    assert f.initial_margin == 100_000.0 and f.maintenance_margin == 60_000.0


def test_funds_query_failure_skips_account():
    """單帳戶 accinfo 失敗 → 唔 emit funds（got_funds=False），positions 照常。"""
    ctx = FakeTradeCtx()
    ctx.funds = (-1, "accinfo failed")
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    pos_events: list = []
    funds_events: list = []
    engine.positions_updated.connect(pos_events.append)
    engine.funds_updated.connect(funds_events.append)
    engine._poll_once()
    assert pos_events == [()]
    assert funds_events == [], "無有效資金數據唔應 emit"


# ------------------------------------------------------------- place order

def test_place_order_success_emits_order_id():
    ctx = FakeTradeCtx()
    ctx.place_results = [(RET_OK, "12345")]
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("HK.00700", TrdSide.BUY, 100.5, 200)
    assert _pump_until(lambda: len(results) >= 1), "worker thread 應 emit order_result"

    ok, msg = results[0]
    assert ok is True and "order_id=12345" in msg
    assert ctx.calls["place_order"] == 1
    assert ctx.calls["unlock_trade"] == 0, "成功唔需要 unlock"
    kw = ctx.last_place_kwargs
    assert (kw["price"], kw["qty"], kw["code"]) == (100.5, 200, "HK.00700")
    assert kw["trd_side"] is TrdSide.BUY


def test_place_order_unlock_retry_on_locked_error():
    """「未解鎖」錯誤 + 有 PIN → unlock_trade 一次 + place_order retry 一次（無循環）。"""
    ctx = FakeTradeCtx()
    ctx.place_results = [(-1, "請先解鎖交易"), (0, "999")]
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("HK.00700", TrdSide.SELL, 50.0, 100, pin="123456")
    assert _pump_until(lambda: len(results) >= 1)

    ok, msg = results[0]
    assert ok is True and "解鎖後重試" in msg and "order_id=999" in msg
    assert ctx.calls["unlock_trade"] == 1, "unlock_trade 最多一次（30s/10 次限制）"
    assert ctx.last_unlock_password == "123456"
    assert ctx.calls["place_order"] == 2, "retry 最多一次，嚴禁循環"


def test_place_order_failure_without_pin_no_unlock_call():
    """「未解鎖」錯誤但無 PIN → 明確提示、唔調 unlock_trade。"""
    ctx = FakeTradeCtx()
    ctx.place_results = [(-1, "請先解鎖交易")]
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("HK.00700", TrdSide.BUY, 10.0, 10)   # pin=None
    assert _pump_until(lambda: len(results) >= 1)

    ok, msg = results[0]
    assert ok is False and "交易未解鎖" in msg
    assert ctx.calls["unlock_trade"] == 0
    assert ctx.calls["place_order"] == 1


def test_place_order_generic_failure_emits_error():
    ctx = FakeTradeCtx()
    ctx.place_results = [(-1, "insufficient buying power")]
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("HK.00700", TrdSide.BUY, 10.0, 10)
    assert _pump_until(lambda: len(results) >= 1)

    ok, msg = results[0]
    assert ok is False and "insufficient buying power" in msg


def test_place_order_rejected_when_closed():
    engine = TradeEngine()
    ctx = FakeTradeCtx()
    _wire_poll_state(engine, ctx)
    engine.stop()   # set _closed

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("HK.00700", TrdSide.BUY, 10.0, 10)
    assert len(results) == 1, "closed → 立即 emit（direct connection）"
    assert results[0][0] is False and "已關閉" in results[0][1]
    assert ctx.calls["place_order"] == 0


def test_place_order_unknown_market_rejected():
    """code 前綴市場未連線 → 明確拒絕訊息（唔 spawn worker）。"""
    engine = TradeEngine()
    _wire_poll_state(engine, FakeTradeCtx())   # 只有 HK

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("JP.7203", TrdSide.BUY, 10.0, 10)
    assert len(results) == 1
    assert results[0][0] is False and "未連線" in results[0][1]


def test_worker_exception_never_crashes_engine():
    """worker thread 內 exception → order_result(False, ...)，engine 存活。"""
    class BoomCtx(FakeTradeCtx):
        def place_order(self, **kwargs):
            self.calls["place_order"] += 1
            raise RuntimeError("boom")

    ctx = BoomCtx()
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("HK.00700", TrdSide.BUY, 10.0, 10)
    assert _pump_until(lambda: len(results) >= 1)

    ok, msg = results[0]
    assert ok is False and "下單異常" in msg and "boom" in msg
    # engine 仍可用（未 crash）：再下一單照樣走流程
    ctx2 = FakeTradeCtx()
    ctx2.place_results = [(0, "555")]
    _wire_poll_state(engine, ctx2)
    results.clear()
    engine.place_order("HK.00700", TrdSide.BUY, 10.0, 10)
    assert _pump_until(lambda: len(results) >= 1)
    assert results[0][0] is True
