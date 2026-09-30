"""PyInstaller frozen 行為單測：.env 路徑解析 + windowed 配置錯誤回報。

frozen 狀態用 monkeypatch.setattr(sys, "frozen", True, raising=False) 模擬（唔需要真 build）；
QMessageBox.critical patch 掉避免 offscreen 下彈窗阻塞。
"""
import sys

from PySide6.QtWidgets import QMessageBox

from config import Config, _default_env_path


def test_default_env_path_dev_mode():
    """開發模式：.env = config.py 同層（專案根目錄）。"""
    from pathlib import Path

    expected = Path(__file__).resolve().parent.parent / ".env"
    assert _default_env_path() == expected


def test_default_env_path_frozen(monkeypatch, tmp_path):
    """frozen 模式：.env = exe 旁邊（sys.executable 同層），唔係 _MEIPASS。"""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    fake_exe = tmp_path / "ICT-Trader.exe"
    fake_exe.touch()
    monkeypatch.setattr(sys, "executable", str(fake_exe))
    assert _default_env_path() == tmp_path / ".env"


def test_from_env_frozen_reads_next_to_exe(monkeypatch, tmp_path):
    """frozen + env_file=None → 讀 exe 旁邊 .env（TRADING_CODE 生效）。"""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    fake_exe = tmp_path / "ict-trader"
    fake_exe.touch()
    monkeypatch.setattr(sys, "executable", str(fake_exe))
    (tmp_path / ".env").write_text("TRADING_CODE=US.AAPL\n")
    for key in ("FUTU_OPEND_HOST", "FUTU_OPEND_PORT", "TRADING_CODE", "KLINE_TYPE"):
        monkeypatch.delenv(key, raising=False)
    cfg = Config.from_env()
    assert cfg.trading_code == "US.AAPL"


def test_from_env_frozen_no_file_uses_defaults(monkeypatch, tmp_path):
    """frozen 但 exe 旁邊冇 .env → 全部 default（唔會 crash）。"""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    fake_exe = tmp_path / "ict-trader"
    fake_exe.touch()
    monkeypatch.setattr(sys, "executable", str(fake_exe))
    for key in ("FUTU_OPEND_HOST", "FUTU_OPEND_PORT", "TRADING_CODE", "KLINE_TYPE"):
        monkeypatch.delenv(key, raising=False)
    cfg = Config.from_env()
    assert cfg.trading_code == "HK.HSImain"


def test_report_config_error_console(monkeypatch):
    """非 windowed（stdout 存在）→ stderr，唔彈框。"""
    import main as main_mod

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert sys.stdout is not None  # pytest console mode
    captured = []
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a: captured.append(a)))
    main_mod._report_config_error("bad KLINE_TYPE")
    assert captured == []


def test_report_config_error_windowed(monkeypatch):
    """frozen + stdout=None（windowed build）→ QMessageBox.critical 彈出。"""
    import main as main_mod

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "stdout", None)
    captured = []
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a: captured.append(a)))
    main_mod._report_config_error("bad KLINE_TYPE")
    assert len(captured) == 1
    title, message = captured[0][1], captured[0][2]
    assert "配置錯誤" in title
    assert "bad KLINE_TYPE" in message
