"""StockCatalog 模糊搜尋單測（純類，零 Qt/futu 依賴）。

覆蓋：suffix / display_text / to_simplified（簡繁）/ register_code_aliases /
canonical_code / search rank-based 兩段式（exact → suffix → prefix → en → cn → substring → typo fuzzy）/
dedup / limit / 13k entries 性能。
"""
from __future__ import annotations

import time

from engine.stock_catalog import (StockCatalog, StockEntry, basic_info_text, display_text,
                                  name_text, register_code_aliases, to_simplified)


def _catalog() -> StockCatalog:
    c = StockCatalog()
    c.replace([
        StockEntry("HK.HSImain", "恒指期货主连", ""),
        StockEntry("HK.00700", "腾讯控股", "TENCENT"),
        StockEntry("US.AAPL", "苹果", "Apple Inc."),
        StockEntry("US.MSFT", "", "Microsoft Corp."),
        StockEntry("US.BABA", "阿里巴巴", "Alibaba Group Holding Ltd"),
    ])
    return c


# ---------------------------------------------------------------- suffix / display

def test_suffix_property():
    assert StockEntry("HK.HSImain").suffix == "HSImain"
    assert StockEntry("US.AAPL").suffix == "AAPL"
    assert StockEntry("NOPE").suffix == "NOPE"  # 無 prefix → 原樣


def test_display_text_both_names():
    e = StockEntry("US.AAPL", "苹果", "Apple Inc.")
    assert display_text(e) == "US.AAPL  苹果  Apple Inc."


def test_display_text_code_only():
    assert display_text(StockEntry("HK.HSImain")) == "HK.HSImain"


def test_name_text_both_names():
    e = StockEntry("US.AAPL", "苹果", "Apple Inc.")
    assert name_text(e) == "苹果 Apple Inc."


def test_name_text_cn_only():
    assert name_text(StockEntry("HK.00700", "腾讯控股", "")) == "腾讯控股"


def test_name_text_en_only():
    assert name_text(StockEntry("US.MSFT", "", "Microsoft Corp.")) == "Microsoft Corp."


def test_name_text_no_names_empty():
    assert name_text(StockEntry("HK.HSImain")) == ""


# ---------------------------------------------------------------- basic_info

def test_basic_info_both_fields():
    e = StockEntry("US.AAPL", "苹果", "Apple Inc.", lot_size=1, listing_date="2016-06-09")
    assert basic_info_text(e) == "每手 1 · 上市 2016-06-09"


def test_basic_info_lot_only():
    e = StockEntry("HK.00700", "腾讯控股", "", lot_size=500, listing_date="")
    assert basic_info_text(e) == "每手 500"


def test_basic_info_listing_only():
    e = StockEntry("US.MSFT", "", "Microsoft Corp.", lot_size=None, listing_date="1986-03-13")
    assert basic_info_text(e) == "上市 1986-03-13"


def test_basic_info_no_fields_empty():
    # seed 主力連續合約等無此數據 → 空字串（LABEL 唔顯示）
    assert basic_info_text(StockEntry("HK.HSImain", "恒指期货主连", "")) == ""


# ---------------------------------------------------------------- to_simplified

def test_to_simplified_traditional_to_simplified():
    assert to_simplified("騰訊控股") == "腾讯控股"
    assert to_simplified("恒指期貨主連") == "恒指期货主连"


def test_to_simplified_ascii_passthrough():
    assert to_simplified("AAPL Inc.") == "AAPL Inc."


def test_to_simplified_empty():
    assert to_simplified("") == ""


# ---------------------------------------------------------------- register_code_aliases

def test_register_code_aliases_mixed_case():
    alias: dict[str, str] = {}
    n = register_code_aliases([StockEntry("HK.HSImain")], alias)
    assert alias == {"HK.HSIMAIN": "HK.HSImain"}
    assert n == 1


def test_register_code_aliases_idempotent():
    alias: dict[str, str] = {}
    register_code_aliases([StockEntry("HK.HSImain")], alias)
    assert register_code_aliases([StockEntry("HK.HSImain")], alias) == 0
    assert alias == {"HK.HSIMAIN": "HK.HSImain"}


def test_register_code_aliases_all_upper_skipped():
    # 全 upper code（upper == code）唔需要 alias
    alias: dict[str, str] = {}
    assert register_code_aliases([StockEntry("US.AAPL")], alias) == 0
    assert alias == {}


# ---------------------------------------------------------------- canonical_code

def test_canonical_code_case_insensitive():
    c = _catalog()
    assert c.canonical_code("hk.hsimain") == "HK.HSImain"
    assert c.canonical_code("  US.AAPL  ") == "US.AAPL"


def test_canonical_code_unknown_or_empty():
    c = _catalog()
    assert c.canonical_code("ZZZ.NOOPE") is None
    assert c.canonical_code("") is None
    assert c.canonical_code(None) is None


# ---------------------------------------------------------------- resolve_unique（Commit 37：Enter 自動解析）

def test_resolve_unique_exact_suffix():
    """bare '00700' → HK.00700；seed 'hsimain' → HK.HSImain。"""
    c = _catalog()
    assert c.resolve_unique("00700").code == "HK.00700"
    assert c.resolve_unique("HSIMAIN").code == "HK.HSImain"


def test_resolve_unique_exact_code_ci():
    """exact code（CI）rank 0 → canonical entry。"""
    c = _catalog()
    e = c.resolve_unique("hk.00700")
    assert e is not None and e.code == "HK.00700"


def test_resolve_unique_ambiguous_same_rank_none():
    """兩個 entry 同 suffix（rank 1 多義）→ None（留俾 dropdown 揀）。"""
    c = StockCatalog()
    c.replace([StockEntry("HK.XYZ123", "甲", ""), StockEntry("US.XYZ123", "乙", "")])
    assert c.resolve_unique("xyz123") is None


def test_resolve_unique_zero_hits_none():
    c = _catalog()
    assert c.resolve_unique("99999") is None


def test_resolve_unique_prefix_or_substring_never_auto():
    """rank 2+（prefix / substring / fuzzy）一律唔自動解析。"""
    c = _catalog()
    assert c.resolve_unique("us.aap") is None      # code prefix（rank 2）
    assert c.resolve_unique("appl") is None        # en substring（rank 6）


def test_resolve_unique_empty_or_none():
    c = _catalog()
    assert c.resolve_unique("") is None
    assert c.resolve_unique(None) is None
    empty = StockCatalog()
    assert empty.resolve_unique("00700") is None   # 空目錄 → None


# ---------------------------------------------------------------- search ranking

def test_search_exact_code_ci():
    c = _catalog()
    res = c.search("hk.hsimain")
    assert [e.code for e in res] == ["HK.HSImain"]


def test_search_suffix_only():
    c = _catalog()
    assert [e.code for e in c.search("hsimain")] == ["HK.HSImain"]
    assert [e.code for e in c.search("00700")] == ["HK.00700"]


def test_search_code_prefix():
    c = _catalog()
    res = c.search("hk.00")
    assert "HK.00700" in [e.code for e in res]


def test_search_english_exact_and_prefix():
    c = _catalog()
    assert [e.code for e in c.search("TENCENT")] == ["HK.00700"]
    assert [e.code for e in c.search("apple")][0] == "US.AAPL"


def test_search_chinese_traditional_query():
    # 繁中 query → t2s → 命中簡體 index（entry name 預先轉簡體）
    c = _catalog()
    assert [e.code for e in c.search("騰訊控股")] == ["HK.00700"]
    assert [e.code for e in c.search("騰訊")][0] == "HK.00700"


def test_search_code_substring():
    c = _catalog()
    res = c.search("0700")  # rank 5（code substring ≥2）
    assert [e.code for e in res] == ["HK.00700"]


def test_search_english_substring():
    c = _catalog()
    res = c.search("soft")  # rank 6（en substring ≥3，"Microsoft Corp."）
    assert "US.MSFT" in [e.code for e in res]


def test_search_chinese_substring():
    c = _catalog()
    res = c.search("控股")
    assert "HK.00700" in [e.code for e in res]


def test_search_typo_fuzzy_suffix_pass2():
    # pass 1 零命中 → difflib ratio ≥0.8 typo tolerance（hhimain vs hsimain ≈0.857）
    c = _catalog()
    assert [e.code for e in c.search("hhimain")] == ["HK.HSImain"]


def test_search_typo_fuzzy_english_pass2():
    # msftt vs "msft"（suffix）ratio ≈0.889 → US.MSFT
    c = _catalog()
    assert [e.code for e in c.search("msftt")][0] == "US.MSFT"


def test_search_no_match():
    c = _catalog()
    assert c.search("zzzqqqxx") == []


def test_search_empty_or_whitespace_query():
    c = _catalog()
    assert c.search("") == []
    assert c.search("   ") == []
    assert c.search(None) == []  # type: ignore[arg-type]


def test_search_limit():
    entries = [StockEntry(f"US.COMPANY{i:03d}", "", f"Company {i}") for i in range(50)]
    c = StockCatalog()
    c.replace(entries)
    res = c.search("company", limit=7)
    assert len(res) == 7


def test_replace_dedup_ci_first_wins():
    c = StockCatalog()
    c.replace([StockEntry("US.AAPL", "苹果"), StockEntry("us.aapl", "Apple dup")])
    assert len(c) == 1
    assert c.entries[0].name_cn == "苹果"


def test_search_empty_catalog():
    c = StockCatalog()
    assert c.search("aapl") == []


# ---------------------------------------------------------------- performance

def test_search_perf_13k_entries_under_2s():
    # ~13k entries（HK+US 實際規模）每次 keystroke pass-1 O(n) 必須頂得順
    entries = [StockEntry(f"US.SYM{i:05d}", f"股票名稱{i}", f"Sym Corp {i}") for i in range(13000)]
    c = StockCatalog()
    t0 = time.perf_counter()
    c.replace(entries)
    assert len(c) == 13000
    # pass-1 hit（prefix）+ pass-2 typo（零命中觸發 difflib 全掃）都要快
    for _ in range(5):
        assert c.search("US.SYM")
        assert c.search("symzzz99999") is not None
    elapsed = time.perf_counter() - t0
    assert elapsed < 2.0, f"13k entries search too slow: {elapsed:.3f}s"
