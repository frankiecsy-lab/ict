"""config 模組單測。

Hermetic 原則：每個測試都清空相關環境變數（monkeypatch），並傳入明確嘅 env_file
路徑，確保唔會受專案根目錄真實 .env 影響。
"""
import dataclasses

import pytest

from config import Config

_ALL_KEYS = [
    "FUTU_OPEND_HOST", "FUTU_OPEND_PORT", "TRADING_CODE", "KLINE_TYPE",
    "HISTORY_COUNT", "VISIBLE_BARS", "CONVENTION", "COLOR_UP", "COLOR_DOWN",
    "BG_COLOR", "GRID_COLOR", "TEXT_COLOR", "AXIS_TEXT_COLOR",
    "LAST_PRICE_COLOR", "DEBUG",
]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for key in _ALL_KEYS:
        monkeypatch.delenv(key, raising=False)


def _rgb(hexstr: str) -> tuple[int, int, int]:
    h = hexstr.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def test_defaults(tmp_path):
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.opend_host == "127.0.0.1"
    assert cfg.opend_port == 11111
    assert cfg.trading_code == "HK.HSImain"
    assert cfg.kline_type == "K_1M"
    assert cfg.period_minutes == 1
    assert cfg.history_count == 1000
    assert cfg.visible_bars == 120
    assert cfg.convention == "HK"
    assert cfg.color_up is None
    assert cfg.color_down is None
    assert cfg.debug is False


def test_env_var_override(monkeypatch, tmp_path):
    monkeypatch.setenv("FUTU_OPEND_PORT", "9999")
    monkeypatch.setenv("TRADING_CODE", "US.AAPL")
    monkeypatch.setenv("KLINE_TYPE", "k_5m")  # 小寫應被正規化
    monkeypatch.setenv("HISTORY_COUNT", "100")
    monkeypatch.setenv("VISIBLE_BARS", "60")
    monkeypatch.setenv("DEBUG", "true")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.opend_port == 9999
    assert cfg.trading_code == "US.AAPL"
    assert cfg.kline_type == "K_5M"
    assert cfg.period_minutes == 5
    assert cfg.history_count == 100
    assert cfg.visible_bars == 60
    assert cfg.debug is True


def test_env_file_loaded(tmp_path):
    env = tmp_path / ".env"
    env.write_text("TRADING_CODE=HK.00700\nFUTU_OPEND_PORT=22222\n", encoding="utf-8")
    cfg = Config.from_env(env_file=env)
    assert cfg.trading_code == "HK.00700"
    assert cfg.opend_port == 22222


def test_process_env_wins_over_file(tmp_path, monkeypatch):
    """已存在嘅程序環境變數優先於 .env（override=False 語義）。"""
    env = tmp_path / ".env"
    env.write_text("TRADING_CODE=HK.00700\n", encoding="utf-8")
    monkeypatch.setenv("TRADING_CODE", "US.TSLA")
    cfg = Config.from_env(env_file=env)
    assert cfg.trading_code == "US.TSLA"


def test_convention_colors():
    hk = Config(convention="HK")
    r, g, _ = _rgb(hk.up_color)
    assert r > g, "HK 慣例：漲應偏紅"
    r, g, _ = _rgb(hk.down_color)
    assert g > r, "HK 慣例：跌應偏綠"

    intl = Config(convention="INTL")
    r, g, _ = _rgb(intl.up_color)
    assert g > r, "INTL 慣例：漲應偏綠"
    r, g, _ = _rgb(intl.down_color)
    assert r > g, "INTL 慣例：跌應偏紅"


def test_color_override_wins():
    cfg = Config(convention="HK", color_up="#123456")
    assert cfg.up_color == "#123456"
    # 只 override up，down 仍跟隨慣例
    r, g, _ = _rgb(cfg.down_color)
    assert g > r


def test_unknown_convention_falls_back_to_hk(monkeypatch, tmp_path):
    monkeypatch.setenv("CONVENTION", "whatever")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.convention == "HK"


def test_unknown_kline_type_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("KLINE_TYPE", "K_9X")
    with pytest.raises(ValueError, match="KLINE_TYPE"):
        Config.from_env(env_file=tmp_path / "no_such.env")


def test_invalid_int_falls_back_to_default(monkeypatch, tmp_path):
    monkeypatch.setenv("FUTU_OPEND_PORT", "not_a_number")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.opend_port == 11111


def test_non_positive_counts_clamped_to_one(monkeypatch, tmp_path):
    monkeypatch.setenv("HISTORY_COUNT", "0")
    monkeypatch.setenv("VISIBLE_BARS", "-5")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.history_count == 1
    assert cfg.visible_bars == 1


def test_config_is_frozen():
    cfg = Config()
    with pytest.raises(dataclasses.FrozenInstanceError):
        cfg.trading_code = "US.AAPL"
