"""Fuzzy autocomplete completer：matching 委派俾 StockCatalog（code / 英文名 / 中文名 + 簡繁互換）。

- `UnfilteredPopupCompletion`：popup 顯示嘅就係 `completionMatches()` 返回嘅 rank-based 結果，
  Qt 唔會再 filter 一次。
- `set_catalog(entries)` 喺 engine `catalog_ready` 時呼叫：rebuild QStandardItemModel +
  返回 display_text → canonical code 映射（activated 時 main_window 用嚟搵返嚴格大小寫 code）。
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
            item = QStandardItem(text)
            item.setData(e.code, Qt.UserRole)
            model.appendRow(item)
            mapping[text] = e.code
        self.setModel(model)
        return mapping

    def completionMatches(self, prefix: str):  # noqa: N802 (Qt naming)
        """每次 keystroke 由 StockCatalog.search() 提供 rank-based 結果（O(n) 單遍）。"""
        return [display_text(e) for e in self._catalog.search(prefix)]
