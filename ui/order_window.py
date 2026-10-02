"""下單版面視窗（Commit 33 專業化改版）：

- **模式選擇器**：模擬盤 SIMULATE / 實盤 REAL——只有實盤先顯示六位數 PIN 輸入 + 解鎖/上鎖按鍵；
  模擬盤無需交易密碼（futu 規則），下單直接 dispatch `trd_env="SIMULATE"`。
- **標的種類自動匹配帳戶**：股票 → 優先 CASH 帳戶、期貨期權 → 優先 MARGIN/STOCK_AND_OPTION
  （`_is_equity_symbol()` + `_match_order_account()` 純函數），下單模塊即時顯示匹配帳戶卡號末四位 + 餘額。
- **底部特大買賣按鍵**：買入=紅 / 賣出=綠（Commit 31 起嘅綠/紅已對調），撳即落單（direct execution，
  專業交易軟件慣例）；in-flight 期間兩按同時禁用。
- **下單即時資訊**：合計金額 = 數量 × 價格 live label + 代碼輸入後顯示中文/英文名稱。
- **訂單表全細節**：11 欄（時間/訂單號/代碼/方向/類型/狀態/數量/價格/已成交/成交均價/帳戶）。
- **水平二分**：今日訂單喺上、持倉喺下（Commit 31 前係左右並排）。
- 帳戶卡片按環境 tab 分類（只 ACTIVE，撳卡可按該帳戶過濾持倉）+ per-account 資金 + env 加總資金面板。

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

from PySide6.QtCore import Qt, QRegularExpression, QTimer, Signal
from PySide6.QtGui import QColor, QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QCheckBox, QDoubleSpinBox, QFrame, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea, QTabWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from config import Config
from engine.trade_engine import (AccountInfo, FundsSnapshot, OrderRow, PositionRow,
                                 TradeEngine, _sum_funds)
from futu import TrdSide
from engine.stock_catalog import name_text
from .stock_completer import StockCompleter, code_from_completion

# 狀態色（跟 MainWindow 深色主題語義）
_OK_COLOR = "#089981"
_ERR_COLOR = "#F23645"
_WARN_COLOR = "#FFB020"

# 買入/賣出特大按鍵（Commit 33）：買=紅 / 賣=綠（用戶指定，同 Commit 31 嘅綠/紅對調）。
# direct execution——撳即落單；:hover 微亮提示可點、:disabled = PIN locked / in-flight。
_BUY_BTN_STYLE = (
    "QPushButton { background: #4A1420; border: 2px solid #F23645; color: #FF8A80;"
    " font-weight: bold; font-size: 18px; }"
    "QPushButton:hover { background: #6B1D2E; color: #FFFFFF; }"
    "QPushButton:disabled { background: #151B23; border-color: #2A3441; color: #4A5568; }")
_SELL_BTN_STYLE = (
    "QPushButton { background: #0B3D2E; border: 2px solid #089981; color: #69F0AE;"
    " font-weight: bold; font-size: 18px; }"
    "QPushButton:hover { background: #0E5C47; color: #FFFFFF; }"
    "QPushButton:disabled { background: #151B23; border-color: #2A3441; color: #4A5568; }")

# 特大按鍵最小高度（px）——「特別大」嘅量化定義，測試斷言用
_BIG_BTN_MIN_HEIGHT = 64


def _is_equity_symbol(code: str) -> bool:
    """標的種類 heuristic：股票 vs 期貨/期權（Commit 33 帳戶自動匹配用）。

    - suffix 以 'main' 結尾 = 主力連續合約 → 期貨（HK.HSImain / SG.CNmain）；
    - suffix 長度 ≥12 = 期權代碼（ticker + 到期日 + 行權價，如 AAPL251219C00200000）；
    - 其餘 = 股票（HK.00700 / US.AAPL / SG.D05——美股 ticker 係字母、唔可以淨係睇數字）。
    """
    suffix = code.split(".", 1)[1] if "." in code else ""
    if not suffix:
        return False
    if suffix.lower().endswith("main"):
        return False
    if len(suffix) >= 12:
        return False
    return True


def _match_order_account(accounts, code: str, trd_env: str):
    """按「模式 + 標的種類」自動匹配下單帳戶（純函數、可單測）。

    過濾：trd_env 匹配 + ACTIVE + 非 MASTER + market ∈ trdmarket_auth。
    優先序：股票 → CASH 帳戶優先；期貨/期權 → MARGIN / STOCK_AND_OPTION 優先；其餘類型殿後。
    無候選 → None（UI 顯示 ⚠ 並阻止下單）。
    """
    market = code.split(".", 1)[0].upper() if "." in code else ""
    candidates = [
        a for a in accounts
        if a.trd_env == trd_env and a.acc_status == "ACTIVE"
        and a.acc_role != "MASTER" and market in a.trdmarket_auth
    ]
    if not candidates:
        return None
    preferred = {"CASH"} if _is_equity_symbol(code) else {"MARGIN", "STOCK_AND_OPTION"}

    def rank(a):
        return 0 if a.acc_type in preferred else 1

    return sorted(candidates, key=rank)[0]

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

    佈局（Commit 33）：PIN bar（含模式選擇器——只實盤先顯示 PIN 輸入）→ main_row[左欄（帳戶卡片 tabs +
    今日訂單/持倉**上下水平二分**表）| 右欄全高（資金/訂金 env tabs + 限價下單 form，底部特大買=紅/賣=綠按鍵）] → status label。
    LOCKED（默認、只實盤有意義）：下單表單 disabled；UNLOCKED：啟用 + countdown。模擬盤無需 PIN、永遠可交易。
    價格欄：follow mode（默認）由市價驅動、disabled；manual mode 需解鎖先可輸入，stepper 自適應步長。
    Commit 31：帳戶卡片撳一下 → 持倉表過濾該帳戶（持倉帶 acc_id/trd_env 標記、雙 env 覆蓋）；下單代碼 =
    模糊自動補全 + 目錄驗證（同 K 綫圖）。Commit 33：買賣按鍵改 direct execution（撳即落單）、
    合計金額/名稱 live label、帳戶按標的種類自動匹配。
    Commit 34：PIN bar + 模式選擇器移入下單 form；`code_changed(str)` signal → K 綫視窗反向同步標的
    （600ms debounce）；數量默認 = 每手單位（lot size）；買賣二次確認 checkbox；訂單/持倉 per-row
    撤單/平倉 + 全部撤單/全部平倉（全部二次確認）；成功/錯誤 status label 高對比當眼。
    """

    code_changed = Signal(str)   # Commit 34：下單代碼變更 → K 綫視窗反向同步（debounce 後 emit canonical code）

    def __init__(self, cfg: Config, *, clock=time.time, unlock_ttl_seconds: float = 24 * 3600) -> None:
        super().__init__()
        self._cfg = cfg
        self._clock = clock
        self._unlock_ttl = unlock_ttl_seconds
        self.setWindowTitle("ICT Trader — 下單版面")
        self.resize(1280, 860)   # 左欄訂單/持倉上下二分（各 11-12 欄）需要寬度

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
        # Commit 34：PIN bar 唔再放頂部——移入右欄限價下單 form 內（_build_order_group）。
        # 主區左右佈局：左欄 = 監控側（帳戶卡片 + 今日訂單/持倉上下水平二分）；右欄 = 交易側全高（資金/訂金 + 限價下單 form）。
        main_row = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.addWidget(self._build_account_cards())
        # Commit 33：水平二分——訂單喺上、持倉喺下（Commit 31 前係左右並排）；各 stretch=1 均分高度。
        tables_row = QVBoxLayout()
        tables_row.addWidget(self._build_orders_group(), 1)      # 上：今日訂單 group（Commit 34：+操作欄 +全部撤單）
        tables_row.addWidget(self._build_positions_group(), 1)   # 下：持倉 group（Commit 34：+操作欄 +全部平倉）
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
        # Commit 34：下單 + 撤單共用同一個 action-done handler（每次 dispatch 恰好 emit 一個 result → 配對成立）
        self._engine.order_result.connect(self._on_action_done)
        self._engine.cancel_result.connect(self._on_action_done)

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

        # Commit 33：模式選擇器 + 標的種類自動匹配帳戶 + 名稱/合計 live label
        self._mode = "SIMULATE"   # 默認模擬盤（安全預設；實盤需明確切換 + PIN 解鎖）
        self._all_accounts: list[AccountInfo] = []          # 全帳戶 snapshot（_on_accounts 更新、匹配用）
        self._matched_acc: AccountInfo | None = None        # 當前匹配嘅下單帳戶（code × mode 決定）
        self._code_names: dict[str, str] = {}               # canonical code → 「中文名 英文名」（set_stock_catalog 建）

        # Commit 34：lot size / 反向同步 / action queue / per-row 操作按鈕狀態
        self._code_lot_sizes: dict[str, int] = {}           # canonical code → 每手單位（set_stock_catalog 建）
        self._last_lot_fill_code: str = ""                  # 上次 auto-fill qty 嘅 code（防重複覆蓋用戶輸入）
        self._last_emitted_code: str = ""                   # 上次 emit code_changed 嘅 canonical code（防 debounce loop）
        self._symbol_debounce = QTimer(self)                # 600ms singleShot → _emit_symbol_if_valid()
        self._symbol_debounce.setSingleShot(True)
        self._symbol_debounce.setInterval(600)
        self._symbol_debounce.timeout.connect(self._emit_symbol_if_valid)
        self._action_queue: list = []                       # 待執行 action（lambda → engine call）；串行化
        self._action_busy: bool = False                     # True = 有 action 等緊 result signal
        self._displayed_orders: tuple[OrderRow, ...] = ()   # 當前顯示嘅訂單行（per-row 撤單按鈕用）
        self._displayed_positions: tuple[PositionRow, ...] = ()   # 當前顯示嘅持倉行（per-row 平倉按鈕用）
        self._pos_row_btns: list[QPushButton] = []          # per-row 平倉按鈕（重繪前 deleteLater 清理）
        self._ord_row_btns: list[QPushButton] = []          # per-row 撤單按鈕（重繪前 deleteLater 清理）

        self._on_code_changed()   # Commit 33：初始代碼（cfg.trading_code）→ 名稱/合計/帳戶 label 就緒
        self._apply_pin_state()   # 初始：SIMULATE 默認 → 表單 enabled；PIN 區隱藏
        self._engine.start(cfg)

    # ------------------------------------------------------------- widget builders

    def _build_pin_bar(self) -> QWidget:
        """PIN bar（Commit 34：移入下單 form）：兩行佈局——row1 = 交易模式選擇器 + countdown；
        row2 = PIN 輸入區（**只實盤先顯示**）/ 模擬盤提示。

        模擬盤無需交易密碼（futu 規則）→ `_pin_box` 隱藏、顯示提示 label；實盤 → masked PIN input +
        解鎖/鎖定按鍵 + countdown。模式切換唔會清空已解鎖嘅 PIN holder（24h 狀態跨模式保留）。
        """
        bar = QWidget()
        v = QVBoxLayout(bar)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        # row1：交易模式選擇器 + countdown
        row1 = QHBoxLayout()
        title = QLabel("交易模式")
        title.setStyleSheet(f"font-weight: bold; color: {self._cfg.text_color};")
        self._mode_sim_btn = QPushButton("模擬盤 SIMULATE")
        self._mode_real_btn = QPushButton("實盤 REAL")
        for btn, checked in ((self._mode_sim_btn, True), (self._mode_real_btn, False)):
            btn.setCheckable(True)
            btn.setChecked(checked)
            btn.setStyleSheet(
                "QPushButton { background: #1E2836; border: 1px solid #2A3441; color: #7A8699; font-weight: bold; }"
                "QPushButton:checked { background: #27435C; border-color: #4FC3F7; color: #FFFFFF; }")
        mode_group = QButtonGroup(self)
        mode_group.setExclusive(True)
        mode_group.addButton(self._mode_sim_btn)
        mode_group.addButton(self._mode_real_btn)

        self._countdown_label = QLabel("")
        self._countdown_label.setStyleSheet(f"color: {_WARN_COLOR};")
        row1.addWidget(title)
        row1.addWidget(self._mode_sim_btn)
        row1.addWidget(self._mode_real_btn)
        row1.addStretch(1)
        row1.addWidget(self._countdown_label)

        # row2：PIN 輸入區（REAL only）/ 模擬盤提示
        self._pin_box = QWidget()
        ph = QHBoxLayout(self._pin_box)
        ph.setContentsMargins(0, 0, 0, 0)
        pin_title = QLabel("交易解鎖")
        pin_title.setStyleSheet(f"font-weight: bold; color: {self._cfg.text_color};")
        self._pin_edit = QLineEdit()
        self._pin_edit.setEchoMode(QLineEdit.EchoMode.Password)   # 永遠圓點，無明文
        self._pin_edit.setPlaceholderText("六位數 PIN")
        self._pin_edit.setMaxLength(6)
        self._pin_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9]{0,6}")))
        self._pin_edit.setFixedWidth(140)
        self._unlock_btn = QPushButton("解鎖")
        self._lock_btn = QPushButton("鎖定")
        ph.addWidget(pin_title)
        ph.addWidget(self._pin_edit)
        ph.addWidget(self._unlock_btn)
        ph.addWidget(self._lock_btn)

        # 模擬盤提示（SIMULATE only）
        self._sim_hint = QLabel("模擬盤無需交易密碼——下單直接執行")
        self._sim_hint.setStyleSheet(f"color: {self._cfg.axis_text_color}; font-size: 12px;")

        row2 = QHBoxLayout()
        row2.addWidget(self._pin_box)
        row2.addWidget(self._sim_hint)
        row2.addStretch(1)

        v.addLayout(row1)
        v.addLayout(row2)

        self._unlock_btn.clicked.connect(self._on_unlock_clicked)
        self._lock_btn.clicked.connect(self._on_lock_clicked)
        # 模式切換：lambda 包零參數調用（toggled 雖只有一個 (bool) overload，統一 lambda 最穩）
        self._mode_sim_btn.toggled.connect(lambda: self._sync_mode())
        self._mode_real_btn.toggled.connect(lambda: self._sync_mode())
        return bar

    def _sync_mode(self) -> None:
        """模式按鍵 toggled → 更新 `self._mode` + PIN 區可見性 + 帳戶重新匹配（env 變咗）。"""
        self._mode = "SIMULATE" if self._mode_sim_btn.isChecked() else "REAL"
        self._refresh_matched_account()   # 匹配依賴 env——切換即刻重算
        self._apply_pin_state()

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

    def _build_positions_group(self) -> QGroupBox:
        """持倉 group（Commit 34）：header row（全部平倉按鍵）+ table 13 欄。

        Commit 31：加「帳戶」欄——持倉帶 acc_id/trd_env 標記、雙 env 覆蓋；撳帳戶卡可按該帳戶過濾。
        Commit 34：加「操作」欄（per-row 平倉按鍵）+ header「全部平倉」——全部二次確認。
        """
        box = QGroupBox("持倉")
        v = QVBoxLayout(box)
        header = QHBoxLayout()
        self._close_all_btn = QPushButton("全部平倉")
        # lambda 包零參數調用（clicked 有 (bool checked) 雙 overload——AGENTS.md #4）
        self._close_all_btn.clicked.connect(lambda: self._on_close_all())
        header.addStretch(1)
        header.addWidget(self._close_all_btn)
        v.addLayout(header)
        self._pos_table = QTableWidget(0, 13)
        self._pos_table.setHorizontalHeaderLabels(
            ["代碼", "名稱", "市場", "帳戶", "數量", "可用", "平均成本", "市價", "市值",
             "未實現盈虧", "今日盈虧", "盈虧%", "操作"])
        self._pos_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._pos_table.verticalHeader().setVisible(False)
        v.addWidget(self._pos_table)
        return box

    def _build_orders_group(self) -> QGroupBox:
        """今日訂單 group：header row（全部撤單按鍵）+ stretchable table（12 欄）。

        Commit 33：訂單在上、持倉在下（垂直二分）；訂單表顯示所有細節
        （訂單號 / 代碼 / 方向 / 類型 / 狀態 / 數量 / 價格 / 已成交 / 成交均價 / 下單時間 / 帳戶）。
        Commit 34：加「操作」欄（per-row 撤單按鍵）+ header「全部撤單」——全部二次確認。
        """
        box = QGroupBox("今日訂單")
        v = QVBoxLayout(box)
        header = QHBoxLayout()
        self._cancel_all_btn = QPushButton("全部撤單")
        # lambda 包零參數調用（clicked 有 (bool checked) 雙 overload——AGENTS.md #4）
        self._cancel_all_btn.clicked.connect(lambda: self._on_cancel_all())
        header.addStretch(1)
        header.addWidget(self._cancel_all_btn)
        v.addLayout(header)
        self._orders_table = QTableWidget(0, 12)
        self._orders_table.setHorizontalHeaderLabels(
            ["訂單號", "代碼", "方向", "類型", "狀態", "數量", "價格",
             "已成交", "成交均價", "下單時間", "帳戶", "操作"])
        self._orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._orders_table.verticalHeader().setVisible(False)
        v.addWidget(self._orders_table)
        return box

    def _build_order_group(self) -> QGroupBox:
        """下單 group（Commit 33）：垂直佈局——code+中文名 / price+follow+qty / 合計金額 / 匹配帳戶 / 底部特大買賣按鍵。

        買=紅、賣=綠，**直接執行**（撳即落單，專業交易軟件慣例），min height 64px；
        取代舊「互斥 checkable side selector + 獨立下單按鍵」。
        """
        box = QGroupBox("限價下單")
        box.setObjectName("orderGroup")   # Commit 34：PIN bar 移入呢度（測試定位用）
        v = QVBoxLayout(box)
        cfg = self._cfg

        # Row 1：代碼（模糊自動補全 + 目錄驗證）+ 中文名稱 label
        row1 = QHBoxLayout()
        code_label = QLabel("代碼")
        self._order_code = QLineEdit(cfg.trading_code)
        # Commit 31：模糊自動補全 + 目錄驗證（同報價 K 綫圖）——保證標的係存在嘅
        self._code_completer = StockCompleter(self)
        self._code_by_text: dict[str, str] = {}   # display_text → canonical code（set_catalog 返回）
        self._order_code.setCompleter(self._code_completer)
        self._code_completer.activated.connect(self._on_code_activated)
        # onChange guard（同 MainWindow）：completer setCompletion() 寫入完整「code + 名稱」→ 剝離返純 code
        self._order_code.textChanged.connect(self._on_code_text_changed)
        # Commit 33：代碼變更 → 名稱 label / 合計金額 / 帳戶重新匹配（統一入口）
        self._order_code.textChanged.connect(self._on_code_changed)
        self._name_label = QLabel("")
        self._name_label.setStyleSheet("color: #90A4AE;")
        row1.addWidget(code_label)
        row1.addWidget(self._order_code, 2)
        row1.addWidget(QLabel("名稱"))
        row1.addWidget(self._name_label, 3)
        v.addLayout(row1)

        # Row 2：價格（spinbox stepper）+ follow icon + 數量
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
        self._order_qty = QLineEdit()
        self._order_qty.setValidator(QIntValidator(1, 10**9))
        self._order_qty.setPlaceholderText("股數")
        # Commit 33：數量變更 → 合計金額 live 更新
        self._order_qty.textChanged.connect(self._refresh_total_label)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("價格"))
        row2.addWidget(self._order_price, 1)
        row2.addWidget(self._follow_btn)
        row2.addWidget(QLabel("數量"))
        row2.addWidget(self._order_qty)
        v.addLayout(row2)

        # Row 3：合計金額（qty × price live 更新）
        self._total_label = QLabel("合計 —")
        self._total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFC400;")
        v.addWidget(self._total_label)

        # Row 4：匹配帳戶 info（按標的種類 × 模式自動匹配）
        self._acc_info_label = QLabel("帳戶 —")
        self._acc_info_label.setStyleSheet("color: #90A4AE;")
        v.addWidget(self._acc_info_label)

        # Commit 34：PIN bar（交易密碼 + 實盤/模擬盤選擇）移入下單 form；二次確認 checkbox
        v.addWidget(self._build_pin_bar())
        self._confirm_cb = QCheckBox("下單前二次確認訂單內容")
        self._confirm_cb.setChecked(True)   # 默認開啟（安全預設）

        # 底部行：特大買賣按鍵（直接執行；買=紅 / 賣=綠）
        btn_row = QHBoxLayout()
        self._buy_btn = QPushButton("買入 BUY")
        self._sell_btn = QPushButton("賣出 SELL")
        for b, style in ((self._buy_btn, _BUY_BTN_STYLE), (self._sell_btn, _SELL_BTN_STYLE)):
            b.setMinimumHeight(_BIG_BTN_MIN_HEIGHT)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(style)
        # clicked 雙 overload → lambda 包零參數調用（AGENTS.md #4）
        self._buy_btn.clicked.connect(lambda: self._on_place_order("BUY"))
        self._sell_btn.clicked.connect(lambda: self._on_place_order("SELL"))
        btn_row.addWidget(self._buy_btn, 1)
        btn_row.addWidget(self._sell_btn, 1)
        v.addLayout(btn_row)

        # toggled 只有單一 (bool) overload → slot 帶明確 bool 參數係正確綁定（唔似 clicked 雙 overload）
        self._follow_btn.toggled.connect(self._on_follow_toggled)
        self._order_price.valueChanged.connect(self._on_price_value_changed)
        return box

    # ------------------------------------------------------------- PIN 狀態機

    def _apply_pin_state(self) -> None:
        """按當前模式 + PIN 狀態同步 UI enable/disable（Commit 33）。

        SIMULATE = 永遠解鎖（futu 規則：模擬盤無需交易密碼）；REAL = 需 PIN holder。
        PIN 區只喺 REAL 顯示、模擬提示 label 相反；買賣按鍵跟隨解鎖狀態。
        """
        self._pin_box.setVisible(self._mode == "REAL")
        self._sim_hint.setVisible(self._mode != "REAL")
        unlocked = self._mode == "SIMULATE" or self._pin_holder is not None
        self._pin_edit.setEnabled(not unlocked)
        self._unlock_btn.setEnabled(not unlocked)
        self._lock_btn.setEnabled(self._pin_holder is not None)   # 有 holder 先可鎖（跨模式保留）
        busy = self._action_busy or bool(self._action_queue)   # Commit 34：有 pending action → 買賣按鍵保持 disabled
        for w in (self._order_code, self._order_qty):
            w.setEnabled(unlocked)
        for b in (self._buy_btn, self._sell_btn):
            b.setEnabled(unlocked and not busy)
        # 價格欄：「解鎖 AND 手動模式」先可編輯——follow mode 由市價驅動（disabled 防用戶輸入被覆蓋）
        self._order_price.setEnabled(unlocked and not self._following)

    def _refresh_matched_account(self) -> None:
        """按當前 code × mode 重算匹配下單帳戶 + 更新 info label（Commit 33）。

        觸發點：模式切換（_sync_mode）、accounts_updated、code 變更、funds 更新（餘額刷新）。
        純顯示邏輯——實際下單時 _on_place_order 再讀 `self._matched_acc`。
        """
        code = self._order_code.text().strip() if hasattr(self, "_order_code") else ""
        self._matched_acc = _match_order_account(self._all_accounts, code, self._mode) if code else None
        acc = self._matched_acc
        if acc is None:
            self._acc_info_label.setText("帳戶 —（無匹配帳戶）" if code else "帳戶 —")
            return
        card = f"…{acc.card_num[-4:]}" if acc.card_num and acc.card_num != "N/A" else str(acc.acc_id)
        snap = self._funds_by_acc.get((acc.trd_env, acc.acc_id))
        bal = _fmt_money(snap.total_assets) if snap is not None else "—"
        env_zh = "實盤" if acc.trd_env == "REAL" else "模擬"
        self._acc_info_label.setText(
            f"帳戶 {env_zh} · {acc.acc_type} · 卡號 {card} · 餘額 {bal}")

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
        """K 綫標的切換 → 下單代碼跟隨（PIN locked 都生效——純顯示，唔涉及交易）。

        Commit 34：價格欄重置為 0（新標的市價由 follow mode 下一個 tick 驅動）+ 清最後市價 +
        記錄 `_last_emitted_code`（防反向同步 debounce 將同一 code emit 返去 K 綫視窗）。
        """
        self._order_code.blockSignals(True)
        try:
            self._order_code.setText(code or "")
        finally:
            self._order_code.blockSignals(False)
        # Commit 34：下單價格跟隨標的改變——重置（follow mode 會用新市價自動填回）
        self._last_followed_price = None
        self._order_price.blockSignals(True)
        try:
            self._order_price.setValue(0.0)
        finally:
            self._order_price.blockSignals(False)
        # 反向同步防 loop：呢個 code 來自 K 綫視窗，唔好再 emit 返去
        self._last_emitted_code = (code or "").strip().upper()
        self._on_code_changed()   # Commit 33：signal 被 block → 手動同步名稱/合計/帳戶 label

    def set_stock_catalog(self, entries: tuple) -> None:
        """MainWindow.catalog_ready re-emit → 載入股票目錄（同 K 綫圖同源；Commit 31）。

        Commit 33：同時建 `self._code_names`（canonical code → 「中文名 英文名」）供名稱 label 顯示。
        Commit 34：同時建 `self._code_lot_sizes`（canonical code → 每手單位）——當前標的 lot 已知即 auto-fill 數量。
        """
        self._code_by_text = self._code_completer.set_catalog(tuple(entries))
        self._code_names = {e.code: name_text(e) for e in entries}
        # Commit 34：lot size map（只收 lot_size 已知且 >0 嘅 entry）
        self._code_lot_sizes = {e.code: int(e.lot_size) for e in entries if e.lot_size}
        self._refresh_name_label()
        self._auto_fill_qty()   # Commit 34：目錄遲到 → 補填當前標的數量（guard 防重複覆蓋）

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

    def _refresh_name_label(self) -> None:
        """代碼變更 → 名稱 label（中文名 + 英文名；目錄未載入 / 未知 code → 空）。Commit 33。"""
        code = self._order_code.text().strip() if hasattr(self, "_order_code") else ""
        name = self._code_names.get(code.upper()) or self._code_names.get(code) or ""
        self._name_label.setText(name)

    def _refresh_total_label(self) -> None:
        """合計金額 label = 數量 × 價格（任一欄空/0 → 「—」）。Commit 33。"""
        try:
            qty = int(self._order_qty.text()) if self._order_qty.text().strip() else 0
        except ValueError:
            qty = 0
        price = self._order_price.value()
        if qty <= 0 or price <= 0:
            self._total_label.setText("合計 —")
            return
        self._total_label.setText(f"合計 {_fmt_money(qty * price)}")

    def _on_code_changed(self) -> None:
        """代碼變更統一入口：名稱 label + 合計 + 帳戶重新匹配（code 決定標的種類）。Commit 33。

        Commit 34：+ auto-fill 數量 = 每手單位（lot size）+ schedule 反向同步 emit 去 K 綫視窗
        （600ms debounce——快速輸入/切換合併成一次 emit）。
        """
        self._refresh_name_label()
        self._auto_fill_qty()
        self._refresh_total_label()
        self._refresh_matched_account()
        self._schedule_symbol_emit()

    def _auto_fill_qty(self) -> None:
        """Commit 34：標的變更 → auto-fill 數量 = 每手最少單位（lot size）。

        Guard `_last_lot_fill_code`：同一 code 只填一次（唔覆蓋用戶其後嘅手動輸入）；
        lot 未知時**唔設 flag**——目錄遲到（set_stock_catalog）仍可以補填。
        """
        code = self._order_code.text().strip()
        if not code or code == self._last_lot_fill_code:
            return
        lot = self._code_lot_sizes.get(code.upper()) or self._code_lot_sizes.get(code)
        if not lot:
            return   # 未知 lot → 唔填、唔設 flag（等目錄載入後補）
        self._order_qty.blockSignals(True)
        try:
            self._order_qty.setText(str(lot))
        finally:
            self._order_qty.blockSignals(False)
        self._last_lot_fill_code = code
        self._refresh_total_label()

    def _schedule_symbol_emit(self) -> None:
        """Commit 34：排程反向同步 emit（600ms singleShot debounce）。"""
        self._symbol_debounce.start()

    def _emit_symbol_if_valid(self) -> None:
        """Debounce timeout → 驗證 + emit `code_changed`（反向同步去 K 綫視窗）。

        規則：空 / 無「.」→ skip；目錄已載入但 code 唔喺目錄 → skip（唔切圖表去唔存在嘅標的）；
        同上次 emit 一樣 → skip（防 K 綫 ↔ 下單同步 loop）。Emit canonical uppercase。
        """
        code = self._order_code.text().strip()
        if not code or "." not in code:
            return
        upper = code.upper()
        if self._code_names and upper not in self._code_names:
            return   # 目錄已載入但未知標的 → 唔 emit
        if upper == self._last_emitted_code:
            return
        self._last_emitted_code = upper
        self.code_changed.emit(upper)

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
        self._refresh_total_label()   # Commit 33：市價驅動 → 合計金額同步更新（signal 被 block，手動補）

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
        """價格變動 → 自適應 stepper 步長（10^(floor(log10(p))−2)）+ 合計金額刷新。"""
        self._order_price.setSingleStep(_price_step(value))
        self._refresh_total_label()   # Commit 33：qty × price live

    # ------------------------------------------------------------- engine signal handlers（GUI thread）

    def _on_accounts(self, accounts: tuple[AccountInfo, ...]) -> None:
        """帳戶 snapshot → 按 env tab 重繪卡片（只 ACTIVE；非 ACTIVE 隱藏；先清舊卡防殘留）。

        Commit 33：存全量 `self._all_accounts`（匹配用，含非 ACTIVE——匹配函數自己過濾）+ 重新匹配。
        """
        self._all_accounts = list(accounts)
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
        self._refresh_matched_account()   # Commit 33：帳戶列表更新 → 重新匹配下單帳戶

    def _on_positions(self, rows: tuple[PositionRow, ...]) -> None:
        """持倉 snapshot → table 重繪（字段同富途 APP 對齊；Commit 31：帳戶卡撳選過濾）。

        Commit 34：加「操作」欄——per-row「平倉」按鈕（qty != 0 先 enabled）；存當前顯示行供回調。
        """
        self._last_positions = rows
        if self._selected_acc is not None:   # 已選帳戶 → 只顯示該帳戶持倉
            env, acc_id = self._selected_acc
            rows = tuple(r for r in rows if (r.trd_env, r.acc_id) == (env, acc_id))
        self._displayed_positions = rows     # Commit 34：per-row「平倉」按鈕回調用呢份（已過濾）
        table = self._pos_table
        # Commit 34：重繪前清理舊 per-row 按鈕（setCellWidget widget 唔會隨 setRowCount shrink 自動刪除）
        for b in self._pos_row_btns:
            b.deleteLater()
        self._pos_row_btns.clear()
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
            # Commit 34：「操作」欄——per-row「平倉」按鈕（qty==0 → disabled）
            btn = QPushButton("平倉")
            btn.setEnabled(row.qty != 0)
            # clicked 雙 overload + slot 帶必填參數 → lambda 包（AGENTS.md #4）
            btn.clicked.connect(lambda _=False, r=row: self._on_close_row(r))
            table.setCellWidget(r, 12, btn)
            self._pos_row_btns.append(btn)

    def _on_account_funds(self, acc_id: int, trd_env: str, funds: FundsSnapshot) -> None:
        """Per-account 資金事件 → 卡片「總資產」+ 該 env tab 加總（GUI 端 per-env fold，重用 engine._sum_funds）。"""
        self._funds_by_acc[(trd_env, acc_id)] = funds   # 累積；失敗帳戶保留上次值
        m = self._matched_acc
        if m is not None and (m.trd_env, m.acc_id) == (trd_env, acc_id):
            self._refresh_matched_account()   # Commit 33：匹配帳戶資金到 → 下單 form「帳戶」label 餘額同步
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
        """今日訂單 snapshot → table 重繪（Commit 33：11 欄全細節；狀態格上色：已成綠 / 失敗・撤單紅 / pending 黃）。

        Commit 34：加「操作」欄——per-row「撤單」按鈕（只可撤狀態先 enabled）+ 存當前顯示行。
        """
        acc_card = {a.acc_id: a.card_num for a in self._all_accounts}   # Commit 33：帳戶欄（卡號末四位）
        table = self._orders_table
        # Commit 34：重繪前清理舊 per-row 按鈕（setCellWidget widget 唔會隨 setRowCount shrink 自動刪除）
        for b in self._ord_row_btns:
            b.deleteLater()
        self._ord_row_btns.clear()
        table.setRowCount(len(rows))
        self._displayed_orders = rows   # Commit 34：per-row「撤單」按鈕回調用呢份
        for r, row in enumerate(rows):
            t = row.create_time or "—"
            card = acc_card.get(row.acc_id)
            acc_text = f"…{card[-4:]}" if card and card != "N/A" else (str(row.acc_id) if row.acc_id else "—")
            values = [
                row.order_id or "—",
                row.code, _SIDE_ZH.get(row.side, row.side or "—"),
                row.order_type or "—", _order_status_zh(row.status),
                f"{row.qty:g}", _fmt_money(row.price),
                f"{row.dealt_qty:g}", _fmt_money(row.dealt_avg_price),
                t[-8:] if len(t) >= 8 else t,   # HH:MM:SS（SDK 格式 'YYYY-MM-DD HH:MM:SS'）
                acc_text,
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
            # Commit 34：「操作」欄——per-row「撤單」按鈕（無 order_id / 已成 / 失敗 / 已撤 → disabled）
            cancellable = bool(row.order_id) and row.status not in _STATUS_GREEN \
                and row.status not in _STATUS_RED
            btn = QPushButton("撤單")
            btn.setEnabled(cancellable)
            # clicked 雙 overload + slot 帶必填參數 → lambda 包（AGENTS.md #4）
            btn.clicked.connect(lambda _=False, r=row: self._on_cancel_row(r))
            table.setCellWidget(r, 11, btn)
            self._ord_row_btns.append(btn)

    def _on_action_done(self, ok: bool, message: str) -> None:
        """Commit 34：下單/撤單結果統一 handler（order_result + cancel_result 共用）。

        status label 更新 → 釋放 action busy flag → queue 仍有 pending 即直接派下一筆；
        queue drain 先按 PIN/mode 恢復按鈕狀態。每次 dispatch 恰好 emit 一個 result signal → 配對永遠成立。
        """
        self._set_status(message, _OK_COLOR if ok else _ERR_COLOR)
        self._action_busy = False
        if self._action_queue:   # 仍有 queued action → 保持按鈕 disabled、直接派下一筆
            self._pump_actions()
        else:
            self._apply_pin_state()   # queue drain → 按 PIN/mode 恢復按鈕狀態（Commit 33）

    def _set_status(self, message: str, color: str) -> None:
        """Commit 34：成功/錯誤 status label 高對比當眼（深底 + 邊框 + 大字）；中性訊息保持原樣。"""
        self._status_label.setText(message)
        if color == _OK_COLOR:   # 成功：深綠底 + 綠邊框 + 亮綠字
            self._status_label.setStyleSheet(
                "background: #0B3D2E; border: 1px solid #089981; color: #69F0AE;"
                " font-size: 15px; font-weight: bold; padding: 6px 10px;")
        elif color == _ERR_COLOR:   # 錯誤：深紅底 + 紅邊框 + 亮紅字
            self._status_label.setStyleSheet(
                "background: #4A1420; border: 1px solid #F23645; color: #FF8A80;"
                " font-size: 15px; font-weight: bold; padding: 6px 10px;")
        else:   # 中性（連線狀態等）：只改字色
            self._status_label.setStyleSheet(f"color: {color};")

    # ------------------------------------------------------------- 下單流程（GUI thread）

    def _on_place_order(self, side_str: str) -> None:
        """買賣特大按鍵直接執行（Commit 33）→ GUI 驗證 → engine.place_order（worker thread 做阻塞 RPC）。

        `side_str` = "BUY" / "SELL"；dispatch 帶 `trd_env=self._mode` + `acc_id=匹配帳戶`；
        PIN 只喺實盤傳（模擬盤無需交易密碼——futu 規則）。in-flight guard：兩按同時禁用。
        """
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
        side = TrdSide.BUY if side_str == "BUY" else TrdSide.SELL
        # Commit 33：實盤需 PIN 解鎖（模擬盤恆解鎖）；匹配帳戶必須存在先可下單
        pin: str | None = None
        if self._mode == "REAL":
            if self._pin_holder is None:
                self._set_status("實盤未解鎖——請輸入六位數 PIN", _ERR_COLOR)
                return
            pin = self._pin_holder.value
        acc = self._matched_acc
        env_zh = "實盤" if self._mode == "REAL" else "模擬盤"
        if acc is None:
            self._set_status(f"無匹配{env_zh}帳戶——無法下單（檢查帳戶狀態/市場授權）", _ERR_COLOR)
            return
        # Commit 34：lot size 驗證——數量必須係每手單位嘅整數倍（目錄已知 lot 先查）
        lot = self._code_lot_sizes.get(code.upper()) or self._code_lot_sizes.get(code)
        if lot and qty % int(lot) != 0:
            self._set_status(f"數量必須係 {lot} 嘅整數倍（每手單位）", _ERR_COLOR)
            return
        # Commit 34：二次確認（checkbox opt-in、默認開啟）——彈出訂單內容摘要先落單
        if self._confirm_cb.isChecked():
            name = self._code_names.get(code.upper()) or self._code_names.get(code) or ""
            detail = (f"方向：{'買入' if side_str == 'BUY' else '賣出'}\n"
                      f"標的：{code}{'  ' + name if name else ''}\n"
                      f"模式：{env_zh}\n"
                      f"帳戶：…{str(acc.acc_id)[-4:]}\n"
                      f"價格 × 數量：{_fmt_money(price)} × {qty:g}\n"
                      f"合計金額：{_fmt_money(price * qty)}")
            ans = QMessageBox.question(
                self, "下單二次確認", f"確認落以下訂單？\n\n{detail}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ans != QMessageBox.StandardButton.Yes:
                self._set_status("已取消下單（二次確認）", _WARN_COLOR)
                return
        # Commit 34：enqueue 串行執行（取代直接 dispatch——多筆操作逐筆等 result 先派下一筆）
        self._enqueue_action(
            lambda: self._engine.place_order(code, side, price, qty, pin=pin, trd_env=self._mode, acc_id=acc.acc_id))

    # ------------------------------------------------------------- Commit 34：action queue + per-row 操作（撤單/平倉）

    def _enqueue_action(self, action) -> None:
        """Commit 34：action 入執行隊列（串行化——同一時間只有一筆 in-flight）。"""
        self._action_queue.append(action)
        # 有 pending action → 買賣按鍵保持 disabled（queue drain 後 _apply_pin_state 恢復）
        self._buy_btn.setEnabled(False)
        self._sell_btn.setEnabled(False)
        self._pump_actions()

    def _pump_actions(self) -> None:
        """Commit 34：idle 且 queue 非空 → dispatch 隊首 action（set busy flag）。"""
        if self._action_busy or not self._action_queue:
            return
        self._action_busy = True
        self._action_queue.pop(0)()

    def _on_cancel_row(self, row: OrderRow) -> None:
        """Commit 34：per-row「撤單」→ 二次確認訂單內容 → engine.cancel_order（REAL-only polling）。"""
        if not row.order_id:
            self._set_status("該訂單無 order_id——無法撤單", _ERR_COLOR)
            return
        detail = (f"訂單號：{row.order_id}\n"
                  f"標的：{row.code}\n"
                  f"方向：{_SIDE_ZH.get(row.side, row.side or '—')}\n"
                  f"狀態：{_order_status_zh(row.status)}\n"
                  f"數量 × 價格：{row.qty:g} × {_fmt_money(row.price)}")
        ans = QMessageBox.question(
            self, "撤單二次確認", f"確認撤銷以下訂單？\n\n{detail}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if ans != QMessageBox.StandardButton.Yes:
            self._set_status("已取消撤單（二次確認）", _WARN_COLOR)
            return
        self._enqueue_action(
            lambda: self._engine.cancel_order(row.order_id, row.code, trd_env="REAL", acc_id=row.acc_id or None))

    def _on_cancel_all(self) -> None:
        """Commit 34：「全部撤單」→ 二次確認（列出可撤訂單數）→ 逐筆 enqueue（串行）。"""
        cancellable = [r for r in self._displayed_orders
                       if r.order_id and r.status not in _STATUS_GREEN and r.status not in _STATUS_RED]
        if not cancellable:
            self._set_status("冇可撤銷嘅訂單", _WARN_COLOR)
            return
        ans = QMessageBox.question(
            self, "全部撤單二次確認", f"確認撤銷以下 {len(cancellable)} 筆訂單？\n\n"
                                      + "\n".join(f"{r.order_id}  {r.code}" for r in cancellable),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if ans != QMessageBox.StandardButton.Yes:
            self._set_status("已取消全部撤單（二次確認）", _WARN_COLOR)
            return
        for row in cancellable:   # 逐筆 enqueue——queue 串行保證逐筆等 result
            self._enqueue_action(
                lambda r=row: self._engine.cancel_order(r.order_id, r.code, trd_env="REAL", acc_id=r.acc_id or None))

    def _on_close_row(self, row: PositionRow) -> None:
        """Commit 34：per-row「平倉」→ PIN gate（實盤先查）→ 二次確認 → 市價反向單。

        平倉 = 對該持倉行**同一帳戶/環境**落市價反向單：qty>0 → SELL、qty<0 → BUY_BACK；
        qty = int(round(abs(qty)))。PIN 檢查喺 confirm dialog **之前**（未解鎖唔好彈確認框）。
        """
        if row.qty == 0:
            self._set_status("該持倉數量為 0——無需平倉", _WARN_COLOR)
            return
        pin: str | None = None
        if row.trd_env == "REAL":   # Commit 34：實盤持倉先要 PIN（模擬盤免）
            if self._pin_holder is None:
                self._set_status("實盤未解鎖——請輸入六位數 PIN", _ERR_COLOR)
                return
            pin = self._pin_holder.value
        side = TrdSide.SELL if row.qty > 0 else TrdSide.BUY_BACK
        qty = int(round(abs(row.qty)))
        env_zh = "實盤" if row.trd_env == "REAL" else "模擬盤"
        detail = (f"標的：{row.code} {row.name}\n"
                  f"帳戶：…{str(row.acc_id)[-4:]}（{env_zh}）\n"
                  f"平倉方向：{'賣出' if side is TrdSide.SELL else '買回'}\n"
                  f"數量：{qty:g}\n"
                  f"方式：市價單")
        ans = QMessageBox.question(
            self, "平倉二次確認", f"確認以市價平倉以下持倉？\n\n{detail}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if ans != QMessageBox.StandardButton.Yes:
            self._set_status("已取消平倉（二次確認）", _WARN_COLOR)
            return
        self._enqueue_action(
            lambda: self._engine.place_order(row.code, side, 0.0, qty, pin=pin,
                                             trd_env=row.trd_env, acc_id=row.acc_id or None, market=True))

    def _on_close_all(self) -> None:
        """Commit 34：「全部平倉」→ PIN gate（有任何實盤持倉先查）→ 二次確認 → 逐筆 enqueue。"""
        closable = [r for r in self._displayed_positions if r.qty != 0]
        if not closable:
            self._set_status("冇可平倉嘅持倉", _WARN_COLOR)
            return
        pin: str | None = None
        has_real = any(r.trd_env == "REAL" for r in closable)
        if has_real:   # 有任何實盤持倉 → 先查 PIN（未解鎖唔好彈確認框）
            if self._pin_holder is None:
                self._set_status("實盤未解鎖——請輸入六位數 PIN", _ERR_COLOR)
                return
            pin = self._pin_holder.value
        ans = QMessageBox.question(
            self, "全部平倉二次確認", f"確認以市價平倉以下 {len(closable)} 筆持倉？\n\n"
                                      + "\n".join(f"{r.code} {r.name}（{r.qty:+g}）" for r in closable),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if ans != QMessageBox.StandardButton.Yes:
            self._set_status("已取消全部平倉（二次確認）", _WARN_COLOR)
            return
        for row in closable:   # 逐筆 enqueue——queue 串行保證逐筆等 result
            side = TrdSide.SELL if row.qty > 0 else TrdSide.BUY_BACK
            qty = int(round(abs(row.qty)))
            self._enqueue_action(
                lambda r=row, s=side, q=qty: self._engine.place_order(
                    r.code, s, 0.0, q, pin=pin, trd_env=r.trd_env, acc_id=r.acc_id or None, market=True))

    # ------------------------------------------------------------- lifecycle

    def shutdown(self) -> None:
        """Clean shutdown：停 countdown/debounce timers + engine.stop()（idempotent）。"""
        self._countdown_timer.stop()
        self._symbol_debounce.stop()   # Commit 34：反向同步 debounce timer
        self._engine.stop()
