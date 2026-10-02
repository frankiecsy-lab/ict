"""下單版面視窗：帳戶卡片按環境 tab 分類（只 ACTIVE，撳卡可按該帳戶過濾持倉）+ per-account 資金 + env 加總資金面板
+ 持倉/今日訂單顯示（持倉帶帳戶標記、雙 env 覆蓋）+ 限價買賣下單（代碼模糊自動補全 + 目錄驗證同 K 綫圖、
買入/賣出 = 綠/紅互斥按鍵、價格默認跟隨市價 + icon 切換手動 + stepper）+ 六位數 PIN 交易解鎖。

PIN 安全設計（用戶要求：6 位臨時密碼絕不明文顯示）:
- input = QLineEdit EchoMode.Password + [0-9]{0,6} validator → UI 永遠圓點；
- holder = _PinHolder（__repr__/__str__ = "***"）→ log/debug 洩唔到明文；
- 只存記憶體、不寫磁碟/.env；解鎖後 24h（unlock_ttl_seconds，clock 可注入方便測試）有效；
- 鎖定按鍵立即清空 holder + 禁用下單表單；expiry tick 自動做同樣嘅事。

Threading：TradeEngine 係 child QObject；所有 RPC 喺 engine worker thread，
本視窗只收 auto-queue signals（immutable snapshot）→ GUI thread 零阻塞。
"""
from __future__ import annotations

import math
import time

from PySide6.QtCore import Qt, QRegularExpression, QTimer
from PySide6.QtGui import QColor, QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QDoubleSpinBox, QFrame, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QPushButton, QScrollArea, QTabWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from config import Config
from engine.trade_engine import (AccountInfo, FundsSnapshot, OrderRow, PositionRow,
                                 TradeEngine, _sum_funds)
from futu import TrdSide
from .stock_completer import StockCompleter, code_from_completion

# 狀態色（跟 MainWindow 深色主題語義）
_OK_COLOR = "#089981"
_ERR_COLOR = "#F23645"
_WARN_COLOR = "#FFB020"

# 買入/賣出按鍵（Commit 31）：買=綠 / 賣=紅互斥 checkable——取代舊 QComboBox
_BUY_BTN_STYLE = (
    "QPushButton { background: #0B3D2E; border: 1px solid #089981; color: #69F0AE; font-weight: bold; }"
    "QPushButton:checked { background: #089981; color: #FFFFFF; }"
    "QPushButton:disabled { background: #151B23; border-color: #2A3441; color: #4A5568; }")
_SELL_BTN_STYLE = (
    "QPushButton { background: #4A1420; border: 1px solid #F23645; color: #FF8A80; font-weight: bold; }"
    "QPushButton:checked { background: #F23645; color: #FFFFFF; }"
    "QPushButton:disabled { background: #151B23; border-color: #2A3441; color: #4A5568; }")

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


def _price_step(price: float) -> float:
    """自適應 stepper 步長 = 10^(floor(log10(p))−2)——55.5→0.1、5.5→0.01、555→1.0；clamp [0.001, 10]。"""
    if price <= 0:
        return 0.001
    step = 10 ** (math.floor(math.log10(price)) - 2)
    return max(0.001, min(step, 10.0))


class OrderWindow(QMainWindow):
    """下單版面（獨立 top-level 視窗，可拖去第二螢幕）。

    佈局：PIN bar → main_row[左欄（帳戶卡片 tabs + 持倉/訂單左右並排表）| 右欄全高（資金/訂金 env tabs + 限價下單 form）] → status label。
    LOCKED（默認）：下單表單 disabled（follow 按鍵除外——模式切換唔係交易動作）；UNLOCKED：啟用 + countdown。
    價格欄：follow mode（默認）由市價驅動、disabled；manual mode 需解鎖先可輸入，stepper 自適應步長。
    Commit 31：帳戶卡片撳一下 → 持倉表過濾該帳戶（持倉帶 acc_id/trd_env 標記、雙 env 覆蓋）；下單代碼 =
    模糊自動補全 + 目錄驗證（同 K 綫圖）、買入/賣出 = 綠/紅互斥按鍵。
    """

    def __init__(self, cfg: Config, *, clock=time.time, unlock_ttl_seconds: float = 24 * 3600) -> None:
        super().__init__()
        self._cfg = cfg
        self._clock = clock
        self._unlock_ttl = unlock_ttl_seconds
        self.setWindowTitle("ICT Trader — 下單版面")
        self.resize(1280, 860)   # 左右並排表格（持倉 12 欄 + 訂單 9 欄）需要寬度

        # 深色主題（跟 MainWindow 配色）
        self.setStyleSheet(
            f"QMainWindow {{ background: {cfg.bg_color}; }}"
            f"QWidget {{ color: {cfg.text_color}; font-family: Consolas; }}"
            f"QGroupBox {{ border: 1px solid {cfg.grid_color}; margin-top: 8px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; color: {cfg.axis_text_color}; }}"
            f"QLineEdit, QComboBox {{ background: #1A212B; border: 1px solid {cfg.grid_color}; "
            f"color: {cfg.text_color}; padding: 3px 6px; }}"
            f"QDoubleSpinBox {{ background: #1A212B; border: 1px solid {cfg.grid_color}; "
            f"color: {cfg.text_color}; padding: 3px 6px; }}"
            f"QPushButton {{ background: #1E2836; border: 1px solid {cfg.grid_color}; "
            f"color: {cfg.text_color}; padding: 4px 14px; }}"
            f"QPushButton:hover {{ background: #27354A; }}"
            f"QPushButton:disabled {{ color: #4A5568; background: #151B23; }}"
            f"QTableWidget {{ background: {cfg.bg_color}; gridline-color: {cfg.grid_color}; border: none; }}"
            f"QFrame#accountCard {{ background: #1A212B; border: 1px solid {cfg.grid_color}; border-radius: 6px; }}"
            f"QTabWidget::pane {{ border: 1px solid {cfg.grid_color}; top: -1px; }}"
            f"QTabBar::tab {{ background: #151B23; color: {cfg.axis_text_color}; padding: 4px 10px; "
            f"border: 1px solid {cfg.grid_color}; border-bottom: none; margin-right: 2px; }}"
            f"QTabBar::tab:selected {{ background: #1A212B; color: {cfg.text_color}; font-weight: bold; }}"
            f"QHeaderView::section {{ background: #1A212B; color: {cfg.axis_text_color}; "
            f"border: none; padding: 3px; }}"
        )

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addWidget(self._build_pin_bar())
        # 主區左右佈局：左欄 = 監控側（帳戶卡片 + 持倉/訂單並排表）；右欄 = 交易側全高（資金/訂金 + 限價下單 form）。
        main_row = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.addWidget(self._build_account_cards())
        tables_row = QHBoxLayout()
        tables_row.addWidget(self._build_positions_table(), 1)   # 左：持倉表
        tables_row.addWidget(self._build_orders_group(), 1)      # 右：今日訂單 group
        left_col.addLayout(tables_row, 1)                        # stretch：表格佔左欄剩餘高度
        right_col = QVBoxLayout()
        right_col.addWidget(self._build_funds_group())
        right_col.addWidget(self._build_order_group(), 1)        # 下單 form 填右欄剩餘高度（交易按鍵喺內）
        main_row.addLayout(left_col, 3)
        main_row.addLayout(right_col, 2)
        root.addLayout(main_row, 1)
        self._status_label = QLabel("等待連線…")
        self._status_label.setStyleSheet(f"color: {cfg.axis_text_color};")
        root.addWidget(self._status_label)
        self.setCentralWidget(central)

        # Engine（child QObject → 同 window 一齊收）；signals auto-queue 去 GUI。
        self._engine = TradeEngine(self)
        self._engine.accounts_updated.connect(self._on_accounts)
        self._engine.positions_updated.connect(self._on_positions)
        self._engine.account_funds_updated.connect(self._on_account_funds)   # per-account（雙 env、ACTIVE）
        self._engine.orders_updated.connect(self._on_orders)
        self._engine.status.connect(lambda m: self._set_status(m, cfg.axis_text_color))
        self._engine.error.connect(lambda m: self._set_status(m, _ERR_COLOR))
        self._engine.order_result.connect(self._on_order_result)

        # Per-account 資金 + 跟隨市價狀態（Commit 30）：
        self._funds_by_acc: dict[tuple[str, int], FundsSnapshot] = {}   # (trd_env, acc_id) → snapshot；失敗帳戶保留上次值
        self._card_funds_labels: dict[tuple[str, int], QLabel] = {}     # (trd_env, acc_id) → 卡片「總資產」label
        self._following = True                                          # 默認跟隨市價模式（manual mode 需 PIN 解鎖先可輸入）
        self._last_followed_price: float | None = None                  # 最後市價（重入 follow mode 時還原）
        # Commit 31：帳戶卡片撳選過濾 + 持倉雙 env 標記
        self._cards_by_acc: dict[tuple[str, int], QFrame] = {}          # (trd_env, acc_id) → card
        self._selected_acc: tuple[str, int] | None = None               # 已選帳戶卡（None = 顯示全部帳戶持倉）
        self._last_positions: tuple[PositionRow, ...] = ()              # 最新持倉 snapshot（撳選變更時重繪）

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

    def _build_account_cards(self) -> QTabWidget:
        """帳戶卡片區：按環境 tab 分類（實盤 REAL / 模擬 SIMULATE），每帳戶一張卡。

        只顯示 ACTIVE 帳戶（_on_accounts 過濾）；非 ACTIVE（DISABLED/N/A）隱藏。
        """
        self._cards_tabs = QTabWidget()
        self._env_card_layouts: dict[str, QVBoxLayout] = {}
        self._env_card_lists: dict[str, list[QFrame]] = {}
        for env in ("REAL", "SIMULATE"):
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
            container = QWidget()
            container.setLayout(layout)
            area = QScrollArea()
            area.setWidgetResizable(True)
            area.setFrameShape(QFrame.Shape.NoFrame)
            area.setWidget(container)
            area.setFixedHeight(200)   # 約 3–4 張卡可見；帳戶多咗自動滾動
            self._cards_tabs.addTab(area, "實盤 REAL" if env == "REAL" else "模擬 SIMULATE")
            self._env_card_layouts[env] = layout
            self._env_card_lists[env] = []
        return self._cards_tabs

    def _make_account_card(self, a: AccountInfo) -> QFrame:
        """單一帳戶卡片：header = id·類型[環境]（標籤）；detail = 卡號末四位/市場/券商/狀態。"""
        cfg = self._cfg
        card = QFrame()
        card.setObjectName("accountCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(8, 6, 8, 6)
        v.setSpacing(2)
        tags = []
        if a.sim_acc_type == "COMPETITION":
            tags.append("比賽")
        if a.acc_role == "MASTER":
            tags.append("主帳戶")
        tag_text = f"（{'、'.join(tags)}）" if tags else ""
        env_zh = "實盤 REAL" if a.trd_env == "REAL" else "模擬 SIMULATE"
        header = QLabel(f"{a.acc_id} · {a.acc_type or '—'} [{env_zh}]{tag_text}")
        header.setStyleSheet(f"font-weight: bold; color: {cfg.text_color};")
        funds_label = QLabel("總資產 —")   # per-account 資金（_on_account_funds 更新）
        funds_label.setStyleSheet(f"font-weight: bold; color: {cfg.text_color};")
        self._card_funds_labels[(a.trd_env, a.acc_id)] = funds_label
        card_num = a.uni_card_num or a.card_num
        detail = (f"卡號 …{card_num[-4:] if card_num else '—'} · 市場 {'/'.join(a.trdmarket_auth) or '—'}\n"
                  f"券商 {a.security_firm or '—'} · 狀態 {a.acc_status or '—'}")
        info = QLabel(detail)
        info.setStyleSheet("color: #7A8699;")
        v.addWidget(header)
        v.addWidget(funds_label)
        v.addWidget(info)
        # Commit 31：撳卡 → 持倉表過濾該帳戶（再撳同一張 = 取消選取顯示全部）
        self._cards_by_acc[(a.trd_env, a.acc_id)] = card
        card.mousePressEvent = lambda _ev, k=(a.trd_env, a.acc_id): self._select_account(k)
        return card

    def _select_account(self, key: tuple[str, int]) -> None:
        """撳帳戶卡片 → 持倉表過濾該帳戶（再撳同一張卡 = 取消選取顯示全部）。"""
        self._selected_acc = None if self._selected_acc == key else key
        self._refresh_card_styles()
        self._on_positions(self._last_positions)   # 用新 filter 重繪

    def _refresh_card_styles(self) -> None:
        """選中卡綠框高亮；其餘回落 window-level 默認樣式。"""
        for k, card in self._cards_by_acc.items():
            if k == self._selected_acc:
                card.setStyleSheet(
                    "QFrame#accountCard { background: #1A212B; border: 2px solid #089981; border-radius: 6px; }")
            else:
                card.setStyleSheet("")   # 空 = 回落 window-level stylesheet 默認樣式

    def _build_funds_group(self) -> QGroupBox:
        """資金/訂金 group：按環境 tab 分類（實盤/模擬），各 tab = 該 env 全部 ACTIVE 帳戶加總嘅 9 欄。"""
        box = QGroupBox("資金 / 訂金")
        outer = QVBoxLayout(box)
        self._funds_tabs = QTabWidget()
        self._env_funds_labels: dict[str, dict[str, QLabel]] = {}
        rows = [
            ("total_assets", "總資產"), ("cash_hkd", "現金 HKD"),
            ("cash_usd", "現金 USD"), ("withdraw_hkd", "可提 HKD"),
            ("withdraw_usd", "可提 USD"), ("buying_power", "購買力"),
            ("initial_margin", "初始保證金（訂金）"), ("maintenance_margin", "維持保證金"),
            ("risk_status", "風控狀態"),
        ]
        for env in ("REAL", "SIMULATE"):
            page = QWidget()
            grid = QVBoxLayout(page)
            labels: dict[str, QLabel] = {}
            for key, label_text in rows:
                row = QHBoxLayout()
                name = QLabel(f"{label_text}：")
                name.setStyleSheet("color: #7A8699;")
                value = QLabel("—")
                value.setStyleSheet(f"font-weight: bold; color: {self._cfg.text_color};")
                labels[key] = value
                row.addWidget(name)
                row.addStretch(1)
                row.addWidget(value)
                grid.addLayout(row)
            self._env_funds_labels[env] = labels
            self._funds_tabs.addTab(page, "實盤 REAL" if env == "REAL" else "模擬 SIMULATE")
        outer.addWidget(self._funds_tabs)
        return box

    def _build_positions_table(self) -> QTableWidget:
        """持倉 table：12 欄（代碼/名稱/市場/帳戶/數量/可用/平均成本/市價/市值/未實現盈虧/今日盈虧/盈虧%）。

        Commit 31：加「帳戶」欄——持倉帶 acc_id/trd_env 標記、雙 env 覆蓋；撳帳戶卡可按該帳戶過濾。
        """
        self._pos_table = QTableWidget(0, 12)
        self._pos_table.setHorizontalHeaderLabels(
            ["代碼", "名稱", "市場", "帳戶", "數量", "可用", "平均成本", "市價", "市值",
             "未實現盈虧", "今日盈虧", "盈虧%"])
        self._pos_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._pos_table.verticalHeader().setVisible(False)
        self._pos_table.horizontalHeader().setStretchLastSection(True)
        return self._pos_table

    def _build_orders_group(self) -> QGroupBox:
        """今日訂單 group：stretchable table（9 欄）——同持倉表左右並排、各佔半邊。"""
        box = QGroupBox("今日訂單")
        v = QVBoxLayout(box)
        self._orders_table = QTableWidget(0, 9)
        self._orders_table.setHorizontalHeaderLabels(
            ["時間", "代碼", "方向", "類型", "狀態", "數量", "價格", "已成交", "成交均價"])
        self._orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._orders_table.verticalHeader().setVisible(False)
        self._orders_table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self._orders_table)
        return box

    def _build_order_group(self) -> QGroupBox:
        """下單 group：code（模糊自動補全 + 目錄驗證）/ 買賣彩色按鍵 / price / qty / 下單按鍵。"""
        box = QGroupBox("限價下單")
        h = QHBoxLayout(box)
        cfg = self._cfg
        code_label = QLabel("代碼")
        self._order_code = QLineEdit(cfg.trading_code)
        # Commit 31：模糊自動補全 + 目錄驗證（同報價 K 綫圖）——保證標的係存在嘅
        self._code_completer = StockCompleter(self)
        self._code_by_text: dict[str, str] = {}   # display_text → canonical code（set_catalog 返回）
        self._order_code.setCompleter(self._code_completer)
        self._code_completer.activated.connect(self._on_code_activated)
        # onChange guard（同 MainWindow）：completer setCompletion() 寫入完整「code + 名稱」→ 剝離返純 code
        self._order_code.textChanged.connect(self._on_code_text_changed)
        # Commit 31：買入/賣出 = 兩個互斥 checkable 按鍵（買=綠 / 賣=紅），取代舊 QComboBox
        self._side_group = QButtonGroup(self)
        self._side_group.setExclusive(True)
        self._buy_btn = QPushButton("買入")
        self._sell_btn = QPushButton("賣出")
        for b, style in ((self._buy_btn, _BUY_BTN_STYLE), (self._sell_btn, _SELL_BTN_STYLE)):
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(style)
            self._side_group.addButton(b)
        self._buy_btn.setChecked(True)   # 默認買入
        price_label = QLabel("價格")
        # 價格 = QDoubleSpinBox：原生 range/validator + 上下箭頭 stepper（自適應步長）；默認跟隨市價模式
        self._order_price = QDoubleSpinBox()
        self._order_price.setRange(0.0, 1e12)
        self._order_price.setDecimals(4)
        self._order_price.setValue(0.0)
        self._order_price.setSingleStep(_price_step(1.0))   # = 0.01；valueChanged 後自適應
        self._follow_btn = QPushButton("🔗")
        self._follow_btn.setCheckable(True)
        self._follow_btn.blockSignals(True)                 # 防 setChecked 喺 state 未就緒時觸發 _on_follow_toggled
        self._follow_btn.setChecked(True)                   # 默認跟隨市價模式
        self._follow_btn.blockSignals(False)
        self._follow_btn.setFixedWidth(34)
        self._follow_btn.setToolTip("跟隨市價（報價自動更新）；點擊切換手動輸入")
        qty_label = QLabel("數量")
        self._order_qty = QLineEdit()
        self._order_qty.setValidator(QIntValidator(1, 10**9))
        self._order_qty.setPlaceholderText("股數")
        self._place_btn = QPushButton("下單")
        h.addWidget(code_label)
        h.addWidget(self._order_code, 2)
        h.addWidget(self._buy_btn)
        h.addWidget(self._sell_btn)
        h.addWidget(price_label)
        h.addWidget(self._order_price, 1)
        h.addWidget(self._follow_btn)
        h.addWidget(qty_label)
        h.addWidget(self._order_qty)
        h.addWidget(self._place_btn)
        self._place_btn.clicked.connect(self._on_place_order)
        # toggled 只有單一 (bool) overload → slot 帶明確 bool 參數係正確綁定（唔似 clicked 雙 overload）
        self._follow_btn.toggled.connect(self._on_follow_toggled)
        self._order_price.valueChanged.connect(self._on_price_value_changed)
        return box

    # ------------------------------------------------------------- PIN 狀態機

    def _apply_pin_state(self) -> None:
        """按當前 _pin_holder 狀態同步 UI enable/disable（LOCKED = holder is None）。"""
        unlocked = self._pin_holder is not None
        self._pin_edit.setEnabled(not unlocked)
        self._unlock_btn.setEnabled(not unlocked)
        self._lock_btn.setEnabled(unlocked)
        for w in (self._order_code, self._buy_btn, self._sell_btn, self._order_qty):   # Commit 31：買賣按鍵跟隨鎖狀態
            w.setEnabled(unlocked)
        # 價格欄：「解鎖 AND 手動模式」先可編輯——follow mode 由市價驅動（disabled 防用戶輸入被覆蓋）
        self._order_price.setEnabled(unlocked and not self._following)
        # follow 按鍵係模式切換（唔係交易動作）→ locked 都可用
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

    # ------------------------------------------------------------- 跨視窗同步（main.py 接線：MainWindow.code_changed / last_price）

    def set_symbol(self, code: str) -> None:
        """K 綫標的切換 → 下單代碼跟隨（PIN locked 都生效——純顯示，唔涉及交易）。"""
        self._order_code.blockSignals(True)
        try:
            self._order_code.setText(code or "")
        finally:
            self._order_code.blockSignals(False)

    def set_stock_catalog(self, entries: tuple) -> None:
        """MainWindow.catalog_ready re-emit → 載入股票目錄（同 K 綫圖同源；Commit 31）。"""
        self._code_by_text = self._code_completer.set_catalog(tuple(entries))

    def _on_code_activated(self, text: str) -> None:
        """Dropdown 選中 → 輸入欄只留 code（名稱唔入欄；同 K 綫圖一致）。"""
        code = code_from_completion(text, self._code_by_text)
        if not code:
            return
        self._order_code.setText(code)

    def _on_code_text_changed(self, text: str) -> None:
        """onChange guard：「code + 名稱」（含空白）剝離返純 code（同 MainWindow）。"""
        if not any(ch.isspace() for ch in text):
            return
        tokens = [t for t in text.split() if t]
        self._order_code.blockSignals(True)
        try:
            self._order_code.setText(tokens[0] if tokens else "")
        finally:
            self._order_code.blockSignals(False)

    def follow_price(self, price: float | None) -> None:
        """最新市價 → 自動更新下單價格（只喺 follow mode；manual mode no-op——唔覆蓋用戶輸入）。"""
        if not self._following or price is None or price <= 0:
            return
        self._last_followed_price = price
        self._order_price.blockSignals(True)   # 防 valueChanged → _on_price_value_changed round-trip
        try:
            self._order_price.setValue(price)
            self._order_price.setSingleStep(_price_step(price))
        finally:
            self._order_price.blockSignals(False)

    def _on_follow_toggled(self, on: bool) -> None:
        """follow 按鍵 toggle：跟隨市價（🔗）↔ 手動輸入（✎）。"""
        self._following = on
        if on:
            self._follow_btn.setText("🔗")
            self._follow_btn.setToolTip("跟隨市價（報價自動更新）；點擊切換手動輸入")
            if self._last_followed_price is not None:   # 重入 follow mode → 還原最後市價
                self.follow_price(self._last_followed_price)
        else:
            self._follow_btn.setText("✎")
            self._follow_btn.setToolTip("手動輸入模式；點擊切換跟隨市價")
        self._apply_pin_state()

    def _on_price_value_changed(self, value: float) -> None:
        """價格變動 → 自適應 stepper 步長（10^(floor(log10(p))−2)）。"""
        self._order_price.setSingleStep(_price_step(value))

    # ------------------------------------------------------------- engine signal handlers（GUI thread）

    def _on_accounts(self, accounts: tuple[AccountInfo, ...]) -> None:
        """帳戶 snapshot → 按 env tab 重繪卡片（只 ACTIVE；非 ACTIVE 隱藏；先清舊卡防殘留）。"""
        for env in ("REAL", "SIMULATE"):
            for c in self._env_card_lists[env]:
                c.setParent(None)
            self._env_card_lists[env].clear()
        self._card_funds_labels.clear()
        self._cards_by_acc.clear()   # Commit 31：重建卡片 registry（撳選過濾）
        active = [a for a in accounts if a.acc_status == "ACTIVE"]
        for env in ("REAL", "SIMULATE"):
            for a in sorted((x for x in active if x.trd_env == env), key=lambda x: x.acc_id):
                card = self._make_account_card(a)
                self._env_card_layouts[env].addWidget(card)
                self._env_card_lists[env].append(card)
        # Commit 31：已選帳戶唔存在 → 取消選取（顯示全部）；重施選中高亮樣式
        if self._selected_acc is not None and self._selected_acc not in self._cards_by_acc:
            self._selected_acc = None
        self._refresh_card_styles()
        # 已收到嘅 per-account 資金 reapply 去新卡（帳戶列表更新後唔會消失）
        for (env, acc_id), snap in self._funds_by_acc.items():
            lbl = self._card_funds_labels.get((env, acc_id))
            if lbl is not None:
                lbl.setText(f"總資產 {_fmt_money(snap.total_assets)}")

    def _on_positions(self, rows: tuple[PositionRow, ...]) -> None:
        """持倉 snapshot → table 重繪（字段同富途 APP 對齊；Commit 31：帳戶卡撳選過濾）。"""
        self._last_positions = rows
        if self._selected_acc is not None:   # 已選帳戶 → 只顯示該帳戶持倉
            env, acc_id = self._selected_acc
            rows = tuple(r for r in rows if (r.trd_env, r.acc_id) == (env, acc_id))
        table = self._pos_table
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [
                row.code, row.name, row.market,
                f"{row.acc_id}·{'實' if row.trd_env == 'REAL' else '模'}",   # Commit 31：帳戶欄（id + env）
                f"{row.qty:g}", f"{row.can_sell_qty:g}",
                _fmt_money(row.avg_cost), _fmt_money(row.last_price),
                _fmt_money(row.market_value), _fmt_money(row.unrealized_pl),
                _fmt_money(row.today_pl),
                f"{row.pl_ratio_pct:+.2f}%",   # 已是百分數數字
            ]
            for c, text in enumerate(values):
                item = QTableWidgetItem(text)
                if c >= 9:   # 未實現盈虧/今日盈虧/盈虧%：正綠負紅（以 unrealized_pl 符號為準）
                    color = _OK_COLOR if row.unrealized_pl >= 0 else _ERR_COLOR
                    item.setForeground(QColor(color))
                table.setItem(r, c, item)

    def _on_account_funds(self, acc_id: int, trd_env: str, funds: FundsSnapshot) -> None:
        """Per-account 資金事件 → 卡片「總資產」+ 該 env tab 加總（GUI 端 per-env fold，重用 engine._sum_funds）。"""
        self._funds_by_acc[(trd_env, acc_id)] = funds   # 累積；失敗帳戶保留上次值
        lbl = self._card_funds_labels.get((trd_env, acc_id))
        if lbl is not None:
            lbl.setText(f"總資產 {_fmt_money(funds.total_assets)}")
        total: FundsSnapshot | None = None
        for (e, _a), s in self._funds_by_acc.items():
            if e == trd_env:
                total = s if total is None else _sum_funds(total, s)
        labels = self._env_funds_labels.get(trd_env)
        if labels is None:   # 理論上唔會（只 emit REAL/SIMULATE）；防禦性 return
            return
        for key in ("total_assets", "cash_hkd", "cash_usd", "withdraw_hkd", "withdraw_usd",
                    "buying_power", "initial_margin", "maintenance_margin"):
            labels[key].setText("—" if total is None else _fmt_money(getattr(total, key)))
        risk_label = labels["risk_status"]
        if total is None:   # 該 env 零帳戶 / 全部查詢失敗 → 全 "—"
            risk_label.setText("—")
            risk_label.setStyleSheet(f"font-weight: bold; color: {self._cfg.text_color};")
            return
        risk_label.setText(_RISK_STATUS_ZH.get(total.risk_status, total.risk_status or "—"))
        if total.risk_status == "LEVEL1":
            risk_label.setStyleSheet(f"font-weight: bold; color: {_ERR_COLOR};")
        elif total.risk_status == "LEVEL2":
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
        price = self._order_price.value()   # QDoubleSpinBox 原生 range/validator（0–1e12、4 小數）
        qty_text = self._order_qty.text().strip()
        if not code or "." not in code:
            self._set_status("代碼格式錯誤（例：HK.00700 / US.AAPL）", _ERR_COLOR)
            return
        # Commit 31：目錄驗證（同報價 K 綫圖）——已載入 → 必須存在 + 正規化大小寫；未載入 → 放行俾 engine/OpenD 最終校驗
        catalog = self._code_completer.catalog()
        if len(catalog):
            canonical = catalog.canonical_code(code)
            if canonical is None:
                self._set_status(f"股票編號唔存在：{code}", _ERR_COLOR)
                return
            code = canonical
        try:
            qty = int(qty_text)
        except ValueError:
            self._set_status("數量必須係數字", _ERR_COLOR)
            return
        if price <= 0 or qty <= 0:
            self._set_status("價格與數量必須大於 0", _ERR_COLOR)
            return
        side = TrdSide.SELL if self._sell_btn.isChecked() else TrdSide.BUY   # Commit 31：買賣按鍵（默認買入 checked）
        pin = self._pin_holder.value if self._pin_holder is not None else None
        self._place_btn.setEnabled(False)   # in-flight guard（order_result 後 re-enable）
        self._engine.place_order(code, side, price, qty, pin=pin)

    # ------------------------------------------------------------- lifecycle

    def shutdown(self) -> None:
        """Clean shutdown：停 countdown timer + engine.stop()（idempotent）。"""
        self._countdown_timer.stop()
        self._engine.stop()
