"""Offscreen smoke test：驗證 frozen / source 入口可正常啟動、渲染一幀、乾淨關閉。

用法（容器內或本機）：QT_QPA_PLATFORM=offscreen python scripts/smoke_test.py [timeout_sec]
- 連唔到 OpenD 係預期行為（只驗 UI 層 + config 載入），engine error signal 唔算失敗；
- exit 0 = 通過。
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from config import Config  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


def main() -> int:
    timeout = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0

    cfg = Config.from_env()
    print(f"[smoke] config OK: code={cfg.trading_code} kline={cfg.kline_type}")

    app = QApplication([])
    window = MainWindow(cfg)
    window.showFullScreen()

    # 處理事件 ~timeout：engine setup thread 會 fail-fast（冇 OpenD）→ error signal → status bar
    QTimer.singleShot(int(timeout * 1000), app.quit)
    rc = app.exec()
    print(f"[smoke] event loop exited (rc={rc})")

    window.shutdown()
    print("[smoke] shutdown OK — PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
