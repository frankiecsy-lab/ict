# CHANGELOG

## [Unreleased] Step 1（2026-09-29）

### Added
- 專案初始化：`.gitignore`、`AGENTS.md` 工作流規範、富途 API 參考文檔。
- `config.py`：frozen dataclass 設定模組，經 `.env` + 程序環境變數讀取（程序環境變數優先）；K 線週期校驗（未知 `KLINE_TYPE` 啟動即報錯）、蠟燭顏色慣例 HK/INTL + 手動色值 override、深色主題配色。
- `conftest.py`：令 pytest 將專案根目錄加入 sys.path。
- `tests/test_config.py`：11 項 hermetic 單測（monkeypatch 清空全部環境變數，唔受真實 `.env` 影響），全過。
- 安裝 PySide6 6.11.2 並 pin `>=6.7,<6.12`；`pip freeze > requirements.txt` 同步完整依賴清單（futu_api==10.5.6508、pandas==3.0.2、numpy==1.26.4…）。

### Next
- Commit 2：蠟燭聚合引擎 + 時間工具（`engine/timeutil.py`、`engine/candle_aggregator.py` + 單測）
- Commit 3：富途行情引擎（`engine/futu_engine.py`，`on_recv_rsp` 實時回調）
- Commit 4：全屏幕深色主題蠟燭圖表 UI（`ui/`）
- Commit 5：`main.py` 整合 + `.env.example` + live smoke test
