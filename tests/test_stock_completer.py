"""StockCompleter 單測（offscreen Qt）：completionMatches 委派 + set_catalog mapping。

覆蓋：catalog 載入後 dropdown 結果 = StockCatalog.search() rank-based 輸出、
display_text → canonical code 映射（嚴格大小寫保留）、typo fuzzy、空目錄。
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from engine.stock_catalog import StockEntry, display_text  # noqa: E402
from ui.stock_completer import StockCompleter  # noqa: E402

_app = QApplication.instance() or QApplication([])


def _entries():
    return [
        StockEntry("HK.HSImain", "恒指期货主连", ""),
        StockEntry("US.AAPL", "苹果", "Apple Inc."),
    ]


def test_completion_matches_delegates_to_catalog():
    c = StockCompleter()
    c.set_catalog(_entries())
    assert display_text(_entries()[0]) in c.completionMatches("hsimain")
    assert c.completionMatches("") == []


def test_set_catalog_returns_display_to_code_mapping():
    entries = _entries()
    c = StockCompleter()
    mapping = c.set_catalog(entries)
    for e in entries:
        assert mapping[display_text(e)] == e.code
    # 嚴格大小寫保留（HK.HSImain 唔係 HK.HSIMAIN）
    assert "HK.HSImain" in mapping.values()


def test_completion_matches_typo_fuzzy():
    c = StockCompleter()
    c.set_catalog(_entries())
    res = c.completionMatches("hhimain")
    assert len(res) == 1
    assert "HK.HSImain" in res[0]


def test_empty_catalog_no_matches():
    c = StockCompleter()
    assert c.completionMatches("aapl") == []
