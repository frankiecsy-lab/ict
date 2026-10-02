"""ICT Trader 入口：Config → QApplication + 雙視窗（K 線 + 下單）→ event loop。

- Config.from_env() 失敗（例如未知 KLINE_TYPE）→ 報錯並 exit(1)，唔開窗口；
  windowed build（無 console，sys.stdout is None）改用 QMessageBox 彈出。
- SIGINT（Ctrl+C）→ 排程 app.quit()，行完 event loop 先 clean shutdown。
- 雙視窗默認 windowed（非全屏、可各自拖去不同螢幕）；K 線視窗 F11 切換全屏幕。
- exec() 返回後 finally 兩個視窗都 shutdown()：close OpenD contexts + join threads。
"""
from __future__ import annotations

import logging
import signal
import sys

from dataclasses import replace as _replace_cfg

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from config import Config
from ui.main_window import MainWindow
from ui.order_window import OrderWindow


def _report_config_error(message: str) -> None:
    """配置錯誤回報：有 console → stderr；windowed build（無 console）→ 彈出對話框。"""
    if getattr(sys, "frozen", False) and sys.stdout is None:
        from PySide6.QtWidgets import QMessageBox

        app = QApplication.instance() or QApplication([])
        QMessageBox.critical(None, "ICT Trader 配置錯誤", message)
    else:
        print(f"配置錯誤：{message}", file=sys.stderr)


def main() -> int:
    try:
        cfg = Config.from_env()
    except ValueError as exc:
        _report_config_error(str(exc))
        return 1

    logging.basicConfig(
        level=logging.DEBUG if cfg.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = QApplication(sys.argv)
    # 雙視窗默認 windowed（非全屏）——各自可拖去不同螢幕；K 線視窗 F11 仍可切全屏幕。
    window = MainWindow(cfg)
    order_window = OrderWindow(cfg)
    # 跨視窗同步：K 綫標的切換 → 下單代碼；最新收市價 → 跟隨市價（auto-queue 跨 thread）
    window.code_changed.connect(order_window.set_symbol)
    window.last_price.connect(order_window.follow_price)
    window.catalog_ready.connect(order_window.set_stock_catalog)   # Commit 31：股票目錄 → 下單代碼補全/驗證
    order_window.code_changed.connect(window.switch_symbol)   # Commit 34：反向同步——下單標的 → K 綫圖
    order_window.set_symbol(window.code_edit.text())   # 初始同步一次（UI-state restored code）

    # Commit 35 R6：全局主題同步——MainWindow toggle → OrderWindow；啟動時用還原後嘅主題（UI state）同步一次
    window.theme_changed.connect(order_window.set_theme)
    order_window.set_theme(window.current_theme())

    def _on_endpoints_changed(payload):
        """Commit 35 R8：OpenD 端點變更（OrderWindow 已寫 .env）→ 選擇性重啟受影響 engine。

        用 payload 對照當前 cfg（唔重新 from_env()——load_dotenv(override=False) 令程序環境變數
        優先於 .env，重讀未必反映剛儲存嘅值；payload = 用戶實際輸入、確定性最高）。
        """
        nonlocal cfg
        if not isinstance(payload, dict):
            return
        quote = tuple(payload.get("quote", ()))
        trade = tuple(payload.get("trade", ()))
        q_changed = len(quote) == 2 and (cfg.quote_host, cfg.quote_port) != (str(quote[0]), int(quote[1]))
        t_changed = len(trade) == 2 and (cfg.trade_host, cfg.trade_port) != (str(trade[0]), int(trade[1]))
        if not (q_changed or t_changed):
            return
        new_cfg = _replace_cfg(
            cfg,
            quote_host=str(quote[0]) if q_changed else cfg.quote_host,
            quote_port=int(quote[1]) if q_changed else cfg.quote_port,
            trade_host=str(trade[0]) if t_changed else cfg.trade_host,
            trade_port=int(trade[1]) if t_changed else cfg.trade_port,
        )
        cfg = new_cfg   # 更新對照基準（下次變更比較用）
        if q_changed:
            window.reconnect(new_cfg)      # FutuEngine restart（保留 periods/code/smt UI 狀態）
        if t_changed:
            order_window.reconnect(new_cfg)   # TradeEngine restart

    order_window.endpoints_changed.connect(_on_endpoints_changed)

    window.show()
    order_window.show()

    def _sigint_handler(signum, frame):  # noqa: ARG001 — signal handler signature
        # Ctrl+C：排程去 GUI event loop quit（唔好喺 signal context 直接做重活）
        QTimer.singleShot(0, app.quit)

    signal.signal(signal.SIGINT, _sigint_handler)

    try:
        return app.exec()
    finally:
        window.shutdown()
        order_window.shutdown()


if __name__ == "__main__":
    sys.exit(main())
