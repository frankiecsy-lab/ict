"""OrderWindow 單測（offscreen Qt + FakeTradeEngine）。

monkeypatch `ui.order_window.TradeEngine` → fake（唔會真係連 OpenD）；
PIN 狀態機用可注入 clock + 直接調 handler（_on_tick / _on_unlock_clicked）測試。
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")   # 必須喺 PySide6 import 前

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from config import Config
from engine.trade_engine import FundsSnapshot, PositionRow
from futu import TrdSide

import ui.order_window as ow
from ui.order_window import OrderWindow, _PinHolder


@pytest.fixture(autouse=True, scope="module")
def _app():
    return QApplication.instance() or QApplication([])


class FakeTradeEngine(QObject):
    """同 TradeEngine 相同 signal 簽名嘅 fake（唔 spawn thread、唔連 OpenD）。"""

    positions_updated = Signal(tuple)
    funds_updated = Signal(object)
    status = Signal(str)
    error = Signal(str)
    order_result = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.started_cfg = None
        self.stopped = False
        self.order_calls: list[tuple] = []

    def start(self, cfg):
        self.started_cfg = cfg

    def stop(self):
        self.stopped = True

    def place_order(self, code, side, price, qty, pin=None):
        self.order_calls.append((code, side, price, qty, pin))


def _make_window(monkeypatch, **kwargs) -> tuple[OrderWindow, FakeTradeEngine]:
    fake = FakeTradeEngine()
    monkeypatch.setattr(ow, "TradeEngine", lambda parent=None: fake)
    w = OrderWindow(Config(), **kwargs)
    return w, fake


def _unlock(w: OrderWindow, pin: str = "123456") -> None:
    w._pin_edit.setText(pin)
    w._on_unlock_clicked()


# ------------------------------------------------------------- PIN 狀態機

def test_default_state_is_locked(monkeypatch):
    """默認 LOCKED：下單表單全 disabled、解鎖/PIN 欄啟用、鎖定禁用。"""
    w, _ = _make_window(monkeypatch)
    assert w._pin_holder is None
    assert w._place_btn.isEnabled() is False
    for widget in (w._order_code, w._side_combo, w._order_price, w._order_qty):
        assert widget.isEnabled() is False
    assert w._unlock_btn.isEnabled() is True
    assert w._pin_edit.isEnabled() is True
    assert w._lock_btn.isEnabled() is False


def test_unlock_with_valid_pin_enables_trading(monkeypatch):
    w, _ = _make_window(monkeypatch)
    _unlock(w)

    assert w._pin_holder is not None
    assert w._place_btn.isEnabled() is True
    for widget in (w._order_code, w._side_combo, w._order_price, w._order_qty):
        assert widget.isEnabled() is True
    assert w._lock_btn.isEnabled() is True
    assert "已解鎖" in w._status_label.text()


def test_reject_short_or_non_digit_pin(monkeypatch):
    """5 位 / 含非數字 → 拒絕（validator 只攔用戶輸入，handler 有自己驗證）。"""
    w, _ = _make_window(monkeypatch)

    w._pin_edit.setText("12345")   # 太短
    w._on_unlock_clicked()
    assert w._pin_holder is None and w._place_btn.isEnabled() is False
    assert "PIN 必須係 6 位數字" in w._status_label.text()

    w._pin_edit.setText("12a456")   # 非數字（programmatic setText 繞過 validator）
    w._on_unlock_clicked()
    assert w._pin_holder is None and w._place_btn.isEnabled() is False


def test_lock_button_clears_pin_immediately(monkeypatch):
    """鎖定：holder 立即清空 + 下單表單 disabled（下次要重新輸入）。"""
    w, _ = _make_window(monkeypatch)
    _unlock(w)
    assert w._pin_holder is not None

    w._on_lock_clicked()
    assert w._pin_holder is None
    assert w._place_btn.isEnabled() is False
    assert w._order_code.isEnabled() is False
    assert w._lock_btn.isEnabled() is False
    assert w._unlock_btn.isEnabled() is True, "鎖定後可以重新解鎖"
    assert w._countdown_label.text() == ""
    assert "已鎖定" in w._status_label.text()


def test_expiry_auto_locks_after_ttl(monkeypatch):
    """Fake clock 過 deadline → _on_tick 自動鎖定（同手動鎖定一樣嘅路徑）。"""
    now = [1000.0]
    w, _ = _make_window(monkeypatch, clock=lambda: now[0], unlock_ttl_seconds=60)

    _unlock(w)
    assert w._pin_holder is not None

    now[0] = 1030.0   # 未過期：tick 只更新 countdown
    w._on_tick()
    assert w._pin_holder is not None
    assert "剩餘" in w._countdown_label.text()

    now[0] = 1061.0   # 過期 → 自動鎖定
    w._on_tick()
    assert w._pin_holder is None
    assert w._place_btn.isEnabled() is False
    assert "解鎖已過期" in w._status_label.text()


def test_pin_never_in_plaintext_repr(monkeypatch):
    """安全鐵律：holder repr/str 一律 '***'；PIN 欄位解鎖後即刻清空。"""
    h = _PinHolder("246810", deadline=999.0)
    assert repr(h) == "***" and str(h) == "***"
    assert "246810" not in repr(h)

    w, _ = _make_window(monkeypatch)
    _unlock(w, pin="246810")
    assert w._pin_edit.text() == "", "解鎖後欄位必須清空——臨時密碼唔留喺 UI"
    assert repr(w._pin_holder) == "***"


# ------------------------------------------------------------- engine signal handlers

def test_positions_table_populated(monkeypatch):
    rows = (
        PositionRow("HK.00700", "騰訊控股", "HK", 100, 50, 300.0, 320.0, 32000.0, 2000.0, 6.67),
        PositionRow("US.AAPL", "Apple", "US", 10, 10, 150.0, 140.0, 1400.0, -100.0, -6.67),
    )
    w, fake = _make_window(monkeypatch)

    fake.positions_updated.emit(rows)   # 同線程 → direct connection

    table = w._pos_table
    assert table.rowCount() == 2
    assert table.item(0, 0).text() == "HK.00700"
    assert table.item(0, 3).text() == "100"      # %g 格式
    assert table.item(0, 9).text() == "+6.67%"   # pl_ratio 已是百分數
    assert table.item(1, 8).text() == "-100.00"

    up = table.item(0, 8).foreground().color().name()
    down = table.item(1, 8).foreground().color().name()
    assert up != down, "盈虧正負應有不同顏色"


def test_funds_labels_updated(monkeypatch):
    funds = FundsSnapshot(
        total_assets=1_234_567.5, cash_hkd=500_000.0, cash_usd=10_000.25,
        withdraw_hkd=400_000.0, withdraw_usd=8_000.0, buying_power=2_000_000.0,
        initial_margin=50_000.0, maintenance_margin=30_000.0)
    w, fake = _make_window(monkeypatch)

    fake.funds_updated.emit(funds)

    assert w._funds_labels["total_assets"].text() == "1,234,567.50"
    assert w._funds_labels["cash_hkd"].text() == "500,000.00"
    assert w._funds_labels["cash_usd"].text() == "10,000.25"
    assert w._funds_labels["buying_power"].text() == "2,000,000.00"
    assert w._funds_labels["initial_margin"].text() == "50,000.00"


def test_order_result_updates_status_label(monkeypatch):
    """成功/失敗 → status label 更新；unlocked 時 re-enable 下單按鍵、locked 保持 disabled。"""
    w, fake = _make_window(monkeypatch)

    # LOCKED：order_result 唔應啟用下單
    fake.order_result.emit(False, "引擎已關閉，無法下單")
    assert "引擎已關閉" in w._status_label.text()
    assert w._place_btn.isEnabled() is False

    # UNLOCKED + in-flight（btn disabled）→ result 後 re-enable
    _unlock(w)
    w._place_btn.setEnabled(False)   # 模擬 in-flight guard
    fake.order_result.emit(True, "下單成功 order_id=1")
    assert "下單成功" in w._status_label.text()
    assert w._place_btn.isEnabled() is True


# ------------------------------------------------------------- 下單流程

def test_place_order_dispatches_to_engine(monkeypatch):
    """GUI 驗證通過 → engine.place_order（pin = holder value）+ in-flight guard。"""
    w, fake = _make_window(monkeypatch)
    _unlock(w, pin="246810")

    w._order_code.setText("HK.00700")
    w._side_combo.setCurrentIndex(0)   # 買入
    w._order_price.setText("55.5")
    w._order_qty.setText("200")
    w._on_place_order()

    assert len(fake.order_calls) == 1
    code, side, price, qty, pin = fake.order_calls[0]
    assert (code, side, price, qty, pin) == ("HK.00700", TrdSide.BUY, 55.5, 200, "246810")
    assert w._place_btn.isEnabled() is False, "in-flight 期間禁用下單按鍵"


def test_place_order_sell_side(monkeypatch):
    w, fake = _make_window(monkeypatch)
    _unlock(w)

    w._order_code.setText("US.AAPL")
    w._side_combo.setCurrentIndex(1)   # 賣出
    w._order_price.setText("140.25")
    w._order_qty.setText("10")
    w._on_place_order()

    assert fake.order_calls[0][1] is TrdSide.SELL


def test_place_order_rejects_invalid_input(monkeypatch):
    """代碼無 '.' / 非數字價格 → 唔 dispatch + 錯誤 status。"""
    w, fake = _make_window(monkeypatch)
    _unlock(w)

    w._order_code.setText("NOPE")   # 無 market prefix
    w._order_price.setText("10")
    w._order_qty.setText("5")
    w._on_place_order()
    assert fake.order_calls == []
    assert "代碼格式錯誤" in w._status_label.text()

    w._order_code.setText("HK.00700")
    w._order_price.setText("abc")   # 非數字（programmatic setText 繞過 validator）
    w._on_place_order()
    assert fake.order_calls == []
    assert "必須係數字" in w._status_label.text()


def test_shutdown_stops_engine(monkeypatch):
    w, fake = _make_window(monkeypatch)
    assert fake.started_cfg is not None, "constructor 應 start engine"
    w.shutdown()
    assert fake.stopped is True
