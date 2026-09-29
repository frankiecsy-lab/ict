"""ICT Trader 入口：Config → QApplication + MainWindow → event loop。

- Config.from_env() 失敗（例如未知 KLINE_TYPE）→ stderr 報錯並 exit(1)，唔開窗口。
- SIGINT（Ctrl+C）→ 排程 app.quit()，行完 event loop 先 clean shutdown。
- exec() 返回後 finally window.shutdown()：close OpenD context + join setup thread。
"""
from __future__ import annotations

import logging
import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from config import Config
from ui.main_window import MainWindow


def main() -> int:
    try:
        cfg = Config.from_env()
    except ValueError as exc:
        print(f"配置錯誤：{exc}", file=sys.stderr)
        return 1

    logging.basicConfig(
        level=logging.DEBUG if cfg.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = QApplication(sys.argv)
    window = MainWindow(cfg)
    window.showFullScreen()

    def _sigint_handler(signum, frame):  # noqa: ARG001 — signal handler signature
        # Ctrl+C：排程去 GUI event loop quit（唔好喺 signal context 直接做重活）
        QTimer.singleShot(0, app.quit)

    signal.signal(signal.SIGINT, _sigint_handler)

    try:
        return app.exec()
    finally:
        window.shutdown()


if __name__ == "__main__":
    sys.exit(main())
