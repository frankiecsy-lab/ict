"""下單版面視窗：實倉資金/持倉/今日訂單顯示 + 全帳戶分類 + 限價買賣下單 + 六位數 PIN 交易解鎖。

PIN 安全設計（用戶要求：6 位臨時密碼絕不明文顯示）:
- input = QLineEdit EchoMode.Password + [0-9]{0,6} validator → UI 永遠圓點；
- holder = _PinHolder（__repr__/__str__ = "***"）→ log/debug 洩唔到明文；
- 只存記憶體、不寫磁碟/.env；解鎖後 24h（unlock_ttl_seconds，clock 可注入方便測試）有效；
- 鎖定按鍵立即清空 holder + 禁用下單表單；expiry tick 自動做同樣嘅事。

Threading：TradeEngine 係 child QObject；所有 RPC 喺 engine worker thread，
本視窗只收 auto-queue signals（immutable snapshot）→ GUI thread 零阻塞。
"""
from __future__ import annotations

import time

from PySide6.QtCore import QRegularExpression, QTimer
from PySide6.QtGui import (QColor, QDoubleValidator, QIntValidator,
                           QRegularExpressionValidator)
from PySide6.QtWidgets import (QComboBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
                               QAbstractItemView)

from config import Config
from engine.trade_engine import (AccountInfo, FundsSnapshot, OrderRow, PositionRow,
                                 TradeEngine)
from futu import TrdSide

# 狀態色（跟 MainWindow 深色主題語義）
_OK_COLOR = "#089981"
_ERR_COLOR = "#F23645"
_WARN_COLOR = "#FFB020"

# OrderStatus → 繁體中文（唔喺表內 fallback 原文）
_ORDER_STATUS_ZH = {
    "UNSUBMITTED": "待提交",
    "WAITING_SUBMIT": "等待提交",
    "SUBMITTING": "提交中",
    "SUBMIT_FAILED": "提交失敗",
    "TIMEOUT": "超時",
    "SUBMITTED": "已提交",
    "FILLED_PART": "部分成交",
    "FILLED_ALL": "全部已成",
    "CANCELLING_PART": "撤單中(部)",
    "CANCELLING_ALL": "撤單中(全)",
    "CANCELLED_PART": "部分撤單",
    "CANCELLED_ALL": "全部撤單",
    "FAILED": "下單失敗",
    "DISABLED": "已失效",
    "DELETED": "已刪除",
    "FILL_CANCELLED": "成交後撤單",
}

# 訂單狀態格上色：已成=綠 / 失敗・撤單・失效=紅 / pending=黃（其餘 fallback 無色）
_STATUS_GREEN = {"FILLED_ALL"}
_STATUS_RED = {"FAILED", "SUBMIT_FAILED", "CANCELLED_PART", "CANCELLED_ALL",
               "DISABLED", "DELETED", "TIMEOUT"}
_STATUS_YELLOW = {"UNSUBMITTED", "WAITING_SUBMIT", "SUBMITTING", "SUBMITTED",
                  "FILLED_PART", "CANCELLING_PART", "CANCELLING_ALL", "FILL_CANCELLED"}

# TrdSide → 中文
_SIDE_ZH = {"BUY": "買入", "SELL": "賣出", "SELL_SHORT": "沽空", "BUY_BACK": "回補"}

# risk_status → 中文（LEVEL3=安全 / LEVEL2=警告 / LEVEL1=危險）
_RISK_STATUS_ZH = {"LEVEL3": "安全", "LEVEL2": "警告", "LEVEL1": "危險"}


def _order_status_zh(status: str) -> str:
    """OrderStatus 值 → 繁體中文；唔喺表內 fallback 原文（空 → '—'）。"""
    return _ORDER_STATUS_ZH.get(status, status or "—")


class _PinHolder:
    """臨時 PIN holder：只存記憶體；repr/str 一律 redacted——防 log/debug 洩明文。"""

    __slots__ = ("value", "deadline")

    def __init__(self, value: str, deadline: float) -> None:
        self.value = value
        self.deadline = deadline

    def __repr__(self) -> str:   # noqa: D105 — 安全：絕不明文
        return "***"

    def __str__(self) -> str:    # noqa: D105 — 安全：絕不明文
        return "***"


def _fmt_money(v: float) -> str:
    """金額顯示：千分位 + 2 小數。"""
    return f"{v:,.2f}"


class OrderWindow(QMainWindow):
    """下單版面（獨立 top-level 視窗，可拖去第二螢幕）。

    佈局：PIN bar → [帳戶分類樹 | 資金/訂金] → 持倉 table → 今日訂單 table → 下單 group → status label。
    LOCKED（默認）：下單表單全 disabled；UNLOCKED：啟用 + countdown 顯示剩餘時間。
    """

    def __init__(self, cfg: Config, *, clock=time.time, unlock_ttl_seconds: float = 24 * 3600) -> None:
        super().__init__()
        self._cfg = cfg
        self._clock = clock
        self._unlock_ttl = unlock_ttl_seconds
        self.setWindowTitle("ICT Trader — 下單版面")
        self.resize(1000, 820)

        # 深色主題（跟 MainWindow 配色）
        self.setStyleSheet(
            f"QMainWindow {{ background: {cfg.bg_color}; }}"
            f"QWidget {{ color: {cfg.text_color}; font-family: Consolas; }}"
            f"QGroupBox {{ border: 1px solid {cfg.grid_color}; margin-top: 8px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; color: {cfg.axis_text_color}; }}"
            f"QLineEdit, QComboBox {{ background: #1A212B; border: 1px solid {cfg.grid_color}; "
            f"color: {cfg.text_color}; padding: 3px 6px; }}"
            f"QPushButton {{ background: #1E2836; border: 1px solid {cfg.grid_color}; "
            f"color: {cfg.text_color}; padding: 4px 14px; }}"
            f"QPushButton:hover {{ background: #27354A; }}"
            f"QPushButton:disabled {{ color: #4A5568; background: #151B23; }}"
            f"QTableWidget, QTreeWidget {{ background: {cfg.bg_color}; gridline-color: {cfg.grid_color}; border: none; }}"
            f"QHeaderView::section {{ background: #1A212B; color: {cfg.axis_text_color}; "
            f"border: none; padding: 3px; }}"
        )

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(self._build_pin_bar())
        top_row = QHBoxLayout()
        top_row.addWidget(self._build_accounts_tree())
        top_row.addWidget(self._build_funds_group(), 1)
        root.addLayout(top_row)
        root.addWidget(self._build_positions_table(), 1)   # stretch：持倉表佔剩餘空間
        root.addWidget(self._build_orders_group())
        root.addWidget(self._build_order_group())
        self._status_label = QLabel("等待連線…")
        self._status_label.setStyleSheet(f"color: {cfg.axis_text_color};")
        root.addWidget(self._status_label)
        self.setCentralWidget(central)

        # Engine（child QObject → 同 window 一齊收）；signals auto-queue 去 GUI。
        self._engine = TradeEngine(self)
        self._engine.accounts_updated.connect(self._on_accounts)
        self._engine.positions_updated.connect(self._on_positions)
        self._engine.funds_updated.connect(self._on_funds)
        self._engine.orders_updated.connect(self._on_orders)
        self._engine.status.connect(lambda m: self._set_status(m, cfg.axis_text_color))
        self._engine.error.connect(lambda m: self._set_status(m, _ERR_COLOR))
        self._engine.order_result.connect(self._on_order_result)

        # PIN 狀態：None = LOCKED（默認）；QTimer countdown tick。
        self._pin_holder: _PinHolder | None = None
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._on_tick)

        self._apply_pin_state()   # 初始 LOCKED：下單表單 disabled
        self._engine.start(cfg)

    # ------------------------------------------------------------- widget builders

    def _build_pin_bar(self) -> QWidget:
        """PIN bar：標題 + masked PIN input + 解鎖/鎖定按鍵 + countdown label。"""
        bar = QWidget()
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        title = QLabel("交易解鎖")
        title.setStyleSheet(f"font-weight: bold; color: {self._cfg.text_color};")
        self._pin_edit = QLineEdit()
        self._pin_edit.setEchoMode(QLineEdit.EchoMode.Password)   # 永遠圓點，無明文
        self._pin_edit.setPlaceholderText("六位數 PIN")
        self._pin_edit.setMaxLength(6)
        self._pin_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9]{0,6}")))
        self._pin_edit.setFixedWidth(140)
        self._unlock_btn = QPushButton("解鎖")
        self._lock_btn = QPushButton("鎖定")
        self._countdown_label = QLabel("")
        self._countdown_label.setStyleSheet(f"color: {_WARN_COLOR};")
        h.addWidget(title)
        h.addWidget(self._pin_edit)
        h.addWidget(self._unlock_btn)
        h.addWidget(self._lock_btn)
        h.addStretch(1)
        h.addWidget(self._countdown_label)
        self._unlock_btn.clicked.connect(self._on_unlock_clicked)
        self._lock_btn.clicked.connect(self._on_lock_clicked)
        return bar

    def _build_accounts_tree(self) -> QTreeWidget:
        """帳戶分類樹：頂層 = REAL/SIMULATE 環境，子項 = 個別帳戶（類型/角色/卡號/市場）。"""
        self._acc_tree = QTreeWidget()
        self._acc_tree.setHeaderHidden(True)
        self._acc_tree.setFixedWidth(340)
        return self._acc_tree

    def _build_funds_group(self) -> QGroupBox:
        """資金/訂金 group：9 個 label（總資產/現金 HKD/USD/可提 HKD/USD/購買力/初始保證金/維持保證金/風控狀態）。"""
        box = QGroupBox("資金 / 訂金")
        grid = QVBoxLayout(box)
        self._funds_labels: dict[str, QLabel] = {}
        rows = [
            ("total_assets", "總資產"), ("cash_hkd", "現金 HKD"),
            ("cash_usd", "現金 USD"), ("withdraw_hkd", "可提 HKD"),
            ("withdraw_usd", "可提 USD"), ("buying_power", "購買力"),
            ("initial_margin", "初始保證金（訂金）"), ("maintenance_margin", "維持保證金"),
            ("risk_status", "風控狀態"),
        ]
        for key, label_text in rows:
            row = QHBoxLayout()
            name = QLabel(f"{label_text}：")
            name.setStyleSheet("color: #7A8699;")
            value = QLabel("—")
            value.setStyleSheet(f"font-weight: bold; color: {self._cfg.text_color};")
            self._funds_labels[key] = value
            row.addWidget(name)
            row.addStretch(1)
            row.addWidget(value)
            grid.addLayout(row)
        return box

    def _build_positions_table(self) -> QTableWidget:
        """持倉 table：11 欄（代碼/名稱/市場/數量/可用/平均成本/市價/市值/未實現盈虧/今日盈虧/盈虧%）。"""
        self._pos_table = QTableWidget(0, 11)
        self._pos_table.setHorizontalHeaderLabels(
            ["代碼", "名稱", "市場", "數量", "可用", "平均成本", "市價", "市值",
             "未實現盈虧", "今日盈虧", "盈虧%"])
        self._pos_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._pos_table.verticalHeader().setVisible(False)
        self._pos_table.horizontalHeader().setStretchLastSection(True)
        return self._pos_table

    def _build_orders_group(self) -> QGroupBox:
        """今日訂單 group：fixed-height table（9 欄）。"""
        box = QGroupBox("今日訂單")
        v = QVBoxLayout(box)
        self._orders_table = QTableWidget(0, 9)
        self._orders_table.setHorizontalHeaderLabels(
            ["時間", "代碼", "方向", "類型", "狀態", "數量", "價格", "已成交", "成交均價"])
        self._orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._orders_table.verticalHeader().setVisible(False)
        self._orders_table.horizontalHeader().setStretchLastSection(True)
        self._orders_table.setFixedHeight(150)
        v.addWidget(self._orders_table)
        return box

    def _build_order_group(self) -> QGroupBox:
        """下單 group：code / side combo / price / qty / 下單按鍵。"""
        box = QGroupBox("限價下單")
        h = QHBoxLayout(box)
        cfg = self._cfg
        code_label = QLabel("代碼")
        self._order_code = QLineEdit(cfg.trading_code)
        self._side_combo = QComboBox()
        self._side_combo.addItems(["買入", "賣出"])
        price_label = QLabel("價格")
        self._order_price = QLineEdit()
        self._order_price.setValidator(QDoubleValidator(0.0, 1e12, 4))
        self._order_price.setPlaceholderText("限價")
        qty_label = QLabel("數量")
        self._order_qty = QLineEdit()
        self._order_qty.setValidator(QIntValidator(1, 10**9))
        self._order_qty.setPlaceholderText("股數")
        self._place_btn = QPushButton("下單")
        h.addWidget(code_label)
        h.addWidget(self._order_code, 2)
        h.addWidget(self._side_combo)
        h.addWidget(price_label)
        h.addWidget(self._order_price)
        h.addWidget(qty_label)
        h.addWidget(self._order_qty)
        h.addWidget(self._place_btn)
        self._place_btn.clicked.connect(self._on_place_order)
        return box

    # ------------------------------------------------------------- PIN 狀態機

    def _apply_pin_state(self) -> None:
        """按當前 _pin_holder 狀態同步 UI enable/disable（LOCKED = holder is None）。"""
        unlocked = self._pin_holder is not None
        self._pin_edit.setEnabled(not unlocked)
        self._unlock_btn.setEnabled(not unlocked)
        self._lock_btn.setEnabled(unlocked)
        for w in (self._order_code, self._side_combo, self._order_price, self._order_qty):
            w.setEnabled(unlocked)
        # 下單按鍵跟隨鎖狀態（in-flight guard 由 _on_place_order/_on_order_result 短暫覆蓋）
        self._place_btn.setEnabled(unlocked)

    def _on_unlock_clicked(self) -> None:
        """解鎖：恰好 6 位數字 → 建 holder（24h deadline）+ 清空欄位 + 啟用交易。"""
        pin = self._pin_edit.text()
        if len(pin) != 6 or not pin.isdigit():
            self._set_status("PIN 必須係 6 位數字", _ERR_COLOR)
            return
        self._pin_holder = _PinHolder(pin, self._clock() + self._unlock_ttl)
        self._pin_edit.clear()   # 欄位即刻清空——臨時密碼唔留喺 UI
        self._apply_pin_state()
        self._countdown_timer.start()
        self._update_countdown_label()
        self._set_status("已解鎖——24 小時內可用臨時密碼交易", _OK_COLOR)

    def _on_lock_clicked(self) -> None:
        """鎖定：立即清空 holder + 禁用下單（下次要重新輸入 PIN）。"""
        self._pin_holder = None
        self._countdown_timer.stop()
        self._countdown_label.setText("")
        self._apply_pin_state()
        self._set_status("已鎖定——臨時密碼已清空", _WARN_COLOR)

    def _on_tick(self) -> None:
        """Countdown tick：expiry → 自動鎖定（同手動鎖定完全一樣嘅路徑）。"""
        holder = self._pin_holder
        if holder is None:
            return
        if self._clock() >= holder.deadline:
            self._on_lock_clicked()
            self._set_status("解鎖已過期——請重新輸入 PIN", _WARN_COLOR)
            return
        self._update_countdown_label()

    def _update_countdown_label(self) -> None:
        """Countdown label：剩餘時間 HH:MM:SS。"""
        holder = self._pin_holder
        if holder is None:
            self._countdown_label.setText("")
            return
        remain = max(0, int(holder.deadline - self._clock()))
        h, rem = divmod(remain, 3600)
        m, s = divmod(rem, 60)
        self._countdown_label.setText(f"剩餘 {h:02d}:{m:02d}:{s:02d}")

    # ------------------------------------------------------------- engine signal handlers（GUI thread）

    def _on_accounts(self, accounts: tuple[AccountInfo, ...]) -> None:
        """帳戶分類 snapshot → 樹重繪（按環境分組：實盤 REAL / 模擬 SIMULATE）。"""
        tree = self._acc_tree
        tree.clear()
        real = [a for a in accounts if a.trd_env == "REAL"]
        sim = [a for a in accounts if a.trd_env != "REAL"]
        for title, group in (("實盤 REAL", real), ("模擬 SIMULATE", sim)):
            top = QTreeWidgetItem([f"{title}（{len(group)}）"])
            tree.addTopLevelItem(top)
            for a in sorted(group, key=lambda x: x.acc_id):
                tags = []
                if a.sim_acc_type == "COMPETITION":
                    tags.append("比賽")
                if a.acc_role == "MASTER":
                    tags.append("主帳戶")
                tag_text = f"（{'、'.join(tags)}）" if tags else ""
                item = QTreeWidgetItem([f"{a.acc_id} · {a.acc_type or '—'}{tag_text}"])
                card = a.uni_card_num or a.card_num
                detail = (f"卡號：…{card[-4:]}（末四位）\n市場：{'/'.join(a.trdmarket_auth) or '—'}\n"
                          f"券商：{a.security_firm or '—'}\n狀態：{a.acc_status or '—'}")
                item.setToolTip(0, detail)
                top.addChild(item)
            top.setExpanded(True)

    def _on_positions(self, rows: tuple[PositionRow, ...]) -> None:
        """持倉 snapshot → table 重繪（字段同富途 APP 對齊）。"""
        table = self._pos_table
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [
                row.code, row.name, row.market,
                f"{row.qty:g}", f"{row.can_sell_qty:g}",
                _fmt_money(row.avg_cost), _fmt_money(row.last_price),
                _fmt_money(row.market_value), _fmt_money(row.unrealized_pl),
                _fmt_money(row.today_pl),
                f"{row.pl_ratio_pct:+.2f}%",   # 已是百分數數字
            ]
            for c, text in enumerate(values):
                item = QTableWidgetItem(text)
                if c >= 8:   # 未實現盈虧/今日盈虧/盈虧%：正綠負紅（以 unrealized_pl 符號為準）
                    color = _OK_COLOR if row.unrealized_pl >= 0 else _ERR_COLOR
                    item.setForeground(QColor(color))
                table.setItem(r, c, item)

    def _on_funds(self, funds: FundsSnapshot) -> None:
        """資金 snapshot → 8 個金額 label + 風控狀態 label（LEVEL1 紅 / LEVEL2 黃）。"""
        mapping = {
            "total_assets": funds.total_assets,
            "cash_hkd": funds.cash_hkd,
            "cash_usd": funds.cash_usd,
            "withdraw_hkd": funds.withdraw_hkd,
            "withdraw_usd": funds.withdraw_usd,
            "buying_power": funds.buying_power,
            "initial_margin": funds.initial_margin,
            "maintenance_margin": funds.maintenance_margin,
        }
        for key, value in mapping.items():
            self._funds_labels[key].setText(_fmt_money(value))
        risk_label = self._funds_labels["risk_status"]
        risk_label.setText(_RISK_STATUS_ZH.get(funds.risk_status, funds.risk_status or "—"))
        if funds.risk_status == "LEVEL1":
            risk_label.setStyleSheet(f"font-weight: bold; color: {_ERR_COLOR};")
        elif funds.risk_status == "LEVEL2":
            risk_label.setStyleSheet(f"font-weight: bold; color: {_WARN_COLOR};")
        else:
            risk_label.setStyleSheet(f"font-weight: bold; color: {self._cfg.text_color};")

    def _on_orders(self, rows: tuple[OrderRow, ...]) -> None:
        """今日訂單 snapshot → table 重繪（狀態格上色：已成綠 / 失敗・撤單紅 / pending 黃）。"""
        table = self._orders_table
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t = row.create_time
            values = [
                t[-8:] if len(t) >= 8 else (t or "—"),   # HH:MM:SS（SDK 格式 'YYYY-MM-DD HH:MM:SS'）
                row.code, _SIDE_ZH.get(row.side, row.side or "—"),
                row.order_type or "—", _order_status_zh(row.status),
                f"{row.qty:g}", _fmt_money(row.price),
                f"{row.dealt_qty:g}", _fmt_money(row.dealt_avg_price),
            ]
            for c, text in enumerate(values):
                item = QTableWidgetItem(text)
                if c == 4:   # 狀態格上色
                    color = (_OK_COLOR if row.status in _STATUS_GREEN
                             else _ERR_COLOR if row.status in _STATUS_RED
                             else _WARN_COLOR if row.status in _STATUS_YELLOW
                             else None)
                    if color is not None:
                        item.setForeground(QColor(color))
                table.setItem(r, c, item)

    def _on_order_result(self, ok: bool, message: str) -> None:
        """下單結果：status label 更新 + re-enable 下單按鍵（LOCKED 狀態保持 disabled）。"""
        self._set_status(message, _OK_COLOR if ok else _ERR_COLOR)
        if self._pin_holder is not None:
            self._place_btn.setEnabled(True)

    def _set_status(self, message: str, color: str) -> None:
        self._status_label.setText(message)
        self._status_label.setStyleSheet(f"color: {color};")

    # ------------------------------------------------------------- 下單流程（GUI thread）

    def _on_place_order(self) -> None:
        """GUI 驗證 → engine.place_order（worker thread 做阻塞 RPC）。"""
        code = self._order_code.text().strip()
        price_text = self._order_price.text().strip()
        qty_text = self._order_qty.text().strip()
        if not code or "." not in code:
            self._set_status("代碼格式錯誤（例：HK.00700 / US.AAPL）", _ERR_COLOR)
            return
        try:
            price = float(price_text)
            qty = int(qty_text)
        except ValueError:
            self._set_status("價格/數量必須係數字", _ERR_COLOR)
            return
        if price <= 0 or qty <= 0:
            self._set_status("價格與數量必須大於 0", _ERR_COLOR)
            return
        side = TrdSide.BUY if self._side_combo.currentIndex() == 0 else TrdSide.SELL
        pin = self._pin_holder.value if self._pin_holder is not None else None
        self._place_btn.setEnabled(False)   # in-flight guard（order_result 後 re-enable）
        self._engine.place_order(code, side, price, qty, pin=pin)

    # ------------------------------------------------------------- lifecycle

    def shutdown(self) -> None:
        """Clean shutdown：停 countdown timer + engine.stop()（idempotent）。"""
        self._countdown_timer.stop()
        self._engine.stop()
