# CHANGELOG

## [Unreleased] Step 1（2026-09-29）

### Added
- 專案初始化：`.gitignore`、`AGENTS.md` 工作流規範、富途 API 參考文檔。
- `config.py`：frozen dataclass 設定模組，經 `.env` + 程序環境變數讀取（程序環境變數優先）；K 線週期校驗（未知 `KLINE_TYPE` 啟動即報錯）、蠟燭顏色慣例 HK/INTL + 手動色值 override、深色主題配色。
- `conftest.py`：令 pytest 將專案根目錄加入 sys.path。
- `tests/test_config.py`：11 項 hermetic 單測（monkeypatch 清空全部環境變數，唔受真實 `.env` 影響），全過。
- 安裝 PySide6 6.11.2 並 pin `>=6.7,<6.12`；`pip freeze > requirements.txt` 同步完整依賴清單（futu_api==10.5.6508、pandas==3.0.2、numpy==1.26.4…）。
- `engine/timeutil.py`：純 stdlib 時間工具——`parse_market_time`（naive parse，兩種格式）、`floor_to_period`（intraday/日/週/月邊界取整）、`bar_key`（正規化 key）、`is_up`。時區鐵律：quote `data_time` 同 kline `time_key` 都係 HKT naive → 永遠唔好 astimezone，確保 live bar key 同歷史 bar key 對得上。
- `engine/candle_aggregator.py`：tick→K 線聚合純類（零 Qt/futu/pandas 依賴）——immutable Bar tuple、OHLC 更新（close=last_price、high/low=max/min）、volume 日累計 delta（`max(0, cum−上一筆)`，seed/rollover 後首筆記 0）、out-of-order guard + duplicate idempotent no-op、日 rollover volume reset；`bars()` 每次返回新 immutable snapshot 供 pyqtSignal 跨線程傳遞。
- `tests/test_timeutil.py`（24 項）+ `tests/test_aggregator.py`（26 項）：合成 tick 序列驗證 seed/OHLC/volume delta/rollover/out-of-order/duplicate/非法輸入/時區不變量/多週期 floor；全套 **61 passed**。
- （2026-09-30）`engine/futu_engine.py`：富途行情引擎（QObject 包裝）——`start()` spawn daemon setup thread 跑 `OpenQuoteContext` 連線 + `request_history_kline` 明確窗口分頁 seed（實測行為：no-window 返回舊數據、window+max_count 返回頭 N 根 → page_req_key 攞晒再 tail）；QUOTE 訂閱後 `_QuoteHandler(StockQuoteHandlerBase).on_recv_rsp()` 喺 callback thread parse tick → `CandleAggregator` 聚合 → emit immutable snapshot（`history_ready` / `bars_changed` / `status` / `error` pyqtSignal，auto-queue 去 GUI）；live tick time-only data_time 補 date = max(anchor, today)；`stop()` idempotent close + join。
- （2026-09-30）`engine/timeutil.py` 擴充：`parse_time_only`（'HH:mm:ss[.SSS]'）、`resolve_tick_datetime`（time-only 補 fallback date / 完整格式直傳）、`history_window`（明確 start/end 窗口，保守覆蓋夜期）。
- （2026-09-30）`tests/test_futu_engine.py`（27 項，mock OpenQuoteContext + 真 pandas DataFrame，零真實連線）+ `test_timeutil.py` 擴充 31 項：分頁/tail/NaN skip/page guard、tick 聚合（seed 更新/rollover/duplicate/out-of-order/NaN/garbage）、tick_date 三分支、_setup 編排、start/stop lifecycle；全套 **116 passed**。

### Next
- Commit 4：全屏幕深色主題蠟燭圖表 UI（`ui/`）
- Commit 5：`main.py` 整合 + `.env.example` + live smoke test
