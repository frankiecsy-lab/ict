"""OpenD 連線測試（Commit 35）：報價 / 交易端點兩段式輕量檢查。

- Stage 1：raw TCP socket pre-check——快速失敗（host/port 錯、OpenD 未啟動），
  唔會建立 SDK context；
- Stage 2：`is_async_connect=True` + `get_global_state()`——協議層握手驗證 +
  登入狀態回報（server_ver / qot_logined / trd_logined）。

⚠️ 關鍵坑（對照安裝 futu-api source `common/open_context_base.py` 驗證）：
`OpenContextBase.__init__` 喺連唔到時進入 **`while True` 無限重試**（每 6s sleep）→
同步構造 context 喺死端點會**永久阻塞**。所以本模組一律 `is_async_connect=True`，
並先做 TCP pre-check。

⚠️ SDK **冇** `test_connect()` API（已 grep 安裝版本確認）——最輕量嘅健康檢查
就係 `get_global_state()`（同 FutuEngine ping loop 同一個 API，AGENTS.md #15）。

阻塞函數——必須喺 worker thread 調用，嚴禁 GUI thread 直接 call。
"""
from __future__ import annotations

import logging
import socket

logger = logging.getLogger(__name__)

_TCP_TIMEOUT_S = 5.0


def _logged_in_flag(value) -> bool:
    """qot_logined / trd_logined 雙形態兜底（bool True/False 或 str '1'/'0'）。

    實測係 proto bool（AGENTS.md #15）；唔靠 truthiness——字串 '0' 會係 truthy。
    """
    return str(value).strip().lower() in ("1", "true")


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
    try:
        with socket.create_connection((host, port), timeout=_TCP_TIMEOUT_S):
            pass
    except OSError as exc:
        return False, f"無法連線 {host}:{port}——{exc}"

    # --- Stage 2：SDK 協議握手 + 登入狀態（async connect，唔會阻塞）---
    from futu import OpenQuoteContext, OpenSecTradeContext, RET_OK, TrdMarket

    ctx = None
    try:
        if kind == "trade":
            ctx = OpenSecTradeContext(
                filter_trdmarket=TrdMarket.NONE, host=host, port=port, is_async_connect=True)
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
