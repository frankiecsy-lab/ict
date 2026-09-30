"""StockCompleter 單測（offscreen Qt）：completionMatches 委派 + set_catalog mapping。

覆蓋：catalog 載入後 dropdown 結果 = StockCatalog.search() rank-based 輸出、
display_text → canonical code 映射（嚴格大小寫保留）、typo fuzzy、空目錄。
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from engine.stock_catalog import StockEntry, display_text  # noqa: E402
from ui.stock_completer import StockCompleter, code_from_completion  # noqa: E402

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


def test_model_item_display_role_is_full_text():
    """Dropdown popup 顯示完整 display_text（code + 中英文名）——名稱要留喺 dropdown。

    （QStandardItem 喺呢個 PySide6/Qt 版本 Display/Edit role 耦合，無法用雙 role 分開；
    輸入欄只留 code 改由 main_window `_on_code_activated` 經 `code_from_completion()` 強制覆蓋。）
    """
    entries = _entries()
    c = StockCompleter()
    c.set_catalog(entries)
    model = c.model()
    assert model.rowCount() == len(entries)
    for i, e in enumerate(entries):
        item = model.item(i)
        assert item.data(Qt.DisplayRole) == display_text(e)  # dropdown 顯示 code + 名稱


def test_code_from_completion_returns_bare_code():
    """選中後輸入欄只留 code：mapping hit → canonical code；miss → 第一 token（code）兜底。"""
    entries = _entries()
    c = StockCompleter()
    mapping = c.set_catalog(entries)

    # mapping hit：完整 display_text → 嚴格大小寫 canonical code
    assert code_from_completion(display_text(entries[0]), mapping) == "HK.HSImain"
    assert code_from_completion(display_text(entries[1]), mapping) == "US.AAPL"

    # mapping miss（例如 Qt 寫入嘅字串同 display_text 唔完全一致）→ 第一 token = code
    assert code_from_completion("HK.HSImain  恒指期货主连", {}) == "HK.HSImain"
    assert code_from_completion("US.AAPL  苹果  Apple Inc.", {}) == "US.AAPL"

    # 純 code（無名）/ 前後空白 / 空字串邊界
    assert code_from_completion("HK.00700", {}) == "HK.00700"
    assert code_from_completion("  US.TSLA  ", {}) == "US.TSLA"
    assert code_from_completion("", {}) is None
