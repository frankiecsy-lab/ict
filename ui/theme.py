"""全局淺色/暗色主題（Commit 35 R6）：Theme dataclass + DARK/LIGHT palette + 視窗級 QSS builder。

設計：
- **視窗級 QSS**：`build_qss(t)` 由 palette 組裝通用 selector，兩視窗 `setStyleSheet()` 共用——
  切換主題 = 重新 setStyleSheet（Qt 自動重繪所有 widget）。
- **蠟燭圖表**：CandleChart paint 時直接讀 `self._cfg` 顏色字段 → `apply_theme(t)` 用
  `dataclasses.replace(cfg, ...)` 換一個新 Config（frozen dataclass，零 paint 代碼改動）+ update()。
- **持久化**：主題偏好經 UIStateStore「theme」欄位存（單行 JSON blob、schema 演化免費——AGENTS.md #12）。

漲跌色（up/down）**跟隨 convention 唔跟隨主題**——HK=紅漲綠跌係市場慣例，淺色模式下亦保持。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """一組完整 UI 配色（frozen → 可安全跨 thread / 存 state dict）。"""

    name: str                 # "dark" / "light"
    bg: str                   # 視窗背景
    panel: str                # 卡片 / 表頭 / 輸入欄背景
    grid: str                 # 圖表網格線 + 分隔邊框
    text: str                 # 主文字
    muted: str                # 次要文字（軸、hint、group title）
    button: str               # 按鈕背景
    button_hover: str         # 按鈕 hover
    button_disabled_bg: str   # disabled 按鈕 / tab 未選中背景
    button_disabled_fg: str   # disabled 文字
    border: str               # group box / 輸入欄邊框
    accent: str               # 高亮色（最新價線、checked 按鈕）


DARK = Theme(
    name="dark", bg="#101418", panel="#1A212B", grid="#1E2530",
    text="#D6DEE8", muted="#7A8699", button="#1E2836", button_hover="#27354A",
    button_disabled_bg="#151B23", button_disabled_fg="#4A5568", border="#2A3441", accent="#FFB020",
)

LIGHT = Theme(
    name="light", bg="#F5F7FA", panel="#FFFFFF", grid="#DDE3EA",
    text="#1A2027", muted="#5A6B7C", button="#FFFFFF", button_hover="#E8EDF3",
    button_disabled_bg="#EEF1F4", button_disabled_fg="#9AA7B4", border="#C3CCD6", accent="#E68A00",
)

THEMES: dict[str, Theme] = {"dark": DARK, "light": LIGHT}


def get_theme(name: str | None) -> Theme:
    """主題名 → Theme；未知 / 空 → DARK（默認暗色，同現行行為一致）。"""
    return THEMES.get((name or "").strip().lower(), DARK)


def build_qss(t: Theme) -> str:
    """視窗級 QSS（通用 selector、兩視窗共用）。

    覆蓋 MainWindow / OrderWindow 現有深色 stylesheet 嘅同一 selector 範圍；
    `QPushButton:checked` = accent 高亮——全局模式按鍵（實盤/模擬）同 indicator toggle
    選中後一眼可辨。
    """
    return (
        f"QMainWindow {{ background: {t.bg}; }}"
        f"QWidget {{ color: {t.text}; font-family: Consolas; }}"
        f"QStatusBar {{ background: {t.bg}; border: none; }}"
        f"QGroupBox {{ border: 1px solid {t.grid}; margin-top: 8px; }}"
        f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; color: {t.muted}; }}"
        f"QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox "
        f"{{ background: {t.panel}; border: 1px solid {t.grid}; color: {t.text}; padding: 3px 6px; }}"
        f"QPushButton {{ background: {t.button}; border: 1px solid {t.border}; "
        f"color: {t.text}; padding: 4px 14px; }}"
        f"QPushButton:hover {{ background: {t.button_hover}; }}"
        f"QPushButton:checked {{ background: {t.accent}; color: #101418; "
        f"border-color: {t.accent}; font-weight: bold; }}"
        f"QPushButton:disabled {{ color: {t.button_disabled_fg}; background: {t.button_disabled_bg}; }}"
        f"QTableWidget, QTableView {{ background: {t.bg}; gridline-color: {t.grid}; border: none; }}"
        f"QFrame#accountCard {{ background: {t.panel}; border: 1px solid {t.border}; border-radius: 6px; }}"
        f"QTabWidget::pane {{ border: 1px solid {t.grid}; top: -1px; }}"
        f"QTabBar::tab {{ background: {t.button_disabled_bg}; color: {t.muted}; padding: 4px 10px; "
        f"border: 1px solid {t.grid}; border-bottom: none; margin-right: 2px; }}"
        f"QTabBar::tab:selected {{ background: {t.panel}; color: {t.text}; font-weight: bold; }}"
        f"QHeaderView::section {{ background: {t.panel}; color: {t.muted}; border: none; padding: 3px; }}"
    )
