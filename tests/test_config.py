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
    "LAST_PRICE_COLOR", "TRD_MARKETS", "DEBUG",
    # Commit 35 R8：報價 / 交易獨立端點（fallback FUTU_OPEND_HOST/PORT）
    "FUTU_QUOTE_HOST", "FUTU_QUOTE_PORT", "FUTU_TRADE_HOST", "FUTU_TRADE_PORT",
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
    assert cfg.trd_markets == ("HK", "US")
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


def test_trd_markets_default(tmp_path):
    """未設 TRD_MARKETS → 預設 ("HK", "US")。"""
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.trd_markets == ("HK", "US")


def test_trd_markets_env_parsing(monkeypatch, tmp_path):
    """Comma-separated + 空白/小寫 → strip、upper；空 token 剔除。"""
    monkeypatch.setenv("TRD_MARKETS", "us, hk ,JP")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.trd_markets == ("US", "HK", "JP")


def test_trd_markets_empty_falls_back_to_default(monkeypatch, tmp_path):
    """全空白/逗號 → 無有效 token → 回落預設。"""
    monkeypatch.setenv("TRD_MARKETS", ", ,")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert cfg.trd_markets == ("HK", "US")


# ---------------------------------------------------------------- Commit 35 R8：報價/交易獨立端點

def test_endpoint_defaults(tmp_path):
    """Commit 35 R8：報價/交易端點預設 127.0.0.1/11111。"""
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert (cfg.quote_host, cfg.quote_port) == ("127.0.0.1", 11111)
    assert (cfg.trade_host, cfg.trade_port) == ("127.0.0.1", 11111)


def test_endpoint_independent_override(monkeypatch, tmp_path):
    """Commit 35 R8：報價/交易端點可指向不同 OpenD 實例（各自獨立 IP+PORT）。"""
    monkeypatch.setenv("FUTU_QUOTE_HOST", "10.0.0.1")
    monkeypatch.setenv("FUTU_QUOTE_PORT", "21111")
    monkeypatch.setenv("FUTU_TRADE_HOST", "10.0.0.2")
    monkeypatch.setenv("FUTU_TRADE_PORT", "31111")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert (cfg.quote_host, cfg.quote_port) == ("10.0.0.1", 21111)
    assert (cfg.trade_host, cfg.trade_port) == ("10.0.0.2", 31111)


def test_endpoint_fallback_to_legacy_opend(monkeypatch, tmp_path):
    """FUTU_QUOTE_*/TRADE_* 未設 → fallback legacy FUTU_OPEND_HOST/PORT（向後相容）。"""
    monkeypatch.setenv("FUTU_OPEND_HOST", "192.168.1.50")
    monkeypatch.setenv("FUTU_OPEND_PORT", "41111")
    cfg = Config.from_env(env_file=tmp_path / "no_such.env")
    assert (cfg.quote_host, cfg.quote_port) == ("192.168.1.50", 41111)
    assert (cfg.trade_host, cfg.trade_port) == ("192.168.1.50", 41111)


def test_save_env_values_updates_in_place_and_appends(tmp_path):
    """Commit 35 R8：save_env_values——已存在行原地更新（註釋/位置保留）、新 key append 檔尾。"""
    from config import save_env_values

    env = tmp_path / ".env"
    env.write_text("# comment\nFUTU_QUOTE_HOST=127.0.0.1\n# another\n", encoding="utf-8")
    path = save_env_values({"FUTU_QUOTE_HOST": "10.9.9.9", "FUTU_TRADE_PORT": "22222"}, env_path=env)
    assert path == env
    lines = env.read_text(encoding="utf-8").splitlines()
    # 原地更新：行位置唔變、註釋保留
    assert lines[0] == "# comment" and lines[1] == "FUTU_QUOTE_HOST=10.9.9.9" and lines[2] == "# another"
    # 新 key append 到檔尾
    assert any(line.strip() == "FUTU_TRADE_PORT=22222" for line in lines)


def test_save_env_values_creates_file_if_missing(tmp_path):
    """Commit 35 R8：.env 唔存在 → 建立並寫入。"""
    from config import save_env_values

    env = tmp_path / ".env"
    path = save_env_values({"FUTU_QUOTE_HOST": "10.9.9.9"}, env_path=env)
    assert path == env and env.exists()
    assert "FUTU_QUOTE_HOST=10.9.9.9" in env.read_text(encoding="utf-8")
