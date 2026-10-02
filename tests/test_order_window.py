"""OrderWindow 單測（offscreen Qt + FakeTradeEngine）。

monkeypatch `ui.order_window.TradeEngine` → fake（唔會真係連 OpenD）；
PIN 狀態機用可注入 clock + 直接調 handler（_on_tick / _on_unlock_clicked）測試。
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")   # 必須喺 PySide6 import 前

import pytest
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QMessageBox, QPushButton

from config import Config
from engine.trade_engine import AccountInfo, FundsSnapshot, OrderRow, PositionRow
from futu import TrdSide

import ui.order_window as ow
from ui.order_window import OrderWindow, _PinHolder, _order_status_zh, _price_step


@pytest.fixture(autouse=True, scope="module")
def _app():
    return QApplication.instance() or QApplication([])


class FakeTradeEngine(QObject):
    """同 TradeEngine 相同 signal 簽名嘅 fake（唔 spawn thread、唔連 OpenD）。"""

    accounts_updated = Signal(tuple)
    positions_updated = Signal(tuple)
    account_funds_updated = Signal(object, str, object)   # (acc_id, trd_env "REAL"/"SIMULATE", FundsSnapshot)——object 唔好 int（18 位 snowflake acc_id，Commit 32）
    orders_updated = Signal(tuple)
    status = Signal(str)
    error = Signal(str)
    order_result = Signal(bool, str)
    cancel_result = Signal(bool, str)   # Commit 34：撤單結果（同 order_result 共用 action-done handler）

    def __init__(self, parent=None):
        super().__init__(parent)
        self.started_cfg = None
        self.stopped = False
        self.order_calls: list[tuple] = []
        self.cancel_calls: list[tuple] = []   # Commit 34：(order_id, code, trd_env, acc_id)

    def start(self, cfg):
        self.started_cfg = cfg

    def stop(self):
        self.stopped = True

    def place_order(self, code, side, price, qty, pin=None, *, trd_env="REAL", acc_id=None, market=False):
        """Commit 33：dispatch 帶 trd_env（模式）+ acc_id（自動匹配帳戶）；Commit 34：market flag。"""
        self.order_calls.append((code, side, price, qty, pin, trd_env, acc_id, market))

    def cancel_order(self, order_id, code, *, trd_env="REAL", acc_id=None):
        """Commit 34：記錄撤單調用（同步 fake——測試需手動 emit result signal drain queue）。"""
        self.cancel_calls.append((order_id, code, trd_env, acc_id))


def _make_window(monkeypatch, **kwargs) -> tuple[OrderWindow, FakeTradeEngine]:
    fake = FakeTradeEngine()
    monkeypatch.setattr(ow, "TradeEngine", lambda parent=None: fake)
    w = OrderWindow(Config(), **kwargs)
    return w, fake


def _unlock(w: OrderWindow, pin: str = "123456") -> None:
    w._pin_edit.setText(pin)
    w._on_unlock_clicked()


# ------------------------------------------------------------- PIN 狀態機

def test_default_state_simulate_unlocked(monkeypatch):
    """Commit 33：默認模擬盤——永遠解鎖（futu 規則：模擬無需交易密碼）；PIN 區隱藏。"""
    w, _ = _make_window(monkeypatch)
    assert w._mode == "SIMULATE"
    assert w._pin_holder is None
    assert w._pin_box.isHidden() is True        # PIN 區只喺 REAL 顯示（isHidden：offscreen 未 show 視窗下 isVisible 恆 False）
    assert w._sim_hint.isHidden() is False
    for widget in (w._order_code, w._buy_btn, w._sell_btn, w._order_qty):
        assert widget.isEnabled() is True       # 模擬盤直接可交易
    assert w._order_price.isEnabled() is False   # follow mode：由市價驅動
    assert w._lock_btn.isEnabled() is False      # 無 holder → 唔使鎖


def test_real_mode_locked_until_pin(monkeypatch):
    """Commit 33：切實盤 → PIN 區顯示 + 下單表單 disabled（直到輸入六位數 PIN）。"""
    w, _ = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)

    assert w._mode == "REAL"
    assert w._pin_box.isHidden() is False       # PIN 區顯示（isHidden：offscreen 未 show 視窗下 isVisible 恆 False）
    assert w._sim_hint.isHidden() is True
    for widget in (w._order_code, w._buy_btn, w._sell_btn, w._order_qty):
        assert widget.isEnabled() is False


def test_unlock_with_valid_pin_enables_trading(monkeypatch):
    """Commit 33：實盤 + 6 位數字 PIN → holder 建立 + 下單表單啟用。"""
    w, _ = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)
    assert w._buy_btn.isEnabled() is False

    _unlock(w)

    assert w._pin_holder is not None
    for widget in (w._order_code, w._buy_btn, w._sell_btn, w._order_qty):
        assert widget.isEnabled() is True
    # 價格欄：follow mode（默認）→ 解鎖後仍 disabled（由市價驅動）；manual mode 需解鎖先可輸入
    assert w._following is True and w._order_price.isEnabled() is False
    assert w._follow_btn.isEnabled() is True, "模式切換按鍵唔係交易動作——永遠可用"
    assert w._lock_btn.isEnabled() is True
    assert "已解鎖" in w._status_label.text()


def test_reject_short_or_non_digit_pin(monkeypatch):
    """5 位 / 含非數字 → 拒絕（validator 只攔用戶輸入，handler 有自己驗證）。"""
    w, _ = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)

    w._pin_edit.setText("12345")   # 太短
    w._on_unlock_clicked()
    assert w._pin_holder is None and w._buy_btn.isEnabled() is False
    assert "PIN 必須係 6 位數字" in w._status_label.text()

    w._pin_edit.setText("12a456")   # 非數字（programmatic setText 繞過 validator）
    w._on_unlock_clicked()
    assert w._pin_holder is None and w._buy_btn.isEnabled() is False


def test_lock_button_clears_pin_immediately(monkeypatch):
    """鎖定：holder 立即清空 + 下單表單 disabled（下次要重新輸入）。"""
    w, _ = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)
    _unlock(w)
    assert w._pin_holder is not None

    w._on_lock_clicked()
    assert w._pin_holder is None
    assert w._buy_btn.isEnabled() is False and w._sell_btn.isEnabled() is False
    assert w._order_code.isEnabled() is False
    assert w._lock_btn.isEnabled() is False
    assert w._unlock_btn.isEnabled() is True, "鎖定後可以重新解鎖"
    assert w._countdown_label.text() == ""
    assert "已鎖定" in w._status_label.text()


def test_expiry_auto_locks_after_ttl(monkeypatch):
    """Fake clock 過 deadline → _on_tick 自動鎖定（同手動鎖定一樣嘅路徑）。"""
    now = [1000.0]
    w, _ = _make_window(monkeypatch, clock=lambda: now[0], unlock_ttl_seconds=60)
    w._mode_real_btn.setChecked(True)

    _unlock(w)
    assert w._pin_holder is not None

    now[0] = 1030.0   # 未過期：tick 只更新 countdown
    w._on_tick()
    assert w._pin_holder is not None
    assert "剩餘" in w._countdown_label.text()

    now[0] = 1061.0   # 過期 → 自動鎖定
    w._on_tick()
    assert w._pin_holder is None
    assert w._buy_btn.isEnabled() is False and w._sell_btn.isEnabled() is False
    assert "解鎖已過期" in w._status_label.text()


def test_pin_never_in_plaintext_repr(monkeypatch):
    """安全鐵律：holder repr/str 一律 '***'；PIN 欄位解鎖後即刻清空。"""
    h = _PinHolder("246810", deadline=999.0)
    assert repr(h) == "***" and str(h) == "***"
    assert "246810" not in repr(h)

    w, _ = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)
    _unlock(w, pin="246810")
    assert w._pin_edit.text() == "", "解鎖後欄位必須清空——臨時密碼唔留喺 UI"
    assert repr(w._pin_holder) == "***"


# ------------------------------------------------------------- engine signal handlers

def test_positions_table_populated(monkeypatch):
    rows = (
        PositionRow("HK.00700", "騰訊控股", "HK", 100, 50, 300.0, 320.0, 32000.0, 2000.0, 6.67, 150.0),
        PositionRow("US.AAPL", "Apple", "US", 10, 10, 150.0, 140.0, 1400.0, -100.0, -6.67, -20.0),
    )
    w, fake = _make_window(monkeypatch)

    fake.positions_updated.emit(rows)   # 同線程 → direct connection

    table = w._pos_table
    assert table.rowCount() == 2
    assert table.columnCount() == 13, "Commit 34：持倉表加「操作」（平倉）欄 → 13 欄"
    assert table.item(0, 0).text() == "HK.00700"
    assert table.item(0, 3).text() == "0·實"     # Commit 31：帳戶欄（acc_id=0 / REAL → 「0·實」）
    assert table.item(0, 4).text() == "100"      # %g 格式
    assert table.item(0, 10).text() == "150.00"  # 今日盈虧（APP 對齊 today_pl_val）
    assert table.item(0, 11).text() == "+6.67%"  # pl_ratio 已是百分數
    assert table.item(1, 9).text() == "-100.00"

    up = table.item(0, 9).foreground().color().name()
    down = table.item(1, 9).foreground().color().name()
    assert up != down, "盈虧正負應有不同顏色"


def test_funds_labels_updated(monkeypatch):
    """Per-account 資金事件 → 該 env tab 9 欄（單帳戶 = 自己數值）+ 其他 env 唔受影響。"""
    funds = FundsSnapshot(
        total_assets=1_234_567.5, cash_hkd=500_000.0, cash_usd=10_000.25,
        withdraw_hkd=400_000.0, withdraw_usd=8_000.0, buying_power=2_000_000.0,
        initial_margin=50_000.0, maintenance_margin=30_000.0, risk_status="LEVEL3")
    w, fake = _make_window(monkeypatch)

    fake.account_funds_updated.emit(7, "REAL", funds)

    real = w._env_funds_labels["REAL"]
    assert real["total_assets"].text() == "1,234,567.50"
    assert real["cash_hkd"].text() == "500,000.00"
    assert real["cash_usd"].text() == "10,000.25"
    assert real["buying_power"].text() == "2,000,000.00"
    assert real["initial_margin"].text() == "50,000.00"
    assert real["risk_status"].text() == "安全", "LEVEL3 → 中文風控狀態"

    sim = w._env_funds_labels["SIMULATE"]
    assert sim["total_assets"].text() == "—", "SIMULATE env 無事件 → 全 '—'"


def _acc(acc_id: int, env: str = "REAL", acc_type: str = "MARGIN", sim_acc_type: str = "",
         role: str = "", auth=("HK",), card: str = "12345678", acc_status: str = "ACTIVE") -> AccountInfo:
    """AccountInfo test factory（keyword 參數，字段順序無關；默認 ACTIVE——非 ACTIVE 會被隱藏）。"""
    return AccountInfo(
        acc_id=acc_id, trd_env=env, acc_type=acc_type, sim_acc_type=sim_acc_type,
        uni_card_num=f"U{card}", card_num=card, security_firm="FUTUSECURITIES",
        trdmarket_auth=tuple(auth), acc_role=role, acc_status=acc_status)


def _funds(total_assets: float = 0.0, **kw) -> FundsSnapshot:
    """FundsSnapshot test factory（未指定字段默認 0 / LEVEL3）。"""
    base = dict(cash_hkd=0.0, cash_usd=0.0, withdraw_hkd=0.0, withdraw_usd=0.0,
                buying_power=0.0, initial_margin=0.0, maintenance_margin=0.0, risk_status="LEVEL3")
    base.update(kw)
    return FundsSnapshot(total_assets=total_assets, **base)


def test_account_cards_render_per_account(monkeypatch):
    """accounts_updated → per-account 卡片按 env tab 分類（REAL/SIMULATE、按 acc_id 排序）+ 標籤 + 卡號末四位常駐可見。"""
    w, fake = _make_window(monkeypatch)

    fake.accounts_updated.emit((
        _acc(2),                                        # REAL 普通
        _acc(1, role="MASTER", auth=("HK", "US")),      # REAL MASTER 主帳戶
        _acc(3, env="SIMULATE", sim_acc_type="COMPETITION", auth=("US",)),   # SIMULATE 比賽
    ))

    assert len(w._env_card_lists["REAL"]) == 2          # 實盤 tab：兩卡
    assert len(w._env_card_lists["SIMULATE"]) == 1      # 模擬 tab：一卡
    texts = "\n".join(l.text() for l in w.findChildren(QLabel))
    assert "1 · MARGIN" in texts          # 卡片 header：acc_id · acc_type
    assert "主帳戶" in texts               # MASTER → 「主帳戶」標籤
    assert "3 · MARGIN" in texts
    assert "比賽" in texts                 # COMPETITION → 「比賽」標籤
    assert "…5678" in texts               # 卡號末四位（uni_card_num U12345678）


def test_account_cards_empty_snapshot(monkeypatch):
    """accounts_updated 空 snapshot → 零卡片、無殘留（先有卡再清空）。"""
    w, fake = _make_window(monkeypatch)

    fake.accounts_updated.emit((
        _acc(2),
        _acc(1, role="MASTER"),
    ))
    assert sum(len(v) for v in w._env_card_lists.values()) == 2

    fake.accounts_updated.emit(())   # 空 snapshot（例如 OpenD 未連線 / 無帳戶）
    assert sum(len(v) for v in w._env_card_lists.values()) == 0


def test_orders_table_populated_with_status_zh_and_color(monkeypatch):
    """Commit 33：orders_updated → table 11 欄全細節（訂單號/代碼/方向/類型/狀態/數量/價格/已成交/均價/時間/帳戶）。"""
    w, fake = _make_window(monkeypatch)

    fake.orders_updated.emit((
        OrderRow("9001", "HK.00700", "BUY", "NORMAL", "FILLED_ALL", 200, 55.5, 200, 55.4,
                 "2026-10-02 09:30:00"),
        OrderRow("9002", "US.AAPL", "SELL", "NORMAL", "SUBMITTED", 10, 140.0, 0, 0.0,
                 "2026-10-02 10:00:05"),
    ))

    table = w._orders_table
    assert table.rowCount() == 2
    assert table.columnCount() == 12, "Commit 34：訂單表加「操作」（撤單）欄 → 12 欄"
    assert table.item(0, 0).text() == "9001"          # 訂單號
    assert table.item(0, 1).text() == "HK.00700"      # 代碼
    assert table.item(0, 2).text() == "買入"           # 方向中文映射
    assert table.item(0, 3).text() == "NORMAL"        # 類型
    assert table.item(0, 4).text() == "全部已成"       # 狀態中文映射
    assert table.item(0, 5).text() == "200"           # 數量 %g
    assert table.item(0, 6).text() == "55.50"         # 價格
    assert table.item(0, 7).text() == "200"           # 已成交
    assert table.item(0, 8).text() == "55.40"         # 成交均價
    assert table.item(0, 9).text() == "09:30:00"      # HH:MM:SS（SDK 'YYYY-MM-DD HH:MM:SS'）
    assert table.item(1, 2).text() == "賣出"
    assert table.item(1, 4).text() == "已提交"

    filled = table.item(0, 4).foreground().color().name()
    pending = table.item(1, 4).foreground().color().name()
    assert filled != pending, "已成（綠）同 pending（黃）應有不同顏色"


def test_order_status_zh_fallback_returns_raw():
    """未知狀態 → 原文 fallback；空字串 → '—'。"""
    assert _order_status_zh("FILLED_ALL") == "全部已成"
    assert _order_status_zh("SOME_NEW_STATUS") == "SOME_NEW_STATUS"
    assert _order_status_zh("") == "—"


def test_order_result_updates_status_label(monkeypatch):
    """成功/失敗 → status label 更新；in-flight guard re-enable（Commit 33：買賣雙按鍵）。"""
    w, fake = _make_window(monkeypatch)

    # REAL + LOCKED：order_result 唔應啟用下單
    w._mode_real_btn.setChecked(True)
    fake.order_result.emit(False, "引擎已關閉，無法下單")
    assert "引擎已關閉" in w._status_label.text()
    assert w._buy_btn.isEnabled() is False and w._sell_btn.isEnabled() is False

    # UNLOCKED + in-flight（btn disabled）→ result 後 re-enable
    _unlock(w)
    w._buy_btn.setEnabled(False)   # 模擬 in-flight guard
    fake.order_result.emit(True, "下單成功 order_id=1")
    assert "下單成功" in w._status_label.text()
    assert w._buy_btn.isEnabled() is True and w._sell_btn.isEnabled() is True


# ------------------------------------------------------------- 下單流程

def test_place_order_dispatches_to_engine(monkeypatch):
    """Commit 33：GUI 驗證通過 → engine.place_order（pin + trd_env + acc_id）+ in-flight guard。"""
    w, fake = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)
    fake.accounts_updated.emit((_acc(1, env="REAL", acc_type="CASH"),))
    assert w._matched_acc is not None
    _unlock(w, pin="246810")

    w._order_code.setText("HK.00700")
    w._order_price.setValue(55.5)      # QDoubleSpinBox（programmatic setValue 唔受 disabled 影響）
    w._order_qty.setText("200")
    w._confirm_cb.setChecked(False)   # Commit 34：跳過二次確認對話框（offscreen 會 block）
    w._on_place_order("BUY")

    assert len(fake.order_calls) == 1
    code, side, price, qty, pin, trd_env, acc_id, market = fake.order_calls[0]
    assert (code, side, price, qty, pin, trd_env, acc_id, market) == \
        ("HK.00700", TrdSide.BUY, 55.5, 200, "246810", "REAL", 1, False)
    assert w._buy_btn.isEnabled() is False and w._sell_btn.isEnabled() is False, "in-flight 期間禁用買賣按鍵"


def test_place_order_sell_side(monkeypatch):
    """Commit 33：賣出特大按鍵 → TrdSide.SELL（模擬盤無需 PIN）。"""
    w, fake = _make_window(monkeypatch)
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH", auth=("US",)),))

    w._order_code.setText("US.AAPL")
    w._order_price.setValue(140.25)
    w._order_qty.setText("10")
    w._confirm_cb.setChecked(False)   # Commit 34：跳過二次確認對話框（offscreen 會 block）
    w._on_place_order("SELL")

    assert fake.order_calls[0][1] is TrdSide.SELL
    assert fake.order_calls[0][5] == "SIMULATE"   # trd_env = 當前模式


def test_place_order_requires_matched_account(monkeypatch):
    """Commit 33：無匹配帳戶（env/市場授權唔符）→ 阻止下單 + 錯誤 status。"""
    w, fake = _make_window(monkeypatch)
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", auth=("US",)),))   # US-only

    w._order_code.setText("HK.00700")   # HK ∉ auth → 無匹配
    assert w._matched_acc is None
    w._order_price.setValue(55.5)
    w._order_qty.setText("200")
    w._on_place_order("BUY")

    assert fake.order_calls == []
    assert "無匹配" in w._status_label.text()


def test_place_order_real_mode_requires_pin(monkeypatch):
    """Commit 33：實盤未解鎖 → 阻止下單（模擬盤恆解鎖、唔受此限制）。"""
    w, fake = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)
    fake.accounts_updated.emit((_acc(1, env="REAL", acc_type="CASH"),))

    w._order_code.setText("HK.00700")
    w._order_price.setValue(55.5)
    w._order_qty.setText("200")
    w._on_place_order("BUY")

    assert fake.order_calls == []
    assert "實盤未解鎖" in w._status_label.text()


def test_place_order_rejects_invalid_input(monkeypatch):
    """代碼無 '.' / 價格 ≤ 0 → 唔 dispatch + 錯誤 status（非數字輸入由 spinbox validator 源頭攔截）。"""
    w, fake = _make_window(monkeypatch)

    w._order_code.setText("NOPE")   # 無 market prefix
    w._order_price.setValue(10.0)
    w._order_qty.setText("5")
    w._on_place_order("BUY")
    assert fake.order_calls == []
    assert "代碼格式錯誤" in w._status_label.text()

    w._order_code.setText("HK.00700")
    w._order_price.setValue(0)   # QDoubleSpinBox 原生 range——剩餘非法值只係 0/負數
    w._on_place_order("BUY")
    assert fake.order_calls == []
    assert "必須大於 0" in w._status_label.text()


def test_shutdown_stops_engine(monkeypatch):
    w, fake = _make_window(monkeypatch)
    assert fake.started_cfg is not None, "constructor 應 start engine"
    w.shutdown()
    assert fake.stopped is True


# ------------------------------------------------------------- 標的同步 / 跟隨市價 / stepper

def test_price_step_magnitudes():
    """_price_step 純函數：10^(floor(log10(p))−2) + clamp [0.01, 10]（Commit 35 R5：價格固定兩位小數）。"""
    assert _price_step(55.5) == pytest.approx(0.1)
    assert _price_step(5.5) == pytest.approx(0.01)
    assert _price_step(555.0) == pytest.approx(1.0)
    assert _price_step(0) == 0.01           # ≤0 → 最小步長（= 顯示精度）
    assert _price_step(-3.0) == 0.01
    assert _price_step(99_999.0) == 10.0    # 上限 clamp
    assert _price_step(0.05) == 0.01        # 下限 clamp（唔可以細過兩位小數顯示精度）


def test_set_symbol_syncs_order_code_even_when_locked(monkeypatch):
    """K 綫標的切換 → 下單代碼跟隨（PIN locked 都生效——純顯示，唔係交易動作）。"""
    w, _ = _make_window(monkeypatch)
    w._mode_real_btn.setChecked(True)   # REAL + LOCKED
    assert w._order_code.isEnabled() is False

    w.set_symbol("US.AAPL")
    assert w._order_code.text() == "US.AAPL"


def test_follow_price_updates_only_in_follow_mode(monkeypatch):
    """follow mode → 市價自動更新；manual mode → no-op（唔覆蓋用戶輸入）；重入 follow 還原最後市價。"""
    w, _ = _make_window(monkeypatch)

    assert w._following is True
    w.follow_price(55.5)
    assert w._order_price.value() == 55.5
    assert w._last_followed_price == 55.5
    w.follow_price(None)   # None / ≤0 → no-op
    w.follow_price(-1.0)
    assert w._order_price.value() == 55.5

    # 切 manual mode → 市價唔再覆蓋
    w._follow_btn.setChecked(False)
    assert w._following is False
    w.follow_price(99.0)
    assert w._order_price.value() == 55.5, "manual mode 唔覆蓋用戶輸入"

    # 重入 follow mode → 還原最後市價（55.5——manual mode 嘅 99.0 no-op、唔計跟隨）
    w._follow_btn.setChecked(True)
    assert w._following is True
    assert w._order_price.value() == 55.5


def test_follow_toggle_glyph_and_manual_requires_unlock(monkeypatch):
    """🔗/✎ glyph toggle + manual mode 價格欄需 PIN 解鎖先可輸入。"""
    w, _ = _make_window(monkeypatch)
    assert w._follow_btn.isChecked() is True and w._follow_btn.text() == "🔗"

    # REAL LOCKED + manual → 價格欄仍 disabled（交易動作要解鎖）
    w._mode_real_btn.setChecked(True)
    w._follow_btn.setChecked(False)
    assert w._following is False and w._follow_btn.text() == "✎"
    assert w._order_price.isEnabled() is False, "manual mode locked 時都要 PIN 解鎖先可輸入"

    _unlock(w)
    assert w._order_price.isEnabled() is True, "解鎖後 manual mode 可輸入"

    # 切返 follow → 再 disabled（由市價驅動）
    w._follow_btn.setChecked(True)
    assert w._following is True and w._follow_btn.text() == "🔗"
    assert w._order_price.isEnabled() is False


def test_account_card_shows_own_funds(monkeypatch):
    """Per-account 資金事件 → 該卡「總資產」label 更新（唔係 env 加總）；未收事件帳戶保持佔位。"""
    w, fake = _make_window(monkeypatch)
    fake.accounts_updated.emit((_acc(1), _acc(2)))

    fake.account_funds_updated.emit(1, "REAL", _funds(total_assets=1_000_000.0))
    assert w._card_funds_labels[("REAL", 1)].text() == "總資產 1,000,000.00"
    assert w._card_funds_labels[("REAL", 2)].text() == "總資產 —"


def test_env_funds_panel_sums_all_accounts_in_env(monkeypatch):
    """右側資金面板 = env 加總（GUI 端 per-env fold，重用 engine._sum_funds）。"""
    w, fake = _make_window(monkeypatch)

    fake.account_funds_updated.emit(1, "REAL", _funds(total_assets=1_000_000.0, cash_hkd=500_000.0))
    fake.account_funds_updated.emit(2, "REAL", _funds(total_assets=2_000_000.0, cash_hkd=300_000.0))

    real = w._env_funds_labels["REAL"]
    assert real["total_assets"].text() == "3,000,000.00"   # 1M + 2M
    assert real["cash_hkd"].text() == "800,000.00"         # 500k + 300k

    sim = w._env_funds_labels["SIMULATE"]
    assert sim["total_assets"].text() == "—", "SIMULATE env 無事件 → 全 '—'"


def test_non_active_accounts_hidden_from_cards(monkeypatch):
    """acc_status != ACTIVE → 隱藏（數據源照 emit、顯示過濾喺 UI 層）。"""
    w, fake = _make_window(monkeypatch)

    fake.accounts_updated.emit((
        _acc(1),                          # ACTIVE
        _acc(2, acc_status="DISABLED"),   # 非 ACTIVE → 隱藏
    ))

    assert len(w._env_card_lists["REAL"]) == 1
    texts = "\n".join(l.text() for l in w.findChildren(QLabel))
    assert "2 · MARGIN" not in texts


# ------------------------------------------------------------- Commit 31：帳戶卡撳選過濾 / 代碼補全驗證 / 買賣按鍵

def test_positions_table_account_column_dual_env(monkeypatch):
    """Commit 31：「帳戶」欄 = acc_id·實/模（雙 env 標記，SIMULATE → 「模」）。"""
    rows = (
        PositionRow("HK.00700", "騰訊控股", "HK", 100, 50, 300.0, 320.0, 32000.0, 2000.0, 6.67, 150.0,
                    acc_id=7, trd_env="REAL"),
        PositionRow("US.AAPL", "Apple", "US", 10, 10, 150.0, 140.0, 1400.0, -100.0, -6.67, -20.0,
                    acc_id=9, trd_env="SIMULATE"),
    )
    w, fake = _make_window(monkeypatch)
    fake.positions_updated.emit(rows)

    table = w._pos_table
    assert table.item(0, 3).text() == "7·實"
    assert table.item(1, 3).text() == "9·模"


def test_account_card_click_filters_positions(monkeypatch):
    """Commit 31：撳帳戶卡 → 持倉過濾該帳戶；再撳同一張卡 = 取消選取顯示全部。"""
    w, fake = _make_window(monkeypatch)
    fake.accounts_updated.emit((_acc(1), _acc(2)))

    rows = (
        PositionRow("HK.00700", "騰訊控股", "HK", 100, 50, 300.0, 320.0, 32000.0, 2000.0, 6.67, 150.0,
                    acc_id=1, trd_env="REAL"),
        PositionRow("US.AAPL", "Apple", "US", 10, 10, 150.0, 140.0, 1400.0, -100.0, -6.67, -20.0,
                    acc_id=2, trd_env="REAL"),
    )
    fake.positions_updated.emit(rows)
    assert w._pos_table.rowCount() == 2

    # 撳卡 1 → 只剩帳戶 1 持倉（_select_account 即刻用 cached snapshot 重繪）
    w._select_account(("REAL", 1))
    assert w._selected_acc == ("REAL", 1)
    assert w._pos_table.rowCount() == 1
    assert w._pos_table.item(0, 0).text() == "HK.00700"

    # 新 snapshot 到達 → 仍經已選帳戶過濾（filter 係持久狀態）
    fake.positions_updated.emit(rows + rows[:1])   # 3 行：acc1×2 + acc2
    assert w._pos_table.rowCount() == 2, "新 snapshot 都要過 filter"

    # 再撳同一張卡 → 取消選取 = 顯示全部
    w._select_account(("REAL", 1))
    assert w._selected_acc is None
    fake.positions_updated.emit(rows)
    assert w._pos_table.rowCount() == 2


def test_selected_account_reset_when_accounts_change(monkeypatch):
    """Commit 31：帳戶列表更新（例如 OpenD 重連）→ 已選卡唔存在 → 自動取消選取。"""
    w, fake = _make_window(monkeypatch)
    fake.accounts_updated.emit((_acc(1),))
    w._select_account(("REAL", 1))
    assert w._selected_acc == ("REAL", 1)

    fake.accounts_updated.emit((_acc(2),))   # 帳戶 1 消失
    assert w._selected_acc is None, "stale selection 必須清空"


def test_set_stock_catalog_populates_completer(monkeypatch):
    """Commit 31：catalog_ready → set_stock_catalog（同 K 綫圖同源）；mapping = display_text → canonical code。"""
    from engine.stock_catalog import StockEntry

    w, _ = _make_window(monkeypatch)
    entries = (StockEntry("HK.00700", "騰訊控股", "Tencent"), StockEntry("US.AAPL", "", "Apple"))
    w.set_stock_catalog(entries)

    assert len(w._code_completer.catalog()) == 2
    # display_text（雙空格 join）→ canonical code mapping
    assert w._code_by_text["HK.00700  騰訊控股  Tencent"] == "HK.00700"


def test_code_activated_and_guard_strip_to_bare_code(monkeypatch):
    """Commit 31：dropdown activated / onChange guard → 輸入欄只留純 code（同 K 綫圖一致）。"""
    from engine.stock_catalog import StockEntry

    w, _ = _make_window(monkeypatch)
    w.set_stock_catalog((StockEntry("HK.00700", "騰訊控股", "Tencent"),))

    # dropdown activated：完整 display_text → mapping hit → 純 code
    w._on_code_activated("HK.00700  騰訊控股  Tencent")
    assert w._order_code.text() == "HK.00700"

    # onChange guard：含空白文本（code + 名稱混入）→ 剝離返第一 token
    w._order_code.setText("US.AAPL Apple Inc")   # 模擬 completer 寫入完整字串
    assert w._order_code.text() == "US.AAPL"


def test_place_order_catalog_validation(monkeypatch):
    """Commit 31：目錄已載入 → 未知代碼拒絕 + 已知代碼正規化大小寫；未載入 → 放行俾 engine/OpenD。"""
    from engine.stock_catalog import StockEntry

    w, fake = _make_window(monkeypatch)   # 默認 SIMULATE（常解鎖）
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH"),))
    w.set_stock_catalog((StockEntry("HK.00700", "騰訊控股", "Tencent"),))

    # 未知代碼 → 拒絕（唔 dispatch）
    w._order_code.setText("XX.99999")
    w._order_price.setValue(10.0)
    w._order_qty.setText("5")
    w._on_place_order("BUY")
    assert fake.order_calls == []
    assert "股票編號唔存在" in w._status_label.text()

    # 已知代碼（小寫輸入）→ 正規化 canonical HK.00700 + dispatch
    w._order_code.setText("hk.00700")
    w._confirm_cb.setChecked(False)   # Commit 34：跳過二次確認對話框（offscreen 會 block）
    w._on_place_order("BUY")
    assert fake.order_calls[0][0] == "HK.00700"

    # 目錄未載入（新視窗）→ 放行俾 engine/OpenD 最終校驗
    w2, fake2 = _make_window(monkeypatch)
    fake2.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH", auth=("SG",)),))
    w2._order_code.setText("SG.D05")
    w2._order_price.setValue(1.0)
    w2._order_qty.setText("1")
    w2._confirm_cb.setChecked(False)   # Commit 34：跳過二次確認對話框（offscreen 會 block）
    w2._on_place_order("BUY")
    assert fake2.order_calls[0][0] == "SG.D05"


def test_big_buy_sell_buttons_style_and_pin(monkeypatch):
    """Commit 33：買賣大按鍵（≥64px、買紅 #F23645 / 賣綠 #089981）+ 跟隨 PIN 鎖狀態。"""
    from ui import order_window as ow

    w, _ = _make_window(monkeypatch)
    assert w._buy_btn.minimumHeight() >= ow._BIG_BTN_MIN_HEIGHT
    assert "F23645" in w._buy_btn.styleSheet(), "買入按鍵必須紅色"
    assert "089981" in w._sell_btn.styleSheet(), "賣出按鍵必須綠色"

    # 默認 SIMULATE → 常解鎖、兩按鍵啟用
    assert w._buy_btn.isEnabled() is True and w._sell_btn.isEnabled() is True

    # REAL + LOCKED → 禁用；PIN 解鎖後恢復
    w._mode_real_btn.setChecked(True)
    assert w._buy_btn.isEnabled() is False and w._sell_btn.isEnabled() is False
    _unlock(w)
    assert w._buy_btn.isEnabled() is True and w._sell_btn.isEnabled() is True


# ------------------------------------------------------------- Commit 33：模式選擇 / 帳戶匹配 / live label

def test_mode_selector_toggles_pin_visibility(monkeypatch):
    """Commit 33：模式選擇器——SIMULATE 隱藏 PIN 區、REAL 顯示；_mode 字串同步。"""
    w, _ = _make_window(monkeypatch)
    assert w._mode == "SIMULATE" and w._pin_box.isHidden() is True

    w._mode_real_btn.setChecked(True)
    assert w._mode == "REAL" and w._pin_box.isHidden() is False and w._sim_hint.isHidden() is True

    w._mode_sim_btn.setChecked(True)
    assert w._mode == "SIMULATE" and w._pin_box.isHidden() is True and w._sim_hint.isHidden() is False


def test_is_equity_symbol_heuristic():
    """Commit 33：股票 vs 期貨/期權 heuristic——suffix 'main' = 期貨主連、長代碼 = 期權。"""
    from ui.order_window import _is_equity_symbol
    assert _is_equity_symbol("HK.00700") is True
    assert _is_equity_symbol("US.AAPL") is True
    assert _is_equity_symbol("SG.D05") is True
    assert _is_equity_symbol("HK.HSImain") is False      # 期貨主連
    assert _is_equity_symbol("SG.CNmain") is False
    assert _is_equity_symbol("US.AAPL251219C00200000") is False   # 期權（長代碼）
    assert _is_equity_symbol("NOPE") is False            # 無市場前綴 → 唔係股票


def test_match_order_account_prefers_cash_for_equity():
    """Commit 33：股票優選 CASH 帳戶；期貨/期權優選 MARGIN / STOCK_AND_OPTION。"""
    from ui.order_window import _match_order_account
    cash = _acc(1, env="SIMULATE", acc_type="CASH")
    margin = _acc(2, env="SIMULATE", acc_type="MARGIN")

    assert _match_order_account((cash, margin), "HK.00700", "SIMULATE").acc_id == 1
    assert _match_order_account((cash, margin), "HK.HSImain", "SIMULATE").acc_id == 2


def test_match_order_account_filters():
    """Commit 33：env 唔符 / 非 ACTIVE / MASTER / 市場唔喺授權——全部過濾。"""
    from ui.order_window import _match_order_account
    accounts = (
        _acc(1, env="REAL", acc_type="CASH"),                    # env 唔符（mode=SIMULATE）
        _acc(2, env="SIMULATE", acc_status="DISABLED"),          # 非 ACTIVE
        _acc(3, env="SIMULATE", role="MASTER"),                  # MASTER 主帳戶
        _acc(4, env="SIMULATE", auth=("US",)),                   # 市場 HK 唔喺授權
    )
    assert _match_order_account(accounts, "HK.00700", "SIMULATE") is None

    ok = _acc(5, env="SIMULATE", acc_type="CASH")
    assert _match_order_account((ok,) + accounts, "HK.00700", "SIMULATE").acc_id == 5


def test_total_label_qty_times_price(monkeypatch):
    """Commit 33：合計金額 label = 數量 × 價格 live 更新（任一欄空/0 → —）。"""
    w, _ = _make_window(monkeypatch)
    assert w._total_label.text() == "合計 —"

    w._order_qty.setText("200")          # price 仍 0 → —
    assert w._total_label.text() == "合計 —"

    w._order_price.setValue(55.5)        # 200 × 55.5 = 11,100.00
    assert w._total_label.text() == "合計 11,100.00"


def test_name_label_shows_catalog_names(monkeypatch):
    """Commit 33：代碼輸入後顯示目錄中文名/英文名；未知 code → 空。"""
    from engine.stock_catalog import StockEntry
    w, _ = _make_window(monkeypatch)
    w.set_stock_catalog((StockEntry("HK.00700", "騰訊控股", "Tencent"),))

    w._order_code.setText("HK.00700")
    assert w._name_label.text() == "騰訊控股 Tencent"   # name_text = 中 + 英單空格 join

    w._order_code.setText("US.AAPL")                    # 目錄未收錄 → 空
    assert w._name_label.text() == ""


def test_matched_account_info_label(monkeypatch):
    """Commit 33：匹配帳戶 info label——env · 類型 · 卡號末四位 · 餘額（資金到即同步）。"""
    w, fake = _make_window(monkeypatch)
    # 初始 code = cfg.trading_code（HK.HSImain，非空）但零帳戶 → 「無匹配」
    assert w._acc_info_label.text() == "帳戶 —（無匹配帳戶）"

    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH"),))
    w.set_symbol("HK.00700")
    assert w._acc_info_label.text() == "帳戶 模擬 · CASH · 卡號 …5678 · 餘額 —"

    fake.account_funds_updated.emit(1, "SIMULATE", _funds(total_assets=999_999.0))
    assert w._acc_info_label.text() == "帳戶 模擬 · CASH · 卡號 …5678 · 餘額 999,999.00"


def test_orders_table_account_column(monkeypatch):
    """Commit 33 + Commit 35 R2：訂單表第 11 欄 = env 前綴 + 來源帳戶（卡號末四位）。"""
    w, fake = _make_window(monkeypatch)
    fake.accounts_updated.emit((_acc(1),))   # REAL、card 12345678

    row = OrderRow(order_id="9001", code="HK.00700", side="BUY", order_type="NORMAL",
                   status="FILLED_ALL", qty=200, price=55.5, dealt_qty=200,
                   dealt_avg_price=55.4, create_time="2026-10-02 09:30:00", acc_id=1)
    fake.orders_updated.emit((row,))

    assert w._orders_table.item(0, 10).text() == "實盤 …5678"


def test_orders_table_account_column_simulate_env(monkeypatch):
    """Commit 35 R2：SIMULATE 訂單 → 「模擬」前綴；無卡號帳戶 → env + acc_id fallback。"""
    w, fake = _make_window(monkeypatch)
    sim_acc = _acc(7, env="SIMULATE", card="N/A")   # 模擬帳戶、無卡號
    fake.accounts_updated.emit((sim_acc,))

    row = OrderRow(order_id="9002", code="US.AAPL", side="SELL", order_type="MARKET",
                   status="OPEN", qty=-100, price=0.0, dealt_qty=0,
                   dealt_avg_price=0.0, create_time="2026-10-02 10:00:00", acc_id=7,
                   trd_env="SIMULATE")
    fake.orders_updated.emit((row,))

    assert w._orders_table.item(0, 10).text() == "模擬 7"


def test_set_symbol_refreshes_labels(monkeypatch):
    """Commit 33：set_symbol（K 綫標的切換）→ code + 名稱 label 同步。"""
    from engine.stock_catalog import StockEntry
    w, fake = _make_window(monkeypatch)
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH", auth=("US",)),))
    w.set_stock_catalog((StockEntry("US.AAPL", "Apple Inc.", "Apple"),))

    w.set_symbol("US.AAPL")
    assert w._order_code.text() == "US.AAPL"
    assert w._name_label.text() == "Apple Inc. Apple"


# ------------------------------------------------------------- Commit 34：PIN bar / lot size / 反向同步 / 二次確認 / 撤單平倉

def _drain_queue(w: OrderWindow, fake: FakeTradeEngine) -> None:
    """Fake engine 係同步嘅（唔會自動 emit result）→ 手動 emit order_result N 次 drain action queue。"""
    total = len(w._action_queue) + (1 if w._action_busy else 0)
    for _ in range(total):
        fake.order_result.emit(True, "ok")


def test_pin_bar_and_confirm_checkbox_inside_order_form(monkeypatch):
    """Commit 34：PIN bar（交易模式選擇 + PIN）同二次確認 checkbox 都喺下單 form 內。"""
    w, _ = _make_window(monkeypatch)

    node = w._pin_box
    while node is not None and node.objectName() != "orderGroup":
        node = node.parentWidget()
    assert node is not None, "PIN bar 必須喺下單 form（objectName=orderGroup）內"

    assert w._confirm_cb.isChecked() is True   # 二次確認默認開


def test_reverse_sync_emits_valid_code(monkeypatch):
    """Commit 34：下單代碼變更 → debounce 後 emit `code_changed`（canonical uppercase）。"""
    from engine.stock_catalog import StockEntry

    w, _ = _make_window(monkeypatch)
    w.set_stock_catalog((StockEntry("HK.00700", "騰訊控股", "TENCENT"),))
    emitted: list[str] = []
    w.code_changed.connect(emitted.append)

    w._order_code.setText("hk.00700")   # debounce 600ms——offscreen 無 event loop 唔會自動 fire
    assert emitted == [], "debounce 未到期唔應該 emit"

    w._emit_symbol_if_valid()           # 手動觸發 timeout callback
    assert emitted == ["HK.00700"]      # canonical uppercase

    w._emit_symbol_if_valid()           # _last_emitted_code guard → 唔重複 emit
    assert len(emitted) == 1


def test_reverse_sync_skips_unknown_or_invalid(monkeypatch):
    """Commit 34：目錄已載入但未知 code / 無「.」→ skip（唔切圖表去無效標的）。"""
    from engine.stock_catalog import StockEntry

    w, _ = _make_window(monkeypatch)
    w.set_stock_catalog((StockEntry("HK.00700", "騰訊控股", "TENCENT"),))
    emitted: list[str] = []
    w.code_changed.connect(emitted.append)

    w._order_code.setText("XX.99999")   # 有「.」但唔喺目錄 → skip
    w._emit_symbol_if_valid()
    assert emitted == []

    w._order_code.setText("NOPE")       # 無「.」→ skip
    w._emit_symbol_if_valid()
    assert emitted == []


def test_set_symbol_primes_last_emitted(monkeypatch):
    """Commit 34：set_symbol（K 綫 → 下單正向同步）prime `_last_emitted_code`——防反向 debounce echo loop。"""
    from engine.stock_catalog import StockEntry

    w, _ = _make_window(monkeypatch)
    w.set_stock_catalog((StockEntry("US.AAPL", "Apple Inc.", "Apple"),))
    emitted: list[str] = []
    w.code_changed.connect(emitted.append)

    w.set_symbol("US.AAPL")             # 正向同步——唔自己 emit、只 prime dedup state
    assert emitted == []

    w._emit_symbol_if_valid()           # debounce 其後 fire → 同 code → skip（防 loop）
    assert emitted == []


def test_qty_autofill_from_lot_size(monkeypatch):
    """Commit 34：標的變更 → auto-fill 數量 = 每手單位；手動輸入唔覆蓋；未知 lot 唔填。"""
    from engine.stock_catalog import StockEntry

    w, _ = _make_window(monkeypatch)
    w.set_stock_catalog((StockEntry("HK.00700", "騰訊控股", "TENCENT", lot_size=500),))
    w._order_code.setText("HK.00700")   # _on_code_changed → auto-fill
    assert w._order_qty.text() == "500"

    w._order_qty.setText("1000")        # 用戶手動輸入
    w._auto_fill_qty()                  # 同 code guard → 唔覆蓋
    assert w._order_qty.text() == "1000"

    w2, _ = _make_window(monkeypatch)   # 目錄未載入 → lot 未知 → 唔填
    w2._order_code.setText("US.AAPL")
    assert w2._order_qty.text() == ""


def test_place_order_rejects_non_lot_multiple(monkeypatch):
    """Commit 34：數量唔係每手單位整數倍 → 拒絕下單；整數倍 → dispatch。"""
    from engine.stock_catalog import StockEntry

    w, fake = _make_window(monkeypatch)   # SIMULATE（常解鎖）
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH"),))
    w.set_stock_catalog((StockEntry("HK.00700", "騰訊控股", "TENCENT", lot_size=500),))

    w._order_code.setText("HK.00700")     # auto-fill 500
    w._order_price.setValue(10.0)
    w._order_qty.setText("300")           # 唔係 500 整數倍
    w._confirm_cb.setChecked(False)       # 跳過二次確認對話框（offscreen 會 block）
    w._on_place_order("BUY")

    assert fake.order_calls == []
    assert "整數倍" in w._status_label.text()

    w._order_qty.setText("1000")          # 500 × 2 → OK
    w._on_place_order("BUY")
    assert len(fake.order_calls) == 1


def test_confirm_checkbox_no_cancels_dispatch(monkeypatch):
    """Commit 34：二次確認 checkbox 開 + 彈框揀 No → 唔 dispatch + warn status。"""
    calls: list = []

    def fake_question(*a, **k):
        calls.append(a)
        return QMessageBox.No

    monkeypatch.setattr(ow.QMessageBox, "question", fake_question)

    w, fake = _make_window(monkeypatch)   # SIMULATE（常解鎖）
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH"),))
    w._order_code.setText("HK.00700")
    w._order_price.setValue(55.5)
    w._order_qty.setText("200")
    assert w._confirm_cb.isChecked() is True   # 默認開
    w._on_place_order("BUY")

    assert len(calls) == 1, "應該彈一次二次確認對話框"
    assert fake.order_calls == []
    assert "已取消下單（二次確認）" in w._status_label.text()


def test_confirm_checkbox_yes_dispatches(monkeypatch):
    """Commit 34：二次確認 checkbox 開 + 彈框揀 Yes → dispatch。"""
    monkeypatch.setattr(ow.QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)

    w, fake = _make_window(monkeypatch)   # SIMULATE（常解鎖）
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH"),))
    w._order_code.setText("HK.00700")
    w._order_price.setValue(55.5)
    w._order_qty.setText("200")
    w._on_place_order("BUY")

    assert len(fake.order_calls) == 1
    assert fake.order_calls[0][5] == "SIMULATE"


def test_confirm_checkbox_off_dispatches_directly(monkeypatch):
    """Commit 34：checkbox 取消 → 唔彈框直接 dispatch（question 被調用即 fail）。"""
    def boom(*a, **k):
        raise AssertionError("checkbox 關閉時唔應該彈二次確認對話框")

    monkeypatch.setattr(ow.QMessageBox, "question", boom)

    w, fake = _make_window(monkeypatch)   # SIMULATE（常解鎖）
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH"),))
    w._order_code.setText("HK.00700")
    w._order_price.setValue(55.5)
    w._order_qty.setText("200")
    w._confirm_cb.setChecked(False)
    w._on_place_order("BUY")

    assert len(fake.order_calls) == 1


def test_cancel_row_button_enabled_by_status(monkeypatch):
    """Commit 34：訂單表 per-row「撤單」按鈕——pending 啟用、已成/已取消 disabled、無 order_id disabled。"""
    rows = (
        OrderRow("9001", "HK.00700", "BUY", "NORMAL", "SUBMITTED", 200, 55.5, 0, 0.0,
                 "2026-10-02 09:30:00"),
        OrderRow("9002", "US.AAPL", "SELL", "NORMAL", "FILLED_ALL", 10, 140.0, 10, 140.0,
                 "2026-10-02 10:00:05"),
        OrderRow("", "HK.00700", "BUY", "NORMAL", "SUBMITTED", 5, 10.0, 0, 0.0,
                 "2026-10-02 10:01:00"),   # 無 order_id → 無法撤
    )
    w, fake = _make_window(monkeypatch)
    fake.orders_updated.emit(rows)

    b0 = w._orders_table.cellWidget(0, 11)
    assert isinstance(b0, QPushButton) and b0.isEnabled() is True, "SUBMITTED → 撤單可用"
    b1 = w._orders_table.cellWidget(1, 11)
    assert isinstance(b1, QPushButton) and b1.isEnabled() is False, "FILLED_ALL → 撤單禁用"
    b2 = w._orders_table.cellWidget(2, 11)
    assert isinstance(b2, QPushButton) and b2.isEnabled() is False, "無 order_id → 撤單禁用"


def test_cancel_row_dispatches_with_real_env(monkeypatch):
    """Commit 34：per-row「撤單」Yes → engine.cancel_order（trd_env=REAL、acc_id 跟行）。"""
    row = OrderRow("9001", "HK.00700", "BUY", "NORMAL", "SUBMITTED", 200, 55.5, 0, 0.0,
                   "2026-10-02 09:30:00", acc_id=1)
    w, fake = _make_window(monkeypatch)
    fake.orders_updated.emit((row,))

    monkeypatch.setattr(ow.QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    w._on_cancel_row(w._displayed_orders[0])

    assert fake.cancel_calls == [("9001", "HK.00700", "REAL", 1)]
    _drain_queue(w, fake)
    assert w._action_busy is False and w._action_queue == []


def test_cancel_row_no_cancels(monkeypatch):
    """Commit 34：per-row「撤單」No → 唔 dispatch + warn status。"""
    row = OrderRow("9001", "HK.00700", "BUY", "NORMAL", "SUBMITTED", 200, 55.5, 0, 0.0,
                   "2026-10-02 09:30:00")
    w, fake = _make_window(monkeypatch)
    fake.orders_updated.emit((row,))

    monkeypatch.setattr(ow.QMessageBox, "question", lambda *a, **k: QMessageBox.No)
    w._on_cancel_row(w._displayed_orders[0])

    assert fake.cancel_calls == []
    assert "已取消撤單（二次確認）" in w._status_label.text()


def test_cancel_all_serialized(monkeypatch):
    """Commit 34：「全部撤單」→ 逐筆 enqueue 串行（首筆即發、其餘排隊等 result）。"""
    rows = tuple(
        OrderRow(str(9001 + i), "HK.00700", "BUY", "NORMAL", "SUBMITTED", 10, 55.0, 0, 0.0,
                 f"2026-10-02 09:3{i}:00")
        for i in range(3)
    )
    w, fake = _make_window(monkeypatch)
    fake.orders_updated.emit(rows)

    monkeypatch.setattr(ow.QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    w._on_cancel_all()

    assert len(fake.cancel_calls) == 1, "首筆即發"
    assert len(w._action_queue) == 2 and w._action_busy is True, "其餘兩筆排隊"

    _drain_queue(w, fake)
    assert len(fake.cancel_calls) == 3
    assert w._action_busy is False and w._action_queue == []


def test_close_row_long_sells_market(monkeypatch):
    """Commit 34：per-row「平倉」長倉 → 市價 SELL（同帳戶/環境、market=True）。"""
    row = PositionRow("HK.00700", "騰訊控股", "HK", 100, 50, 300.0, 320.0, 32000.0, 2000.0,
                      6.67, 150.0, acc_id=7, trd_env="SIMULATE")
    w, fake = _make_window(monkeypatch)   # SIMULATE mode（常解鎖）
    fake.positions_updated.emit((row,))

    monkeypatch.setattr(ow.QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    w._on_close_row(w._displayed_positions[0])

    assert fake.order_calls == [("HK.00700", TrdSide.SELL, 0.0, 100, None, "SIMULATE", 7, True)]
    _drain_queue(w, fake)


def test_close_row_short_buys_back(monkeypatch):
    """Commit 34：per-row「平倉」短倉（qty<0）→ 市價 BUY_BACK、數量取 abs。"""
    row = PositionRow("US.AAPL", "Apple", "US", -50, -50, 150.0, 140.0, -7000.0, 500.0,
                      3.33, 20.0, acc_id=8, trd_env="SIMULATE")
    w, fake = _make_window(monkeypatch)   # SIMULATE mode（常解鎖）
    fake.positions_updated.emit((row,))

    monkeypatch.setattr(ow.QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    w._on_close_row(w._displayed_positions[0])

    assert fake.order_calls == [("US.AAPL", TrdSide.BUY_BACK, 0.0, 50, None, "SIMULATE", 8, True)]
    _drain_queue(w, fake)


def test_close_real_position_requires_pin(monkeypatch):
    """Commit 34：實盤持倉平倉 → PIN gate 喺 confirm dialog **之前**（未解鎖唔彈框）。"""
    row = PositionRow("HK.00700", "騰訊控股", "HK", 100, 50, 300.0, 320.0, 32000.0, 2000.0,
                      6.67, 150.0, acc_id=9)   # trd_env 默認 REAL

    def boom(*a, **k):
        raise AssertionError("未解鎖唔應該彈確認框")

    monkeypatch.setattr(ow.QMessageBox, "question", boom)

    w, fake = _make_window(monkeypatch)   # SIMULATE mode、無 PIN holder
    fake.positions_updated.emit((row,))
    w._on_close_row(w._displayed_positions[0])

    assert fake.order_calls == []
    assert "實盤未解鎖" in w._status_label.text()


def test_close_all_dispatches_per_position(monkeypatch):
    """Commit 34：「全部平倉」→ 逐筆 enqueue（長倉 SELL / 短倉 BUY_BACK、全部市價單）。"""
    rows = (
        PositionRow("HK.00700", "騰訊控股", "HK", 100, 50, 300.0, 320.0, 32000.0, 2000.0,
                    6.67, 150.0, acc_id=7, trd_env="SIMULATE"),
        PositionRow("US.AAPL", "Apple", "US", -50, -50, 150.0, 140.0, -7000.0, 500.0,
                    3.33, 20.0, acc_id=8, trd_env="SIMULATE"),
    )
    w, fake = _make_window(monkeypatch)   # SIMULATE mode（常解鎖）
    fake.positions_updated.emit(rows)

    monkeypatch.setattr(ow.QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    w._on_close_all()

    assert len(fake.order_calls) == 1 and len(w._action_queue) == 1, "首筆即發、其餘排隊"

    _drain_queue(w, fake)
    assert len(fake.order_calls) == 2
    sides = {c[1] for c in fake.order_calls}
    assert sides == {TrdSide.SELL, TrdSide.BUY_BACK}
    assert all(c[7] is True for c in fake.order_calls), "全部市價單"


def test_status_label_prominent_style(monkeypatch):
    """Commit 34：交易成功/錯誤 status label 當眼明顯（深色底 + 粗體大字）。"""
    w, fake = _make_window(monkeypatch)

    fake.order_result.emit(True, "ok")
    ss_ok = w._status_label.styleSheet()
    assert "#0B3D2E" in ss_ok and "font-weight: bold" in ss_ok, "成功 → 深綠底粗體"

    fake.order_result.emit(False, "err")
    ss_err = w._status_label.styleSheet()
    assert "#4A1420" in ss_err and "font-weight: bold" in ss_err, "失敗 → 深紅底粗體"


def test_action_queue_keeps_buttons_disabled_until_drained(monkeypatch):
    """Commit 34：action queue 未 drain 完 → 買賣按鍵保持 disabled（防並發下單）。"""
    w, fake = _make_window(monkeypatch)   # SIMULATE（常解鎖）
    fake.accounts_updated.emit((_acc(1, env="SIMULATE", acc_type="CASH"),))

    w._order_code.setText("HK.00700")
    w._order_price.setValue(55.5)
    w._order_qty.setText("200")
    w._confirm_cb.setChecked(False)       # 跳過二次確認對話框（offscreen 會 block）
    w._on_place_order("BUY")              # action 1 in-flight → 禁用
    assert w._buy_btn.isEnabled() is False and w._sell_btn.isEnabled() is False

    w._enqueue_action(lambda: None)       # action 2 排隊
    fake.order_result.emit(True, "ok")    # done 1 → pump 2（仍 busy）
    assert w._buy_btn.isEnabled() is False and w._sell_btn.isEnabled() is False

    fake.order_result.emit(True, "ok")    # done 2 → queue 空 → _apply_pin_state 恢復
    assert w._buy_btn.isEnabled() is True and w._sell_btn.isEnabled() is True


# ---------------------------------------------------------------- Commit 35：下單頁實戰升級

def test_mode_buttons_top_bar_exclusive_switch(monkeypatch):
    """Commit 35 R3：實盤/模擬盤按喺下單頁頂部（全局切換、互斥）；form 內 mode selector 已移除。"""
    w, _ = _make_window(monkeypatch)
    assert w._mode_sim_btn.isChecked() is True and w._mode == "SIMULATE"   # 默認模擬盤
    w._mode_real_btn.click()
    assert w._mode == "REAL"
    assert w._mode_real_btn.isChecked() is True and not w._mode_sim_btn.isChecked(), "互斥組"
    w._mode_sim_btn.click()
    assert w._mode == "SIMULATE"


def test_env_funds_mini_panels_both_envs(monkeypatch):
    """Commit 35 R4：實盤/模擬資金明細移去右上角（per-env 9 欄 label 組）。"""
    w, fake = _make_window(monkeypatch)
    assert set(w._env_funds_labels) == {"REAL", "SIMULATE"}
    for env in ("REAL", "SIMULATE"):
        fields = w._env_funds_labels[env]
        assert len(fields) == 9
        assert all(isinstance(l, QLabel) and l.text() == "—" for l in fields.values())
    # per-account 資金事件 → 對應 env mini panel 更新（total_assets 欄）
    fake.account_funds_updated.emit(1, "SIMULATE", _funds(total_assets=88_000.0))
    assert w._env_funds_labels["SIMULATE"]["total_assets"].text() != "—"


def test_price_spinbox_two_decimals(monkeypatch):
    """Commit 35 R5：交易價格固定小數後兩位（如 3.33）。"""
    w, _ = _make_window(monkeypatch)
    assert w._order_price.decimals() == 2


def test_set_symbol_forces_follow_mode_and_resets_price(monkeypatch):
    """Commit 35 R1：標的改變 → 強制返跟隨現價模式（即使用戶已切手動輸入）+ 價格重置等新市價。"""
    w, _ = _make_window(monkeypatch)
    w._follow_btn.setChecked(False)   # 先切去手動輸入
    assert w._following is False
    w.set_symbol("HK.00700")
    assert w._following is True, "強制返跟隨模式"
    assert w._order_price.value() == 0.0, "重置（新標的市價會喺下一個 tick 填入）"


def test_set_symbol_then_tick_fills_current_price(monkeypatch):
    """Commit 35 R1：標的改變後，新市價 tick → 訂單價格 = 現價（兩位小數顯示）。"""
    w, _ = _make_window(monkeypatch)
    w.set_symbol("HK.00700")
    w.follow_price(3.3349)
    assert w._order_price.value() == pytest.approx(3.33), "兩位小數（如 3.33）"


def test_endpoint_settings_defaults_from_cfg(monkeypatch):
    """Commit 35 R8：OpenD 連線設定面板——報價/交易各自 IP+PORT（默認 127.0.0.1/11111）。"""
    w, _ = _make_window(monkeypatch)
    assert w._quote_host_edit.text() == "127.0.0.1" and w._quote_port_spin.value() == 11111
    assert w._trade_host_edit.text() == "127.0.0.1" and w._trade_port_spin.value() == 11111


def test_save_endpoints_writes_env_and_emits_payload(monkeypatch, tmp_path):
    """Commit 35 R8：儲存並重連 → 寫四個端點變數去 .env + emit endpoints_changed（int port）。"""
    w, _ = _make_window(monkeypatch)
    written: dict = {}

    def fake_save(updates, env_path=None):
        written.update(updates)
        return tmp_path / ".env"

    monkeypatch.setattr(ow, "save_env_values", fake_save)
    payloads = []
    w.endpoints_changed.connect(payloads.append)

    w._quote_host_edit.setText("10.0.0.5")
    w._quote_port_spin.setValue(22222)
    w._trade_host_edit.setText("10.0.0.6")
    w._trade_port_spin.setValue(33333)
    w._on_save_endpoints_clicked()

    assert written == {"FUTU_QUOTE_HOST": "10.0.0.5", "FUTU_QUOTE_PORT": "22222",
                       "FUTU_TRADE_HOST": "10.0.0.6", "FUTU_TRADE_PORT": "33333"}
    assert payloads == [{"quote": ("10.0.0.5", 22222), "trade": ("10.0.0.6", 33333)}]


def test_save_endpoints_empty_host_falls_back_to_loopback(monkeypatch, tmp_path):
    """Commit 35 R8：空 host → fallback 127.0.0.1（唔寫空值）。"""
    w, _ = _make_window(monkeypatch)
    written: dict = {}

    def fake_save(updates, env_path=None):
        written.update(updates)
        return tmp_path / ".env"

    monkeypatch.setattr(ow, "save_env_values", fake_save)
    w._quote_host_edit.setText("   ")
    w._on_save_endpoints_clicked()
    assert written["FUTU_QUOTE_HOST"] == "127.0.0.1"


def test_conn_test_button_worker_updates_status_label(monkeypatch):
    """Commit 35 R8：連線測試按鍵 → _ConnTester worker thread（阻塞調用唔喺 GUI thread）；
    result auto-queue 返去更新狀態 label。"""
    w, _ = _make_window(monkeypatch)
    calls = []

    def fake_test_endpoint(kind, host, port):
        calls.append((kind, host, port))
        return True, "10.9.9.9:22222 連線成功"

    monkeypatch.setattr(ow.connection_test, "test_endpoint", fake_test_endpoint)

    w._quote_host_edit.setText("10.9.9.9")
    w._quote_port_spin.setValue(22222)
    w._start_conn_test("quote")

    # worker thread → auto-queue signal；等 drain（offscreen：pump events 至 label 更新或 timeout）
    from PySide6.QtCore import QEventLoop
    loop = QEventLoop()
    timer = QTimer()
    timer.timeout.connect(lambda: loop.quit() if "報價端點" in w._conn_status_label.text() else None)
    timer.start(10)
    QTimer.singleShot(3000, loop.quit)   # timeout guard（防 hang）
    loop.exec()
    timer.stop()

    assert calls == [("quote", "10.9.9.9", 22222)]
    assert w._conn_status_label.text().startswith("報價端點") and "連線成功" in w._conn_status_label.text()


def test_order_form_row_spacing(monkeypatch):
    """Commit 35 R7：下單 FORM 合理隔行（10px）。"""
    w, _ = _make_window(monkeypatch)
    group = next(g for g in w.findChildren(QGroupBox) if g.objectName() == "orderGroup")
    assert group.layout().spacing() == 10
