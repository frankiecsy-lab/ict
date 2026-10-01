"""股票目錄與模糊搜尋（autocomplete 後端，純類零 Qt/futu 依賴）。

資料來源：futu `get_stock_basicinfo(Market.HK/US)`——`code` 係**嚴格大小寫**嘅正規形式
（例如主力連續合約 `HK.HSImain`），`name` 中文名、`english_name` 英文名。
目錄由 engine setup thread 一次性 fetch（嚴禁 per-keystroke 打 API）。

模糊搜尋設計（rank-based，兩段式）:
- Pass 1（O(n) 單遍）：exact code → suffix exact → code prefix → en exact/prefix →
  cn(簡體化) exact/prefix → code substring(≥2) → en substring(≥3) → cn substring；
- Pass 2（只有 pass 1 零命中先至行，避免 ~13k × difflib 常規開銷）：
  difflib SequenceMatcher ratio ≥0.8 typo tolerance（suffix / en / cn）。

簡繁互換：query 每次 keystroke 做一次 t2s（OpenCC），entry 中文名喺 replace() build index
時預先轉簡體存低——唔會 per-keystroke 對 ~13k entries 做轉換。OpenCC import 失敗 → identity fallback。
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass

_FUZZY_MIN_RATIO = 0.8

_cc = None
_cc_failed = False


def to_simplified(text: str) -> str:
    """Traditional → Simplified（OpenCC t2s）；ASCII/簡體原樣通過；import 失敗 identity fallback。"""
    global _cc, _cc_failed
    if not text or _cc_failed:
        return text
    if _cc is None:
        try:
            from opencc import OpenCC
            _cc = OpenCC("t2s")
        except Exception:  # noqa: BLE001 — OpenCC 缺失 → identity（繁中 query 會少啲命中）
            _cc_failed = True
            return text
    return _cc.convert(text)


@dataclass(frozen=True)
class StockEntry:
    """單隻股票：code 保留 API 返回嘅嚴格大小寫正規形式。

    lot_size = 每手股數（期貨 = 合約乘數）；listing_date = 'yyyy-MM-dd'（API 已停止維護但仍有返回）。
    """

    code: str
    name_cn: str = ""
    name_en: str = ""
    lot_size: int | None = None
    listing_date: str = ""

    @property
    def suffix(self) -> str:
        return self.code.split(".", 1)[1] if "." in self.code else self.code


def display_text(e: StockEntry) -> str:
    """Dropdown 顯示行：`CODE  中文名  英文名`（空欄位略過）。"""
    parts = [e.code]
    if e.name_cn:
        parts.append(e.name_cn)
    if e.name_en:
        parts.append(e.name_en)
    return "  ".join(parts)


def name_text(e: StockEntry) -> str:
    """名稱部分（獨立 LABEL 顯示用，輸入欄只留 code）：`中文名 英文名`（空欄位略過、全缺 → 空字串）。"""
    return " ".join(p for p in (e.name_cn, e.name_en) if p)


def basic_info_text(e: StockEntry) -> str:
    """基本資料行（標的輸入欄下方 LABEL）：`每手 N · 上市 yyyy-MM-dd`。

    空欄位略過、全缺 → 空字串（seed 主力連續合約等無此數據時唔顯示）。
    """
    parts = []
    if e.lot_size is not None:
        parts.append(f"每手 {e.lot_size}")
    if e.listing_date:
        parts.append(f"上市 {e.listing_date}")
    return " · ".join(parts)


def register_code_aliases(entries, alias_map: dict[str, str]) -> int:
    """將大小寫敏感嘅正規 code 註冊入 alias table（upper form → canonical）。

    純函數：engine 傳自己嘅 `_CODE_ALIASES` 入嚟，保持 engine dict private。
    返回新增/更新嘅條目數。
    """
    n = 0
    for e in entries:
        upper = e.code.upper()
        if upper != e.code and alias_map.get(upper) != e.code:
            alias_map[upper] = e.code
            n += 1
    return n


def _fuzzy_ratio(a: str, b: str) -> float:
    """SequenceMatcher ratio + length-gap 預篩（gap 太大 ratio 唔可能達標 → 直接 0）。"""
    la, lb = len(a), len(b)
    if not la or not lb:
        return 0.0
    if abs(la - lb) > max(2, min(la, lb)):
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


class StockCatalog:
    """Immutable snapshot 股票目錄 + rank-based 模糊搜尋。

    replace() 預先計算每 entry 嘅 index tuple（code_l / suffix_l / en_l / cn_s），
    search() 單遍 O(n)——~13k entries 每次 keystroke 都頂得順。
    """

    def __init__(self) -> None:
        self._entries: tuple[StockEntry, ...] = ()
        self._idx: tuple[tuple[str, str, str, str], ...] = ()
        self._code_ci: dict[str, str] = {}

    def replace(self, entries) -> None:
        """整批替換目錄（engine fetch 完一次過入）。重覆 code（CI）保留首條。"""
        kept: list[StockEntry] = []
        idx: list[tuple[str, str, str, str]] = []
        code_ci: dict[str, str] = {}
        seen: set[str] = set()
        for e in entries:
            key = e.code.lower()
            if key in seen:
                continue
            seen.add(key)
            code_ci[key] = e.code
            kept.append(e)
            idx.append((key, e.suffix.lower(), (e.name_en or "").strip().lower(),
                        to_simplified(e.name_cn or "")))
        self._entries = tuple(kept)
        self._idx = tuple(idx)
        self._code_ci = code_ci

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> tuple[StockEntry, ...]:
        return self._entries

    def canonical_code(self, raw: str | None) -> str | None:
        """Case-insensitive exact code → 嚴格大小寫正規形式；未知/空 → None。"""
        if not raw:
            return None
        return self._code_ci.get(raw.strip().lower())

    def search(self, query: str, limit: int = 20) -> list[StockEntry]:
        """模糊搜尋：rank-based 兩段式（見 module docstring）。返回按 rank 排序嘅 entries。"""
        q = (query or "").strip()
        if not q or not self._entries:
            return []
        ql = q.lower()
        qs = to_simplified(q).lower()
        hits: list[tuple[int, int]] = []
        for i, (code_l, suffix_l, en_l, cn_s) in enumerate(self._idx):
            if code_l == ql:
                rank = 0
            elif suffix_l == ql:
                rank = 1
            elif code_l.startswith(ql):
                rank = 2
            elif en_l and (en_l == ql or en_l.startswith(ql)):
                rank = 3
            elif cn_s and (cn_s == qs or cn_s.startswith(qs)):
                rank = 4
            elif len(ql) >= 2 and ql in code_l:
                rank = 5
            elif len(ql) >= 3 and en_l and ql in en_l:
                rank = 6
            elif cn_s and qs in cn_s:
                rank = 7
            else:
                continue
            hits.append((rank, i))
        if hits:
            hits.sort(key=lambda t: t[0])  # stable → 同 rank 內保持目錄順序
            return [self._entries[i] for _, i in hits[:limit]]
        # Pass 2：typo tolerance（只有 pass 1 零命中先至行）
        if len(ql) < 2:
            return []
        scored: list[tuple[float, int]] = []
        for i, (code_l, suffix_l, en_l, cn_s) in enumerate(self._idx):
            best = _fuzzy_ratio(ql, suffix_l)
            if en_l and (r := _fuzzy_ratio(ql, en_l)) > best:
                best = r
            if cn_s and qs != ql and (r := _fuzzy_ratio(qs, cn_s)) > best:
                best = r
            if best >= _FUZZY_MIN_RATIO:
                scored.append((best, i))
        scored.sort(key=lambda t: (-t[0], t[1]))
        return [self._entries[i] for _, i in scored[:limit]]
