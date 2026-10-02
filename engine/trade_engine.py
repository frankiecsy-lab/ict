"""Futu 交易引擎：OpenSecTradeContext per-market contexts + 實倉持倉/資金輪詢 + 限價下單。

Threading model（鏡像 engine/futu_engine.py）:
- start() spawn daemon setup thread 跑 OpenSecTradeContext / get_acc_list 等阻塞操作；
- setup 成功後啟動 polling loop（每 _POLL_INTERVAL 秒 position_list_query + accinfo_query，
  refresh_cache=False 走 OpenD cache → 無頻率限制風險）；generation counter 防重啟洩漏；
- place_order() GUI-thread entry 只做 sanity check + spawn 短命 daemon worker——
  **所有阻塞 RPC 一律喺 worker thread**，GUI thread 零阻塞；
- 跨線程傳 immutable snapshot（PositionRow / FundsSnapshot frozen dataclass），auto-queue signal。

SDK 事實（futu_api==10.5.6508，實測驗證）:
1. Trading context = OpenSecTradeContext(filter_trdmarket, host, port)——唔係 TrdContext；
   filter_trdmarket 會過濾可見帳戶 → 多市場要一個 context per market。
2. get_acc_list() 返回 **pandas DataFrame**（欄：acc_id/trd_env/card_num/...）；trd_env 係字串
   （TrdEnv.REAL == "REAL"，FtEnum 值即字串）。
3. position_list_query / accinfo_query 返回 (ret, msg)——成功時 msg = list[dict]（唔係 DataFrame）；
   無效字段值 = NoneDataValue 字串 'N/A'。pl_ratio **已是百分數數字**（100 × proto plRatio）。
4. place_order(price, qty, code, trd_side) 成功 → (RET_OK, order_id_str)；失敗 → (RET_ERROR, err_msg)。
5. unlock_trade(password) SDK 內部 MD5；頻率限制 **10 次/30s/user ID** → 最多一次 retry、嚴禁循環。
   且要求先拉過 get_acc_list（_setup() 已滿足）。
"""
from __future__ import annotations

import logging
import math
import threading
import time
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from futu import RET_OK, OpenSecTradeContext, TrdEnv, TrdMarket, TrdSide

logger = logging.getLogger(__name__)

# 持倉/資金輪詢間隔（秒）——refresh_cache=False 走 OpenD cache，5s 安全
_POLL_INTERVAL = 5.0


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


@dataclass(frozen=True)
class PositionRow:
    """單筆持倉 immutable snapshot（GUI 渲染用）。"""

    code: str
    name: str
    market: str
    qty: float
    can_sell_qty: float
    cost_price: float
    last_price: float
    market_value: float
    pl_val: float
    pl_ratio_pct: float   # 已是百分數數字（20 = +20%）


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


class TradeEngine(QObject):
    """實倉交易引擎：per-market OpenSecTradeContext + 5s 持倉/資金輪詢 + worker-thread 下單。

    Signals（全部 auto-queue 去 GUI）:
    - positions_updated(tuple[PositionRow])：每輪 poll 後嘅全量持倉 snapshot
    - funds_updated(FundsSnapshot)：跨帳戶加總資金/訂金
    - status(str) / error(str)：連線與操作狀態訊息
    - order_result(bool, str)：(success, message)——下單結果（worker thread emit）
    """

    positions_updated = Signal(tuple)
    funds_updated = Signal(object)
    status = Signal(str)
    error = Signal(str)
    order_result = Signal(bool, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cfg = None
        self._ctxs: dict[str, OpenSecTradeContext] = {}      # {market → ctx}
        self._accounts: dict[str, list[tuple[int, str]]] = {}  # {market → [(acc_id, card_num)]} REAL only
        self._thread: threading.Thread | None = None         # setup thread
        self._workers: list[threading.Thread] = []           # order worker threads（stop() join 晒）
        self._poll_thread: threading.Thread | None = None    # polling loop thread
        self._poll_stop = threading.Event()                  # stop()/supersede → 喚醒 poll loop 退出
        self._poll_gen = 0                                   # generation counter：重啟後舊 thread 自然退出
        self._closed = False                                 # stop() 後抑制 emit / reject order
        self._lock = threading.Lock()

    @property
    def cfg(self):
        return self._cfg

    # ------------------------------------------------------------- lifecycle

    def start(self, cfg) -> None:
        """啟動 per-market trading contexts + 持倉/資金輪詢（背景 daemon thread，立即返回）。"""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return  # 已經 starting/started
            self._closed = False
            self._cfg = cfg
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
        """逐市場建 OpenSecTradeContext + get_acc_list 過濾 REAL 帳戶；成功後啟動 poll loop。"""
        cfg = self._cfg
        if cfg is None or self._closed:
            return
        self.status.emit("連線 OpenD 交易服務中…")
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
            real_accounts = [
                (int(row.acc_id), str(row.card_num))
                for _, row in data.iterrows() if row.trd_env == TrdEnv.REAL
            ]
            with self._lock:
                self._ctxs[market] = ctx
                self._accounts[market] = real_accounts
        total_accs = sum(len(v) for v in self._accounts.values())
        if self._closed:
            return
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
        """單輪 poll：逐 (market, account) 查持倉 + 資金；每次查詢獨立 try/except（單筆失敗唔殺整輪）。"""
        positions: list[PositionRow] = []
        funds = FundsSnapshot(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        got_funds = False
        for market in sorted(self._ctxs):
            ctx = self._ctxs.get(market)
            if ctx is None:
                continue
            for acc_id, _card in self._accounts.get(market, ()):
                rows = self._query_positions(ctx, acc_id)
                positions.extend(rows)
                info = self._query_funds(ctx, acc_id)
                if info is not None:
                    funds = _sum_funds(funds, info)
                    got_funds = True
        if self._closed:
            return   # emit 前最後一道防線（stop() 已 set _closed）
        self.positions_updated.emit(tuple(positions))
        if got_funds:
            self.funds_updated.emit(funds)

    # ------------------------------------------------------------- queries（poll thread 內）

    def _query_positions(self, ctx, acc_id: int) -> list[PositionRow]:
        """position_list_query → [PositionRow]；失敗/無數據 → []。"""
        try:
            ret, data = ctx.position_list_query(trd_env=TrdEnv.REAL, acc_id=acc_id, refresh_cache=False)
        except Exception as exc:  # noqa: BLE001 — 單筆查詢失敗唔殺整輪 poll
            logger.exception("position_list_query failed (acc=%s)", acc_id)
            return []
        if ret != RET_OK or not isinstance(data, list):
            return []
        out = []
        for row in data:
            try:
                out.append(PositionRow(
                    code=str(row.get("code", "")),
                    name=str(row.get("stock_name", "") or ""),
                    market=str(row.get("position_market", "") or ""),
                    qty=_f(row.get("qty")),
                    can_sell_qty=_f(row.get("can_sell_qty")),
                    cost_price=_f(row.get("cost_price")),
                    last_price=_f(row.get("nominal_price")),
                    market_value=_f(row.get("market_val")),
                    pl_val=_f(row.get("pl_val")),
                    pl_ratio_pct=_f(row.get("pl_ratio")),   # 已是百分數數字，唔好再 ×100
                ))
            except Exception:  # noqa: BLE001 — 單行損壞跳過
                logger.exception("bad position row skipped")
        return out

    def _query_funds(self, ctx, acc_id: int) -> FundsSnapshot | None:
        """accinfo_query → 單帳戶 FundsSnapshot；失敗/無數據 → None。"""
        try:
            ret, data = ctx.accinfo_query(trd_env=TrdEnv.REAL, acc_id=acc_id, refresh_cache=False)
        except Exception as exc:  # noqa: BLE001 — 單筆查詢失敗唔殺整輪 poll
            logger.exception("accinfo_query failed (acc=%s)", acc_id)
            return None
        if ret != RET_OK or not isinstance(data, list) or not data:
            return None
        info = data[0]   # 普通證券帳戶：首行含晒 hk_*/us_* 子字段
        return FundsSnapshot(
            total_assets=_f(info.get("total_assets")),
            cash_hkd=_f(info.get("hk_cash")),
            cash_usd=_f(info.get("us_cash")),
            withdraw_hkd=_f(info.get("hk_avl_withdrawal_cash")),
            withdraw_usd=_f(info.get("us_avl_withdrawal_cash")),
            buying_power=_f(info.get("power")),
            initial_margin=_f(info.get("initial_margin")),
            maintenance_margin=_f(info.get("maintenance_margin")),
        )

    # ------------------------------------------------------------- place order（worker thread）

    def place_order(self, code: str, side: TrdSide, price: float, qty: int, pin: str | None = None) -> None:
        """GUI-thread entry：sanity check + spawn 短命 daemon worker（阻塞 RPC 唔喺 GUI thread）。"""
        with self._lock:
            if self._closed:
                self.order_result.emit(False, "引擎已關閉，無法下單")
                return
            market = code.split(".", 1)[0].upper() if "." in code else ""
            ctx = self._ctxs.get(market)
        if ctx is None:
            configured = ", ".join(sorted(self._ctxs)) or "（無）"
            self.order_result.emit(False, f"市場 {market!r} 未連線（已配置：{configured}）")
            return
        thread = threading.Thread(
            target=self._order_worker, args=(ctx, code, side, price, qty, pin),
            name="trade-order", daemon=True)
        with self._lock:
            if self._closed:   # double-check：spawn 前一刻 stop() 咗
                self.order_result.emit(False, "引擎已關閉，無法下單")
                return
            self._workers.append(thread)
        thread.start()

    def _order_worker(self, ctx, code: str, side: TrdSide, price: float, qty: int, pin: str | None) -> None:
        """阻塞 place_order；「未解鎖」錯誤 + 有 PIN → unlock_trade 一次 + retry 一次（30s/10 次限制，無循環）。"""
        try:
            ret, msg = ctx.place_order(price=price, qty=qty, code=code, trd_side=side)
            if ret == RET_OK and not _needs_unlock(str(msg)):
                self.order_result.emit(True, f"下單成功 order_id={msg}")
                return
            err = str(msg)
            if pin is not None and _needs_unlock(err):
                uret, umsg = ctx.unlock_trade(pin)
                if uret != RET_OK:
                    self.order_result.emit(False, f"解鎖失敗：{umsg}")
                    return
                ret2, msg2 = ctx.place_order(price=price, qty=qty, code=code, trd_side=side)
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


def _sum_funds(a: FundsSnapshot, b: FundsSnapshot) -> FundsSnapshot:
    """跨帳戶加總資金 snapshot。"""
    return FundsSnapshot(
        total_assets=a.total_assets + b.total_assets,
        cash_hkd=a.cash_hkd + b.cash_hkd,
        cash_usd=a.cash_usd + b.cash_usd,
        withdraw_hkd=a.withdraw_hkd + b.withdraw_hkd,
        withdraw_usd=a.withdraw_usd + b.withdraw_usd,
        buying_power=a.buying_power + b.buying_power,
        initial_margin=a.initial_margin + b.initial_margin,
        maintenance_margin=a.maintenance_margin + b.maintenance_margin,
    )
