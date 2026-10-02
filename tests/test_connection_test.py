"""Commit 35 R8：engine/connection_test.py——OpenD 端點連線測試（TCP pre-check + get_global_state）。

零 OpenD 依賴：Stage-1 TCP pre-check 喺死端口即刻失敗（唔會觸發 futu import / 長等待）；
`_logged_in_flag` 純函數覆蓋 qot_logined/trd_logined 雙形態（AGENTS.md #15）。
"""
import contextlib
import socket
import threading

import pytest

from engine import connection_test


def _dead_port() -> int:
    """bind port 0 → 攞 ephemeral port → close——該端口保證冇人 listen。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.parametrize("value,expected", [
    (True, True), ("1", True), ("true", True), ("TRUE", True), (" 1 ", True),
    (False, False), ("0", False), ("false", False), (None, False),
    ("", False), ("N/A", False),
])
def test_logged_in_flag_dual_form(value, expected):
    """bool/str 雙形態兜底（proto bool = True/False；legacy docstring str '1'/'0'）——唔靠 truthiness。"""
    assert connection_test._logged_in_flag(value) is expected


@pytest.mark.parametrize("kind", ["quote", "trade"])
def test_endpoint_dead_port_fails_fast(kind):
    """Stage-1 TCP pre-check：端口冇人 listen → 即刻失敗（訊息含實際 host:port）。"""
    port = _dead_port()
    ok, msg = connection_test.test_endpoint(kind, "127.0.0.1", port)
    assert ok is False
    assert str(port) in msg


def test_endpoint_empty_host_falls_back_to_loopback():
    """空 host → fallback 127.0.0.1（錯誤訊息含實際使用嘅地址）。"""
    port = _dead_port()
    ok, msg = connection_test.test_endpoint("quote", "   ", port)
    assert ok is False and "127.0.0.1" in msg


def test_endpoint_invalid_port_type():
    """非數字 port → 即刻失敗（唔做 socket 嘗試）。"""
    ok, msg = connection_test.test_endpoint("trade", "127.0.0.1", "abc")   # type: ignore[arg-type]
    assert ok is False and "PORT 無效" in msg


def test_tcp_reachable_dead_port():
    """tcp_reachable helper：死端口 → (False, 訊息含 host:port)。"""
    port = _dead_port()
    ok, msg = connection_test.tcp_reachable("127.0.0.1", port)
    assert ok is False and str(port) in msg


@contextlib.contextmanager
def _live_tcp_server():
    """本地 TCP listener（accept 一次 handshake）——Stage-1 通過 + Stage-2 mock 測試用。"""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    def _accept_once():
        conn, _ = srv.accept()
        conn.close()

    t = threading.Thread(target=_accept_once, daemon=True)
    t.start()
    try:
        yield port
    finally:
        srv.close()


def test_tcp_reachable_live_port():
    """tcp_reachable helper：本地 listener → (True, "")。"""
    with _live_tcp_server() as port:
        ok, msg = connection_test.tcp_reachable("127.0.0.1", port)
    assert ok is True and msg == ""


def test_trade_stage2_sync_ctx_without_async_kwarg(monkeypatch):
    """Commit 36 B2 regression guard：trade kind Stage-2 **唔可以**傳 is_async_connect——
    安裝 SDK 嘅 OpenSecTradeContext.__init__ 冇呢個參數（傳入 → TypeError: unexpected keyword argument）。"""
    import futu

    class FakeCtx:
        def get_global_state(self):
            return 0, {"server_ver": "10.5", "qot_logined": True, "trd_logined": True}

        def close(self):
            pass

    captured: dict = {}

    def fake_ctor(filter_trdmarket=None, host="", port=0, **kw):
        captured.update(kw)
        return FakeCtx()

    monkeypatch.setattr(futu, "OpenSecTradeContext", fake_ctor)
    with _live_tcp_server() as port:
        ok, msg = connection_test.test_endpoint("trade", "127.0.0.1", port)
    assert ok is True and "連線成功" in msg and "交易登入：✅" in msg
    assert "is_async_connect" not in captured   # B2 核心斷言


def test_trade_stage2_ctor_exception_reported(monkeypatch):
    """trade kind Stage-2 ctor raise → (False, 異常訊息)（唔 propagate）。"""
    import futu

    def boom(**kw):
        raise RuntimeError("ctor exploded")

    monkeypatch.setattr(futu, "OpenSecTradeContext", boom)
    with _live_tcp_server() as port:
        ok, msg = connection_test.test_endpoint("trade", "127.0.0.1", port)
    assert ok is False and "連線測試異常" in msg


def test_trade_stage2_timeout_reports_failure(monkeypatch):
    """TCP 開住但唔係 OpenD（ctor 阻塞）→ timeout thread 回報失敗，唔會 hang。"""
    import futu

    release = threading.Event()

    def blocking_ctor(**kw):
        release.wait(10)   # 模擬 sync constructor 無限重試
        raise RuntimeError("should not reach")

    monkeypatch.setattr(futu, "OpenSecTradeContext", blocking_ctor)
    monkeypatch.setattr(connection_test, "_TRADE_CONNECT_TIMEOUT_S", 0.2)
    with _live_tcp_server() as port:
        ok, msg = connection_test.test_endpoint("trade", "127.0.0.1", port)
    release.set()   # 令 leaked daemon thread 即刻退出
    assert ok is False and "超時" in msg
