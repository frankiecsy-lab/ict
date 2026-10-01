"""應用程式設定模組。

唯一事實來源係 .env 檔案（範本見 .env.example）；本模組只負責讀取環境變數並
組裝成 immutable Config。純 stdlib + python-dotenv 實現，無 Qt / futu 依賴，
可獨立單測。

.env 路徑：開發模式 = 專案根目錄；PyInstaller frozen（onedir）= exe 旁邊——
用戶部署時將 .env 放喺 dist/ICT-Trader-win/.env（或 Ubuntu 版同層）即可。
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _default_env_path() -> Path:
    """預設 .env 路徑。

    開發模式 = 專案根目錄（config.py 同層）；PyInstaller frozen 模式 = exe 旁邊
    （onedir dist 目錄）——唔係 sys._MEIPASS（temp dir，啟動後即刪、用戶改唔到）。
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name(".env")
    return Path(__file__).resolve().with_name(".env")

# K 線週期（futu KLType 列舉名）→ 分鐘數；未知週期直接報錯，避免靜默用錯聚合粒度
_KLINE_PERIOD_MINUTES = {
    "K_1M": 1,
    "K_3M": 3,
    "K_5M": 5,
    "K_15M": 15,
    "K_30M": 30,
    "K_60M": 60,
    "K_DAY": 24 * 60,
    "K_WEEK": 7 * 24 * 60,
    "K_MON": 30 * 24 * 60,
}

# 公開：UI combo / engine 校驗共用（insertion order = 顯示順序）
KLINE_TYPES: tuple[str, ...] = tuple(_KLINE_PERIOD_MINUTES)


def kline_period_minutes(ktype: str) -> int | None:
    """K 線週期名 → 分鐘數；未知返回 None。"""
    return _KLINE_PERIOD_MINUTES.get(ktype)

# 蠟燭顏色慣例：HK=紅漲綠跌 / INTL=綠漲紅跌
_CONVENTION_COLORS = {
    "HK": {"up": "#F23645", "down": "#089981"},
    "INTL": {"up": "#089981", "down": "#F23645"},
}


def _str(key: str, default: str) -> str:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    return raw.strip()


def _int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Config:
    """不可變運行配置；一律經 from_env() 構造。"""

    # --- 富途 OpenD 連線 ---
    opend_host: str = "127.0.0.1"
    opend_port: int = 11111

    # --- 行情 ---
    trading_code: str = "HK.HSImain"
    kline_type: str = "K_1M"
    history_count: int = 1000
    smt_code: str | None = None       # SMT Divergence 配對副標的（None/空 = 功能關閉）

    # --- 圖表顯示 ---
    visible_bars: int = 120
    convention: str = "HK"           # HK=紅漲綠跌 / INTL=綠漲紅跌
    color_up: str | None = None      # 手動 override（如 "#FF4D4F"）；None=跟隨慣例
    color_down: str | None = None

    # --- 深色主題色（可經 .env 覆蓋）---
    bg_color: str = "#101418"
    grid_color: str = "#1E2530"
    text_color: str = "#D6DEE8"
    axis_text_color: str = "#7A8699"
    last_price_color: str = "#FFB020"

    debug: bool = False

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "Config":
        """由 .env + 程序環境變數讀取配置。

        已存在嘅程序環境變數優先於 .env 檔案（load_dotenv override=False），
        方便測試與部署時臨時覆蓋。
        """
        if env_file is None:
            env_file = _default_env_path()
        load_dotenv(env_file, override=False)

        kline_type = _str("KLINE_TYPE", "K_1M").upper()
        if kline_type not in _KLINE_PERIOD_MINUTES:
            valid = ", ".join(sorted(_KLINE_PERIOD_MINUTES))
            raise ValueError(f"未知 KLINE_TYPE={kline_type!r}，可選：{valid}")

        convention = _str("CONVENTION", "HK").upper()
        if convention not in _CONVENTION_COLORS:
            convention = "HK"

        return cls(
            opend_host=_str("FUTU_OPEND_HOST", "127.0.0.1"),
            opend_port=_int("FUTU_OPEND_PORT", 11111),
            trading_code=_str("TRADING_CODE", "HK.HSImain"),
            kline_type=kline_type,
            history_count=max(1, _int("HISTORY_COUNT", 1000)),
            smt_code=_str("SMT_CODE", "") or None,   # SMT Divergence 配對副標的（空 = 關閉）
            visible_bars=max(1, _int("VISIBLE_BARS", 120)),
            convention=convention,
            color_up=_str("COLOR_UP", "") or None,
            color_down=_str("COLOR_DOWN", "") or None,
            bg_color=_str("BG_COLOR", "#101418"),
            grid_color=_str("GRID_COLOR", "#1E2530"),
            text_color=_str("TEXT_COLOR", "#D6DEE8"),
            axis_text_color=_str("AXIS_TEXT_COLOR", "#7A8699"),
            last_price_color=_str("LAST_PRICE_COLOR", "#FFB020"),
            debug=_bool("DEBUG", False),
        )

    @property
    def period_minutes(self) -> int:
        """K 線週期（分鐘），供 CandleAggregator 使用。"""
        return _KLINE_PERIOD_MINUTES[self.kline_type]

    @property
    def up_color(self) -> str:
        return self.color_up or _CONVENTION_COLORS[self.convention]["up"]

    @property
    def down_color(self) -> str:
        return self.color_down or _CONVENTION_COLORS[self.convention]["down"]
