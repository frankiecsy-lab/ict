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
- **Valid Order Block（VOB，有效訂單塊）**：通過三重過濾嘅 OB——①前置流動性掃蕩
  （origin 前 lookback 窗口內有 bar 創下窗口新低/新高且之後到 origin 再冇跌穿/升穿）+
  ②未失效（body close 穿邊界先算失效，wick 唔算）+ ③同方向 FVG 與 OB body 價格嚴格重疊。
  矩形畫完整 OB body；end = min(OB 失效、最早匹配 FVG 填補)。HTF 對齊 / LTF CISD
  計時超出單週期 zone 層範圍（見 README）。
- **Breaker Block**：「失效咗嘅 OB」——bullish OB 被後續 bar close 跌穿 body 下界後
  翻轉做 bearish 阻力；bearish 對稱（high 升穿上界 → 翻轉 bullish 支持）。矩形 = 原 OB
  body，自失效 bar 向右延伸直到價格收返去 zone 另一邊（mitigation 完成）。
- **Kill Zone**：標準 ICT session 時間帶（ET wall clock）：Asia 20:00–24:00 /
  London KZ 02:00–05:00 / NY KZ 07:00–10:00 / London Close 10:00–12:00。bar time_key
  係 HKT naive（見 engine/timeutil.py 時區鐵律）→ stdlib zoneinfo 轉 America/New_York
  （DST-aware）做分類；呢個轉換只供顯示，永遠唔涉及 bar key 產生。
- **Daily reference lines**：DO = 每日開市價線段（只跨當日）；PH/PL/PC = 前一交易日
  high/low/close 全寬水平線。
- **Liquidity Levels（流動性池 BSL/SSL）**：pivot swing high/low（前後各 pivot bar 嘅
  局部極值）按價格聚類——同一價位被 ≥min_touches 個 pivot 觸及 = 流動性池（equal highs /
  equal lows）。BSL=上方 buy-side 阻力（swing high 群、price > last_close）、SSL=下方
  sell-side 支撐（swing low 群、price < last_close）；只畫相對於最新 close 未失效嘅池。
  線段由首次觸及 bar 畫到右緣（end=None）。
- **Structure Breaks（BOS / CHoCH）**：追蹤趨勢方向 + 已確認 pivot swing high/low——
  順勢突破最近結構極值 = **BOS**（延續）；首次逆勢突破 = **CHoCH**（反轉訊號，翻轉
  direction）。pivot 需前後各 k bar 確認（喺 i=s+k 先算 confirmed），每個 pivot 只觸發
  一次（break 後 consumed、等下一個新 pivot）。標記畫喺 break 發生嘅 bar。
- **Premium / Discount**：最近 lookback bar 嘅 dealing range（high max / low min）→
  equilibrium = midpoint；premium zone = [eq, high]（上方 sell 區）、discount zone =
  [low, eq]（下方 buy 區）。兩條全寬水平帶（start_idx=0、end_idx=None），背景層。
- **OTE（Optimal Trade Entry）**：最近位移腿嘅 62%–79% Fibonacci 回撤帶（golden pocket
  ~70.5%）。用 pivot swing high/low 搵出**最近一個**極值 + 其前最近反向極值做 origin——
  bullish OTE = [H-0.79·span, H-0.62·span]（由 swing high H 回落）、bearish 對稱。最多兩帶。

全部 O(n) 純函數；bars = tuple[Bar, ...]，Bar = (time_key, open, high, low, close, volume)
（同 ui/candle_chart.py / engine/candle_aggregator.py 定義）。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Zone:
    """價格錨定指標矩形。

    kind ∈ {"ob", "fvg", "confluence", "breaker", "vob", "ote", "premium", "discount"}；
    side ∈ {"bullish", "bearish"}。start_idx = origin bar 嘅 global index（矩形左緣）；
    end_idx=None 表示仍活躍（畫到 plot 右緣），否則喺該 bar 被填補/失效。top/bottom 係價格
    （top > bottom）。premium/discount 用 start_idx=0/end_idx=None 表全寬水平帶。
    """

    kind: str
    side: str
    start_idx: int
    end_idx: int | None
    top: float
    bottom: float


@dataclass(frozen=True)
class RefLine:
    """水平參考線。

    kind ∈ {"do", "ph", "pl", "pc"}（Daily Open / Prev Day High/Low/Close）。
    start_idx/end_idx = 線段覆蓋嘅 bar index 範圍；end_idx=None 表示全寬（畫到右緣）。
    """

    kind: str
    price: float
    start_idx: int
    end_idx: int | None


@dataclass(frozen=True)
class Level:
    """水平流動性池線（獨立於 Zone 矩形、RefLine daily 參考）。

    kind ∈ {"bsl", "ssl"}（Buy-Side / Sell-Side Liquidity）；price = 價位；
    start_idx/end_idx = 線段覆蓋嘅 bar index 範圍，end_idx=None 表示畫到右緣。
    """

    kind: str
    price: float
    start_idx: int
    end_idx: int | None


@dataclass(frozen=True)
class Marker:
    """結構突破標記（BOS / CHoCH）——畫喺特定 bar 上嘅箭頭/三角，唔係價格矩形。

    kind ∈ {"bos", "choch"}：BOS=Break of Structure（順勢延續）、CHoCH=Change of
    Character（首次逆勢 = 反轉訊號）。direction ∈ {"up", "down"}；idx = bar global index。
    """

    kind: str
    direction: str
    idx: int


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


def detect_breaker_blocks(bars) -> tuple[Zone, ...]:
    """偵測全部 Breaker Block（失效 OB 翻轉）。

    觸發條件同 Order Block（強陽/陰線 BOS + body ≥ range 50% → origin = 最近反向 K 線
    body），但 zone 唔喺 trigger 時記錄——要等**失效**先成立：bullish OB 被後續 bar
    close < body 下界（k）→ 翻轉 bearish breaker；bearish OB 被 high > body 上界 →
    翻轉 bullish。矩形 = 原 OB body，start_idx=k（失效 bar），向右延伸直到價格收返去
    zone 另一邊（mitigation：bearish close > top / bullish close < bottom）→ end_idx；
    未收返 → None。同一 origin candle 只記錄一次（dedup）。
    """
    if len(bars) < 2:
        return ()
    zones: list[Zone] = []
    seen_origins: set[int] = set()
    prior_high = float(bars[0][2])   # bars[:i] running high/low（同 detect_order_blocks）
    prior_low = float(bars[0][3])
    for i in range(1, len(bars)):
        o, h_, l_, c = (float(v) for v in bars[i][1:5])
        body = abs(c - o)
        if body >= 0.5 * (h_ - l_) and (c > prior_high or c < prior_low):
            side = "bullish" if c > prior_high else "bearish"
            j = i - 1                # 向前找最近一根反向 K 線（同 OB）
            while j >= 0:
                if (side == "bullish" and bars[j][4] < bars[j][1]) or \
                   (side == "bearish" and bars[j][4] > bars[j][1]):
                    break
                j -= 1
            if j >= 0 and j not in seen_origins:
                ob_o, ob_c = float(bars[j][1]), float(bars[j][4])
                top, bottom = max(ob_o, ob_c), min(ob_o, ob_c)
                k = None             # 失效 bar：close 跌穿下界（bullish）/ high 升穿上界（bearish）
                for m in range(i + 1, len(bars)):
                    if (side == "bullish" and bars[m][4] < bottom) or \
                       (side == "bearish" and bars[m][2] > top):
                        k = m
                        break
                if k is not None:    # 冇失效 → 唔係 breaker（只係普通 OB）
                    seen_origins.add(j)
                    brk_side = "bearish" if side == "bullish" else "bullish"
                    end_idx = None   # mitigation：收返去 zone 另一邊
                    for m in range(k + 1, len(bars)):
                        if (brk_side == "bearish" and bars[m][4] > top) or \
                           (brk_side == "bullish" and bars[m][4] < bottom):
                            end_idx = m
                            break
                    zones.append(Zone("breaker", brk_side, k, end_idx, top, bottom))
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


def _has_liquidity_sweep(bars, j: int, side: str, lookback: int = 20) -> bool:
    """前置流動性掃蕩 proxy（valid OB 研究條件①「No sweep, no order block」）。

    窗口 [max(0, j-lookback)..j] 內存在 s < j，其 low（bullish）/ high（bearish）：
      (a) 創下窗口新低/新高——跌破之前結構（low[s] < min(low[win..s-1])）；且
      (b) 係終端極值——之後到 origin j 再冇跌穿/升穿（low[s] <= min(low[s+1..j])）。
    s == win 起點無 prior 結構可比 → 唔計；j==0 / lookback<=0 → False。O(lookback²)。
    """
    if j <= 0 or lookback <= 0:
        return False
    win = max(0, j - lookback)
    for s in range(win + 1, j):         # s > win：要有 prior 結構先談得上「掃蕩」
        if side == "bullish":
            ext = float(bars[s][3])     # low
            prior_min = min(float(b[3]) for b in bars[win:s])
            after_min = min((float(b[3]) for b in bars[s + 1:j + 1]), default=float("inf"))
            if ext < prior_min and ext <= after_min:
                return True
        else:                           # bearish 對稱（high）
            ext = float(bars[s][2])     # high
            prior_max = max(float(b[2]) for b in bars[win:s])
            after_max = max((float(b[2]) for b in bars[s + 1:j + 1]), default=float("-inf"))
            if ext > prior_max and ext >= after_max:
                return True
    return False


def detect_valid_order_blocks(bars, sweep_lookback: int = 20) -> tuple[Zone, ...]:
    """Valid Order Block（VOB）：通過三重過濾嘅 OB。

    ICT valid OB 研究四條件中可單週期實作嘅三個（見 README / AGENTS.md 知識庫）：
      ① 前置流動性掃蕩——_has_liquidity_sweep() proxy；
      ② 未失效——ob.end_idx is None（body close 穿邊界 = 失效，wick 唔算）；
      ③ OB+FVG 共鳴——存在同方向 FVG 與 OB body 價格嚴格重疊。
    矩形畫**完整 OB body**（唔係重疊帶）——用戶要睇「邊個訂單塊有效」；end_idx =
    min(OB 失效、最早匹配 FVG 填補)（_min_end）。每個 OB 最多一個 vob zone。
    """
    if len(bars) < 2:
        return ()
    ob_zones = detect_order_blocks(bars)
    fvg_zones = detect_fvg(bars)
    out: list[Zone] = []
    for ob in ob_zones:
        if ob.end_idx is not None:      # ② 已失效 → 唔有效（變 Breaker，由 brk 層負責）
            continue
        if not _has_liquidity_sweep(bars, ob.start_idx, ob.side, sweep_lookback):
            continue                    # ① 無前置掃蕩
        best_end = None                 # 匹配 FVG 中最早嘅 end（None = 到右緣）
        matched = False
        for fvg in fvg_zones:           # ③ 同方向 FVG 價格重疊（confluence_zones 公式）
            if fvg.side != ob.side:
                continue
            lo = max(ob.bottom, fvg.bottom)
            hi = min(ob.top, fvg.top)
            if hi <= lo:
                continue                # 無嚴格價格重疊
            matched = True
            end_idx = _min_end(ob.end_idx, fvg.end_idx)   # ob 未失效 → 實為 fvg.end
            if best_end is None or (end_idx is not None and end_idx < best_end):
                best_end = end_idx
        if matched:
            out.append(Zone("vob", ob.side, ob.start_idx, best_end, ob.top, ob.bottom))
    return tuple(out)


# ---------------------------------------------------------------- Kill Zones

#: ICT session 時間帶（ET wall clock，分鐘）：(key, start_min, end_min)。
KILL_ZONES: tuple[tuple[str, int, int], ...] = (
    ("asia", 20 * 60, 24 * 60),        # Asia / Sydney session
    ("london", 2 * 60, 5 * 60),        # London Kill Zone
    ("new_york", 7 * 60, 10 * 60),     # New York Kill Zone（含 AM open）
    ("london_close", 10 * 60, 12 * 60)  # London Close / PM session
)

#: band label（畫喺圖上嘅短名）。
_KZ_LABELS: dict[str, str] = {
    "asia": "ASIA", "london": "LDN", "new_york": "NY", "london_close": "LDC"
}


def kill_zone_bands(bars) -> tuple[tuple[int, int, str], ...]:
    """將 bars 分組成連續 Kill Zone band：tuple[(start_idx, end_idx, session_key), ...]。

    bar time_key 係 HKT naive（engine/timeutil.py 時區鐵律）→ stdlib zoneinfo 轉
    America/New_York（DST-aware）做**顯示分類**；轉換只讀 key、永遠唔涉及 bar key
    產生。非 intraday key（長度 ≠ 16，如 K_DAY/K_MON）自動 skip（session 概念只對
    分鐘級有意義）。zoneinfo 不可用（無 tzdata）→ 優雅降級 ()。
    """
    try:
        from zoneinfo import ZoneInfo
        hkt = ZoneInfo("Asia/Hong_Kong")
        et = ZoneInfo("America/New_York")
    except Exception:                 # ZoneInfoNotFoundError / tzdata 缺失 → 無 band
        return ()
    bands: list[tuple[int, int, str]] = []
    cur_key: str | None = None
    cur_start = 0
    offset_cache: dict[str, int] = {}   # date → HKT−ET 分鐘（DST 一年最多變兩次）
    for i, b in enumerate(bars):
        key = b[0]
        if len(key) != 16:             # 'yyyy-MM-dd HH:mm' 先有 session 意義
            session = None
        else:
            try:
                dt = datetime(int(key[:4]), int(key[5:7]), int(key[8:10]),
                              int(key[11:13]), int(key[14:16]))
            except ValueError:         # 畸形 key → skip（唔會 crash）
                session = None
            else:
                date_s = key[:10]
                off = offset_cache.get(date_s)
                if off is None:        # HKT naive → aware → ET wall clock
                    et_wall = dt.replace(tzinfo=hkt).astimezone(et)
                    off = int((dt - et_wall.replace(tzinfo=None)).total_seconds() // 60)
                    offset_cache[date_s] = off
                m = (dt.hour * 60 + dt.minute - off) % 1440   # ET wall-clock 分鐘
                session = next((k for k, s, e in KILL_ZONES if s <= m < e), None)
        if session != cur_key:         # session 變化 → 收前一段、開新段
            if cur_key is not None:
                bands.append((cur_start, i - 1, cur_key))
            cur_key = session
            cur_start = i
    if cur_key is not None:
        bands.append((cur_start, len(bars) - 1, cur_key))
    return tuple(bands)


# ---------------------------------------------------------------- Daily reference lines

def daily_reference_lines(bars) -> tuple[RefLine, ...]:
    """Daily Open / Prev Day HLC 參考線。

    DO：每日第一根 bar 嘅 open → 只跨當日嘅線段（start/end = 當日首尾 index）。
    PH/PL/PC：前一交易日（倒数第二個日組）high max / low min / close → 全寬水平線
    （start=0、end=None）。非 intraday key（長度 < 10，如 K_MON 'yyyy-MM'）→ ()。
    """
    if not bars or len(bars[0][0]) < 10:
        return ()
    groups: list[tuple[int, int]] = []   # (first_idx, last_idx) per date
    prev_date = None
    for i, b in enumerate(bars):
        d = b[0][:10]
        if d != prev_date:
            groups.append((i, i))
            prev_date = d
        else:
            groups[-1] = (groups[-1][0], i)
    out: list[RefLine] = []
    for s, e in groups:                  # DO：每日開市價線段
        out.append(RefLine("do", float(bars[s][1]), s, e))
    if len(groups) >= 2:                 # PH/PL/PC：前一交易日（倒数第二組）全寬線
        ps, pe = groups[-2]
        ph = max(float(b[2]) for b in bars[ps:pe + 1])
        pl = min(float(b[3]) for b in bars[ps:pe + 1])
        pc = float(bars[pe][4])
        out.append(RefLine("ph", ph, 0, None))
        out.append(RefLine("pl", pl, 0, None))
        out.append(RefLine("pc", pc, 0, None))
    return tuple(out)


# ---------------------------------------------------------------- Liquidity Levels (BSL/SSL)

def _swing_points(bars, k: int, which: str) -> list[tuple[int, float]]:
    """pivot 極值點：which="high" → high[i] ≥ [i-k..i+k] 全部 high；"low" 對稱（≤）。

    邊界 bar（i<k 或 i≥n-k）唔計。返回 [(idx, price), ...]，O(n·k)。
    """
    n = len(bars)
    out: list[tuple[int, float]] = []
    for i in range(k, n - k):
        if which == "high":
            v = float(bars[i][2])
            if all(v >= float(bars[j][2]) for j in range(i - k, i + k + 1)):
                out.append((i, v))
        else:
            v = float(bars[i][3])
            if all(v <= float(bars[j][3]) for j in range(i - k, i + k + 1)):
                out.append((i, v))
    return out


def _cluster_by_price(points: list[tuple[int, float]], tol_frac: float) -> list[tuple[float, list[int]]]:
    """按價格排序後貪心聚類：相鄰差 ≤ tol_frac×price 合併做一簇。

    返回 [(cluster_max_price, [idxs...]), ...]（保留全部簇，size 過濾由 caller 做）。
    """
    if not points:
        return []
    clusters: list[list] = []   # each: [max_price, [idxs]]
    for idx, price in sorted(points, key=lambda p: p[1]):
        if clusters and (price - clusters[-1][0]) <= tol_frac * max(1e-9, price):
            clusters[-1][0] = max(clusters[-1][0], price)
            clusters[-1][1].append(idx)
        else:
            clusters.append([price, [idx]])
    return [(c[0], c[1]) for c in clusters]


def detect_liquidity_levels(bars, pivot: int = 3, min_touches: int = 2,
                            tol_frac: float = 0.002) -> tuple[Level, ...]:
    """流動性池（BSL/SSL）：pivot swing high/low 按價格聚類，≥min_touches 觸及嘅價位先算。

    BSL=上方 buy-side 阻力（swing high 群、price > last_close）、SSL=下方 sell-side
    支撐（swing low 群、price < last_close）。線段由首次觸及 bar 畫到右緣（end=None）。
    O(n·k)。
    """
    if len(bars) < 2 * pivot + 1 or min_touches < 2:
        return ()
    last_close = float(bars[-1][4])
    out: list[Level] = []
    for which, kind in (("high", "bsl"), ("low", "ssl")):
        clusters = _cluster_by_price(_swing_points(bars, pivot, which), tol_frac)
        for price, idxs in clusters:
            if len(idxs) < min_touches:
                continue
            if (kind == "bsl" and price > last_close) or \
               (kind == "ssl" and price < last_close):
                out.append(Level(kind, price, min(idxs), None))
    bsl = sorted((l for l in out if l.kind == "bsl"), key=lambda l: -l.price)
    ssl = sorted((l for l in out if l.kind == "ssl"), key=lambda l: l.price)
    return tuple(bsl + ssl)


# ---------------------------------------------------------------- Structure Breaks (BOS / CHoCH)

def _is_swing_high(bars, s: int, k: int) -> bool:
    """bar s 係 pivot swing high：high[s] 嚴格大於前後各 k 根嘅 high。

    邊界（s-k<0 或 s+k≥n）→ False。喺 i=s+k 確認（呢時 [s+1..s+k] 已齊）。O(k)。
    """
    n = len(bars)
    if s - k < 0 or s + k >= n:
        return False
    h = float(bars[s][2])
    for j in range(s - k, s + k + 1):
        if j != s and float(bars[j][2]) >= h:
            return False
    return True


def _is_swing_low(bars, s: int, k: int) -> bool:
    """bar s 係 pivot swing low：low[s] 嚴格小於前後各 k 根嘅 low。對稱 _is_swing_high。"""
    n = len(bars)
    if s - k < 0 or s + k >= n:
        return False
    l = float(bars[s][3])
    for j in range(s - k, s + k + 1):
        if j != s and float(bars[j][3]) <= l:
            return False
    return True


def detect_structure_breaks(bars, k: int = 2) -> tuple[Marker, ...]:
    """BOS / CHoCH 結構突破標記（單週期、確定性狀態機）。

    趨勢 direction ∈ {None,"up","down"}；追蹤最近**已確認且未 break**嘅 pivot swing
    high/low（last_sh / last_sl，(price, idx)）。逐 bar：
      - direction="up"：close > last_sh → **BOS up**（順勢延續）並 consumed；
        否則 close < last_sl → **CHoCH down**（首次逆勢 = 反轉），direction→"down"。
      - direction="down" 對稱（close < last_sl → BOS down；close > last_sh → CHoCH up）。
      - direction=None：首個結構 break 建立趨勢（記做 BOS）。
    每 bar 最多一個標記（if/elif）；break 後該 pivot consumed（設 None），等下一個新
    confirmed pivot。pivot 喺 i=s+k 確認（marker check 用**之前**嘅 state，故新 pivot
    只俾未來 bar break）。O(n·k)。
    """
    n = len(bars)
    if n < 2 * k + 1:
        return ()
    markers: list[Marker] = []
    direction: str | None = None
    last_sh: tuple[float, int] | None = None   # (price, idx) 最近已確認未 break swing high
    last_sl: tuple[float, int] | None = None   # (price, idx) 最近已確認未 break swing low
    for i in range(n):
        c = float(bars[i][4])
        if direction == "up":
            if last_sh is not None and c > last_sh[0]:
                markers.append(Marker("bos", "up", i))
                last_sh = None                       # consumed——等下一個新 pivot high
            elif last_sl is not None and c < last_sl[0]:
                markers.append(Marker("choch", "down", i))
                direction = "down"                   # 首次逆勢 → 反轉
        elif direction == "down":
            if last_sl is not None and c < last_sl[0]:
                markers.append(Marker("bos", "down", i))
                last_sl = None                       # consumed——等下一個新 pivot low
            elif last_sh is not None and c > last_sh[0]:
                markers.append(Marker("choch", "up", i))
                direction = "up"                     # 首次逆勢 → 反轉
        else:  # None——首個結構 break 建立趨勢（記做 BOS）
            if last_sh is not None and c > last_sh[0]:
                markers.append(Marker("bos", "up", i))
                direction = "up"
                last_sh = None
            elif last_sl is not None and c < last_sl[0]:
                markers.append(Marker("bos", "down", i))
                direction = "down"
                last_sl = None
        s = i - k
        if s >= 0:
            if _is_swing_high(bars, s, k):
                last_sh = (float(bars[s][2]), s)     # arm 一個新可 break high
            if _is_swing_low(bars, s, k):
                last_sl = (float(bars[s][3]), s)     # arm 一個新可 break low
    return tuple(markers)


# ---------------------------------------------------------------- Premium / Discount

def detect_premium_discount(bars, lookback: int = 50) -> tuple[Zone, ...]:
    """Premium/Discount：最近 lookback bar 嘅 dealing range → equilibrium 分界。

    dealing range = bars[-lookback:]（lookback<=0 → 全部）嘅 high max（range_high）/
    low min（range_low）；equilibrium = (high+low)/2。**premium zone** = [eq, high]
    （上方 sell 區，side="bearish"）、**discount zone** = [low, eq]（下方 buy 區，
    side="bullish"）。兩條全寬水平帶（start_idx=0、end_idx=None）。flat（high<=low）→ ()。
    """
    if len(bars) < 2:
        return ()
    win = bars[-lookback:] if lookback > 0 else bars
    hi = max(float(b[2]) for b in win)
    lo = min(float(b[3]) for b in win)
    if hi <= lo:
        return ()
    eq = (hi + lo) / 2.0
    return (Zone("premium", "bearish", 0, None, hi, eq),
            Zone("discount", "bullish", 0, None, eq, lo))


# ---------------------------------------------------------------- OTE（Optimal Trade Entry）

def detect_ote_zones(bars, k: int = 3) -> tuple[Zone, ...]:
    """OTE：最近位移腿嘅 62%–79% Fibonacci 回撤帶（golden pocket ~70.5%）。

    pivot swing high/low（_swing_points，k bar 確認）搵出**最近一個**極值 + 其前最近
    反向極值做 origin：
      - bullish OTE（buy zone）：origin = 該 swing high 之前最近嘅 swing low L、extreme =
        swing high H → 帶 [H-0.79·span, H-0.62·span]（價格由 H 回落入呢個帶）。
      - bearish OTE（sell zone）：origin = 該 swing low 之前最近嘅 swing high H、extreme =
        swing low L → 帶 [L+0.62·span, L+0.79·span]。
    start_idx = extreme pivot index、end_idx=None（活躍到右緣）。最多兩個 zone；無 origin
    / span<=0 → 該方向唔產出。O(n·k)。
    """
    if len(bars) < 2 * k + 1:
        return ()
    highs = _swing_points(bars, k, "high")   # [(idx, price), ...] idx 遞增
    lows = _swing_points(bars, k, "low")
    out: list[Zone] = []
    if highs and lows:                       # bullish OTE：最近 swing high + 其前最近 swing low
        hi_idx, hi_price = highs[-1]
        prior_low = next((p for i, p in reversed(lows) if i < hi_idx), None)
        if prior_low is not None and hi_price > prior_low:
            span = hi_price - prior_low
            out.append(Zone("ote", "bullish", hi_idx, None,
                            hi_price - 0.62 * span, hi_price - 0.79 * span))
    if highs and lows:                       # bearish OTE：最近 swing low + 其前最近 swing high
        lo_idx, lo_price = lows[-1]
        prior_high = next((p for i, p in reversed(highs) if i < lo_idx), None)
        if prior_high is not None and prior_high > lo_price:
            span = prior_high - lo_price
            out.append(Zone("ote", "bearish", lo_idx, None,
                            lo_price + 0.79 * span, lo_price + 0.62 * span))
    return tuple(out)
