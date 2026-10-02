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
from engine.trade_engine import OrderRow, TradeEngine, _f, _needs_unlock


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
        self.orders = (RET_OK, [])                    # order_list_query（今日訂單）
        self.place_results: list[tuple] = []          # [(ret, msg), ...]；最後一個重複使用
        self.unlock_result = (RET_OK, "ok")
        self.closed = False
        self.last_place_kwargs: dict | None = None
        self.calls = {
            "get_acc_list": 0, "position_list_query": 0, "accinfo_query": 0,
            "order_list_query": 0, "place_order": 0, "unlock_trade": 0,
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

    def order_list_query(self, **kwargs):
        self.calls["order_list_query"] += 1
        return self.orders

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
    # Commit 35：交易 OpenD 獨立端點（trade_host/trade_port）——Config dataclass 永遠有呢兩欄
    return SimpleNamespace(trd_markets=markets, opend_host="127.0.0.1", opend_port=11111,
                           trade_host="127.0.0.1", trade_port=11111)


def _acc_df(rows: list[dict]) -> pd.DataFrame:
    """get_acc_list 返回 DataFrame（trd_env 係字串：TrdEnv.REAL == "REAL"）。"""
    return pd.DataFrame(rows)


@pytest.fixture(autouse=True)
def _engine():
    engine = TradeEngine()
    yield engine
    engine.stop()   # idempotent——所有測試後都 clean shutdown


@pytest.fixture(autouse=True)
def _tcp_ok(monkeypatch):
    """Commit 36：_setup() TCP pre-check 預設通過——現有測試聚焦 ctx mock 邏輯（零真實網絡）；重試行為有專項測試。"""
    monkeypatch.setattr(te, "tcp_reachable", lambda host, port: (True, ""))


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
    ctx.acc_list = (RET_OK, _acc_df([{"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1",
                                      "acc_status": "ACTIVE"}]))
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
    ctx.acc_list = (RET_OK, _acc_df([{"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1",
                                      "acc_status": "ACTIVE"}]))
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
    us.acc_list = (RET_OK, _acc_df([{"acc_id": 2, "trd_env": TrdEnv.REAL, "card_num": "C2",
                                     "acc_status": "ACTIVE"}]))

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


def test_setup_tcp_retry_until_success(monkeypatch):
    """Commit 36：TCP pre-check 失敗 → error emit + 自動重試；重試成功 → setup 繼續（唔會永久阻塞）。"""
    ctx = FakeTradeCtx()
    _install_ctx_factory(monkeypatch, {"HK": ctx})
    results = iter([(False, "Connection refused"), (True, "")])
    monkeypatch.setattr(te, "tcp_reachable", lambda h, p: next(results))
    monkeypatch.setattr(te, "CONNECT_RETRY_INTERVAL_S", 0.01)   # 測試唔等真 5s

    engine = TradeEngine()
    error_events: list[str] = []
    status_events: list[str] = []
    engine.error.connect(error_events.append)
    engine.status.connect(status_events.append)
    engine._cfg = _cfg(("HK",))
    engine._setup()
    assert len(error_events) == 1 and "連唔到交易 OpenD" in error_events[0], f"errors={error_events}"
    assert any("連線 OpenD 交易服務中" in m for m in status_events), "重試成功後 setup 應繼續"


# ------------------------------------------------------------- poll / queries

def _wire_poll_state(engine: TradeEngine, ctx: FakeTradeCtx, acc_id: int = 7, order_acc: bool = True) -> None:
    """Wire poll state：ctxs + REAL accounts（+ per-account funds target + 可下單 acc_id，除非 order_acc=False）。"""
    engine._ctxs["HK"] = ctx
    engine._accounts["HK"] = [(acc_id, "card")]
    engine._funds_targets = [("HK", acc_id, "REAL")]   # per-account funds polling（雙 env、ACTIVE only）
    if order_acc:
        engine._order_accs["HK"] = acc_id


def test_positions_signal_emits_mapped_rows():
    """position_list_query dict → PositionRow 映射（APP 對齊字段組、'N/A'→0.0）。"""
    ctx = FakeTradeCtx()
    ctx.positions = (RET_OK, [{
        "code": "HK.00700", "stock_name": "騰訊控股", "position_market": "HK",
        "qty": 100, "can_sell_qty": 50, "average_cost": 300.0, "nominal_price": 320.0,
        "market_val": 32000.0, "pl_ratio_avg_cost": 6.67, "unrealized_pl": 2000.0,
        "today_pl_val": 150.0,
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
    assert row.avg_cost == 300.0 and row.last_price == 320.0
    assert row.market_value == 32000.0 and row.unrealized_pl == 2000.0
    assert row.pl_ratio_pct == 6.67, "pl_ratio_avg_cost 已是百分數數字，唔好再 ×100"
    assert row.today_pl == 150.0


def test_positions_dataframe_input_normalized():
    """live bug regression：position_list_query 成功返回 **DataFrame**（非 list）→ _rows() normalize。"""
    ctx = FakeTradeCtx()
    ctx.positions = (RET_OK, pd.DataFrame([{
        "code": "US.AAPL", "stock_name": "Apple", "position_market": "US",
        "qty": 10, "can_sell_qty": 10, "average_cost": 150.0, "nominal_price": 140.0,
        "market_val": 1400.0, "pl_ratio_avg_cost": -6.67, "unrealized_pl": -100.0,
        "today_pl_val": -20.0,
    }]))
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    pos_events: list = []
    engine.positions_updated.connect(pos_events.append)
    engine._poll_once()

    assert len(pos_events) == 1 and len(pos_events[0]) == 1, "DataFrame 必須 normalize 到 rows"
    row = pos_events[0][0]
    assert (row.code, row.avg_cost, row.unrealized_pl, row.pl_ratio_pct, row.today_pl) == \
        ("US.AAPL", 150.0, -100.0, -6.67, -20.0)


def test_funds_dataframe_input_normalized():
    """live bug regression：accinfo_query 成功返回 **DataFrame** → _rows() normalize + per-account event。"""
    ctx = FakeTradeCtx()
    ctx.funds = (RET_OK, pd.DataFrame([{
        "total_assets": 500_000.0, "hk_cash": 200_000.0, "us_cash": 1_000.0,
        "hk_avl_withdrawal_cash": 150_000.0, "us_avl_withdrawal_cash": 800.0,
        "power": 900_000.0, "initial_margin": 20_000.0, "maintenance_margin": 12_000.0,
        "risk_status": "LEVEL3",
    }]))
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    funds_events: list = []
    engine.account_funds_updated.connect(lambda *a: funds_events.append(a))   # 3-arg signal → tuple
    engine._poll_once()

    assert len(funds_events) == 1, "DataFrame 必須 normalize（舊 isinstance(data, list) live 靜默失敗）"
    acc_id, env_str, f = funds_events[0]
    assert (acc_id, env_str) == (7, "REAL"), "per-account event：(acc_id, trd_env, snapshot)"
    assert f.total_assets == 500_000.0 and f.buying_power == 900_000.0
    assert f.risk_status == "LEVEL3"


def test_account_funds_signal_accepts_snowflake_acc_id():
    """Commit 32 live bug regression：富途 acc_id 係 18 位 snowflake（~2.8e17）——超出 PySide6
    Signal(int) 嘅 C 4-byte signed int 上限（2^31-1）→ shiboken OverflowError + emit 靜默失效。
    signal param 必須係 object，大整數原樣傳遞。"""
    engine = TradeEngine()
    funds_events: list = []
    engine.account_funds_updated.connect(lambda *a: funds_events.append(a))
    acc_id = 281756477678772637   # 用戶 live 實測嘅真實 acc_id（18 位）
    engine.account_funds_updated.emit(acc_id, "REAL", object())

    assert len(funds_events) == 1, "emit 必須成功交付（Signal(int) 會 OverflowError / 靜默失效）"
    assert funds_events[0][0] == acc_id, "acc_id 必須原樣傳遞（唔好截斷/溢出）"


def test_orders_dataframe_input_normalized():
    """live bug regression：order_list_query 成功返回 **DataFrame** → OrderRow 映射。"""
    ctx = FakeTradeCtx()
    ctx.orders = (RET_OK, pd.DataFrame([{
        "order_id": "777", "code": "HK.00700", "trd_side": "BUY", "order_type": "NORMAL",
        "order_status": "FILLED_PART", "qty": 200, "price": 55.5,
        "dealt_qty": 100, "dealt_avg_price": 55.4, "create_time": "2026-10-02 09:30:00",
    }]))
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    orders_events: list = []
    engine.orders_updated.connect(orders_events.append)
    engine._poll_once()

    assert len(orders_events) == 1 and len(orders_events[0]) == 1
    o = orders_events[0][0]
    assert (o.order_id, o.code, o.side, o.status) == ("777", "HK.00700", "BUY", "FILLED_PART")
    assert o.qty == 200.0 and o.dealt_qty == 100.0 and o.create_time.endswith("09:30:00")


def test_positions_query_failure_returns_empty():
    ctx = FakeTradeCtx()
    ctx.positions = (-1, "query failed")
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    pos_events: list = []
    engine.positions_updated.connect(pos_events.append)
    engine._poll_once()
    assert pos_events == [()], "查詢失敗 → 空 tuple（唔 crash）"


def test_funds_signal_emits_per_account_events():
    """多帳戶 accinfo_query → **逐個 emit** per-account event（各自總額；engine 唔再加總——GUI 端按 env 分組加總）。"""
    ctx = FakeTradeCtx()
    base = {
        "total_assets": 1_000_000.0, "hk_cash": 500_000.0, "us_cash": 10_000.0,
        "hk_avl_withdrawal_cash": 400_000.0, "us_avl_withdrawal_cash": 8_000.0,
        "power": 2_000_000.0, "initial_margin": 50_000.0, "maintenance_margin": 30_000.0,
        "risk_status": "LEVEL3",
    }
    ctx.funds = (RET_OK, [base])
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)
    # 第二個帳戶：per-account event（GUI 端按 env 分組加總）
    engine._funds_targets = [("HK", 7, "REAL"), ("HK", 8, "REAL")]

    funds_events: list = []
    engine.account_funds_updated.connect(lambda *a: funds_events.append(a))   # 3-arg signal → tuple
    engine._poll_once()

    assert len(funds_events) == 2, "每帳戶一個獨立 event（唔再跨帳戶加總）"
    by_acc = {acc_id: snap for acc_id, _env, snap in funds_events}
    assert set(by_acc) == {7, 8}
    for f in by_acc.values():
        assert f.total_assets == 1_000_000.0, "各自總額（engine 唔加總）"
        assert f.cash_hkd == 500_000.0 and f.cash_usd == 10_000.0
        assert f.withdraw_hkd == 400_000.0 and f.withdraw_usd == 8_000.0
        assert f.buying_power == 2_000_000.0


def test_funds_risk_status_per_account_passthrough():
    """per-account event：risk_status 原樣透傳（跨帳戶「取最嚴重」係 GUI 端 _sum_funds 嘅事）。"""
    ctx = FakeTradeCtx()
    # 兩帳戶：acc 7 LEVEL3、acc 8 LEVEL1 → 各自 event 保留自己嘅 risk_status
    responses = {7: {"total_assets": 100.0, "risk_status": "LEVEL3"},
                 8: {"total_assets": 200.0, "risk_status": "LEVEL1"}}

    def accinfo_query(acc_id=None, **kwargs):
        ctx.calls["accinfo_query"] += 1
        return (RET_OK, [responses[acc_id]])

    ctx.accinfo_query = accinfo_query   # instance attr shadow method（per-acc response）
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)
    engine._funds_targets = [("HK", 7, "REAL"), ("HK", 8, "REAL")]

    funds_events: list = []
    engine.account_funds_updated.connect(lambda *a: funds_events.append(a))   # 3-arg signal → tuple
    engine._poll_once()

    by_acc = {acc_id: snap for acc_id, _env, snap in funds_events}
    assert set(by_acc) == {7, 8}
    assert by_acc[7].total_assets == 100.0 and by_acc[7].risk_status == "LEVEL3"
    assert by_acc[8].total_assets == 200.0 and by_acc[8].risk_status == "LEVEL1", "per-account 原樣透傳"


def test_funds_query_failure_skips_account():
    """單帳戶 accinfo 失敗 → 唔 emit account_funds_updated（GUI 保留上次值），positions 照常。"""
    ctx = FakeTradeCtx()
    ctx.funds = (-1, "accinfo failed")
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    pos_events: list = []
    funds_events: list = []
    engine.positions_updated.connect(pos_events.append)
    engine.account_funds_updated.connect(lambda *a: funds_events.append(a))   # 3-arg signal → tuple
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
    assert kw["acc_id"] == 7, "place_order 必須帶明確 acc_id（per-market 下單帳戶）"


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


# ------------------------------------------------------------- 帳戶分類 / 訂單輪詢

def test_setup_classifies_all_accounts_and_excludes_master(monkeypatch):
    """get_acc_list 收集全部帳戶（REAL/SIMULATE/比賽）；MASTER 主帳戶唔可選做下單帳戶。"""
    ctx = FakeTradeCtx()
    rows = [
        # acc 1：REAL MASTER 主帳戶（auth HK,US）→ 分類可見、polling 計入、但唔可落單
        {"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1", "uni_card_num": "U1",
         "acc_type": "MARGIN", "sim_acc_type": "", "security_firm": "FUTUSECURITIES",
         "trdmarket_auth": ("HK", "US"), "acc_role": "MASTER", "acc_status": "ACTIVE"},
        # acc 2：REAL 非 MASTER（auth HK）→ HK 市場下單帳戶
        {"acc_id": 2, "trd_env": TrdEnv.REAL, "card_num": "C2", "uni_card_num": "U2",
         "acc_type": "MARGIN", "sim_acc_type": "", "security_firm": "FUTUSECURITIES",
         "trdmarket_auth": ("HK",), "acc_role": "", "acc_status": "ACTIVE"},
        # acc 3：SIMULATE 比賽帳戶 → 分類面板可見、唔入 polling / 下單
        {"acc_id": 3, "trd_env": "SIMULATE", "card_num": "C3", "uni_card_num": "U3",
         "acc_type": "MARGIN", "sim_acc_type": "COMPETITION", "security_firm": "",
         "trdmarket_auth": ("US",), "acc_role": "", "acc_status": "ACTIVE"},
    ]
    ctx.acc_list = (RET_OK, _acc_df(rows))
    _install_ctx_factory(monkeypatch, {"HK": ctx})

    engine = TradeEngine()
    accounts_events: list = []
    status_events: list[str] = []
    engine.accounts_updated.connect(accounts_events.append)
    engine.status.connect(status_events.append)
    engine._cfg = _cfg(("HK",))
    engine._setup()

    assert len(accounts_events) == 1, "分類面板 accounts_updated 必須 emit"
    accs = accounts_events[0]
    assert {a.acc_id for a in accs} == {1, 2, 3}, "所有帳戶類型都要可見（含 SIMULATE/比賽）"
    by_id = {a.acc_id: a for a in accs}
    assert by_id[1].acc_role == "MASTER" and by_id[1].trdmarket_auth == ("HK", "US")
    assert by_id[3].sim_acc_type == "COMPETITION" and by_id[3].trd_env == "SIMULATE"
    # MASTER 排除：HK 下單帳戶 = acc 2（首個非 MASTER、REAL、auth 含 HK）
    assert engine._order_accs.get("HK") == 2, "MASTER 主帳戶唔可以落單"
    # polling 只計 REAL 帳戶（acc 1 + 2），SIMULATE 唔入
    assert {aid for aid, _c in engine._accounts["HK"]} == {1, 2}
    assert any("已連線：2 個實倉帳戶" in m for m in status_events), f"status={status_events}"


def test_setup_dedupes_accounts_across_market_contexts(monkeypatch):
    """同一帳戶出現喺多個市場 context → _all_accounts 按 (trd_env, acc_id) dedupe。"""
    ctx = FakeTradeCtx()   # HK/US 共用同一 fake（get_acc_list 返回相同）
    rows = [
        {"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1",
         "trdmarket_auth": ("HK", "US"), "acc_role": "", "acc_status": "ACTIVE"},
        {"acc_id": 2, "trd_env": TrdEnv.REAL, "card_num": "C2",
         "trdmarket_auth": ("US",), "acc_role": "", "acc_status": "ACTIVE"},
    ]
    ctx.acc_list = (RET_OK, _acc_df(rows))
    _install_ctx_factory(monkeypatch, {"HK": ctx, "US": ctx})

    engine = TradeEngine()
    accounts_events: list = []
    engine.accounts_updated.connect(accounts_events.append)
    engine._cfg = _cfg(("HK", "US"))
    engine._setup()

    assert len(accounts_events) == 1
    accs = accounts_events[0]
    assert [a.acc_id for a in accs] == [1, 2], "dedupe：同一帳戶唔可重複出現"
    # per-market polling list 各自獨立（每個 context 查自己嗰份 REAL 帳戶）
    assert {aid for aid, _c in engine._accounts["HK"]} == {1, 2}
    assert {aid for aid, _c in engine._accounts["US"]} == {1, 2}
    # funds_targets 按 (env, acc_id) dedupe：首個發現嘅 market（HK）決定用邊個 ctx
    assert [(m, a, e) for m, a, e in engine._funds_targets] == [("HK", 1, "REAL"), ("HK", 2, "REAL")]


def test_setup_excludes_non_active_accounts_from_polling(monkeypatch):
    """acc_status != "ACTIVE"（DISABLED）→ 排除出 _accounts / _funds_targets / 下單選擇，但 accounts_updated 仍可見。"""
    ctx = FakeTradeCtx()
    rows = [
        {"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1",
         "trdmarket_auth": ("HK",), "acc_role": "", "acc_status": "DISABLED"},
        {"acc_id": 2, "trd_env": TrdEnv.REAL, "card_num": "C2",
         "trdmarket_auth": ("HK",), "acc_role": "", "acc_status": "ACTIVE"},
    ]
    ctx.acc_list = (RET_OK, _acc_df(rows))
    _install_ctx_factory(monkeypatch, {"HK": ctx})

    engine = TradeEngine()
    accounts_events: list = []
    engine.accounts_updated.connect(accounts_events.append)
    engine._cfg = _cfg(("HK",))
    engine._setup()

    accs = accounts_events[0]
    assert {a.acc_id for a in accs} == {1, 2}, "accounts_updated 照舊 emit 全部帳戶（含 DISABLED）"
    by_id = {a.acc_id: a for a in accs}
    assert by_id[1].acc_status == "DISABLED" and by_id[2].acc_status == "ACTIVE"
    # DISABLED 排除出 polling / funds / 下單選擇（三處一致）
    assert {aid for aid, _c in engine._accounts["HK"]} == {2}, "DISABLED 唔入 positions/orders polling"
    assert [(m, a, e) for m, a, e in engine._funds_targets] == [("HK", 2, "REAL")], "DISABLED 唔入資金輪詢"
    assert engine._order_accs.get("HK") == 2, "下單帳戶 = 唯一 ACTIVE"


def test_setup_funds_targets_cover_both_envs_active_only(monkeypatch):
    """_funds_targets 覆蓋雙 env（REAL + SIMULATE）全部 ACTIVE 帳戶——GUI per-account 資金面板數據源。"""
    ctx = FakeTradeCtx()
    rows = [
        {"acc_id": 1, "trd_env": TrdEnv.REAL, "card_num": "C1",
         "trdmarket_auth": ("HK",), "acc_role": "", "acc_status": "ACTIVE"},
        {"acc_id": 2, "trd_env": "SIMULATE", "card_num": "C2",
         "trdmarket_auth": ("US",), "acc_role": "", "acc_status": "ACTIVE"},
    ]
    ctx.acc_list = (RET_OK, _acc_df(rows))
    _install_ctx_factory(monkeypatch, {"HK": ctx})

    engine = TradeEngine()
    engine._cfg = _cfg(("HK",))
    engine._setup()

    assert [(m, a, e) for m, a, e in engine._funds_targets] == [
        ("HK", 1, "REAL"), ("HK", 2, "SIMULATE")], "雙 env ACTIVE 帳戶都入資金輪詢"


def test_orders_poll_interval_respects_30s_limit():
    """order_list_query 限頻 10 次/30s → 獨立 30s 間隔（注入 _time_fn 確定性測試）。"""
    ctx = FakeTradeCtx()
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)

    orders_events: list = []
    engine.orders_updated.connect(orders_events.append)

    now = [1000.0]
    engine._time_fn = lambda: now[0]

    engine._poll_once()   # 首輪：_last_order_poll=0.0 → 即查
    assert ctx.calls["order_list_query"] == 1, "首輪 poll 應即查訂單"
    assert len(orders_events) == 1

    now[0] = 1029.0       # 30s 內 → 唔查（限頻安全）
    engine._poll_once()
    assert ctx.calls["order_list_query"] == 1, "30s 內唔可再查 order_list_query"
    assert len(orders_events) == 1

    now[0] = 1030.0       # 滿 30s → 再查
    engine._poll_once()
    assert ctx.calls["order_list_query"] == 2
    assert len(orders_events) == 2


def test_place_order_rejected_when_no_order_account():
    """市場已連線但冇可下單帳戶（例如只有 MASTER）→ 明確拒絕、唔 spawn worker。"""
    engine = TradeEngine()
    ctx = FakeTradeCtx()
    _wire_poll_state(engine, ctx, order_acc=False)   # _order_accs 空

    results: list[tuple] = []
    engine.order_result.connect(lambda ok, msg: results.append((ok, msg)))
    engine.place_order("HK.00700", TrdSide.BUY, 10.0, 10)
    assert len(results) == 1, "無下單帳戶 → 立即 emit（direct connection）"
    assert results[0][0] is False and "冇可下單帳戶" in results[0][1]
    assert ctx.calls["place_order"] == 0


# ---------------------------------------------------------------- Commit 35 R2：雙 env 訂單輪詢 + 即時刷新

def test_orders_poll_covers_both_envs():
    """Commit 35 R2：訂單輪詢覆蓋兩個 env（此前 hardcoded REAL——SIMULATE 訂單「下咗單但唔顯示」bug）。"""
    ctx = FakeTradeCtx()

    def order_list_query(trd_env=None, acc_id=None, **kw):
        ctx.calls["order_list_query"] += 1
        env = "REAL" if trd_env == TrdEnv.REAL else "SIMULATE"
        return (RET_OK, [{
            "order_id": f"{env}-1", "code": "HK.00700", "trd_side": "BUY",
            "order_type": "NORMAL", "order_status": "FILLED_ALL", "qty": 200,
            "price": 55.5, "dealt_qty": 200, "dealt_avg_price": 55.4,
            "create_time": "2026-10-02 09:30:00",
        }])

    ctx.order_list_query = order_list_query   # instance attr shadow method（per-env scripted response）
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)
    engine._funds_targets = [("HK", 1, "REAL"), ("HK", 2, "SIMULATE")]

    events: list[tuple] = []
    engine.orders_updated.connect(events.append)
    engine._poll_once()

    assert ctx.calls["order_list_query"] == 2, "每個 (env, acc_id) target 各查一次"
    rows = events[0]
    assert len(rows) == 2
    assert {r.trd_env for r in rows} == {"REAL", "SIMULATE"}


def test_refresh_orders_worker_merges_cache_and_emits_full():
    """Commit 35 R2：下單/撤單成功後即時刷新——重查目標帳戶 → merge 其他帳戶 cache → emit 全量。"""
    ctx = FakeTradeCtx()

    def order_list_query(trd_env=None, acc_id=None, **kw):
        ctx.calls["order_list_query"] += 1
        return (RET_OK, [{
            "order_id": "R-new", "code": "HK.00700", "trd_side": "BUY",
            "order_type": "NORMAL", "order_status": "OPEN", "qty": 200,
            "price": 55.5, "dealt_qty": 0, "dealt_avg_price": 0.0,
            "create_time": "2026-10-02 09:31:00",
        }])

    ctx.order_list_query = order_list_query
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)   # REAL acc 7

    sim_row = OrderRow(order_id="S-old", code="US.AAPL", side="SELL", order_type="NORMAL",
                       status="OPEN", qty=-100.0, price=0.0, dealt_qty=0.0,
                       dealt_avg_price=0.0, create_time="2026-10-02 10:00:00",
                       acc_id=8, trd_env="SIMULATE")

    events: list[tuple] = []
    engine.orders_updated.connect(events.append)
    engine._refresh_orders_worker([("HK", 7, "REAL")], {("SIMULATE", 8): [sim_row]})

    assert ctx.calls["order_list_query"] == 1, "只查目標帳戶（限頻安全）"
    assert engine._orders_cache[("SIMULATE", 8)] == [sim_row], "其他帳戶 cache 保留"
    ids = {r.order_id for r in events[0]}
    assert ids == {"R-new", "S-old"}, "merge 後 emit 全量"


def test_refresh_orders_now_filters_targets_by_env_and_acc(monkeypatch):
    """Commit 35 R2：refresh_orders_now(trd_env, acc_id) → worker 只查匹配 (env, acc_id) 嘅 targets。"""
    captured: dict = {}

    class _FakeThread:
        def __init__(self, target=None, args=(), **kw):
            captured["target"], captured["args"] = target, args

        def start(self):
            pass   # 唔真跑 worker（直接斷言 spawn 參數）

    monkeypatch.setattr(te.threading, "Thread", _FakeThread)

    ctx = FakeTradeCtx()
    engine = TradeEngine()
    _wire_poll_state(engine, ctx)
    engine._funds_targets = [("HK", 7, "REAL"), ("US", 8, "SIMULATE")]
    with engine._lock:
        engine._orders_cache = {("SIMULATE", 8): []}

    engine.refresh_orders_now("SIMULATE")
    assert captured["args"][0] == [("US", 8, "SIMULATE")]

    engine.refresh_orders_now("REAL", acc_id=7)
    assert captured["args"][0] == [("HK", 7, "REAL")]
