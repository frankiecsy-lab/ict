"""ICT 指標偵測純邏輯（零 Qt/futu 依賴，可獨立單測）。

定義參考標準 ICT / TradingView 圖層慣例：

- **FVG（Fair Value Gap）**：三根 K 線失衡——bullish 當 c1.high < c3.low →
  gap 區間 [c1.high, c3.low]；bearish 對稱。矩形自第三根（c3）向右延伸，直到
  「完全填補」（bullish：後續 bar low ≤ 區間下界；bearish：high ≥ 上界）。
- **Order Block（OB）**：強陽/陰線觸發 BOS（close 突破之前所有 bar 的 high/low，
  且 body ≥ 自身 range 50%）→ 取觸發前**最近一根反向 K 線**嘅 open–close body
  [min(o,c), max(o,c)] 做矩形。後續 bar close 跌穿 body 遠端邊界 → 失效。
- **Confluence（共鳴）**：同方向 OB ∩ FVG 價格區間重疊 → 重疊帶高亮
  （兩個開關同時開啟時由 CandleChart 自動派生）。

全部 O(n) 純函數；bars = tuple[Bar, ...]，Bar = (time_key, open, high, low, close, volume)
（同 ui/candle_chart.py / engine/candle_aggregator.py 定義）。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Zone:
    """價格錨定指標矩形。

    kind ∈ {"ob", "fvg", "confluence"}；side ∈ {"bullish", "bearish"}。
    start_idx = origin bar 嘅 global index（矩形左緣）；end_idx=None 表示仍活躍
    （畫到 plot 右緣），否則喺該 bar 被填補/失效。top/bottom 係價格（top > bottom）。
    """

    kind: str
    side: str
    start_idx: int
    end_idx: int | None
    top: float
    bottom: float


def detect_fvg(bars) -> tuple[Zone, ...]:
    """偵測全部 FVG（三根 K 線失衡）。

    i ≥ 2：bullish = bars[i-2].high < bars[i].low → zone [bars[i-2].high, bars[i].low]；
    bearish 對稱。矩形自第三根 c3（index i）向右延伸直到完全填補；未填補 → end_idx=None。
    """
    zones: list[Zone] = []
    n = len(bars)
    for i in range(2, n):
        c1, c3 = bars[i - 2], bars[i]
        if c1[2] < c3[3]:            # high(c1) < low(c3) → bullish gap
            top, bottom, side = float(c3[3]), float(c1[2]), "bullish"
        elif c1[3] > c3[2]:          # low(c1) > high(c3) → bearish gap
            top, bottom, side = float(c1[3]), float(c3[2]), "bearish"
        else:
            continue
        end_idx = None
        for j in range(i + 1, n):
            if (side == "bullish" and bars[j][3] <= bottom) or \
               (side == "bearish" and bars[j][2] >= top):
                end_idx = j          # 完全填補 → 矩形止於呢根 bar
                break
        zones.append(Zone("fvg", side, i, end_idx, top, bottom))
    return tuple(zones)


def detect_order_blocks(bars) -> tuple[Zone, ...]:
    """偵測全部 Order Block（最後一根反向 K 線 + BOS 觸發）。

    Bullish OB：強陽線（close > 之前所有 bar high = BOS up，且 body ≥ 自身 range 50%）
      → 向前找最近一根陰線 j → 矩形 = 該陰線 open–close body。
    Bearish OB 對稱（BOS down → 最近一根陽線）。後續 bar close 跌穿 body 下界
    （bullish）/ 升穿上界（bearish）→ end_idx 失效位置。doji 唔做 origin；
    同一 origin candle j 只記錄一次（dedup，避免連續強線產生重疊矩形）。
    """
    if len(bars) < 2:
        return ()
    zones: list[Zone] = []
    seen_origins: set[int] = set()
    prior_high = float(bars[0][2])   # bars[:i] 嘅 running high/low（O(n)，唔逐次 max）
    prior_low = float(bars[0][3])
    for i in range(1, len(bars)):
        o, h_, l_, c = (float(v) for v in bars[i][1:5])
        body = abs(c - o)
        if body >= 0.5 * (h_ - l_) and (c > prior_high or c < prior_low):
            side = "bullish" if c > prior_high else "bearish"
            # 向前找最近一根反向 K 線（bullish OB ← 陰線 close<open；bearish OB ← 陽線）
            j = i - 1
            while j >= 0:
                if (side == "bullish" and bars[j][4] < bars[j][1]) or \
                   (side == "bearish" and bars[j][4] > bars[j][1]):
                    break
                j -= 1
            if j >= 0 and j not in seen_origins:
                ob_o, ob_c = float(bars[j][1]), float(bars[j][4])
                top, bottom = max(ob_o, ob_c), min(ob_o, ob_c)
                end_idx = None
                for k in range(i + 1, len(bars)):
                    if (side == "bullish" and bars[k][4] < bottom) or \
                       (side == "bearish" and bars[k][2] > top):
                        end_idx = k    # close 跌穿/升穿 body 遠端邊界 → 失效
                        break
                seen_origins.add(j)
                zones.append(Zone("ob", side, j, end_idx, top, bottom))
        prior_high = max(prior_high, h_)
        prior_low = min(prior_low, l_)
    return tuple(zones)


def confluence_zones(ob_zones: tuple[Zone, ...], fvg_zones: tuple[Zone, ...]) -> tuple[Zone, ...]:
    """Confluence：同方向 OB ∩ FVG 價格區間重疊 → 重疊帶。

    重疊帶 = [max(bottoms), min(tops)]（須嚴格 > 0）；時間區間 = 兩矩形活躍區間交集
    （end_idx=None = 「到右緣」→ 取另一邊嘅 end；兩者皆 None → None）。
    """
    out: list[Zone] = []
    for ob in ob_zones:
        for fvg in fvg_zones:
            if ob.side != fvg.side:
                continue             # 異向重疊唔算共鳴（bullish OB + bearish FVG 互相矛盾）
            lo = max(ob.bottom, fvg.bottom)
            hi = min(ob.top, fvg.top)
            if hi <= lo:
                continue             # 價格無重疊
            start_idx = max(ob.start_idx, fvg.start_idx)
            end_idx = _min_end(ob.end_idx, fvg.end_idx)
            if end_idx is not None and start_idx >= end_idx:
                continue             # 時間區間無交集（一個已失效、另一個先開始）
            out.append(Zone("confluence", ob.side, start_idx, end_idx, float(hi), float(lo)))
    return tuple(out)


def _min_end(a: int | None, b: int | None) -> int | None:
    """兩個「end」邊界嘅交集：None = 到右緣（視為 +∞）。"""
    if a is None or b is None:
        return b if a is None else a
    return min(a, b)
