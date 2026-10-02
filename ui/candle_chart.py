"""全屏幕深色主題蠟燭圖表（純 QPainter，零第三方圖表庫）。

Backpressure：update_bars() 只記錄 immutable snapshot + 起 singleShot QTimer(30ms)，
tick burst 都最多 ~30fps repaint，永遠 render 最新 snapshot。

互動視圖狀態：X 軸 = (可見根數, 右偏移)——右偏移 0 = 右 pin 跟隨 live 數據；
Y 軸 = 手動價格範圍（None = auto-fit）。手勢：wheel = X 軸縮放（錨定游標）、
Ctrl/Shift + wheel = Y 軸縮放、左鍵拖曳 = 左右平移、右鍵拖曳 = 垂直平移、
雙擊 = reset_view() 重置。縮放係多段式：每個物理 wheel notch / 按鍵點擊 = 一階 ×/÷1.25
（wheel_notches() 將 Windows ±120° angleDelta 正規化返 ±1 階——唔正規化會令單 notch
直接跳去 min/max 極限，表現成「只有兩段」）；zoom_in()/zoom_out() 俾 control bar
放大/縮小按鍵（中心錨定）。

Overlay 擴展點：add_overlay(fn)；fn(painter, bars, price_rect) —— 預留俾日後
ICT FVG / Order Block / Kill Zone 圖層（Step 1 零 overlay）。
"""
from __future__ import annotations

import dataclasses
import math
from datetime import timedelta
from typing import Callable

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from engine.indicators import (_KZ_LABELS, Level, Marker, RefLine, Zone, confluence_zones,
                               daily_reference_lines, detect_breaker_blocks,
                               detect_fvg, detect_liquidity_levels,
                               detect_order_blocks, detect_ote_zones,
                               detect_premium_discount, detect_session_high_low,
                               detect_smt_divergence, detect_structure_breaks,
                               detect_valid_order_blocks,
                               kill_zone_bands, weekly_monthly_reference_lines)
from engine.timeutil import bar_key_to_dt

# (time_key, open, high, low, close, volume)
Bar = tuple[str, float, float, float, float, float]

_M_LEFT = 12
_M_RIGHT = 78      # 右軸 price label + last-price tag
_M_TOP = 34        # OHLCV readout 區
_M_BOTTOM = 26     # 時間軸 label
_VOL_RATIO = 0.22  # volume subpane 佔 plot 高度比例
_PANE_GAP = 10


# ---------------------------------------------------------------- 純 layout 函數（可獨立單測）

def visible_slice(bars: tuple[Bar, ...], count: int) -> tuple[Bar, ...]:
    """右 pin：取最後 `count` 根；空輸入 / 非法 count → 空。"""
    if not bars or count <= 0:
        return ()
    return visible_window(bars, count, 0)


def price_range(bars: tuple[Bar, ...]) -> tuple[float, float] | None:
    """可見 low/high + 5% padding；flat/單價時退化用 1% 或絕對 1.0。空 → None。"""
    if not bars:
        return None
    lo = min(b[3] for b in bars)
    hi = max(b[2] for b in bars)
    pad = (hi - lo) * 0.05 or abs(hi) * 0.01 or 1.0
    return lo - pad, hi + pad


def volume_max(bars: tuple[Bar, ...]) -> float:
    """volume subpane 刻度上限；全零 → 1.0（防除零）。"""
    if not bars:
        return 1.0
    v = max(b[5] for b in bars)
    return v if v > 0 else 1.0


def nice_step(span: float, target_lines: int = 6) -> float:
    """「漂亮」grid step（1/2/2.5/5 × 10^n），令水平 gridline 約 target_lines 條。"""
    if span <= 0:
        return 1.0
    raw = span / max(1, target_lines)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= m * mag:
            return m * mag
    return 10.0 * mag


def time_label(key: str) -> str:
    """時間軸 label：intraday 'yyyy-MM-dd HH:mm' → 'HH:mm'；日/週線保留原 key。"""
    if len(key) >= 16 and key[10] == " ":
        return key[11:]
    return key


def fmt_price(p: float) -> str:
    return f"{p:.2f}"


# ---------------------------------------------------------------- X/Y 視圖狀態純函數（pan/zoom，可獨立單測）

_MIN_X_BARS = 5       # X 軸縮放下限（可見根數）
_MAX_X_BARS = 2000    # X 軸縮放上限
_Y_ZOOM_FLOOR = 1e-4  # Y 軸 span 下限（相對於當前 span，防退化範圍 / 除零爆炸）
_WHEEL_NOTCH_DEG = 120.0  # Windows 標準 wheel 單 notch angleDelta.y() 幅度
_RIGHT_MARGIN_BARS = 5    # 右側留白：5 個空 bar-slot（bar 唔貼住價格軸，易閱讀；純視覺、唔改數據窗口）


def wheel_notches(angle_delta_y: int) -> float:
    """將原始 wheel angleDelta.y() 正規化成「階數」（每物理 notch ±1 階）。

    Windows 每個物理 notch 報 ±120°；唔正規化會令單 notch 變 1.25**120 ≈ 3e13 →
    X 軸縮放直接 clamp 去 min/max 極限（只達得到兩段）、Y 軸 span 無上限爆炸。
    """
    return float(angle_delta_y) / _WHEEL_NOTCH_DEG if angle_delta_y else 0.0


def _clamp_offset(off: float, total_bars: int, count: int) -> float:
    """右偏移 clamp 到 [0, max(0, total − count)]——唔可以越過最舊一根 bar。"""
    if total_bars <= 0 or count <= 0:
        return 0.0
    return max(0.0, min(float(off), float(total_bars - count)))


def visible_slice_range(bars: tuple[Bar, ...], count: int, right_offset: float) -> tuple[int, int]:
    """可見視窗嘅 global index 範圍 (start, end)——同 visible_window() 共用同一公式（DRY）。

    ICT 指標 zone 用 global bar index 記錄，paintEvent 靠呢個映射返可見視窗 local index。
    空輸入 / 非法 count → (0, 0)。
    """
    if not bars or count <= 0:
        return (0, 0)
    n = len(bars)
    off = int(round(_clamp_offset(right_offset, n, count)))
    end = n - off
    start = max(0, end - count)
    return start, end


def visible_window(bars: tuple[Bar, ...], count: int, right_offset: float) -> tuple[Bar, ...]:
    """可見視窗（X 軸 pan/zoom 狀態 → slice）。

    count = 可見根數；right_offset = 距數據尾部嘅 bar 數（0 = 右 pin 跟隨 live）。
    Clamp 到數據邊界：左邊唔夠數據 → 視窗收窄（右側留白，唔會繞圈）；小數偏移四捨五入到整根。
    """
    if not bars or count <= 0:
        return ()
    start, end = visible_slice_range(bars, count, right_offset)
    return bars[start:end]


def zoom_x(count: int, right_offset: float, total_bars: int, anchor_frac: float, delta: float):
    """X 軸 wheel 縮放（游標錨定）→ 新 (可見根數, 右偏移)。

    delta > 0 = 放大（少啲 bar）、< 0 = 縮細；每 notch ×/÷ 1.25（支持小數 notch）。
    anchor_frac：游標喺 plot 區嘅相對橫向位置 [0,1]——縮放後游標下面嗰根 bar 保持同一屏幕位置。
    """
    if delta == 0 or count <= 0 or total_bars <= 0:
        return int(count), _clamp_offset(right_offset, total_bars, count)
    new_count = max(_MIN_X_BARS, min(_MAX_X_BARS, round(count * (1.25 ** (-delta)))))
    f = max(0.0, min(1.0, float(anchor_frac)))
    off = _clamp_offset(right_offset, total_bars, count)
    end = total_bars - int(round(off))
    start = max(0, end - count)
    g = start + f * (end - start)  # 游標下面嘅 global index（float）
    new_off = float(total_bars) - (g + (1.0 - f) * new_count)
    return new_count, _clamp_offset(new_off, total_bars, new_count)


def pan_x(count: int, right_offset: float, total_bars: int, delta_bars: float):
    """X 軸拖曳平移 → 新 (可見根數, 右偏移)。

    delta_bars > 0 = 視窗移向舊數據（offset 增加）；< 0 = 移向新數據。邊界由 _clamp_offset 兜底。
    """
    return int(count), _clamp_offset(right_offset + delta_bars, total_bars, count)


def zoom_y(lo: float, hi: float, anchor_frac: float, delta: float):
    """Y 軸 wheel 縮放（游標錨定）→ 新價格範圍 (lo, hi)。

    delta > 0 = 放大；anchor_frac = 游標喺 price 區嘅相對垂直位置 [0,1]（0=頂部=hi 側），
    縮放後游標下面嗰個價保持同一屏幕位置。span 下限 = 當前 span × _Y_ZOOM_FLOOR。
    """
    if delta == 0 or hi <= lo:
        return float(lo), float(hi)
    f = max(0.0, min(1.0, float(anchor_frac)))
    span = hi - lo
    new_span = max(span * (1.25 ** (-delta)), span * _Y_ZOOM_FLOOR)
    p = hi - f * span  # 游標下面嘅價
    new_lo = p - (1.0 - f) * new_span
    return new_lo, new_lo + new_span


def pan_y(lo: float, hi: float, delta_price: float):
    """Y 軸拖曳平移 → 範圍整體位移 delta_price（正 = 視窗移向更高價）。"""
    return lo + delta_price, hi + delta_price


# ---------------------------------------------------------------- 時間視窗純函數（多 pane 時間軸同步，可獨立單測）

def window_time_range(bars: tuple[Bar, ...], count: int, right_offset: float, period_minutes: int) -> tuple | None:
    """可見視窗 → (start_dt, end_dt)：首根 bar 起始時間、尾根 bar **結束**時間（= 尾根 start + period）。

    多 pane 時間軸同步用——各 pane 週期不同（bar 密度不同），必須用**時間**而唔係 bar index
    對齊。end_dt 取「完整覆蓋」視窗嘅時刻（尾根 bar 結束），令較粗週期嘅 pane 套入嚟時
    該日/該週 bar 一定 overlap 到。無數據 / 視窗空 → None。
    """
    vis = visible_window(bars, count, right_offset)
    if not vis:
        return None
    start_dt = bar_key_to_dt(vis[0][0])
    end_start = bar_key_to_dt(vis[-1][0])
    if start_dt is None or end_start is None:
        return None
    end_dt = end_start + timedelta(minutes=period_minutes)
    return start_dt, end_dt


def infer_period_minutes(bars: tuple[Bar, ...]) -> int:
    """由 bar key 間隔推斷本 pane 週期（分鐘）——多 pane 時間軸同步用。

    取相鄰 bar start 嘅**中位數**間隔（robust：跳過休市/夜期缺口）。bar <2 根 → 1（單根視窗
    只需 +period 算 end，推唔到就用最小值兜底）。各 pane 週期不同，必須各自推斷自己嘅 bar 密度。
    """
    if len(bars) < 2:
        return 1
    gaps = []
    prev = None
    for b in bars:
        dt = bar_key_to_dt(b[0])
        if dt is None:
            continue
        if prev is not None:
            g = (dt - prev).total_seconds() / 60.0
            if g > 0:
                gaps.append(g)
        prev = dt
    if not gaps:
        return 1
    gaps.sort()
    med = gaps[len(gaps) // 2]
    return max(1, int(round(med)))


def time_window_indices(bars: tuple[Bar, ...], start_dt, end_dt, period_minutes: int) -> tuple[int, int] | None:
    """(start_dt, end_dt) → bars 內 [start_idx, end_idx]（含尾）；無 overlap bar → None。

    **span-overlap** 語義：取「bar 時間跨度 [key_start, key_start+period) 同視窗 [start_dt, end_dt)
    有交集」嘅連續區間——即 `key_start < end_dt and key_start + period > start_dt`。用 span（唔係
    bar start ∈ window）先至跨週期對齊得返：較粗 pane 嘅 bar start 會早於較細 pane 視窗 start，
    純「start ∈」永遠 match 唔到。供 set_time_window() 將外部時間視窗映射返本 pane 嘅 bar slice。
    """
    if not bars or start_dt is None or end_dt is None:
        return None
    period = timedelta(minutes=period_minutes)
    n = len(bars)
    s = e = -1
    for i, b in enumerate(bars):
        dt = bar_key_to_dt(b[0])
        if dt is None:
            continue
        if dt < end_dt and dt + period > start_dt:  # span overlap（半開區間）
            if s < 0:
                s = i
            e = i
    if s < 0:
        return None
    return s, e


# ---------------------------------------------------------------- widget

class CandleChart(QWidget):
    """蠟燭 + volume subpane + crosshair + last-price line；數據源係 immutable snapshot。"""

    # 用戶 pan/zoom X 軸（時間視窗改變）→ emit (start_dt, end_dt)；供多 pane 時間軸同步。
    # set_time_window()（程序化同步）唔會再 emit → 無回授循環。
    view_changed = Signal(object, object)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._bars: tuple[Bar, ...] = ()
        self._mouse_pos: QPointF | None = None
        self._overlays: list[Callable[[QPainter, tuple[Bar, ...], QRectF], None]] = []
        # ICT 指標層（OB / FVG / Confluence / Breaker）：toggle key → 啟用；zones = per-key 偵測結果
        # （Zone 用 global bar index，喺 repaint tick 重算——tick burst coalesce 內只算一次）
        self._indicator_enabled: dict[str, bool] = {}
        self._zones: dict[str, tuple[Zone, ...]] = {}
        self._kz_bands: tuple[tuple[int, int, str], ...] = ()   # Kill Zone session bands（global index 範圍）
        self._ref_lines: tuple[RefLine, ...] = ()                # Daily Open / Prev Day HLC 參考線
        self._levels: tuple[Level, ...] = ()                     # Liquidity Levels BSL/SSL 流動性池
        self._markers: tuple[Marker, ...] = ()                   # Structure Breaks BOS/CHoCH 標記
        self._pd_zones: tuple[Zone, ...] = ()                    # Premium/Discount dealing range 帶（背景層）
        self._session_lines: tuple[RefLine, ...] = ()            # Session High/Low per-day 範圍線
        self._wm_lines: tuple[RefLine, ...] = ()                 # Prev Week/Month HLC 全寬參考線
        self._smt_bars: tuple[Bar, ...] = ()                     # SMT Divergence 配對副標的 snapshot（time_key 對齊）
        self._smt_markers: tuple[Marker, ...] = ()               # SMT bearish/bullish 背離標記
        # 互動視圖狀態（X/Y pan/zoom；reset_view() 還原預設）
        self._view_count = max(1, int(cfg.visible_bars))  # X zoom：可見根數
        self._right_offset = 0.0                          # X pan：距數據尾部 bar 數（0=右 pin 跟 live）
        self._y_range: tuple[float, float] | None = None  # Y 手動範圍；None=auto-fit
        self._drag_mode: str | None = None                # 'x'/'y'/None
        self._last_drag_pos: QPointF | None = None
        self._syncing = False                             # set_time_window() 程序化同步中（抑制 view_changed）
        self._period_minutes = 1                          # 本 pane bar 週期（分鐘），update_bars 時由 key 間隔推斷
        self._repaint_timer = QTimer(self)
        self._repaint_timer.setSingleShot(True)
        self._repaint_timer.setInterval(30)  # backpressure：coalesce tick burst
        self._repaint_timer.timeout.connect(self._on_repaint_tick)

    # ------------------------------------------------------------- public API

    def apply_theme(self, t) -> None:
        """切換淺色/暗色主題（Commit 35 R6）：換一個新 Config（frozen dataclass replace），
        paint 時讀 `self._cfg` 嘅顏色字段自動跟隨——零 paint 代碼改動。

        只覆蓋背景 / 網格 / 文字 / 軸 / 最新價線五個主題色；up/down 漲跌色跟 convention
        （市場慣例）唔跟主題，visible_bars 等其餘字段原樣保留。
        """
        self._cfg = dataclasses.replace(
            self._cfg,
            bg_color=t.bg, grid_color=t.grid, text_color=t.text,
            axis_text_color=t.muted, last_price_color=t.accent,
        )
        self.update()

    def update_bars(self, bars: tuple[Bar, ...]) -> None:
        """接收新 snapshot（Signal queued 過嚟）；30ms 內多次調用只 repaint 一次。"""
        self._bars = tuple(bars)
        self._period_minutes = infer_period_minutes(self._bars)  # 本 pane bar 密度（時間視窗同步用）
        if not self._repaint_timer.isActive():
            self._repaint_timer.start()

    def set_smt_bars(self, bars: tuple[Bar, ...]) -> None:
        """接收 SMT Divergence 配對副標的 snapshot；同 update_bars 一樣 coalesce repaint。"""
        self._smt_bars = tuple(bars)
        if not self._repaint_timer.isActive():
            self._repaint_timer.start()

    def add_overlay(self, fn: Callable[[QPainter, tuple[Bar, ...], QRectF], None]) -> None:
        """註冊 overlay 繪製函數（喺蠟燭之後、crosshair 之前畫）。"""
        self._overlays.append(fn)

    # ------------------------------------------------------------- ICT 指標層

    def set_indicator(self, key: str, on: bool) -> None:
        """開關一個指標圖層（"ob"/"fvg"/"vob"/"brk"/"kz"/"ref"/"liq"/"bos"/"pd"/"ote"/"shl"/"wmref"/"smt"）；立即重算 + repaint。"""
        self._indicator_enabled[key] = bool(on)
        self._recompute_zones()
        self.update()

    def _on_repaint_tick(self) -> None:
        """30ms backpressure tick：先重算啟用中指標嘅 zones，再 repaint（coalesce 窗口內只算一次）。"""
        self._recompute_zones()
        self.update()

    def _recompute_zones(self) -> None:
        """對全部啟用指標用完整 snapshot 重算偵測結果；冇啟用 → 清空。

        Confluence 唔係獨立開關——OB + FVG 同時啟用時自動派生（同向價格區間重疊帶）。
        VOB（有效訂單塊）係獨立圖層——detect_valid_order_blocks() 內部自算 OB+FVG，
        唔依賴 ob/fvg 開關狀態。KZ bands / ref lines / liquidity levels / structure
        markers / premium-discount 存獨立狀態（_kz_bands / _ref_lines / _levels /
        _markers / _pd_zones / _session_lines / _wm_lines / _smt_markers），唔入 zones dict；任何 recompute 都先重置
        八者（toggle off → 清空，唔會殘留舊 band/line/level/marker/pd/session/wm/smt）。OTE 入
        zones["ote"]（同 FVG/OB 一樣價格錨定矩形、畫喺蠟燭上面）。SMT Divergence 需要主標的 +
        配對副標的兩份 snapshot（_smt_bars）——任一缺失 → 無 marker。
        """
        self._kz_bands = ()
        self._ref_lines = ()
        self._levels = ()
        self._markers = ()
        self._pd_zones = ()
        self._session_lines = ()
        self._wm_lines = ()
        self._smt_markers = ()
        if not any(self._indicator_enabled.values()):
            self._zones = {}
            return
        zones: dict[str, tuple[Zone, ...]] = {}
        fvg_zones = ()
        ob_zones = ()
        if self._indicator_enabled.get("fvg"):
            fvg_zones = detect_fvg(self._bars)
            zones["fvg"] = fvg_zones
        if self._indicator_enabled.get("ob"):
            ob_zones = detect_order_blocks(self._bars)
            zones["ob"] = ob_zones
        if self._indicator_enabled.get("brk"):
            zones["breaker"] = detect_breaker_blocks(self._bars)
        if self._indicator_enabled.get("vob"):
            zones["vob"] = detect_valid_order_blocks(self._bars)   # 自含 OB+FVG，獨立於 ob/fvg 開關
        if ob_zones and fvg_zones:
            zones["confluence"] = confluence_zones(ob_zones, fvg_zones)
        if self._indicator_enabled.get("kz"):
            self._kz_bands = kill_zone_bands(self._bars)
        if self._indicator_enabled.get("ref"):
            self._ref_lines = daily_reference_lines(self._bars)
        if self._indicator_enabled.get("shl"):
            self._session_lines = detect_session_high_low(self._bars)   # Session High/Low per-day 範圍線（獨立圖層）
        if self._indicator_enabled.get("wmref"):
            self._wm_lines = weekly_monthly_reference_lines(self._bars)   # Prev Week/Month HLC 全寬線（獨立圖層）
        if self._indicator_enabled.get("liq"):
            self._levels = detect_liquidity_levels(self._bars)   # BSL/SSL 流動性池（獨立圖層）
        if self._indicator_enabled.get("bos"):
            self._markers = detect_structure_breaks(self._bars)  # BOS/CHoCH 結構突破標記（獨立圖層）
        if self._indicator_enabled.get("pd"):
            self._pd_zones = detect_premium_discount(self._bars)  # Premium/Discount dealing range（獨立背景層）
        if self._indicator_enabled.get("ote"):
            zones["ote"] = detect_ote_zones(self._bars)          # OTE Fibonacci 回撤帶（價格錨定矩形，畫喺蠟燭上面）
        if self._indicator_enabled.get("smt") and self._bars and self._smt_bars:
            self._smt_markers = detect_smt_divergence(self._bars, self._smt_bars)  # SMT 背離標記（獨立圖層）
        self._zones = zones

    def reset_view(self) -> None:
        """重置視圖狀態返預設（右 pin + auto-fit Y）；雙擊觸發，main_window 喺切換標的時亦調用。"""
        self._view_count = max(1, int(self._cfg.visible_bars))
        self._right_offset = 0.0
        self._y_range = None
        self.update()
        if self._bars:
            self._emit_view_changed()  # 重置後時間視窗改變 → 同步其他 pane

    def zoom_in(self, steps: int = 1) -> None:
        """放大 N 階（可見根數減少）；俾 control bar「放大」按鍵。每階 ×/÷1.25、中心錨定。"""
        self._zoom_x_steps(+steps)

    def zoom_out(self, steps: int = 1) -> None:
        """縮小 N 階（可見根數增加）；俾 control bar「縮小」按鍵。每階 ×/÷1.25、中心錨定。"""
        self._zoom_x_steps(-steps)

    def _zoom_x_steps(self, delta: float) -> None:
        """按鍵分步 X 軸縮放：無數據 / 零階 → no-op；anchor = plot 中心（f=0.5）。"""
        if not self._bars or delta == 0:
            return
        self._view_count, self._right_offset = zoom_x(
            self._view_count, self._right_offset, len(self._bars), 0.5, float(delta))
        self.update()
        self._emit_view_changed()  # X 軸縮放 → 同步其他 pane

    # ------------------------------------------------------------- 時間視窗（多 pane 同步）

    def time_window(self) -> tuple | None:
        """當前可見視窗嘅 (start_dt, end_dt)；無數據 → None。end = 尾根 bar 結束（含本 pane period）。"""
        return window_time_range(self._bars, self._view_count, self._right_offset, self._period_minutes)

    def set_time_window(self, start_dt, end_dt) -> bool:
        """程序化將本 pane 可見視窗對齊到 (start_dt, end_dt)（多 pane 時間軸同步）。

        依 bar key **span-overlap** 映射返本 pane 嘅 bar slice（各週期 bar 密度不同，用時間對齊）；
        **唔會 emit view_changed**（程序化、非用戶操作 → 無回授循環）。範圍內無 overlap bar → no-op。
        返回有冇實際改動視圖。
        """
        if not self._bars or start_dt is None or end_dt is None:
            return False
        idx = time_window_indices(self._bars, start_dt, end_dt, self._period_minutes)
        if idx is None:
            return False
        s, e = idx
        n = len(self._bars)
        new_count = max(1, e - s + 1)
        new_offset = float(n - 1 - e)  # 尾根可見 bar = e → right_offset = n-1-e
        if (new_count, round(new_offset)) == (self._view_count, int(round(self._right_offset))):
            return False
        self._syncing = True
        try:
            self._view_count = new_count
            self._right_offset = new_offset
        finally:
            self._syncing = False
        self.update()
        return True

    def _emit_view_changed(self) -> None:
        """用戶 X 軸 pan/zoom 後 emit 當前時間視窗（程序化同步中 / 無數據 → 唔 emit）。"""
        if self._syncing or not self._bars:
            return
        rng = window_time_range(self._bars, self._view_count, self._right_offset, self._period_minutes)
        if rng is not None:
            self.view_changed.emit(rng[0], rng[1])

    # ------------------------------------------------------------- geometry helpers

    def _panes(self):
        """返回 (plot_rect, price_rect, vol_rect)。"""
        w = max(10, self.width() - _M_LEFT - _M_RIGHT)
        h = max(10, self.height() - _M_TOP - _M_BOTTOM)
        plot = QRectF(_M_LEFT, _M_TOP, w, h)
        vol_h = h * _VOL_RATIO
        price = QRectF(plot.x(), plot.y(), w, h - vol_h - _PANE_GAP)
        vol = QRectF(plot.x(), plot.y() + h - vol_h, w, vol_h)
        return plot, price, vol

    def _bar_x(self, i: int, n: int, rect: QRectF) -> float:
        """第 i 根 bar（0-based，左→右）嘅中心 x。"""
        slot = self._bar_slot(n, rect)
        return rect.x() + (i + 0.5) * slot

    def _bar_slot(self, n: int, rect: QRectF) -> float:
        """單一 bar-slot 寬度：plot 寬 ÷（可見根數 + 右側留白）——右端恆空出 5 個 slot。"""
        return rect.width() / max(1, n + _RIGHT_MARGIN_BARS)

    # ------------------------------------------------------------- events

    def wheelEvent(self, event):  # noqa: N802 (Qt naming)
        if not self._bars:
            return
        plot, price_r, _vol = self._panes()
        pos = event.position()
        delta = wheel_notches(event.angleDelta().y())  # ±120°/notch → ±1 階（多段式縮放）
        if delta == 0:
            return
        if event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier):
            # Y 軸縮放（游標錨定）：Ctrl/Shift + wheel；每 notch 一階 ×/÷1.25
            rng = self._y_range or price_range(visible_window(self._bars, self._view_count, self._right_offset)) or (0.0, 1.0)
            f = (pos.y() - price_r.top()) / max(1e-9, price_r.height()) if price_r.contains(pos) else 0.5
            self._y_range = zoom_y(rng[0], rng[1], f, delta)
        else:
            # X 軸縮放（游標錨定）：plain wheel；每 notch 一階 ×/÷1.25（多段式，唔再直跳極限）
            f = (pos.x() - plot.left()) / max(1e-9, plot.width()) if plot.contains(pos) else 0.5
            self._view_count, self._right_offset = zoom_x(self._view_count, self._right_offset, len(self._bars), f, delta)
        self.update()
        if not (event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)):
            self._emit_view_changed()  # X 軸縮放 → 同步其他 pane（Y 軸唔影響時間視窗）

    def mousePressEvent(self, event):  # noqa: N802 (Qt naming)
        if not self._bars:
            return
        if event.button() == Qt.LeftButton:
            self._drag_mode = 'x'
            self._last_drag_pos = event.position()
        elif event.button() == Qt.RightButton:
            self._drag_mode = 'y'
            self._last_drag_pos = event.position()

    def mouseMoveEvent(self, event):  # noqa: N802 (Qt naming)
        pos = event.position()
        moved_x = False
        if self._drag_mode and self._last_drag_pos is not None and self._bars:
            plot, price_r, _vol = self._panes()
            dx = pos.x() - self._last_drag_pos.x()
            dy = pos.y() - self._last_drag_pos.y()
            if self._drag_mode == 'x':
                slot = self._bar_slot(len(visible_window(self._bars, self._view_count, self._right_offset)), plot)
                # 拖右（dx>0）→ 視窗移向舊數據（offset 增加）
                self._view_count, self._right_offset = pan_x(self._view_count, self._right_offset, len(self._bars), dx / max(1e-9, slot))
                moved_x = True
            else:
                rng = self._y_range or price_range(visible_window(self._bars, self._view_count, self._right_offset)) or (0.0, 1.0)
                span = max(1e-9, rng[1] - rng[0])
                # 拖下（dy>0）→ 範圍移向更高價
                self._y_range = pan_y(rng[0], rng[1], dy * span / max(1e-9, price_r.height()))
            self._last_drag_pos = pos
        self._mouse_pos = pos
        self.update()
        if moved_x:
            self._emit_view_changed()  # X 軸平移 → 同步其他 pane（Y 軸唔影響時間視窗）

    def mouseReleaseEvent(self, event):  # noqa: N802 (Qt naming)
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            self._drag_mode = None
            self._last_drag_pos = None

    def mouseDoubleClickEvent(self, event):  # noqa: N802 (Qt naming)
        if event.button() == Qt.LeftButton:
            self.reset_view()

    def contextMenuEvent(self, event):  # noqa: N802 (Qt naming)
        event.ignore()  # 右鍵保留俾垂直平移，唔彈出系統選單

    def mouseLeaveEvent(self, event):  # noqa: N802 (Qt naming)
        self._mouse_pos = None
        self.update()

    # ------------------------------------------------------------- paint

    def paintEvent(self, _event):  # noqa: N802 (Qt naming)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        cfg = self._cfg
        bg = QColor(cfg.bg_color)
        p.fillRect(self.rect(), bg)

        if not self._bars:
            p.setPen(QColor(cfg.text_color))
            f = QFont("Consolas", 12)
            p.setFont(f)
            p.drawText(self.rect(), Qt.AlignCenter, "等待行情數據…")
            return

        bars = visible_window(self._bars, self._view_count, self._right_offset)
        n = len(bars)
        plot, price_r, vol_r = self._panes()
        rng = self._y_range or price_range(bars) or (0.0, 1.0)
        lo, hi = rng

        def y_price(v: float) -> float:
            return price_r.bottom() - (v - lo) / (hi - lo) * price_r.height()

        axis_font = QFont("Consolas", 8)
        p.setFont(axis_font)

        # --- grid + 右軸 price labels
        step = nice_step(hi - lo)
        first = math.ceil(lo / step) * step
        p.setPen(QColor(cfg.grid_color))
        v = first
        while v <= hi:
            y = y_price(v)
            if price_r.top() <= y <= price_r.bottom():
                p.drawLine(int(price_r.left()), int(y), int(price_r.right()), int(y))
                p.setPen(QColor(cfg.axis_text_color))
                p.drawText(QRectF(price_r.right() + 4, y - 8, _M_RIGHT - 8, 16),
                           Qt.AlignLeft | Qt.AlignVCenter, fmt_price(v))
                p.setPen(QColor(cfg.grid_color))
            v += step

        # --- 時間軸 gridline + labels（間隔 ~90px）
        label_every = max(1, n // max(1, int(plot.width() // 90)))
        for i in range(0, n, label_every):
            x = int(self._bar_x(i, n, plot))
            p.setPen(QColor(cfg.grid_color))
            p.drawLine(x, int(price_r.top()), x, int(vol_r.bottom()))
            p.setPen(QColor(cfg.axis_text_color))
            p.drawText(QRectF(x - 40, vol_r.bottom() + 4, 80, 16),
                       Qt.AlignHCenter | Qt.AlignTop, time_label(bars[i][0]))

        # --- Kill Zone session bands（背景層：volume/蠟燭之前畫；indigo fill + label）
        vmax = volume_max(bars)
        slot = self._bar_slot(n, plot)
        body_w = max(1.0, slot * 0.7)
        if self._kz_bands:
            s0, _e0 = visible_slice_range(self._bars, self._view_count, self._right_offset)
            kz_c = QColor("#5C6BC0")
            for start, end, key in self._kz_bands:
                if end < s0:
                    continue                       # band 完全喺視窗前 → skip
                li = max(0, start - s0)
                re_ = min(n - 1, end - s0)
                x_left = plot.left() + li * slot
                x_right = plot.left() + (re_ + 1) * slot
                band = QRectF(x_left, plot.top(), x_right - x_left, plot.height())
                fill = QColor(kz_c)
                fill.setAlpha(30)
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(fill))
                p.drawRect(band)
                if band.width() >= 34:             # 夠寬先畫 label（zoom out 避免擠塞）
                    lab = QColor(kz_c)
                    lab.setAlpha(150)
                    p.setPen(lab)
                    p.drawText(QRectF(x_left + 2, plot.top() + 2, band.width() - 4, 14),
                               Qt.AlignLeft | Qt.AlignTop, _KZ_LABELS.get(key, key))

        # --- Premium/Discount dealing range（背景層：KZ 之後、volume/蠟燭之前；premium 紅 tint / discount 綠 tint + EQ 線）
        if self._pd_zones:
            for z in self._pd_zones:
                y_t, y_b = y_price(z.top), y_price(z.bottom)
                top_y = max(y_t, price_r.top())    # clip 入 price 區（唔會畫去 volume subpane / margin）
                bot_y = min(y_b, price_r.bottom())
                if top_y >= bot_y:
                    continue                       # 完全喺當前 Y 範圍外 → 唔畫
                band = QRectF(plot.left(), top_y, plot.width(), bot_y - top_y)   # start=0/end=None → 全寬
                fill = QColor("#F23645" if z.kind == "premium" else "#089981")
                fill.setAlpha(18)                  # 極淡 tint：premium=bearish 紅 / discount=bullish 綠
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(fill))
                p.drawRect(band)
            eq_price = self._pd_zones[0].bottom     # equilibrium = premium.bottom == discount.top（兩帶交界）
            y_eq = y_price(eq_price)
            if price_r.top() <= y_eq <= price_r.bottom():
                p.setPen(QPen(QColor("#CFD8DC"), 1, Qt.SolidLine))   # EQ 線：palette 唯一藍灰（可 pixel-count）
                p.drawLine(int(plot.left()), int(y_eq), int(plot.right()), int(y_eq))
                p.drawText(QRectF(plot.left() + 2, y_eq - 14, 30, 12),
                           Qt.AlignLeft | Qt.AlignBottom, "EQ")

        # --- volume subpane（先畫，蠟燭層喺上面；bar 寬度同蠟燭 body 一致）
        up_c = QColor(cfg.up_color)
        down_c = QColor(cfg.down_color)
        p.setPen(Qt.NoPen)
        for i, b in enumerate(bars):
            x = self._bar_x(i, n, plot)
            h_px = (b[5] / vmax) * vol_r.height()
            color = up_c if b[4] >= b[1] else down_c
            p.setBrush(QBrush(color))
            p.drawRect(QRectF(x - body_w / 2, vol_r.bottom() - h_px, body_w, max(1.0, h_px)))

        # --- 蠟燭（wick + body）
        for i, b in enumerate(bars):
            key, o, h_, l_, c, _v = b
            x = self._bar_x(i, n, plot)
            color = up_c if c >= o else down_c
            p.setPen(QPen(color, 1))
            p.drawLine(int(x), int(y_price(h_)), int(x), int(y_price(l_)))
            top, bot = sorted((y_price(o), y_price(c)))
            body_h = max(1.0, bot - top)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawRect(QRectF(x - body_w / 2, top, body_w, body_h))

        # --- ICT 指標層（OB / FVG / Breaker / Confluence / VOB / OTE）：價格錨定矩形畫喺蠟燭上面；zone index 係 global →
        #     visible_slice_range() 映射返 local；完全喺視窗外 / Y 範圍外嘅 zone skip。
        #     繪製順序 fvg → ob → breaker → confluence → vob → ote（vob/ote 高優先級最上層）
        if self._zones:
            s0, _e0 = visible_slice_range(self._bars, self._view_count, self._right_offset)
            for kind in ("fvg", "ob", "breaker", "confluence", "vob", "ote"):
                for z in self._zones.get(kind, ()):
                    if z.end_idx is not None and z.end_idx < s0:
                        continue                       # 已喺視窗前填補/失效 → skip
                    li = max(0, z.start_idx - s0)      # 左緣 local index
                    re_ = n - 1 if z.end_idx is None else min(n - 1, z.end_idx - s0)
                    if re_ < li:
                        continue                       # 同可見視窗無重疊 → skip
                    x_left = plot.left() + li * slot   # bar li slot 左緣
                    x_right = plot.right() if z.end_idx is None else plot.left() + (re_ + 1) * slot
                    y_t, y_b = y_price(z.top), y_price(z.bottom)
                    top_y = max(y_t, price_r.top())    # clip 入 price 區（唔會畫去 volume subpane / margin）
                    bot_y = min(y_b, price_r.bottom())
                    if top_y >= bot_y:
                        continue                       # zone 完全喺當前 Y 範圍上/下方 → 唔畫
                    rect = QRectF(x_left, top_y, x_right - x_left, bot_y - top_y)
                    if kind == "confluence":
                        base = QColor("#B388FF")       # 紫色 accent：同橙色 last-price line、紅綠蠟燭易分辨
                        alpha, dash = 100, Qt.SolidLine
                    elif kind == "fvg":
                        base = up_c if z.side == "bullish" else down_c
                        alpha, dash = 45, Qt.DashLine  # 虛線邊框同 OB 視覺區分
                    elif kind == "breaker":
                        base = QColor("#4DD0E1")       # cyan accent：失效 OB 翻轉（獨立於 up/down 色）
                        alpha, dash = 70, Qt.SolidLine
                    elif kind == "vob":
                        base = QColor("#69F0AE")       # 亮綠：有效訂單塊（三重驗證通過）高優先級
                        alpha, dash = 45, Qt.SolidLine
                    elif kind == "ote":
                        base = QColor("#FFC400")       # 金色：OTE golden pocket（62%–79% Fibonacci 回撤帶）
                        alpha, dash = 50, Qt.SolidLine
                    else:                              # ob
                        base = up_c if z.side == "bullish" else down_c
                        alpha, dash = 80, Qt.SolidLine
                    fill = QColor(base)
                    fill.setAlpha(alpha)
                    p.setPen(Qt.NoPen)
                    p.setBrush(QBrush(fill))
                    p.drawRect(rect)
                    p.setPen(QPen(base, 2 if kind in ("vob", "ote") else 1, dash))   # vob/ote 加粗邊框強調優先級
                    p.setBrush(Qt.NoBrush)
                    p.drawRect(rect)

        # --- Daily reference lines（DO 線段 + PH/PL/PC 全寬水平線；畫喺 zone 之後、overlay 之前）
        if self._ref_lines:
            s0, _e0 = visible_slice_range(self._bars, self._view_count, self._right_offset)
            ref_colors = {"do": "#90A4AE", "ph": "#FFD54F", "pl": "#64B5F6", "pc": "#E0E0E0"}
            for rl in self._ref_lines:
                if rl.end_idx is not None and rl.end_idx < s0:
                    continue                       # 線段完全喺視窗前 → skip
                y = y_price(rl.price)
                if y < price_r.top() or y > price_r.bottom():
                    continue                       # 超出當前 Y 範圍 → 唔畫
                li = max(0, rl.start_idx - s0)
                re_ = n - 1 if rl.end_idx is None else min(n - 1, rl.end_idx - s0)
                x_left = plot.left() + li * slot
                x_right = (plot.right() if rl.end_idx is None
                           else plot.left() + (re_ + 1) * slot)
                color = QColor(ref_colors[rl.kind])
                p.setPen(QPen(color, 1, Qt.DashLine if rl.kind == "do" else Qt.SolidLine))
                p.drawLine(int(x_left), int(y), int(x_right), int(y))
                p.drawText(QRectF(x_left + 2, y - 14, 30, 12),
                           Qt.AlignLeft | Qt.AlignBottom, rl.kind.upper())

        # --- Session High/Low（per-day 範圍線段；畫喺 ref lines 之後、levels 之前）
        if self._session_lines:
            s0, _e0 = visible_slice_range(self._bars, self._view_count, self._right_offset)
            session_colors = {"sh": "#FF6E40", "sl": "#9CCC65"}   # SH 深橙 / SL 青檸綠（palette 唯一）
            for rl in self._session_lines:
                if rl.end_idx is not None and rl.end_idx < s0:
                    continue                       # 線段完全喺視窗前 → skip
                y = y_price(rl.price)
                if y < price_r.top() or y > price_r.bottom():
                    continue                       # 超出當前 Y 範圍 → 唔畫
                li = max(0, rl.start_idx - s0)
                re_ = n - 1 if rl.end_idx is None else min(n - 1, rl.end_idx - s0)
                x_left = plot.left() + li * slot
                x_right = (plot.right() if rl.end_idx is None
                           else plot.left() + (re_ + 1) * slot)
                color = QColor(session_colors[rl.kind])
                p.setPen(QPen(color, 1, Qt.SolidLine))   # 實線：當日實際範圍（已成交）
                p.drawLine(int(x_left), int(y), int(x_right), int(y))

        # --- Weekly/Monthly reference lines（Prev Week / Prev Month HLC 全寬水平線；畫喺 session lines 之後）
        if self._wm_lines:
            wm_colors = {"pwh": "#00ACC1", "pwl": "#0097A7", "pwc": "#26C6DA",   # weekly 青色系（palette 唯一）
                         "pmh": "#9575CD", "pml": "#7E57C2", "pmc": "#B39DDB"}  # monthly 紫色系（palette 唯一）
            for rl in self._wm_lines:
                y = y_price(rl.price)
                if y < price_r.top() or y > price_r.bottom():
                    continue                       # 超出當前 Y 範圍 → 唔畫
                color = QColor(wm_colors[rl.kind])
                dash = Qt.DashDotLine if rl.kind.startswith("pw") else Qt.DotLine   # weekly 點劃線 / monthly 虛點線
                p.setPen(QPen(color, 1, dash))
                p.drawLine(int(plot.left()), int(y), int(plot.right()), int(y))     # 全部全寬（end_idx=None）
                p.drawText(QRectF(plot.left() + 2, y - 14, 30, 12),
                           Qt.AlignLeft | Qt.AlignBottom, rl.kind.upper())

        # --- Liquidity Levels（BSL/SSL 流動性池水平線；畫喺 ref lines 之後、overlay 之前）
        if self._levels:
            s0, _e0 = visible_slice_range(self._bars, self._view_count, self._right_offset)
            level_colors = {"bsl": "#FF80AB", "ssl": "#7C4DFF"}   # BSL 粉紅 / SSL 深紫（palette 唯一）
            for lv in self._levels:
                if lv.end_idx is not None and lv.end_idx < s0:
                    continue                       # 線段完全喺視窗前 → skip
                y = y_price(lv.price)
                if y < price_r.top() or y > price_r.bottom():
                    continue                       # 超出當前 Y 範圍 → 唔畫
                li = max(0, lv.start_idx - s0)
                re_ = n - 1 if lv.end_idx is None else min(n - 1, lv.end_idx - s0)
                x_left = plot.left() + li * slot
                x_right = (plot.right() if lv.end_idx is None
                           else plot.left() + (re_ + 1) * slot)
                color = QColor(level_colors[lv.kind])
                p.setPen(QPen(color, 1, Qt.DashLine))   # 虛線：流動性池（未觸及前係「潛在」位）
                p.drawLine(int(x_left), int(y), int(x_right), int(y))
                p.drawText(QRectF(x_left + 2, y - 14, 30, 12),
                           Qt.AlignLeft | Qt.AlignBottom, lv.kind.upper())

        # --- Structure Breaks + SMT Divergence（結構突破/背離標記；畫喺 levels 之後、overlay 之前）
        #     每個 marker = 特定 bar 上嘅小三角：direction "up" → high 上方指上、「down」→ low 下方指下。
        all_markers = self._markers + self._smt_markers   # BOS/CHoCH + SMT bearish/bullish（同三角形樣式）
        if all_markers:
            s0, _e0 = visible_slice_range(self._bars, self._view_count, self._right_offset)
            marker_colors = {"bos": "#FF9100", "choch": "#E040FB",   # BOS 橙 / CHoCH 品紅（palette 唯一）
                             "smt_bearish": "#FF4081",               # SMT bearish 粉紅（palette 唯一）
                             "smt_bullish": "#18FFFF"}               # SMT bullish 青（palette 唯一）
            for mk in all_markers:
                li = mk.idx - s0
                if li < 0 or li >= n:
                    continue                       # 標記喺可見視窗外 → skip
                b = bars[li]                        # (key, o, h, l, c, v)
                x = self._bar_x(li, n, plot)        # bar 中心 x（同蠟燭 body 對齊）
                if mk.direction == "up":            # 向上突破 → 三角喺 high 上方指上
                    y_base = y_price(b[2]) - 3      # 底邊（貼住 high 之上少少）
                    y_apex = y_base - 10            # 頂點（更上，Qt y 向下增大）
                else:                               # 向下突破 → 三角喺 low 下方指下
                    y_base = y_price(b[3]) + 3      # 底邊（貼住 low 之下少少）
                    y_apex = y_base + 10            # 頂點（更下）
                color = QColor(marker_colors[mk.kind])
                half = max(4.0, min(slot * 0.4, 8.0))   # 三角半寬跟 bar 寬度、clamp [4,8]px
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(color))
                p.drawPolygon(QPolygonF([QPointF(x - half, y_base), QPointF(x + half, y_base),
                                         QPointF(x, y_apex)]))
                label = {"bos": "BOS", "choch": "CHoCH"}.get(mk.kind, "SMT")
                p.setPen(color)
                ly = (y_apex - 14) if mk.direction == "up" else (y_apex + 2)
                p.drawText(QRectF(x - 20, ly, 40, 12), Qt.AlignHCenter | Qt.AlignVCenter, label)

        # --- overlays（通用擴展點；ICT FVG / Order Block 已係一級指標層，見上）
        for fn in self._overlays:
            fn(p, bars, price_r)

        # --- last-price dashed line + 右軸 tag（跟隨「真正最新一根 bar」self._bars[-1]，
        #     唔係可見視窗最右邊嗰根——pan 左走遠後仍顯示真實最新價；若最新價超出當前
        #     Y 範圍（auto-fit 只 fit 可見 bars / 手動 Y zoom/pan）→ 整條線 + tag 唔畫，
        #     同 gridline 一樣 bounds-check，避免繪製出界）
        last = self._bars[-1]
        y_last = y_price(last[4])
        if price_r.top() <= y_last <= price_r.bottom():
            lp_color = QColor(cfg.last_price_color)
            p.setPen(QPen(lp_color, 1, Qt.DashLine))
            p.drawLine(int(price_r.left()), int(y_last), int(price_r.right()), int(y_last))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(lp_color))
            tag = QRectF(price_r.right() + 2, y_last - 9, _M_RIGHT - 6, 18)
            p.drawRect(tag)
            p.setPen(QColor("#101418"))
            p.drawText(tag, Qt.AlignCenter, fmt_price(last[4]))

        # --- crosshair + OHLCV readout
        if self._mouse_pos is not None:
            mx = self._mouse_pos.x()
            my = self._mouse_pos.y()
            if plot.contains(QPointF(mx, my)):
                i = min(n - 1, max(0, int((mx - plot.left()) / slot)))
                cx = self._bar_x(i, n, plot)
                p.setPen(QPen(QColor(cfg.text_color), 1, Qt.DashLine))
                p.drawLine(int(cx), int(price_r.top()), int(cx), int(vol_r.bottom()))
                if price_r.contains(QPointF(mx, my)):
                    p.drawLine(int(plot.left()), int(my), int(plot.right()), int(my))
                b = bars[i]
                up = b[4] >= b[1]
                p.setPen(QColor(cfg.up_color if up else cfg.down_color))
                f = QFont("Consolas", 9)
                p.setFont(f)
                readout = (f"{b[0]}   O {fmt_price(b[1])}  H {fmt_price(b[2])}  "
                           f"L {fmt_price(b[3])}  C {fmt_price(b[4])}  V {b[5]:,.0f}")
                p.drawText(QRectF(plot.left(), plot.top() - _M_TOP + 6, plot.width(), 18),
                           Qt.AlignLeft | Qt.AlignVCenter, readout)
