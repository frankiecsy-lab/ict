"""engine/indicators.py 純邏輯單測（零 Qt/futu 依賴）。

覆蓋：FVG bullish/bearish/無 gap（touching）/fill/unfilled/multiple；
OB 觸發 + 最近反向線選擇 + body 邊界 + 失效 + doji skip + weak bar no-trigger + dedup；
confluence 同向重疊 / 無價格重疊 / 異向排除 / 時間區間無交集 / end 邊界取 min；
VOB 有效訂單塊 bullish/bearish + 無掃蕩拒收 + FVG 無重疊拒收 + OB 已失效拒收；
Breaker bullish/bearish OB 翻轉 + mitigation + 冇失效唔算 breaker + dedup；
Kill Zones EST/EDT（DST）session 分類 + band 分組 + 非 intraday skip；
Daily ref lines DO 線段 + PH/PL/PC 全寬線 + 單日無 prev day + monthly key skip。

Bar = (time_key, open, high, low, close, volume)——FVG/OB/Breaker 偵測邏輯唔用
time_key（全部 case 共用同一 fake key）；Kill Zones / Daily ref lines 讀 time_key。
"""
from __future__ import annotations

from engine.indicators import (Level, Marker, RefLine, Zone, confluence_zones, daily_reference_lines,
                               detect_breaker_blocks, detect_fvg, detect_liquidity_levels,
                               detect_order_blocks, detect_structure_breaks,
                               detect_valid_order_blocks, kill_zone_bands)


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


# ---------------------------------------------------------------- Breaker Block

def test_breaker_bullish_ob_flips_to_bearish():
    """bullish OB [10.1,10.4]（origin=b1 body）被 b3 close(9.6)<下界失效 → bearish breaker
    start=3；b4 close(10.5)>上界 10.4 mitigation → end_idx=4。"""
    bars = (bar(10.0, 10.5, 9.8, 10.2),
            bar(10.4, 10.6, 10.0, 10.1),   # bearish origin，body [10.1, 10.4]
            bar(10.1, 11.2, 10.0, 11.0),   # strong BOS up trigger（i=2）
            bar(10.9, 11.0, 9.5, 9.6),     # close < 10.1 → 失效 k=3
            bar(9.7, 10.6, 9.5, 10.5))     # close > 10.4 → mitigation end=4
    assert detect_breaker_blocks(bars) == (Zone("breaker", "bearish", 3, 4, 10.4, 10.1),)


def test_breaker_bearish_ob_flips_to_bullish():
    """bearish OB [10.0,10.3]（origin=b1 body）被 b3 high(10.5)>上界失效 → bullish breaker
    start=3；b4 close(9.8)<下界 10.0 mitigation → end_idx=4。"""
    bars = (bar(10.0, 10.5, 9.8, 10.2),
            bar(10.0, 10.4, 9.9, 10.3),    # bullish origin，body [10.0, 10.3]
            bar(10.3, 10.4, 9.0, 9.2),     # strong BOS down trigger（i=2）
            bar(9.3, 10.5, 9.2, 10.4),     # high > 10.3 → 失效 k=3
            bar(10.2, 10.3, 9.7, 9.8))     # close < 10.0 → mitigation end=4
    assert detect_breaker_blocks(bars) == (Zone("breaker", "bullish", 3, 4, 10.3, 10.0),)


def test_breaker_unmitigated_stays_open():
    """失效後冇 bar 收返去 zone 另一邊 → end_idx=None（畫到右緣）。"""
    bars = (bar(10.0, 10.5, 9.8, 10.2),
            bar(10.4, 10.6, 10.0, 10.1),   # bearish origin，body [10.1, 10.4]
            bar(10.1, 11.2, 10.0, 11.0),   # trigger i=2
            bar(10.9, 11.0, 9.5, 9.6))     # close < 10.1 → k=3、之後冇 bar → end=None
    assert detect_breaker_blocks(bars) == (Zone("breaker", "bearish", 3, None, 10.4, 10.1),)


def test_ob_without_invalidation_is_not_breaker():
    """OB 觸發但後續冇失效（價格一直喺 body 上）→ 只係普通 OB、唔產生 breaker。"""
    bars = (bar(10.0, 10.5, 9.8, 10.2),
            bar(10.4, 10.6, 10.0, 10.1),   # bearish origin，body [10.1, 10.4]
            bar(10.1, 11.2, 10.0, 11.0),   # trigger i=2
            bar(10.5, 11.5, 10.4, 11.4))   # close > 下界 → 冇失效
    assert detect_breaker_blocks(bars) == ()


def test_breaker_dedup_same_origin():
    """兩根強線指向同一 origin j=1 → 只記錄一次；失效喺 b4（close 9.7<10.1）→ k=4、end=None。"""
    bars = (bar(10.0, 10.5, 9.8, 10.2),
            bar(10.4, 10.6, 10.0, 10.1),   # bearish origin，body [10.1, 10.4]
            bar(10.1, 11.2, 10.0, 11.0),   # trigger i=2 → origin j=1
            bar(11.0, 12.4, 10.9, 12.3),   # trigger i=3 → 同 origin → dedup
            bar(12.0, 12.5, 9.6, 9.7))     # close < 10.1 → k=4
    assert detect_breaker_blocks(bars) == (Zone("breaker", "bearish", 4, None, 10.4, 10.1),)


def test_breaker_empty_and_single_bar():
    """空 / 單根 → 無 trigger 可能 → ()。"""
    assert detect_breaker_blocks(()) == ()
    assert detect_breaker_blocks((bar(1, 2, 0.5, 1.5),)) == ()


# ---------------------------------------------------------------- Kill Zones

def _kz_bar(t: str):
    """Kill Zone bar（time_key = HKT naive 'yyyy-MM-dd HH:mm'）。"""
    return (t, 100.0, 101.0, 99.5, 100.5, 1000.0)


def test_kill_zones_est_winter_sessions():
    """EST（HKT−ET=780min）：09:30→ET20:30 asia、12:00→ET23:00 asia、13:00→ET00:00 無、
    15:00→ET02:00 london、17:30→ET04:30 london、18:00→ET05:00 無 → 兩個 band。"""
    bars = tuple(_kz_bar(f"2026-01-15 {t}") for t in
                 ("09:30", "12:00", "13:00", "15:00", "17:30", "18:00"))
    assert kill_zone_bands(bars) == ((0, 1, "asia"), (3, 4, "london"))


def test_kill_zones_edt_summer_sessions():
    """EDT（HKT−ET=720min，DST）：09:30→ET21:30 asia、14:00→ET02:00 london。"""
    bars = (_kz_bar("2026-07-15 09:30"), _kz_bar("2026-07-15 14:00"))
    assert kill_zone_bands(bars) == ((0, 0, "asia"), (1, 1, "london"))


def test_kill_zones_all_four_sessions():
    """EST 一日覆蓋全部四個 session：asia / new_york / london_close（隔日）/ london。"""
    bars = (_kz_bar("2026-01-15 09:30"),   # ET 20:30 → asia
            _kz_bar("2026-01-15 20:30"),   # ET 07:30 → new_york
            _kz_bar("2026-01-15 23:30"),   # ET 10:30 → london_close
            _kz_bar("2026-01-16 15:00"))   # ET 02:00 → london（隔日、session 變化開新 band）
    assert kill_zone_bands(bars) == (
        (0, 0, "asia"), (1, 1, "new_york"), (2, 2, "london_close"), (3, 3, "london"))


def test_kill_zones_non_intraday_keys_skipped():
    """K_DAY（'yyyy-MM-dd'，長度 10）/ K_MON（'yyyy-MM'，長度 7）→ session 無意義 → ()。"""
    day_bars = tuple(_kz_bar(f"2026-09-{d:02d}") for d in (28, 29, 30))
    mon_bars = (_kz_bar("2026-08"), _kz_bar("2026-09"))
    assert kill_zone_bands(day_bars) == ()
    assert kill_zone_bands(mon_bars) == ()


def test_kill_zones_empty():
    """空 bars → ()。"""
    assert kill_zone_bands(()) == ()


# ---------------------------------------------------------------- Daily reference lines

def test_daily_ref_lines_multi_day():
    """兩日數據：DO 線段各跨當日；PH/PL/PC = 前一交易日（09-30）high max / low min / close。"""
    bars = (bar(10.0, 10.5, 9.8, 10.2, t="2026-09-30 09:30"),
            bar(10.2, 10.6, 10.0, 10.4, t="2026-09-30 10:00"),
            bar(10.5, 10.7, 10.1, 10.6, t="2026-10-01 09:30"))
    assert daily_reference_lines(bars) == (
        RefLine("do", 10.0, 0, 1),
        RefLine("do", 10.5, 2, 2),
        RefLine("ph", 10.6, 0, None),
        RefLine("pl", 9.8, 0, None),
        RefLine("pc", 10.4, 0, None),
    )


def test_daily_ref_lines_single_day_no_prev():
    """單日 → 只有 DO（無前一交易日 → PH/PL/PC 唔存在）。"""
    bars = (bar(10.0, 10.5, 9.8, 10.2, t="2026-09-30 09:30"),
            bar(10.2, 10.6, 10.0, 10.4, t="2026-09-30 10:00"))
    assert daily_reference_lines(bars) == (RefLine("do", 10.0, 0, 1),)


def test_daily_ref_lines_monthly_keys_skipped():
    """K_MON（'yyyy-MM'，長度 < 10）→ 無日級概念 → ()。"""
    bars = (_kz_bar("2026-08"), _kz_bar("2026-09"))
    assert daily_reference_lines(bars) == ()


def test_daily_ref_lines_empty():
    """空 bars → ()。"""
    assert daily_reference_lines(()) == ()


# ---------------------------------------------------------------- Valid Order Blocks (VOB)

def _vob_bullish_bars():
    """8-bar bullish VOB 序列：整固 → sweep low 8.9（s=3）→ origin 陰線 j=4 body [9.3,9.6]
    → 小陽 c1（high 9.5 喺 OB 範圍內）→ trigger i=6 BOS up → FVG@7 = [high(b5)=9.5, low(b7)=9.8]。"""
    return (bar(10.0, 10.2, 9.9, 10.1),   # b0 整固
            bar(10.1, 10.3, 10.0, 10.2),  # b1 整固
            bar(10.2, 10.4, 9.8, 9.9),    # b2 陰線（prior_high=10.4）
            bar(9.9, 10.0, 8.9, 9.5),     # b3 sweep：low 8.9 = 窗口新低且之後再冇跌穿
            bar(9.6, 9.7, 9.2, 9.3),      # b4 origin 陰線 → OB body [9.3, 9.6]
            bar(9.3, 9.5, 9.2, 9.4),      # b5 小陽 c1（high 9.5 喺 OB 範圍內）
            bar(9.4, 11.2, 9.3, 11.1),    # b6 trigger i=6：BOS up（c>10.4）+ body ≥ range/2
            bar(11.1, 11.5, 9.8, 11.2))   # b7 → bullish FVG@7 [9.5, 9.8] 同 OB 嚴格重疊


def test_vob_bullish_valid():
    """三重過濾全過（sweep + 未失效 + FVG 重疊）→ 完整 OB body vob zone。"""
    assert detect_valid_order_blocks(_vob_bullish_bars()) == \
        (Zone("vob", "bullish", 4, None, 9.6, 9.3),)


def test_vob_bearish_mirror():
    """價格軸鏡像序列 → bearish VOB（sweep high 11.1 + origin 陽線 body [10.4,10.7] + FVG@7 重疊）。"""
    bars = (bar(10.0, 10.1, 9.8, 9.9), bar(9.9, 10.0, 9.7, 9.8),
            bar(9.8, 10.2, 9.6, 10.1), bar(10.1, 11.1, 10.0, 10.5),
            bar(10.4, 10.8, 10.3, 10.7), bar(10.7, 10.8, 10.5, 10.6),
            bar(10.6, 10.7, 8.8, 8.9), bar(8.9, 10.2, 8.5, 8.8))
    assert detect_valid_order_blocks(bars) == \
        (Zone("vob", "bearish", 4, None, 10.7, 10.4),)


def test_vob_rejected_without_sweep():
    """b3 low 改 9.7（無窗口新低 → 無流動性掃蕩）→ OB 存在但唔有效。"""
    bars = _vob_bullish_bars()[:3] + (bar(9.9, 10.0, 9.7, 9.5),) + _vob_bullish_bars()[4:]
    assert detect_valid_order_blocks(bars) == ()


def test_vob_rejected_without_fvg_overlap():
    """b5 high 改 9.7 → FVG@7 = [9.7, 9.8] 存在但同 OB body [9.3,9.6] 無價格重疊 → 唔有效。"""
    bars = _vob_bullish_bars()[:5] + (bar(9.3, 9.7, 9.2, 9.4),) + _vob_bullish_bars()[6:]
    assert detect_valid_order_blocks(bars) == ()


def test_vob_rejected_when_ob_invalidated():
    """加 b8 close=9.1 < bottom 9.3 → OB 已失效（end_idx=8，屬 Breaker 層）→ 唔有效。"""
    bars = _vob_bullish_bars() + (bar(11.0, 11.1, 9.0, 9.1),)
    assert detect_valid_order_blocks(bars) == ()


def test_vob_empty_and_short():
    """空 / 單根 → 無 OB 可形成 → ()。"""
    assert detect_valid_order_blocks(()) == ()
    assert detect_valid_order_blocks((bar(1, 2, 0.5, 1.5),)) == ()


# ---------------------------------------------------------------- Liquidity Levels (BSL/SSL)

def _liq_bars():
    """16-bar 序列（pivot=3）：兩個 swing high @3/@9 同價 12 → BSL；兩個 swing low @5/@10
    同價 9 → SSL。last_close=10.5（BSL 12 > 10.5、SSL 9 < 10.5）。"""
    return (bar(9.6, 10, 9.5, 9.8),      # b0
            bar(9.9, 11, 9.8, 10.4),     # b1
            bar(10.1, 11.5, 10, 11.2),   # b2
            bar(10.3, 12, 10.2, 11.8),   # b3 swing high @3（high=12）
            bar(11.4, 11.5, 10, 10.6),   # b4
            bar(10.2, 11, 9, 9.3),       # b5 swing low @5（low=9）
            bar(9.9, 10.5, 9.8, 10.4),   # b6
            bar(10.1, 11, 10, 10.8),     # b7
            bar(10.3, 11.5, 10.2, 11.3), # b8
            bar(10.4, 12, 10, 11.7),     # b9 swing high @9（high=12）
            bar(11.4, 11.5, 9, 9.4),     # b10 swing low @10（low=9）
            bar(9.9, 11, 9.8, 10.7),     # b11
            bar(10.1, 10.5, 10, 10.4),   # b12
            bar(10.3, 11, 10.2, 10.9),   # b13
            bar(10.1, 11.5, 10, 11.3),   # b14
            bar(10.6, 11, 9.6, 10.5))    # b15 last_close=10.5


def test_liquidity_bsl_and_ssl_pools():
    """兩個 equal highs（@3/@9 同價 12）→ BSL；兩個 equal lows（@5/@10 同價 9）→ SSL。"""
    assert detect_liquidity_levels(_liq_bars()) == (
        Level("bsl", 12.0, 3, None),
        Level("ssl", 9.0, 5, None),
    )


def test_liquidity_no_pool_when_highs_not_equal():
    """b9 high 改 11.8（唔再同 b3 嘅 12 聚類）→ BSL 消失，只餘 SSL。"""
    bars = _liq_bars()[:9] + (bar(10.4, 11.8, 10, 11.7),) + _liq_bars()[10:]
    assert detect_liquidity_levels(bars) == (Level("ssl", 9.0, 5, None),)


def test_liquidity_single_touch_not_a_pool():
    """min_touches=3 → 只有兩個觸及嘅池唔夠 → ()。"""
    assert detect_liquidity_levels(_liq_bars(), min_touches=3) == ()


def test_liquidity_empty_and_short():
    """空 / 單根 / 少於 2*pivot+1（7）bar → 無 pivot 可判斷 → ()。"""
    assert detect_liquidity_levels(()) == ()
    assert detect_liquidity_levels((bar(1, 2, 0.5, 1.5),)) == ()
    six = tuple(bar(10 + i * 0.1, 11 + i * 0.1, 9 + i * 0.1, 10.5 + i * 0.1) for i in range(6))
    assert detect_liquidity_levels(six) == ()


# ---------------------------------------------------------------- Structure Breaks (BOS / CHoCH)

def _bos_choch_bars():
    """12-bar 序列（k=2）：swing high @2（high=12，i=4 確認）→ b5 close 12.6 > 12 → BOS up @5
    （建立 uptrend、consumed）。之後 pullback 形成 swing low @8（low=12.4，i=10 確認）→
    b11 close 12.3 < 12.4 → CHoCH down @11（首次逆勢 = 反轉）。"""
    return (bar(10.0, 10.5, 9.8, 10.3),   # b0
            bar(10.3, 11.2, 10.2, 11.0),  # b1
            bar(11.0, 12.0, 10.9, 11.6),  # b2 swing high @2（high=12）
            bar(11.6, 11.8, 11.5, 11.7),  # b3
            bar(11.7, 11.9, 11.6, 11.8),  # b4（i=4 確認 s=2 → last_sh=(12,2)）
            bar(11.8, 13.0, 11.7, 12.6),  # b5 close 12.6 > 12 → BOS up @5
            bar(12.6, 13.4, 12.5, 13.2),  # b6
            bar(13.2, 13.8, 12.9, 13.6),  # b7
            bar(13.6, 13.7, 12.4, 13.0),  # b8 swing low @8（low=12.4）
            bar(13.0, 13.9, 12.8, 13.7),  # b9
            bar(13.7, 14.0, 13.0, 13.9),  # b10（i=10 確認 s=8 → last_sl=(12.4,8)）
            bar(13.9, 14.0, 12.2, 12.3))  # b11 close 12.3 < 12.4 → CHoCH down @11


def _bos_continuation_bars():
    """11-bar 序列（k=2）：swing high @2（high=12，i=4 確認）→ b5 close 12.6 > 12 → BOS up @5。
    pullback 形成更高 swing high @7（high=13.8，i=9 確認）→ b10 close 14.0 > 13.8 →
    BOS up @10（順勢延續、第二個結構 break）。"""
    return (bar(10.0, 10.5, 9.8, 10.3),   # b0
            bar(10.3, 11.2, 10.2, 11.0),  # b1
            bar(11.0, 12.0, 10.9, 11.6),  # b2 swing high @2（high=12）
            bar(11.6, 11.8, 11.5, 11.7),  # b3
            bar(11.7, 11.9, 11.6, 11.8),  # b4（i=4 確認 s=2 → last_sh=(12,2)）
            bar(11.8, 13.0, 11.7, 12.6),  # b5 close 12.6 > 12 → BOS up @5
            bar(12.6, 13.4, 12.5, 13.2),  # b6
            bar(13.2, 13.8, 12.9, 13.6),  # b7 swing high @7（high=13.8）
            bar(13.6, 13.7, 12.4, 13.5),  # b8
            bar(13.5, 13.6, 12.8, 13.4),  # b9（i=9 確認 s=7 → last_sh=(13.8,7)）
            bar(13.4, 14.2, 13.3, 14.0))  # b10 close 14.0 > 13.8 → BOS up @10


def test_structure_bos_up_then_choch_down():
    """順勢突破建立 uptrend（BOS up）→ 首次逆勢跌破 swing low = CHoCH down（反轉）。"""
    assert detect_structure_breaks(_bos_choch_bars()) == (
        Marker("bos", "up", 5),
        Marker("choch", "down", 11),
    )


def test_structure_bos_continuation():
    """uptrend 內兩個更高 swing high 各被突破 → 兩個 BOS up（順勢延續、唔係 CHoCH）。"""
    assert detect_structure_breaks(_bos_continuation_bars()) == (
        Marker("bos", "up", 5),
        Marker("bos", "up", 10),
    )


def test_structure_empty_and_short():
    """空 / 少於 2*k+1（k=2 → 5）bar → 無 pivot 可確認 → ()。"""
    assert detect_structure_breaks(()) == ()
    four = tuple(bar(10 + i * 0.1, 11 + i * 0.1, 9 + i * 0.1, 10.5 + i * 0.1) for i in range(4))
    assert detect_structure_breaks(four) == ()
