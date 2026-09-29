# ICT TRADER

跨平台（Windows 11 / Ubuntu）全屏幕 K 線終端，基於 Inner Circle Trader (ICT) 方法論。Step 1 目標：透過本地富途 OpenD（`futu-api`）取得歷史 K 線，並用**實時報價回調**（subclass `StockQuoteHandlerBase`、覆蓋 `on_recv_rsp(self, rsp_pb)`）驅動當前蠟燭即時更新——唔係 polling、唔係 K 線 push。

## 📍 最新進度 / 發佈日誌

| 日期 | 階段 | 更新摘要 |
|---|---|---|
| 2026-09-30 | Step 1 · Commit 5（**Step 1 完成**） | 新增 `main.py` 入口：`Config.from_env()`（未知 KLINE_TYPE → stderr 報錯 exit(1)）→ QApplication + MainWindow `showFullScreen()`；SIGINT（Ctrl+C）排程 `app.quit()` 行完 event loop 先收；`exec()` 返回後 finally `window.shutdown()` clean stop。新增 `.env.example` 配置範本。**Live smoke test 實測通過**：offscreen 連真 OpenD → `history_ready` 300 根（夜期數據至 2026-09-30 03:00）→ QUOTE 訂閱成功 → close 乾淨斷線。全套 **136 passed** |
| 2026-09-30 | Step 1 · Commit 4 | 新增全屏幕深色主題蠟燭圖表 UI：`ui/candle_chart.py`（純 QPainter、零第三方圖表庫——蠟燭 + volume subpane + nice-step grid/右軸 price label + last-price dashed line 同右軸 tag + crosshair OHLCV readout；backpressure = immutable snapshot + singleShot `QTimer(30ms)` coalesce repaint，tick burst 最多 ~30fps；`add_overlay()` 預留 ICT FVG / Order Block / Kill Zone 擴展點）+ `ui/main_window.py`（F11 全屏幕切換 / Esc 關閉、engine signal → chart 接線、深色主題跟 `.env` 配色）。20 項新單測全過（全套 **136 passed**）。剩餘：main.py 整合 |
| 2026-09-30 | Step 1 · Commit 3 | 新增富途行情引擎 `engine/futu_engine.py`：OpenD setup daemon thread + `request_history_kline` 明確窗口分頁 seed + QUOTE 訂閱 `_QuoteHandler.on_recv_rsp` 實時回調聚合（pyqtSignal 跨線程 immutable snapshot）；`timeutil` 加 `parse_time_only` / `resolve_tick_datetime`（time-only tick 補 date）/ `history_window`。55 項新單測全過（全套 **116 passed**）。剩餘：全屏幕圖表 UI → main.py 整合 |
| 2026-09-29 | Step 1 · Commit 2 | 新增蠟燭聚合引擎：`engine/timeutil.py`（naive parse + 週期 floor + bar key，時區鐵律）+ `engine/candle_aggregator.py`（tick→K 線聚合：OHLC 更新、volume delta、日 rollover reset、out-of-order guard）；50 項新單測全過（全套 61 passed）。剩餘：富途行情引擎 → 全屏幕圖表 UI → main.py 整合 |
| 2026-09-29 | Step 1 · Commit 1 | 專案初始化：`config.py` 設定模組（frozen dataclass + `.env` 唯一事實來源，11 項單測全過）；安裝並 pin PySide6 6.11.2；`requirements.txt` 經 `pip freeze` 同步。剩餘：蠟燭聚合引擎 → 富途行情引擎 → 全屏幕圖表 UI → main.py 整合 |

### Step 1 進度（✅ 全部完成）
- [x] Commit 1：`config.py` 設定模組（frozen dataclass + `.env`，11 項單測）
- [x] Commit 2：`engine/timeutil.py` + `engine/candle_aggregator.py`（tick→蠟燭聚合，純類單測）
- [x] Commit 3：`engine/futu_engine.py`（OpenD setup thread + pyqtSignal + `on_recv_rsp` 回調；27 項 mock 單測）
- [x] Commit 4：`ui/main_window.py` + `ui/candle_chart.py`（全屏幕深色主題蠟燭圖、volume subpane、crosshair、overlay hook）
- [x] Commit 5：`main.py` 入口 + `.env.example` + live smoke test

### 下一步（Step 2 候選，未定範圍）
- ICT 指標 overlay：經 `CandleChart.add_overlay()` 加 FVG / Order Block / Kill Zone 圖層

## Features（Step 1 目標）

- **全屏幕終端**：PySide6/Qt6 全屏幕窗口，F11 切換全屏幕，Esc 關閉。
- **富途 K 線資料源**：本地 OpenD（預設 `127.0.0.1:11111`），預設標的 `HK.HSImain`（恒指期貨主連），預設週期 1 分鐘，歷史深度預設 300 根。
- **實時報價回調更新**：訂閱 QUOTE → `_QuoteHandler(StockQuoteHandlerBase).on_recv_rsp()`；tick 即時聚合入當前蠟燭（close=最新價、high/low=max/min、volume=日累計成交量 delta）。
- **紅漲綠跌（港股慣例）**：`.env` 可切 `CONVENTION=INTL`（綠漲紅跌）或用 `COLOR_UP` / `COLOR_DOWN` 手動 override。
- **深色主題圖表**：蠟燭 + last-price dashed line 同右軸 tag + OHLCV readout + volume subpane + crosshair。
- **Overlay 擴展點**：`CandleChart.add_overlay()` 預留俾日後 ICT FVG / Order Block / Kill Zone 圖層（Step 1 零 overlay）。

## Architecture

### 文件結構

```
D:\coding\ICT_v1\
├─ main.py                     # ✅ entry：Config → QApplication + MainWindow(showFullScreen)；SIGINT 排程 quit；finally clean shutdown
├─ config.py                   # ✅ frozen dataclass Config.from_env()，純 stdlib+dotenv，無 Qt/futu import
├─ engine\                     # ✅ timeutil / candle_aggregator（純類）/ futu_engine（QObject：OpenD 連線 + seed + QUOTE 回調聚合）
├─ ui\                         # ✅ main_window / candle_chart（純 QPainter；backpressure coalesce repaint；add_overlay 擴展點）
├─ tests\                      # test_config.py ✅；test_timeutil.py ✅；test_aggregator.py ✅；test_futu_engine.py ✅（mock ctx，零真實連線）；test_candle_chart.py ✅（20 項純 layout 函數單測，零 Qt app 依賴）
├─ .env                        # gitignored；唯一事實來源（host/port/標的/週期/convention）
├─ .env.example                # ✅ commit 嘅配置文檔（複製做 .env）
└─ requirements.txt            # pip freeze 輸出（PySide6==6.11.2、futu_api==10.5.6508…）
```

### Threading & Signal 模型

- futu-api **每個 context 只有一條 callback thread** → `on_recv_rsp` 必須快，唔好做重活/阻塞。
- `request_history_kline` 係同步阻塞 → 放獨立 setup daemon thread（唔係 GUI thread）。
- **聚合喺 callback thread 做**；GUI 只負責 render。跨線程傳 **immutable tuple-of-tuples snapshot**（bar = `(time_key, open, high, low, close, volume)`），經 `pyqtSignal` queued 過 GUI——無共享可變狀態、無鎖。
- **Backpressure**：chart widget 用 dirty flag + singleShot `QTimer(30ms)` coalesce repaint → tick burst 都最多 ~30fps redraw，永遠 render 最新 snapshot。

### 歷史 K 線取得（實測驗證行為）

- **必須明確窗口**：`request_history_kline` 唔帶 start/end 對 HK.HSImain 會返回一年前舊數據 → `history_window()` 用 now() 計算保守窗口（覆蓋夜期 ~834 min/日）。
- **返回頭 N 根而非最近 N 根**：window + max_count 返回時間序頭 N 根 → `page_req_key` 分頁攞晒（1000 根/頁）再 tail `history_count` 根。
- **按欄位名提取**：DataFrame 欄位順序係 open/close/high/low（唔係 OHLC）→ 一律 `df[["time_key","open","high","low","close","volume"]]`。
- **Live tick data_time 係 time-only**（'HH:mm:ss.SSS'，無日期）→ `resolve_tick_datetime()` 補 date = max(anchor, today)；anchor = seed 最後一根 bar 嘅日期（處理夜期跨午夜 + clock skew）。

### 時區鐵律

Quote `data_time` 同 kline `time_key` 對 HK.HSImain 都係 **HKT naive string** → parse naive、floor 到週期邊界、**永遠唔好 astimezone / 加 tzinfo**。呢個係 live bar key 同歷史 bar key 對得上嘅前提。

已知近似：期貨夜期嘅「交易日」界線未必等於日曆午夜，rollover volume reset 係合理近似（跨界嗰根 bar volume 可能微差）。

## Tech Stack

- Python 3.12（Windows 11 / Ubuntu；純 Python + Qt6，無平台特定代碼）
- PySide6（Qt6，LGPL）——pin `>=6.7,<6.12`，現裝 6.11.2
- futu-api ≥ 10.4.6408（現裝 10.5.6508）
- python-dotenv —— `.env` 讀取
- pytest —— 單測

## How to Run

```bash
python -m pip install -r requirements.txt
copy .env.example .env    # Windows；Ubuntu: cp .env.example .env
# 按下方表格填 FUTU_OPEND_HOST / FUTU_OPEND_PORT 等（全部可選，預設已可用）
python main.py            # 全屏幕啟動；F11 切換全屏幕、Esc 關閉、Ctrl+C clean exit
```

> 前提：本地富途 OpenD 已開（預設 `127.0.0.1:11111`）。連唔到時窗口會照開，status bar 顯示錯誤訊息。

## Tests

```bash
python -m pytest tests/ -q
```

## .env 配置鍵

| Key | 預設值 | 說明 |
|---|---|---|
| `FUTU_OPEND_HOST` | `127.0.0.1` | OpenD 主機 |
| `FUTU_OPEND_PORT` | `11111` | OpenD 端口 |
| `TRADING_CODE` | `HK.HSImain` | 交易標的（富途代碼格式） |
| `KLINE_TYPE` | `K_1M` | K 線週期：`K_1M/K_3M/K_5M/K_15M/K_30M/K_60M/K_DAY/K_WEEK/K_MON`；未知值啟動時報錯 |
| `HISTORY_COUNT` | `300` | 歷史 K 線根數（≥1） |
| `VISIBLE_BARS` | `120` | 圖表右 pin 顯示嘅蠟燭數（≥1） |
| `CONVENTION` | `HK` | 蠟燭顏色慣例：`HK`=紅漲綠跌 / `INTL`=綠漲紅跌；未知值回落 HK |
| `COLOR_UP` / `COLOR_DOWN` | （空=跟隨慣例） | 手動 override 色值，如 `#FF4D4F` |
| `BG_COLOR` / `GRID_COLOR` / `TEXT_COLOR` / `AXIS_TEXT_COLOR` / `LAST_PRICE_COLOR` | 深色主題預設 | 圖表配色，可覆蓋 |
| `DEBUG` | `false` | tick log 等除錯輸出（`1/true/yes/on` 為真） |

> 已存在嘅程序環境變數優先於 `.env` 檔案（`load_dotenv(override=False)`），方便測試與部署時臨時覆蓋。
