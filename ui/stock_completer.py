"""Fuzzy autocomplete completer：matching 委派俾 StockCatalog（code / 英文名 / 中文名 + 簡繁互換）。

- `UnfilteredPopupCompletion`：popup 顯示嘅就係 `completionMatches()` 返回嘅 rank-based 結果，
  Qt 唔會再 filter 一次。
- Model item 用完整 `display_text(e)`（code + 中英文名）→ dropdown popup 顯示名稱；**輸入欄
  TEXT FIELD 只留 code** 由 main_window `_on_code_activated` 經 `code_from_completion()` 還原
  嚴格大小寫 canonical code 後 `setText(code)` 強制覆蓋。（QStandardItem 喺呢個 PySide6/Qt 版本
  Display/Edit role 係耦合嘅——設 EditRole 會連帶改 DisplayRole，無法用雙 role 分開 dropdown
  顯示同輸入欄字串。）
- `set_catalog(entries)` 喺 engine `catalog_ready` 時呼叫：rebuild QStandardItemModel +
  返回 display_text → canonical code 映射（activated 時 main_window 用嚟搵返嚴格大小寫 code）。
- `catalog()` 暴露內部 StockCatalog snapshot——main_window `_do_switch()` 驗證輸入編號存在
  （`canonical_code()`）同更新名稱 LABEL（`name_text()`）用。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QCompleter

from engine.stock_catalog import StockCatalog, display_text


class StockCompleter(QCompleter):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._catalog = StockCatalog()
        self.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setModel(QStandardItemModel(self))

    def set_catalog(self, entries) -> dict[str, str]:
        """Rebuild model（catalog_ready 時呼叫）；返回 display_text → canonical code 映射。"""
        self._catalog.replace(entries)
        model = QStandardItemModel(self)
        mapping: dict[str, str] = {}
        for e in entries:
            text = display_text(e)
            item = QStandardItem(text)  # DisplayRole/TextRole = full text（dropdown popup 顯示 code + 名稱）
            model.appendRow(item)
            mapping[text] = e.code
        self.setModel(model)
        return mapping

    def catalog(self) -> StockCatalog:
        """內部目錄 snapshot（main_window 驗證輸入編號存在 / 還原 canonical code 用）。"""
        return self._catalog

    def completionMatches(self, prefix: str):  # noqa: N802 (Qt naming)
        """每次 keystroke 由 StockCatalog.search() 提供 rank-based 結果（O(n) 單遍）。"""
        return [display_text(e) for e in self._catalog.search(prefix)]


def code_from_completion(text: str, mapping: dict[str, str]) -> str | None:
    """由 dropdown 選中嘅字串還原嚴格大小寫 canonical code（TEXT FIELD 只留 code）。

    `text` 命中 mapping（display_text → code）→ 返回 canonical code；否則取第一個 whitespace
    token（`display_text()` 格式 code 永遠係第一 token，probe 驗證過）兜底——確保名稱唔入輸入欄。
    """
    if text in mapping:
        return mapping[text]
    stripped = text.strip()
    return stripped.split()[0] if stripped else None
