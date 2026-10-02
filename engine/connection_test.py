"""OpenD 連線測試（Commit 35）：報價 / 交易端點兩段式輕量檢查。

- Stage 1：raw TCP socket pre-check——快速失敗（host/port 錯、OpenD 未啟動），
  唔會建立 SDK context；
- Stage 2：協議層握手驗證 + 登入狀態回報（server_ver / qot_logined / trd_logined）。

⚠️ 關鍵坑（對照安裝 futu-api source `common/open_context_base.py` 驗證）：
1. `OpenContextBase.__init__` 喺連唔到時進入 **`while True` 無限重試**（每 6s sleep）→
   同步構造 context 喺死端點會**永久阻塞**；
2. 只有 `OpenQuoteContext` expose `is_async_connect` 參數——安裝 SDK 嘅
   `OpenSecTradeContext.__init__` **唔接受佢**（傳入 → TypeError: unexpected keyword
   argument）→ trade kind 只能「TCP pre-check + timeout 包 sync 構造」兜底。

⚠️ SDK **冇** `test_connect()` API（已 grep 安裝版本確認）——最輕量嘅健康檢查
就係 `get_global_state()`（同 FutuEngine ping loop 同一個 API，AGENTS.md #15）。

阻塞函數——必須喺 worker thread 調用，嚴禁 GUI thread 直接 call。
"""
from __future__ import annotations

import logging
import socket
import threading

logger = logging.getLogger(__name__)

_TCP_TIMEOUT_S = 5.0
# trade kind sync 構造超時（秒）——TCP pre-check 已保證端口可達，呢度兜「TCP 開住但唔係 OpenD」邊界
_TRADE_CONNECT_TIMEOUT_S = 15.0
# engine 連線前重試間隔（秒）——FutuEngine / TradeEngine _setup() TCP fast-fail 後自動重試到 OpenD 起或 stop()
CONNECT_RETRY_INTERVAL_S = 5.0


def tcp_reachable(host: str, port: int) -> tuple[bool, str]:
    """Stage-1 raw TCP reachability check（快速失敗）。

    :return: (ok, message)——失敗時 message 含實際 host:port 同異常資訊；
      FutuEngine / TradeEngine 連線前重試循環共用呢個 helper。
    """
    try:
        with socket.create_connection((host, port), timeout=_TCP_TIMEOUT_S):
            return True, ""
    except OSError as exc:
        return False, f"無法連線 {host}:{port}——{exc}"


def _logged_in_flag(value) -> bool:
    """qot_logined / trd_logined 雙形態兜底（bool True/False 或 str '1'/'0'）。

    實測係 proto bool（AGENTS.md #15）；唔靠 truthiness——字串 '0' 會係 truthy。
    """
    return str(value).strip().lower() in ("1", "true")


def _connect_trade_ctx(host: str, port: int):
    """timeout 包 OpenSecTradeContext 構造（trade kind 冇 is_async_connect 參數）。

    sync constructor 對死端點會無限重試（AGENTS.md #20）；TCP pre-check 已保證端口可達，
    呢度只兜「TCP 開住但唔係 OpenD」——daemon thread + join(timeout)，超時回報失敗。
    :return: (ctx | None, err | None)
    """
    from futu import OpenSecTradeContext, TrdMarket

    box: dict = {}

    def _worker() -> None:
        try:
            box["ctx"] = OpenSecTradeContext(
                filter_trdmarket=TrdMarket.NONE, host=host, port=port)
        except Exception as exc:  # noqa: BLE001 — 測試路徑，任何異常 → (None, err)
            box["err"] = exc

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(_TRADE_CONNECT_TIMEOUT_S)
    if "ctx" in box:
        return box["ctx"], None
    if "err" in box:
        return None, box["err"]
    return None, TimeoutError(f"OpenSecTradeContext 連線超時（>{_TRADE_CONNECT_TIMEOUT_S:.0f}s）")


def test_endpoint(kind: str, host: str, port: int) -> tuple[bool, str]:
    """測試一個 OpenD 端點可唔可用。

    :param kind: "quote"（OpenQuoteContext）或 "trade"（OpenSecTradeContext）。
    :return: (ok, message)——message 係人讀得嘅結果描述（成功含 server_ver + 登入狀態）。
    """
    host = (host or "").strip() or "127.0.0.1"
    try:
        port = int(port)
    except (TypeError, ValueError):
        return False, f"PORT 無效：{port!r}"

    # --- Stage 1：TCP reachability（快速失敗）---
    ok, msg = tcp_reachable(host, port)
    if not ok:
        return False, msg

    # --- Stage 2：SDK 協議握手 + 登入狀態 ---
    from futu import OpenQuoteContext, RET_OK

    ctx = None
    try:
        if kind == "trade":
            # 安裝 SDK 嘅 OpenSecTradeContext 冇 is_async_connect（傳入 → TypeError）→ timeout 包 sync 構造
            ctx, err = _connect_trade_ctx(host, port)
            if err is not None:
                return False, f"連線測試異常：{err}"
        else:
            ctx = OpenQuoteContext(host=host, port=port, is_async_connect=True)
        ret, data = ctx.get_global_state()
    except Exception as exc:  # noqa: BLE001 — 測試路徑，任何異常都轉成 (False, msg)
        logger.exception("connection test failed (%s %s:%s)", kind, host, port)
        return False, f"連線測試異常：{exc}"
    finally:
        if ctx is not None:
            try:
                ctx.close()
            except Exception:  # noqa: BLE001 — cleanup path
                pass

    if ret != RET_OK or not isinstance(data, dict):
        return False, f"OpenD 回應錯誤：{data}"

    server_ver = str(data.get("server_ver", "N/A"))
    qot_ok = _logged_in_flag(data.get("qot_logined"))
    trd_ok = _logged_in_flag(data.get("trd_logined"))
    if kind == "trade":
        state = f"交易登入：{'✅' if trd_ok else '❌ 未登入'}（行情：{'已登入' if qot_ok else '未登入'}）"
    else:
        state = f"行情登入：{'✅' if qot_ok else '❌ 未登入'}"
    return True, f"{host}:{port} 連線成功——OpenD {server_ver}，{state}"
