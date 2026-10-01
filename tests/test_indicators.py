"""engine/indicators.py 純邏輯單測（零 Qt/futu 依賴）。

覆蓋：FVG bullish/bearish/無 gap（touching）/fill/unfilled/multiple；
OB 觸發 + 最近反向線選擇 + body 邊界 + 失效 + doji skip + weak bar no-trigger + dedup；
confluence 同向重疊 / 無價格重疊 / 異向排除 / 時間區間無交集 / end 邊界取 min。

Bar = (time_key, open, high, low, close, volume)——偵測邏輯唔用 time_key，
全部 case 共用同一 fake key（重複 key 合法）。
"""
from __future__ import annotations

from engine.indicators import Zone, confluence_zones, detect_fvg, detect_order_blocks


def bar(o: float, h: float, l: float, c: float, v: float = 1000.0,
        t: str = "2026-09-30 09:00"):
    """Bar tuple（time_key 固定——偵測邏輯唔讀佢）。"""
    return (t, o, h, l, c, v)


# ---------------------------------------------------------------- FVG

def test_fvg_bullish_basic():
    """c1.high(10) < c3.low(11) → bullish gap [10, 11]，自第三根向右、未填補 end=None。"""
    bars = (bar(9, 10, 8.5, 9.5), bar(9.5, 10.5, 9, 10.4), bar(10.5, 12, 11, 11.8))
    assert detect_fvg(bars) == (Zone("fvg", "bullish", 2, None, 11.0, 10.0),)


def test_fvg_bearish_basic():
    """c1.low(20) > c3.high(19) → bearish gap [19, 20]。"""
    bars = (bar(21, 22, 20, 20.5), bar(20.5, 21, 18.5, 19), bar(18.5, 19, 17, 17.5))
    assert detect_fvg(bars) == (Zone("fvg", "bearish", 2, None, 20.0, 19.0),)


def test_fvg_no_gap_when_touching():
    """c1.high == c3.low（touching、無失衡空間）→ 唔算 FVG。"""
    bars = (bar(9, 10, 8.5, 9.5), bar(9.5, 10.5, 9, 10.4), bar(10, 12, 10, 11.8))
    assert detect_fvg(bars) == ()


def test_fvg_empty_and_short_sequences():
    """空 / 單根 / 兩根 → 無三根 K 線可判斷 → ()。"""
    assert detect_fvg(()) == ()
    assert detect_fvg((bar(1, 2, 0.5, 1.5),)) == ()
    assert detect_fvg((bar(1, 2, 0.5, 1.5), bar(1.5, 3, 1, 2.5))) == ()


def test_fvg_filled_terminates_zone():
    """bullish FVG [10,11]@2 → 後續 bar low(9.9) ≤ 下界 10 → end_idx=3（完全填補）。"""
    bars = (bar(9, 10, 8.5, 9.5), bar(9.5, 10.5, 9, 10.4),
            bar(10.5, 12, 11, 11.8), bar(11, 11.5, 9.9, 10.2))
    assert detect_fvg(bars) == (Zone("fvg", "bullish", 2, 3, 11.0, 10.0),)


def test_fvg_unfilled_stays_open():
    """後續 bar low(10.5) > 下界 10 → 未填補 → end_idx=None（畫到右緣）。"""
    bars = (bar(9, 10, 8.5, 9.5), bar(9.5, 10.5, 9, 10.4),
            bar(10.5, 12, 11, 11.8), bar(11, 12, 10.5, 11.5))
    assert detect_fvg(bars) == (Zone("fvg", "bullish", 2, None, 11.0, 10.0),)


def test_fvg_multiple_zones_mixed_fill():
    """兩個獨立 gap：第一個被填補（end=3）、第二個仍活躍；中間無 gap 嘅 triple 唔計。"""
    bars = (bar(9, 10, 8.5, 9.5),      # i=2: c1.high=10 < c3.low=11 → FVG [10,11]@2
            bar(9.5, 10.5, 9, 10.4),
            bar(10.5, 12, 11, 11.8),
            bar(10.2, 11, 9.8, 10.6),  # i=3/4: overlap、無 gap；low=9.8 ≤ 10 → 填補 FVG@2
            bar(10.6, 12.5, 10.4, 12.2),
            bar(12.8, 15, 12.6, 14.5))  # i=5: c1.high=11 < c3.low=12.6 → FVG [11,12.6]@5
    assert detect_fvg(bars) == (
        Zone("fvg", "bullish", 2, 3, 11.0, 10.0),
        Zone("fvg", "bullish", 5, None, 12.6, 11.0),
    )


# ---------------------------------------------------------------- Order Block

def test_ob_bullish_trigger_and_origin():
    """強陽線 BOS up（close 11.9 > prior_high 10.5、body ≥ range/2）→
    最近一根陰線 j=1 → OB = 該陰線 body [9.8, 10.2]，start_idx=1。"""
    bars = (bar(10, 10.5, 9.8, 10.2),   # bullish（唔係 origin）
            bar(10.2, 10.3, 9.7, 9.8),  # bearish → origin，body [9.8, 10.2]
            bar(9.9, 12, 9.85, 11.9))   # strong BOS up trigger
    assert detect_order_blocks(bars) == (Zone("ob", "bullish", 1, None, 10.2, 9.8),)


def test_ob_invalidated_by_close_beyond_body():
    """後續 bar close(9.75) < body 下界 9.8 → end_idx=3；該 bar 本身唔係 trigger。"""
    bars = (bar(10, 10.5, 9.8, 10.2),
            bar(10.2, 10.3, 9.7, 9.8),
            bar(9.9, 12, 9.85, 11.9),   # trigger → OB [9.8, 10.2]@1
            bar(10.5, 10.6, 9.7, 9.75))  # close < 9.8 → 失效 @3（c=9.75 ≥ prior_low 9.7、唔係 trigger）
    assert detect_order_blocks(bars) == (Zone("ob", "bullish", 1, 3, 10.2, 9.8),)


def test_ob_skips_doji_when_scanning_back():
    """向前掃時 doji（c==o、唔陰唔陽）跳過 → origin = 再前面嗰根真陰線 j=0。"""
    bars = (bar(10, 10.4, 9.6, 9.7),   # bearish → origin，body [9.7, 10]
            bar(9.8, 10.2, 9.75, 9.8),  # doji（c==o）→ skip
            bar(9.9, 13, 9.85, 12.9))   # strong BOS up trigger
    assert detect_order_blocks(bars) == (Zone("ob", "bullish", 0, None, 10.0, 9.7),)


def test_ob_weak_bar_no_trigger():
    """body(0.5) < range/2（2.625）→ 唔算強線、唔觸發 OB（即使 close 突破 prior_high）。"""
    bars = (bar(10, 10.2, 9.8, 10.1),
            bar(10.1, 10.15, 9.6, 9.85),  # c=9.85 ≥ prior_low 9.8 → 本身唔係 trigger
            bar(9.8, 15, 9.75, 10.3))     # body=0.5 < 2.625 → no trigger（c=10.3 > prior_high 但弱線）
    assert detect_order_blocks(bars) == ()


def test_ob_dedup_same_origin():
    """連續兩根強線都指向同一 origin j=0 → 只記錄一次（避免重疊矩形）。"""
    bars = (bar(10, 10.3, 9.6, 9.7),   # bearish → origin，body [9.7, 10]
            bar(9.8, 12, 9.75, 11.9),  # strong BOS up → OB@0
            bar(11.9, 14, 11.85, 13.9))  # strong BOS up → origin 已見 → dedup
    assert detect_order_blocks(bars) == (Zone("ob", "bullish", 0, None, 10.0, 9.7),)


def test_ob_empty_and_single_bar():
    """空 / 單根 → 無 trigger 可能 → ()。"""
    assert detect_order_blocks(()) == ()
    assert detect_order_blocks((bar(1, 2, 0.5, 1.5),)) == ()


# ---------------------------------------------------------------- Confluence

def test_confluence_same_side_overlap():
    """同向 OB [9.8,10.2]@1 + FVG [10.0,11.0]@2 → 重疊帶 [10.0,10.2]，start=max=2、end=None。"""
    ob = (Zone("ob", "bullish", 1, None, 10.2, 9.8),)
    fvg = (Zone("fvg", "bullish", 2, None, 11.0, 10.0),)
    assert confluence_zones(ob, fvg) == (Zone("confluence", "bullish", 2, None, 10.2, 10.0),)


def test_confluence_no_price_overlap():
    """價格區間無重疊（OB [9.8,10.2] vs FVG [10.5,11.0]）→ ()。"""
    ob = (Zone("ob", "bullish", 1, None, 10.2, 9.8),)
    fvg = (Zone("fvg", "bullish", 2, None, 11.0, 10.5),)
    assert confluence_zones(ob, fvg) == ()


def test_confluence_opposite_sides_excluded():
    """異向重疊唔算共鳴（bullish OB + bearish FVG 互相矛盾）→ ()。"""
    ob = (Zone("ob", "bullish", 1, None, 10.2, 9.8),)
    fvg = (Zone("fvg", "bearish", 2, None, 10.5, 10.0),)
    assert confluence_zones(ob, fvg) == ()


def test_confluence_temporal_non_overlap():
    """OB 已喺 FVG 開始前失效（end=5 < start=max(1,10)=10）→ 時間無交集 → ()。"""
    ob = (Zone("ob", "bullish", 1, 5, 10.2, 9.8),)
    fvg = (Zone("fvg", "bullish", 10, None, 11.0, 10.0),)
    assert confluence_zones(ob, fvg) == ()


def test_confluence_end_takes_min():
    """OB 活躍（end=None）+ FVG 已填補（end=7）→ 重疊帶 end=min(None,7)=7。"""
    ob = (Zone("ob", "bullish", 1, None, 10.2, 9.8),)
    fvg = (Zone("fvg", "bullish", 2, 7, 11.0, 10.0),)
    assert confluence_zones(ob, fvg) == (Zone("confluence", "bullish", 2, 7, 10.2, 10.0),)
