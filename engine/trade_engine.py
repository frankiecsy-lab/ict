"""Futu 交易引擎：OpenSecTradeContext per-market contexts + 實倉持倉/資金/訂單輪詢 + 限價下單。

Threading model（鏡像 engine/futu_engine.py）:
- start() spawn daemon setup thread 跑 OpenSecTradeContext / get_acc_list 等阻塞操作；
- setup 成功後啟動 polling loop：每 _POLL_INTERVAL 秒 position_list_query + accinfo_query
  （refresh_cache=False 走 OpenD cache → 無頻率限制風險）；訂單用獨立 _ORDER_POLL_INTERVAL
  間隔（order_list_query 限頻 10 次/30s、refresh_cache=True 保鮮度）；generation counter 防重啟洩漏；
- place_order() GUI-thread entry 只做 sanity check + spawn 短命 daemon worker——
  **所有阻塞 RPC 一律喺 worker thread**，GUI thread 零阻塞；
- 跨線程傳 immutable snapshot（PositionRow / FundsSnapshot / AccountInfo / OrderRow frozen dataclass），auto-queue signal。

SDK 事實（futu_api==10.5.6508，對照本機安裝 source 驗證）:
1. Trading context = OpenSecTradeContext(filter_trdmarket, host, port)——唔係 TrdContext；
   filter_trdmarket 會過濾可見帳戶 → 多市場要一個 context per market。
2. get_acc_list() 返回 **pandas DataFrame**（欄：acc_id/trd_env/acc_type/sim_acc_type/uni_card_num/
   card_num/security_firm/trdmarket_auth(list)/acc_status/acc_role/jp_acc_type）；trd_env 係字串
   （TrdEnv.REAL == "REAL"，FtEnum 值即字串）。
3. position_list_query / accinfo_query / order_list_query **成功時全部返回 pandas DataFrame**——
   `isinstance(data, list)` live 永遠 False（靜默失敗）→ 一律經 `_rows()` normalize。
4. 持倉字段必須用 APP 對齊組：average_cost / unrealized_pl / pl_ratio_avg_cost（已是百分數數字）/
   today_pl_val；cost_price / pl_val / pl_ratio 係攤薄口徑、同 APP 顯示唔符 → 禁用。
5. place_order(price, qty, code, trd_side, acc_id=...) 成功 → (RET_OK, order_id_str)；失敗 → (RET_ERROR, err_msg)。
   MASTER 主帳戶唔可以落單——必須明確傳非 MASTER、且 trdmarket_auth 含目標市場嘅 acc_id。
6. unlock_trade(password) SDK 內部 MD5；頻率限制 **10 次/30s/user ID** → 最多一次 retry、嚴禁循環。
   且要求先拉過 get_acc_list（_setup() 已滿足）。
"""
from __future__ import annotations

import logging
import math
import threading
import time
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from futu import OrderType, RET_OK, OpenSecTradeContext, TrdEnv, TrdMarket, TrdSide

logger = logging.getLogger(__name__)

# 持倉/資金輪詢間隔（秒）——refresh_cache=False 走 OpenD cache，5s 安全
_POLL_INTERVAL = 5.0
# 訂單輪詢間隔（秒）——order_list_query 限頻 10 次/30s → 獨立 30s 間隔 + refresh_cache=True
_ORDER_POLL_INTERVAL = 30.0


def _needs_unlock(msg: str) -> bool:
    """place_order 失敗訊息是否「交易未解鎖」類錯誤（中英雙形態兜底）。"""
    m = msg or ""
    return "解鎖" in m or "unlock" in m.lower()


def _f(value, default: float = 0.0) -> float:
    """SDK 無效字段值（NoneDataValue='N/A' / None / NaN）→ default；有效數 → float。"""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        v = float(value)
        return default if math.isnan(v) else v
    return default


def _s(value) -> str:
    """SDK 字串字段（NoneDataValue='N/A' / None / NaN）→ ''；有效值 → strip 後原字串。"""
    if value is None:
        return ""
    try:
        if isinstance(value, float) and math.isnan(value):
            return ""
    except TypeError:
        pass
    text = str(value).strip()
    return "" if text in ("", "N/A") else text


def _rows(data) -> list[dict]:
    """SDK query 結果 normalize 做 list[dict]。

    futu_api 10.5.x 成功時返回 **pandas DataFrame**——`isinstance(data, list)` live 永遠 False
    （靜默失敗）；DataFrame → to_dict("records")、list → 原樣（測試兼容）、其他 → []。
    """
    if data is None:
        return []
    if hasattr(data, "to_dict"):   # pandas DataFrame
        try:
            return data.to_dict("records")
        except Exception:  # noqa: BLE001 — 異常形態當無數據
            logger.exception("_rows: DataFrame to_dict failed")
            return []
    if isinstance(data, list):
        return data
    return []


@dataclass(frozen=True)
class PositionRow:
    """單筆持倉 immutable snapshot（GUI 渲染用；字段同富途 APP 顯示對齊）。"""

    code: str
    name: str
    market: str
    qty: float
    can_sell_qty: float
    avg_cost: float          # average_cost——實際買入均價（APP「平均成本」）
    last_price: float        # nominal_price——現價
    market_value: float      # market_val——持倉市值
    unrealized_pl: float     # unrealized_pl——按均價計嘅浮動盈虧
    pl_ratio_pct: float      # pl_ratio_avg_cost——已是百分數數字（20 = +20%）
    today_pl: float          # today_pl_val——今日盈虧
    acc_id: int = 0          # 來源帳戶（Commit 31：per-account 持倉過濾用；default 保舊構造相容）
    trd_env: str = "REAL"    # 來源環境 "REAL"/"SIMULATE"（同上）


@dataclass(frozen=True)
class FundsSnapshot:
    """跨帳戶加總嘅資金/訂金 immutable snapshot。"""

    total_assets: float
    cash_hkd: float
    cash_usd: float
    withdraw_hkd: float
    withdraw_usd: float
    buying_power: float
    initial_margin: float
    maintenance_margin: float
    risk_status: str         # LEVEL3=安全 / LEVEL2=警告 / LEVEL1=危險（跨帳戶取最嚴重）


@dataclass(frozen=True)
class AccountInfo:
    """單筆帳戶分類資訊（GUI 帳戶樹用；全 env、按 (trd_env, acc_id) dedupe）。"""

    acc_id: int
    trd_env: str             # REAL / SIMULATE
    acc_type: str            # CASH / MARGIN / STOCK_AND_OPTION ...
    sim_acc_type: str        # COMPETITION = 比賽帳戶，否則 N/A
    uni_card_num: str        # 統一卡號（REAL 帳戶末四位同 APP/桌面端對得上）
    card_num: str
    security_firm: str
    trdmarket_auth: tuple[str, ...]   # 可交易市场列表
    acc_role: str            # MASTER = 主帳戶（唔可以落單）
    acc_status: str


@dataclass(frozen=True)
class OrderRow:
    """單筆訂單 immutable snapshot（GUI 今日訂單表用）。"""

    order_id: str
    code: str
    side: str                # BUY / SELL / SELL_SHORT / BUY_BACK
    order_type: str          # NORMAL / MARKET ...
    status: str              # SUBMITTED / FILLED_ALL ...（OrderStatus 值）
    qty: float
    price: float
    dealt_qty: float
    dealt_avg_price: float
    create_time: str
    acc_id: int = 0          # 來源帳戶（Commit 33：訂單表 per-account 顯示；default 保舊構造相容）


class TradeEngine(QObject):
    """實倉交易引擎：per-market OpenSecTradeContext + 5s 持倉/資金輪詢 + 30s 訂單輪詢 + worker-thread 下單。

    Signals（全部 auto-queue 去 GUI）:
    - accounts_updated(tuple[AccountInfo])：setup 完成後嘅全帳戶分類 snapshot（全 env、dedupe）
    - positions_updated(tuple[PositionRow])：每輪 poll 後嘅全量持倉 snapshot
    - account_funds_updated(object, str, object)：per-account (acc_id, trd_env, FundsSnapshot)——雙 env、ACTIVE only（GUI 端按 env 分組加總；acc_id 參數係 object 唔好 int，見下方註解）
    - orders_updated(tuple[OrderRow])：今日訂單 snapshot（30s 間隔、限頻安全）
    - status(str) / error(str)：連線與操作狀態訊息
    - order_result(bool, str)：(success, message)——下單結果（worker thread emit）
    - cancel_result(bool, str)：(success, message)——撤單結果（worker thread emit）
    """

    accounts_updated = Signal(tuple)
    positions_updated = Signal(tuple)
    # acc_id 用 object（唔好 int）：富途 acc_id 係 18 位 snowflake ID（~2.8e17），超出 PySide6 Signal(int)
    # 嘅 C 4-byte signed int 上限（2^31-1）→ shiboken OverflowError + emit 靜默失效（Commit 32 live bug）。
    account_funds_updated = Signal(object, str, object)  # (acc_id: int, trd_env "REAL"/"SIMULATE", FundsSnapshot)——per-account、雙 env、ACTIVE only
    orders_updated = Signal(tuple)
    status = Signal(str)
    error = Signal(str)
    order_result = Signal(bool, str)
    cancel_result = Signal(bool, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cfg = None
        self._ctxs: dict[str, OpenSecTradeContext] = {}      # {market → ctx}
        self._accounts: dict[str, list[tuple[int, str]]] = {}  # {market → [(acc_id, card_num)]} REAL + ACTIVE only（持倉/訂單輪詢）
        self._funds_targets: list[tuple[str, int, str]] = []   # [(market, acc_id, trd_env_str)]：雙 env、ACTIVE only（資金 per-account 輪詢，(env,acc_id) dedupe）
        self._order_accs: dict[str, int] = {}                 # {market → 可下單 acc_id}：非 MASTER + trdmarket_auth 含該市場
        self._all_accounts: list[AccountInfo] = []            # 全帳戶 dedupe（分類面板）
        self._thread: threading.Thread | None = None         # setup thread
        self._workers: list[threading.Thread] = []           # order worker threads（stop() join 晒）
        self._poll_thread: threading.Thread | None = None    # polling loop thread
        self._poll_stop = threading.Event()                  # stop()/supersede → 喚醒 poll loop 退出
        self._poll_gen = 0                                   # generation counter：重啟後舊 thread 自然退出
        self._closed = False                                 # stop() 後抑制 emit / reject order
        self._lock = threading.Lock()
        self._time_fn = time.time                            # 可注入 clock（訂單輪詢間隔測試）
        self._last_order_poll = 0.0                          # 初始化 0 → 首輪 poll 即查訂單

    @property
    def cfg(self):
        return self._cfg

    # ------------------------------------------------------------- lifecycle

    def start(self, cfg) -> None:
        """啟動 per-market trading contexts + 持倉/資金/訂單輪詢（背景 daemon thread，立即返回）。"""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return  # 已經 starting/started
            self._closed = False
            self._cfg = cfg
            self._ctxs.clear()          # restart-safe：清舊 state（stop() 後重啟唔會累積重複帳戶）
            self._accounts.clear()
            self._funds_targets.clear()
            self._order_accs.clear()
            self._all_accounts.clear()
            self._last_order_poll = 0.0
            thread = threading.Thread(target=self._setup, name="trade-setup", daemon=True)
            self._thread = thread
        thread.start()

    def stop(self) -> None:
        """Idempotent 關閉：set _closed、停 poll loop、join setup + order workers、close 所有 ctxs。"""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            workers = list(self._workers)
            self._workers.clear()
            thread = self._thread
            self._thread = None
            poll_thread = self._poll_thread
            self._poll_thread = None
        self._poll_stop.set()   # 喚醒 poll loop（若喺 wait）→ 下輪偵測退出
        for t in (thread, *workers):
            if t is not None and t.is_alive():
                t.join(timeout=10)
        if poll_thread is not None and poll_thread.is_alive():
            poll_thread.join(timeout=5)
        self._close_ctxs()

    def _close_ctxs(self) -> None:
        """Close 所有 market contexts（idempotent；exception 只 log）。"""
        for market, ctx in list(self._ctxs.items()):
            try:
                ctx.close()
            except Exception:  # noqa: BLE001 — shutdown path，唔 propagate
                logger.exception("close %s trade context failed", market)
        self._ctxs.clear()

    # ------------------------------------------------------------- setup（daemon thread）

    def _setup(self) -> None:
        """逐市場建 OpenSecTradeContext + get_acc_list 收集全部帳戶；成功後啟動 poll loop。"""
        cfg = self._cfg
        if cfg is None or self._closed:
            return
        self.status.emit("連線 OpenD 交易服務中…")
        seen: set[tuple[str, int]] = set()   # (trd_env, acc_id) dedupe——同一帳戶可出現喺多個市場 context
        for market in cfg.trd_markets:
            if self._closed:
                return
            mkt_enum = getattr(TrdMarket, market, None)
            if mkt_enum is None or mkt_enum == TrdMarket.NONE:
                self.error.emit(f"未知市場 {market!r}（TRD_MARKETS 可選：HK/US/CN/JP…）")
                continue
            try:
                ctx = OpenSecTradeContext(
                    filter_trdmarket=mkt_enum, host=cfg.opend_host, port=cfg.opend_port)
            except Exception as exc:  # noqa: BLE001 — 單市場失敗唔影響其他市場
                logger.exception("create %s trade context failed", market)
                self.error.emit(f"{market} 市場連線失敗：{exc}")
                continue
            try:
                ret, data = ctx.get_acc_list()
            except Exception as exc:  # noqa: BLE001 — OpenD 未就緒 / 斷線
                logger.exception("get_acc_list (%s) failed", market)
                self.error.emit(f"{market} 市場帳戶查詢失敗：{exc}")
                try:
                    ctx.close()
                except Exception:  # noqa: BLE001
                    pass
                continue
            if ret != RET_OK or data is None:
                msg = str(data) if data is not None else "未知錯誤"
                self.error.emit(f"{market} 市場帳戶查詢失敗：{msg}")
                try:
                    ctx.close()
                except Exception:  # noqa: BLE001
                    pass
                continue
            real_accounts: list[tuple[int, str]] = []
            for _, row in data.iterrows():
                acc_id = int(row.acc_id)
                env = str(row.trd_env)
                key = (env, acc_id)
                active = _s(getattr(row, "acc_status", "")) == "ACTIVE"  # SDK: ACTIVE / DISABLED / N/A——只保留 ACTIVE
                if key not in seen:
                    seen.add(key)
                    self._all_accounts.append(_account_info_from_row(acc_id, row))
                    if active:
                        # 首個發現嘅 market 決定用邊個 ctx；seen dedupe 保證 (env, acc_id) 只入一次
                        self._funds_targets.append((market, acc_id, env))
                if env == TrdEnv.REAL and active:
                    real_accounts.append((acc_id, str(row.card_num)))
            with self._lock:
                self._ctxs[market] = ctx
                self._accounts[market] = real_accounts
        total_accs = sum(len(v) for v in self._accounts.values())
        if self._closed:
            return
        # per-market 下單帳戶選擇：首個非 MASTER、REAL、且 trdmarket_auth 含該市場嘅帳戶（MASTER 主帳戶唔可以落單）
        by_id = {a.acc_id: a for a in self._all_accounts}
        for market, accs in self._accounts.items():
            for acc_id, _card in accs:
                info = by_id.get(acc_id)
                if info is None or info.trd_env != TrdEnv.REAL:
                    continue
                if info.acc_status != "ACTIVE":   # 防禦性：_accounts 上游已過濾，此處雙保險
                    continue
                if info.acc_role == "MASTER":
                    continue
                if market not in info.trdmarket_auth:
                    continue
                self._order_accs[market] = acc_id
                break
        # 分類面板永遠 emit（即使零 REAL——只讀模式下 SIMULATE/比賽帳戶都要可見）
        if self._all_accounts:
            self.accounts_updated.emit(tuple(self._all_accounts))
        if total_accs == 0:
            self.status.emit("未找到實倉（REAL）帳戶——下單版面只讀顯示，無法下單")
            return
        markets = ", ".join(sorted(self._ctxs))
        self.status.emit(f"已連線：{total_accs} 個實倉帳戶（市場：{markets}）")
        self._start_poll_loop()

    # ------------------------------------------------------------- polling loop

    def _start_poll_loop(self) -> None:
        """啟動持倉/資金 poll thread；generation counter 防重啟洩漏（鏡像 _ping_loop）。"""
        with self._lock:
            if self._closed:
                return
            self._poll_gen += 1
            gen = self._poll_gen
            self._poll_stop.clear()
            thread = threading.Thread(target=self._poll_loop, args=(gen,), name="trade-poll", daemon=True)
            self._poll_thread = thread
        thread.start()

    def _poll_loop(self, gen: int) -> None:
        """定時 poll loop：每輪 position_list_query + accinfo_query → emit snapshots。

        退出條件：stop()（_poll_stop set / _closed）或被新 poll loop supersede（gen mismatch）。
        """
        while not self._poll_stop.is_set():
            if gen != self._poll_gen or self._closed:
                break
            self._poll_once()
            self._poll_stop.wait(_POLL_INTERVAL)

    def _poll_once(self) -> None:
        """單輪 poll：持倉 per-account（雙 env、ACTIVE，Commit 31）；資金 per-account 獨立 emit；訂單按獨立 30s 間隔查。

        每次查詢獨立 try/except（單筆失敗唔殺整輪）。
        """
        # 持倉輪詢：per-account、雙 env（Commit 31——重用 _funds_targets，同 funds loop 同一來源；
        # position_list_query 無文檔限頻 → 5s polling 安全）。每行 tag (acc_id, trd_env) 供 GUI 過濾。
        positions: list[PositionRow] = []
        for market, acc_id, trd_env in self._funds_targets:
            ctx = self._ctxs.get(market)
            if ctx is None:
                continue
            rows = self._query_positions(ctx, acc_id, trd_env)
            positions.extend(rows)
        # 資金輪詢：per-account、雙 env（accinfo_query 無文檔限頻）；逐個 emit，失敗帳戶跳過（GUI 保留上次值）
        for market, acc_id, trd_env in self._funds_targets:
            ctx = self._ctxs.get(market)
            if ctx is None:
                continue
            info = self._query_funds(ctx, acc_id, trd_env)
            if info is not None and not self._closed:
                self.account_funds_updated.emit(acc_id, trd_env, info)
        # 訂單輪詢：獨立 30s 間隔（order_list_query 限頻 10 次/30s）；首輪即查（_last_order_poll=0.0）
        if self._time_fn() - self._last_order_poll >= _ORDER_POLL_INTERVAL:
            self._last_order_poll = self._time_fn()
            orders: list[OrderRow] = []
            for market in sorted(self._ctxs):
                ctx = self._ctxs.get(market)
                if ctx is None:
                    continue
                for acc_id, _card in self._accounts.get(market, ()):
                    orders.extend(self._query_orders(ctx, acc_id))
            if not self._closed:
                self.orders_updated.emit(tuple(orders))
        if self._closed:
            return   # emit 前最後一道防線（stop() 已 set _closed）
        self.positions_updated.emit(tuple(positions))

    # ------------------------------------------------------------- queries（poll thread 內）

    def _query_positions(self, ctx, acc_id: int, trd_env: str = "REAL") -> list[PositionRow]:
        """position_list_query → [PositionRow]；失敗/無數據 → []。字段用 APP 對齊組（FIELD_MAPPING）。

        Commit 31：trd_env 參數化（雙 env per-account polling）+ 每行 tag (acc_id, trd_env)——
        GUI 端按選中帳戶卡片過濾持倉表。
        """
        env_enum = TrdEnv.REAL if trd_env == "REAL" else TrdEnv.SIMULATE
        try:
            ret, data = ctx.position_list_query(trd_env=env_enum, acc_id=acc_id, refresh_cache=False)
        except Exception as exc:  # noqa: BLE001 — 單筆查詢失敗唔殺整輪 poll
            logger.exception("position_list_query failed (acc=%s)", acc_id)
            return []
        if ret != RET_OK:
            return []
        out = []
        for row in _rows(data):
            try:
                out.append(PositionRow(
                    code=str(row.get("code", "")),
                    name=_s(row.get("stock_name")),
                    market=_s(row.get("position_market")),
                    qty=_f(row.get("qty")),
                    can_sell_qty=_f(row.get("can_sell_qty")),
                    avg_cost=_f(row.get("average_cost")),          # APP「平均成本」（禁用攤薄 cost_price）
                    last_price=_f(row.get("nominal_price")),
                    market_value=_f(row.get("market_val")),
                    unrealized_pl=_f(row.get("unrealized_pl")),    # 按均價計浮動盈虧（禁用 pl_val）
                    pl_ratio_pct=_f(row.get("pl_ratio_avg_cost")),   # 已是百分數數字，唔好再 ×100
                    today_pl=_f(row.get("today_pl_val")),
                    acc_id=acc_id,
                    trd_env=trd_env,
                ))
            except Exception:  # noqa: BLE001 — 單行損壞跳過
                logger.exception("bad position row skipped")
        return out

    def _query_funds(self, ctx, acc_id: int, trd_env: str) -> FundsSnapshot | None:
        """accinfo_query → 單帳戶 FundsSnapshot；失敗/無數據 → None。trd_env = "REAL"/"SIMULATE"（顯式映射 enum）。"""
        env_enum = TrdEnv.REAL if trd_env == "REAL" else TrdEnv.SIMULATE
        try:
            ret, data = ctx.accinfo_query(trd_env=env_enum, acc_id=acc_id, refresh_cache=False)
        except Exception as exc:  # noqa: BLE001 — 單筆查詢失敗唔殺整輪 poll
            logger.exception("accinfo_query failed (acc=%s)", acc_id)
            return None
        if ret != RET_OK:
            return None
        rows = _rows(data)
        if not rows:
            return None
        info = rows[0]   # 普通證券帳戶：首行含晒 hk_*/us_* 子字段
        return FundsSnapshot(
            total_assets=_f(info.get("total_assets")),
            cash_hkd=_f(info.get("hk_cash")),
            cash_usd=_f(info.get("us_cash")),
            withdraw_hkd=_f(info.get("hk_avl_withdrawal_cash")),
            withdraw_usd=_f(info.get("us_avl_withdrawal_cash")),
            buying_power=_f(info.get("power")),
            initial_margin=_f(info.get("initial_margin")),
            maintenance_margin=_f(info.get("maintenance_margin")),
            risk_status=_s(info.get("risk_status")),   # LEVEL3=安全 / LEVEL2=警告 / LEVEL1=危險
        )

    def _query_orders(self, ctx, acc_id: int) -> list[OrderRow]:
        """order_list_query（無 start/end = 今日訂單）→ [OrderRow]；失敗/無數據 → []。"""
        try:
            ret, data = ctx.order_list_query(trd_env=TrdEnv.REAL, acc_id=acc_id, refresh_cache=True)
        except Exception as exc:  # noqa: BLE001 — 單筆查詢失敗唔殺整輪 poll
            logger.exception("order_list_query failed (acc=%s)", acc_id)
            return []
        if ret != RET_OK:
            return []
        out = []
        for row in _rows(data):
            try:
                out.append(OrderRow(
                    order_id=_s(row.get("order_id")),
                    code=str(row.get("code", "")),
                    side=_s(row.get("trd_side")),
                    order_type=_s(row.get("order_type")),
                    status=_s(row.get("order_status")),
                    qty=_f(row.get("qty")),
                    price=_f(row.get("price")),
                    dealt_qty=_f(row.get("dealt_qty")),
                    dealt_avg_price=_f(row.get("dealt_avg_price")),
                    create_time=_s(row.get("create_time")),
                    acc_id=acc_id,
                ))
            except Exception:  # noqa: BLE001 — 單行損壞跳過
                logger.exception("bad order row skipped")
        return out

    # ------------------------------------------------------------- place order（worker thread）

    def place_order(self, code: str, side: TrdSide, price: float, qty: int, pin: str | None = None,
                    *, trd_env: str = "REAL", acc_id: int | None = None, market: bool = False) -> None:
        """GUI-thread entry：sanity check + spawn 短命 daemon worker（阻塞 RPC 唔喺 GUI thread）。

        Commit 33：`trd_env`/`acc_id` keyword-only——UI 端按「模式選擇器 + 標的種類自動匹配帳戶」
        明確指定目標；兩者都省略時 fallback 舊行為（REAL + `_order_accs[market]`）。
        Commit 34：`market=True` → 市價單（order_type=OrderType.MARKET、price=0）——平倉操作用。
        """
        with self._lock:
            if self._closed:
                self.order_result.emit(False, "引擎已關閉，無法下單")
                return
            mkt = code.split(".", 1)[0].upper() if "." in code else ""
            ctx = self._ctxs.get(mkt)
            target_acc = acc_id if acc_id is not None else self._order_accs.get(mkt)
        if ctx is None:
            configured = ", ".join(sorted(self._ctxs)) or "（無）"
            self.order_result.emit(False, f"市場 {mkt!r} 未連線（已配置：{configured}）")
            return
        if target_acc is None:
            env_zh = "實盤" if trd_env == "REAL" else "模擬盤"
            self.order_result.emit(
                False, f"{env_zh} {mkt!r} 冇可下單帳戶——需非 MASTER ACTIVE 帳戶且 trdmarket_auth 含 {mkt}")
            return
        thread = threading.Thread(
            target=self._order_worker, args=(ctx, target_acc, code, side, price, qty, pin, trd_env, market),
            name="trade-order", daemon=True)
        with self._lock:
            if self._closed:   # double-check：spawn 前一刻 stop() 咗
                self.order_result.emit(False, "引擎已關閉，無法下單")
                return
            self._workers.append(thread)
        thread.start()

    def _order_worker(self, ctx, acc_id: int, code: str, side: TrdSide, price: float, qty: int, pin: str | None,
                      trd_env: str = "REAL", market: bool = False) -> None:
        """阻塞 place_order（明確 acc_id + env）；「未解鎖」錯誤 + 有 PIN → unlock_trade 一次 + retry 一次（30s/10 次限制，無循環）。

        Commit 33：`trd_env` = "REAL"/"SIMULATE"——模擬盤無需交易密碼（futu 規則），pin 自然為 None。
        Commit 34：`market=True` → OrderType.MARKET + price=0（市價單，平倉操作用）。
        """
        env_enum = TrdEnv.REAL if trd_env == "REAL" else TrdEnv.SIMULATE
        order_kw: dict = {"code": code, "trd_side": side, "acc_id": acc_id, "trd_env": env_enum}
        if market:
            order_kw.update(price=0, order_type=OrderType.MARKET)   # 市價單：price 無意義（傳 0）
        else:
            order_kw["price"] = price                               # 限價單（默認 OrderType.NORMAL）
        try:
            ret, msg = ctx.place_order(qty=qty, **order_kw)
            if ret == RET_OK and not _needs_unlock(str(msg)):
                self.order_result.emit(True, f"下單成功 order_id={msg}")
                return
            err = str(msg)
            if pin is not None and _needs_unlock(err):
                uret, umsg = ctx.unlock_trade(pin)
                if uret != RET_OK:
                    self.order_result.emit(False, f"解鎖失敗：{umsg}")
                    return
                ret2, msg2 = ctx.place_order(qty=qty, **order_kw)
                if ret2 == RET_OK and not _needs_unlock(str(msg2)):
                    self.order_result.emit(True, f"下單成功（解鎖後重試）order_id={msg2}")
                else:
                    self.order_result.emit(False, f"解鎖後重試失敗：{msg2}")
            elif pin is None and _needs_unlock(err):
                self.order_result.emit(False, "交易未解鎖——請輸入六位數 PIN 並撳「解鎖」")
            else:
                self.order_result.emit(False, err)
        except Exception as exc:  # noqa: BLE001 — worker exception 絕唔 crash engine
            logger.exception("place_order worker failed (code=%s)", code)
            self.order_result.emit(False, f"下單異常：{exc}")

    # ------------------------------------------------------------- cancel order（worker thread）

    def cancel_order(self, order_id: str, code: str, *, trd_env: str = "REAL", acc_id: int | None = None) -> None:
        """GUI-thread entry：撤單 sanity check + spawn 短命 daemon worker。

        Commit 34：`order_id`/`code` 由 UI 訂單表行提供（row.acc_id / row.trd_env）；
        `acc_id=None` fallback `_order_accs[market]`（同 place_order）。結果經 `cancel_result` emit。
        """
        with self._lock:
            if self._closed:
                self.cancel_result.emit(False, "引擎已關閉，無法撤單")
                return
            market = code.split(".", 1)[0].upper() if "." in code else ""
            ctx = self._ctxs.get(market)
            target_acc = acc_id if acc_id is not None else self._order_accs.get(market)
        if ctx is None:
            configured = ", ".join(sorted(self._ctxs)) or "（無）"
            self.cancel_result.emit(False, f"市場 {market!r} 未連線（已配置：{configured}）")
            return
        if target_acc is None:
            env_zh = "實盤" if trd_env == "REAL" else "模擬盤"
            self.cancel_result.emit(
                False, f"{env_zh} {market!r} 冇可下單帳戶——需非 MASTER ACTIVE 帳戶且 trdmarket_auth 含 {market}")
            return
        thread = threading.Thread(
            target=self._cancel_worker, args=(ctx, target_acc, order_id), kwargs={"trd_env": trd_env},
            name="trade-cancel", daemon=True)
        with self._lock:
            if self._closed:   # double-check：spawn 前一刻 stop() 咗
                self.cancel_result.emit(False, "引擎已關閉，無法撤單")
                return
            self._workers.append(thread)
        thread.start()

    def _cancel_worker(self, ctx, acc_id: int, order_id: str, *, trd_env: str = "REAL") -> None:
        """阻塞 cancel_order（明確 acc_id + env）；結果經 `cancel_result` emit。"""
        env_enum = TrdEnv.REAL if trd_env == "REAL" else TrdEnv.SIMULATE
        try:
            ret, msg = ctx.cancel_order(order_id=order_id, acc_id=acc_id, trd_env=env_enum)
            if ret == RET_OK:
                self.cancel_result.emit(True, f"撤單成功 order_id={order_id}")
            else:
                self.cancel_result.emit(False, str(msg))
        except Exception as exc:  # noqa: BLE001 — worker exception 絕唔 crash engine
            logger.exception("cancel_order worker failed (order_id=%s)", order_id)
            self.cancel_result.emit(False, f"撤單異常：{exc}")


def _account_info_from_row(acc_id: int, row) -> AccountInfo:
    """get_acc_list DataFrame row → AccountInfo（trdmarket_auth 兼容 list / comma-str 雙形態）。"""
    auth = getattr(row, "trdmarket_auth", None) or []
    if isinstance(auth, str):
        auth = [m.strip() for m in auth.split(",") if m.strip()]
    return AccountInfo(
        acc_id=acc_id,
        trd_env=str(row.trd_env),
        acc_type=_s(getattr(row, "acc_type", "")),
        sim_acc_type=_s(getattr(row, "sim_acc_type", "")),
        uni_card_num=_s(getattr(row, "uni_card_num", "")),
        card_num=_s(getattr(row, "card_num", "")),
        security_firm=_s(getattr(row, "security_firm", "")),
        trdmarket_auth=tuple(str(m) for m in auth),
        acc_role=_s(getattr(row, "acc_role", "")),
        acc_status=_s(getattr(row, "acc_status", "")),
    )


# LEVEL1=危險 最嚴重；空字串 = 無資訊（severity 0）
_RISK_SEVERITY = {"LEVEL1": 3, "LEVEL2": 2, "LEVEL3": 1}


def _sum_funds(a: FundsSnapshot, b: FundsSnapshot) -> FundsSnapshot:
    """跨帳戶加總資金 snapshot；risk_status 取兩者較嚴重（空 = 無資訊）。"""
    risk = a.risk_status if _RISK_SEVERITY.get(a.risk_status, 0) >= _RISK_SEVERITY.get(b.risk_status, 0) else b.risk_status
    return FundsSnapshot(
        total_assets=a.total_assets + b.total_assets,
        cash_hkd=a.cash_hkd + b.cash_hkd,
        cash_usd=a.cash_usd + b.cash_usd,
        withdraw_hkd=a.withdraw_hkd + b.withdraw_hkd,
        withdraw_usd=a.withdraw_usd + b.withdraw_usd,
        buying_power=a.buying_power + b.buying_power,
        initial_margin=a.initial_margin + b.initial_margin,
        maintenance_margin=a.maintenance_margin + b.maintenance_margin,
        risk_status=risk,
    )
