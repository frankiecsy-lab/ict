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

import math
from datetime import timedelta
from typing import Callable

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from engine.indicators import Zone, confluence_zones, detect_fvg, detect_order_blocks
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
        # ICT 指標層（OB / FVG / Confluence）：toggle key → 啟用；zones = per-key 偵測結果
        # （Zone 用 global bar index，喺 repaint tick 重算——tick burst coalesce 內只算一次）
        self._indicator_enabled: dict[str, bool] = {}
        self._zones: dict[str, tuple[Zone, ...]] = {}
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

    def update_bars(self, bars: tuple[Bar, ...]) -> None:
        """接收新 snapshot（Signal queued 過嚟）；30ms 內多次調用只 repaint 一次。"""
        self._bars = tuple(bars)
        self._period_minutes = infer_period_minutes(self._bars)  # 本 pane bar 密度（時間視窗同步用）
        if not self._repaint_timer.isActive():
            self._repaint_timer.start()

    def add_overlay(self, fn: Callable[[QPainter, tuple[Bar, ...], QRectF], None]) -> None:
        """註冊 overlay 繪製函數（喺蠟燭之後、crosshair 之前畫）。"""
        self._overlays.append(fn)

    # ------------------------------------------------------------- ICT 指標層

    def set_indicator(self, key: str, on: bool) -> None:
        """開關一個指標圖層（"ob" / "fvg"）；立即重算 zones + repaint，唔使等下一 tick。"""
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
        """
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
        if ob_zones and fvg_zones:
            zones["confluence"] = confluence_zones(ob_zones, fvg_zones)
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
        slot = rect.width() / max(1, n)
        return rect.x() + (i + 0.5) * slot

    def _bar_slot(self, n: int, rect: QRectF) -> float:
        return rect.width() / max(1, n)

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

        # --- volume subpane（先畫，蠟燭層喺上面；bar 寬度同蠟燭 body 一致）
        vmax = volume_max(bars)
        slot = self._bar_slot(n, plot)
        body_w = max(1.0, slot * 0.7)
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

        # --- ICT 指標層（OB / FVG / Confluence）：價格錨定矩形畫喺蠟燭上面；zone index 係 global →
        #     visible_slice_range() 映射返 local；完全喺視窗外 / Y 範圍外嘅 zone skip。
        #     繪製順序 fvg → ob → confluence（confluence 最上層）
        if self._zones:
            s0, _e0 = visible_slice_range(self._bars, self._view_count, self._right_offset)
            for kind in ("fvg", "ob", "confluence"):
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
                    else:                              # ob
                        base = up_c if z.side == "bullish" else down_c
                        alpha, dash = 80, Qt.SolidLine
                    fill = QColor(base)
                    fill.setAlpha(alpha)
                    p.setPen(Qt.NoPen)
                    p.setBrush(QBrush(fill))
                    p.drawRect(rect)
                    p.setPen(QPen(base, 1, dash))
                    p.setBrush(Qt.NoBrush)
                    p.drawRect(rect)

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
