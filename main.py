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
    order_window.set_symbol(window.code_edit.text())   # 初始同步一次（UI-state restored code）
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
