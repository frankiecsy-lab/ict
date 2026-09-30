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
from typing import Callable

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

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


def visible_window(bars: tuple[Bar, ...], count: int, right_offset: float) -> tuple[Bar, ...]:
    """可見視窗（X 軸 pan/zoom 狀態 → slice）。

    count = 可見根數；right_offset = 距數據尾部嘅 bar 數（0 = 右 pin 跟隨 live）。
    Clamp 到數據邊界：左邊唔夠數據 → 視窗收窄（右側留白，唔會繞圈）；小數偏移四捨五入到整根。
    """
    if not bars or count <= 0:
        return ()
    n = len(bars)
    off = int(round(_clamp_offset(right_offset, n, count)))
    end = n - off
    start = max(0, end - count)
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


# ---------------------------------------------------------------- widget

class CandleChart(QWidget):
    """蠟燭 + volume subpane + crosshair + last-price line；數據源係 immutable snapshot。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._bars: tuple[Bar, ...] = ()
        self._mouse_pos: QPointF | None = None
        self._overlays: list[Callable[[QPainter, tuple[Bar, ...], QRectF], None]] = []
        # 互動視圖狀態（X/Y pan/zoom；reset_view() 還原預設）
        self._view_count = max(1, int(cfg.visible_bars))  # X zoom：可見根數
        self._right_offset = 0.0                          # X pan：距數據尾部 bar 數（0=右 pin 跟 live）
        self._y_range: tuple[float, float] | None = None  # Y 手動範圍；None=auto-fit
        self._drag_mode: str | None = None                # 'x'/'y'/None
        self._last_drag_pos: QPointF | None = None
        self._repaint_timer = QTimer(self)
        self._repaint_timer.setSingleShot(True)
        self._repaint_timer.setInterval(30)  # backpressure：coalesce tick burst
        self._repaint_timer.timeout.connect(self.update)

    # ------------------------------------------------------------- public API

    def update_bars(self, bars: tuple[Bar, ...]) -> None:
        """接收新 snapshot（pyqtSignal queued 過嚟）；30ms 內多次調用只 repaint 一次。"""
        self._bars = tuple(bars)
        if not self._repaint_timer.isActive():
            self._repaint_timer.start()

    def add_overlay(self, fn: Callable[[QPainter, tuple[Bar, ...], QRectF], None]) -> None:
        """註冊 overlay 繪製函數（喺蠟燭之後、crosshair 之前畫）。"""
        self._overlays.append(fn)

    def reset_view(self) -> None:
        """重置視圖狀態返預設（右 pin + auto-fit Y）；雙擊觸發，main_window 喺切換標的時亦調用。"""
        self._view_count = max(1, int(self._cfg.visible_bars))
        self._right_offset = 0.0
        self._y_range = None
        self.update()

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
        if self._drag_mode and self._last_drag_pos is not None and self._bars:
            plot, price_r, _vol = self._panes()
            dx = pos.x() - self._last_drag_pos.x()
            dy = pos.y() - self._last_drag_pos.y()
            if self._drag_mode == 'x':
                slot = self._bar_slot(len(visible_window(self._bars, self._view_count, self._right_offset)), plot)
                # 拖右（dx>0）→ 視窗移向舊數據（offset 增加）
                self._view_count, self._right_offset = pan_x(self._view_count, self._right_offset, len(self._bars), dx / max(1e-9, slot))
            else:
                rng = self._y_range or price_range(visible_window(self._bars, self._view_count, self._right_offset)) or (0.0, 1.0)
                span = max(1e-9, rng[1] - rng[0])
                # 拖下（dy>0）→ 範圍移向更高價
                self._y_range = pan_y(rng[0], rng[1], dy * span / max(1e-9, price_r.height()))
            self._last_drag_pos = pos
        self._mouse_pos = pos
        self.update()

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

        # --- overlays（ICT FVG / Order Block / Kill Zone 擴展點）
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
