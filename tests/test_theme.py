"""Commit 35 R6：ui/theme.py——全局淺色/暗色主題（Theme dataclass + QSS builder）。

純邏輯層測試（零 Qt widget）：get_theme fallback、THEMES registry、frozen 不變性、
build_qss selector 覆蓋 + palette 顏色注入；另含 ui.main_window._cfg_theme 的
「.env 顏色覆蓋疊加去基礎主題」行為。
"""
from dataclasses import FrozenInstanceError

import pytest

from ui.theme import DARK, LIGHT, THEMES, build_qss, get_theme


def test_get_theme_known_names():
    assert get_theme("dark") is DARK
    assert get_theme("light") is LIGHT
    # case-insensitive + strip（持久化/用戶輸入形態兜底）
    assert get_theme("Light") is LIGHT
    assert get_theme("  DARK ") is DARK


def test_get_theme_unknown_falls_back_to_dark():
    """未知 / 空 / None → DARK fallback（任何損壞值都唔 crash）。"""
    assert get_theme("nope") is DARK
    assert get_theme("") is DARK
    assert get_theme(None) is DARK


def test_themes_dict_keys():
    assert set(THEMES) == {"dark", "light"}


def test_theme_is_frozen():
    """Theme = frozen dataclass——palette 不可變（防運行時意外改色）。"""
    with pytest.raises(FrozenInstanceError):
        DARK.bg = "#000000"   # type: ignore[misc]


@pytest.mark.parametrize("theme", [DARK, LIGHT])
def test_build_qss_covers_core_selectors(theme):
    """兩套主題 QSS 都要覆蓋核心 widget selector（全局生效，唔係單視窗）。"""
    qss = build_qss(theme)
    for sel in ("QMainWindow", "QWidget", "QPushButton", "QLineEdit",
                "QComboBox", "QTableWidget", "QGroupBox", "QTabBar::tab"):
        assert sel in qss, f"{theme.name} QSS 缺 selector: {sel}"


def test_build_qss_uses_palette_colors_and_themes_differ():
    dark_qss = build_qss(DARK)
    light_qss = build_qss(LIGHT)
    assert DARK.bg in dark_qss and LIGHT.bg in light_qss
    assert dark_qss != light_qss


def test_cfg_theme_overlay_applies_env_colors():
    """_cfg_theme：.env 顏色覆蓋疊加去基礎主題（bg/grid/text/muted/accent），其餘字段保持。"""
    from types import SimpleNamespace

    from ui.main_window import _cfg_theme

    cfg = SimpleNamespace(bg_color="#112233", grid_color="#445566", text_color="#778899",
                          axis_text_color="#AABBCC", last_price_color="#DD0000")
    t = _cfg_theme(DARK, cfg)
    assert (t.bg, t.grid, t.text, t.muted, t.accent) == \
        ("#112233", "#445566", "#778899", "#AABBCC", "#DD0000")
    # 非顏色字段保持基礎主題值（button/border/panel…）
    assert t.button == DARK.button and t.border == DARK.border and t.name == "dark"
