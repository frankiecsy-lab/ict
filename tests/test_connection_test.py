"""Commit 35 R8：engine/connection_test.py——OpenD 端點連線測試（TCP pre-check + get_global_state）。

零 OpenD 依賴：Stage-1 TCP pre-check 喺死端口即刻失敗（唔會觸發 futu import / 長等待）；
`_logged_in_flag` 純函數覆蓋 qot_logined/trd_logined 雙形態（AGENTS.md #15）。
"""
import socket

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
