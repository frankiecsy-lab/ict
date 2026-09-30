"""全屏幕深色主題蠟燭圖表（純 QPainter，零第三方圖表庫）。

Backpressure：update_bars() 只記錄 immutable snapshot + 起 singleShot QTimer(30ms)，
tick burst 都最多 ~30fps repaint，永遠 render 最新 snapshot。

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
    return bars[-count:]


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


# ---------------------------------------------------------------- widget

class CandleChart(QWidget):
    """蠟燭 + volume subpane + crosshair + last-price line；數據源係 immutable snapshot。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._bars: tuple[Bar, ...] = ()
        self._mouse_pos: QPointF | None = None
        self._overlays: list[Callable[[QPainter, tuple[Bar, ...], QRectF], None]] = []
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

    def mouseMoveEvent(self, event):  # noqa: N802 (Qt naming)
        self._mouse_pos = event.position()
        self.update()

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

        bars = visible_slice(self._bars, cfg.visible_bars)
        n = len(bars)
        plot, price_r, vol_r = self._panes()
        rng = price_range(bars) or (0.0, 1.0)
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

        # --- last-price dashed line + 右軸 tag
        last = bars[-1]
        y_last = y_price(last[4])
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
