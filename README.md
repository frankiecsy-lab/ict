# ICT TRADER

跨平台（Windows 11 / Ubuntu）全屏幕 K 線終端，基於 Inner Circle Trader (ICT) 方法論。Step 1 目標：透過本地富途 OpenD（`futu-api`）取得歷史 K 線，並用**實時報價回調**（subclass `StockQuoteHandlerBase`、覆蓋 `on_recv_rsp(self, rsp_pb)`）驅動當前蠟燭即時更新——唔係 polling、唔係 K 線 push。

## 📍 最新進度 / 發佈日誌

| 日期 | 階段 | 更新摘要 |
|---|---|---|
| 2026-09-30 | Step 2 · Commit 8 | **K 線圖 X/Y 軸縮放 + 手勢 + 左右平移**：`ui/candle_chart.py` 新增互動視圖狀態（X = (可見根數, 右偏移)——右偏移 0 = 右 pin 跟隨 live；Y = 手動價格範圍，None=auto-fit）+ 五個純函數（`visible_window`/`zoom_x`/`pan_x`/`zoom_y`/`pan_y`：游標錨定縮放、邊界 clamp、可獨立單測）。手勢：wheel = X 軸縮放（錨定游標，每 notch ×/÷1.25）、Ctrl/Shift+wheel = Y 軸縮放、左鍵拖曳 = 左右平移、右鍵拖曳 = 垂直平移、雙擊 = `reset_view()`；切換標的自動 reset。30 項新單測（全套 **252 passed**） |
| 2026-09-30 | Step 2 · Commit 7 | **歷史 K 線預設深度 300 → 1000 根**：`config.py` `history_count` dataclass default + `from_env()` fallback、`.env.example` `HISTORY_COUNT=1000` 同步更新；seed 分頁邏輯（page_req_key 1000 根/頁）天然支援——1000 根通常單頁即返。全套 **222 passed** |
| 2026-09-30 | Step 2 · Commit 6 | **輸入欄 onChange guard：代碼同名稱永唔會同時入欄**（live 使用發現：popup 開住撳 Enter，completer `setCompletion()` 會喺 `activated` signal **之前**將完整 display_text「code + 名稱」寫入 TEXT FIELD）：新增 `_on_code_text_changed()`（接 `textChanged`）——欄位一出現空白（= code + 名稱混入）即刻取第一 whitespace token 剝離返純 code，`blockSignals` 避免多餘 round-trip、無空白再觸發自然 no-op 唔死循環；任何路徑（手動輸入 / dropdown Enter / activated）下欄位都只持有純編號。移除 `_do_switch()` 嘅含空白拒絕門（guard 已確保欄位永遠無空白，變死代碼）。3 項新單測（全套 **222 passed**） |
| 2026-09-30 | Step 2 · Commit 5 | **輸入欄只收純編號 + 存在性驗證 + 獨立名稱 LABEL**：(1) `_do_switch()` 新增兩道門——含空白（混入股票名稱，例「HK.00700 騰訊」）即拒絕；目錄載入後經 `StockCatalog.canonical_code()` 驗證編號存在並正規化嚴格大小寫（`hk.00700` → `HK.00700`），未知編號 → status bar 報錯唔切換（唔會打到 OpenD）；目錄未載入時放行俾 engine/OpenD 最終校驗。(2) control bar 新增獨立 `QLabel` 名稱欄——經新純函數 `engine/stock_catalog.py::name_text()`（中文名 + 英文名，空欄位略過）顯示當前標的嘅中英文名，目錄載入 / dropdown 選中 / 手動切換時同步更新；**名稱永不入 TEXT FIELD**。12 項新單測（`test_main_window.py` offscreen Qt + fake engine、`name_text` ×4、`StockCompleter.catalog()` accessor）全套 **219 passed** |
| 2026-09-30 | Step 2 · Commit 4 | **輸入欄 TEXT FIELD 只留 code（名稱唔入輸入欄）**：dropdown popup 繼續顯示完整 `display_text`（code + 中英文名），選中後經新增純函數 `ui/stock_completer.py::code_from_completion()` 還原嚴格大小寫 canonical code——mapping hit → canonical、miss → 取 display_text 第一 whitespace token（code 永遠係第一 token）兜底；`_on_code_activated` 一律 `setText(code)` 強制覆蓋，確保任何路徑下輸入欄都只出現 code。實測發現 QStandardItem 喺呢個 PySide6/Qt 版本 **Display/Edit role 耦合**（設 EditRole 會連帶改 DisplayRole）→ 無法用雙 role 分開 dropdown 顯示同輸入欄字串，故改用 handler 強制覆蓋方案。2 項新單測（全套 **207 passed**） |
| 2026-09-30 | Step 2 · Commit 3 | **K 線週期按鍵組 + volume 矩形 + seed 擴充**：(1) K 線週期由 QComboBox 換做 checkable QPushButton group（QButtonGroup exclusive，`:checked` 用 `cfg.last_price_color` 背景 + bold），`current_period()` / `_do_switch()` 一次傳齊 code+period → `engine.switch()`；(2) volume subpane 由細線改成同蠟燭 body 一樣寬嘅填充矩形（`body_w = slot * 0.7`，紅漲綠跌跟 config）；(3) `_SEED_ENTRIES` 擴充至三隻 HK 指數期貨主連（HSImain/HHImain/MHImain），`_CODE_ALIASES` 加對應 upper→canonical 映射。全套 **205 passed** |
| 2026-09-30 | Step 2 · Commit 2 | **股票編號模糊輸入自動補全**（中英文名 + 簡體/繁體）：新增 `engine/stock_catalog.py`——`StockEntry(code, name_cn, name_en)` + `StockCatalog.search()` rank-based 兩段評分（code 精確 → suffix → prefix → 英文名 → 中文名（OpenCC t2s 簡繁正規化）→ substring → difflib typo fuzzy ≥0.8，query 每 keystroke 轉簡體、entry 名 index build 時預計算）；`engine/futu_engine.py::_fetch_catalog()` 經 `get_stock_basicinfo` fetch HK+US（per-market try/except + dedup），**live 實測 API 冇 `english_name` 欄位同唔含主力連續合約** → `_SEED_ENTRIES` seed 補返 `HK.HSImain`；subscribe 成功後 emit `catalog_ready`，mixed-case code 自動註冊入 `_CODE_ALIASES`；新增 `ui/stock_completer.py`（`StockCompleter`：UnfilteredPopupCompletion、matching 全委派 catalog）+ control bar 輸入欄 dropdown。Live smoke：HK 3798 / US 13111 隻；新單測（全套 **205 passed**） |
| 2026-09-30 | Step 2 · Fix | **主力連續合約代碼大小寫敏感 bug**（live 使用發現）：`switch()` 嘅 `.strip().upper()` 會將 `hk.hsimain` 變 `HK.HSIMAIN`，OpenD 拒收（「未知股票 HSIMAIN」）→ 新增 `_CODE_ALIASES` + `_normalize_code()`（upper 後映返正規形式），switch 路徑同啟動 `.env` code 路徑一致應用；5 項新單測（全套 **165 passed**） |
| 2026-09-30 | Step 2 · Commit 1 | **運行時切換標的與 K 線週期**：頂部 control bar（標的編號輸入欄 `HK.XXXXX`/`US.XXX` + 週期 combo，returnPressed / activated → `engine.switch()`）；engine 重構為 immutable `_State(agg, code, kline_type, anchor)` reference——switch worker thread 做 unsubscribe → fetch+seed → subscribe，**全部驗證通過先 atomic swap**，任何失敗 rollback（resubscribe 舊標的、圖表保持 live）；handler per-row code filter + emit 前 identity check 兜底 in-flight push；time-only tick fallback date 改用**市場時區**（zoneinfo：HK=Asia/Hong_Kong / US=America/New_York——美股喺 HKT 機上「今日」差一日）；`config.py` 公開 `KLINE_TYPES` + `kline_period_minutes()`。24 項新/改單測（全套 **160 passed**）+ live smoke：真 OpenD 實切 HK.HSImain K_1M → hk.00700 K_5M（小寫自動 normalize）成功、300 bars、乾淨斷線；實測發現 `unsubscribe()` 訂閱未滿 1 分鐘會失敗→已入 AGENTS.md 知識庫 |
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

### Step 2 進度（運行時切換 + 模糊自動補全）
- [x] Commit 1：control bar + `engine.switch()` / `_reconfigure()` / rollback + `_State` atomic swap + 市場時區 fallback date
- [x] Commit 2：股票目錄 fuzzy autocomplete（`stock_catalog.py` rank-based 搜尋 + OpenCC 簡繁轉換、`get_stock_basicinfo` fetch + seed、`StockCompleter` dropdown）
- [x] Commit 3：K 線週期按鍵組（checkable QButtonGroup exclusive）+ volume subpane 填充矩形 + `_SEED_ENTRIES` 擴充三隻 HK 指數期貨主連
- [x] Commit 4：輸入欄 TEXT FIELD 只留 code——dropdown 顯示完整 `display_text`，選中後經 `code_from_completion()` 還原 canonical code 強制覆蓋（QStandardItem Display/Edit role 耦合 → 無法雙 role）
- [x] Commit 5：輸入欄**只收純編號 + 存在性驗證**（含空白/名稱即拒絕；目錄載入後 `canonical_code()` 驗證存在 + 正規化大小寫，未知編號報錯唔切換）+ **獨立名稱 LABEL**（`name_text()` 顯示中英文名，名稱永不入輸入欄）
- [x] Commit 6：輸入欄 **onChange guard**——`textChanged` handler 即刻剝離「code + 名稱」返純 code（completer `setCompletion()` 喺 activated 前寫完整 display_text 嘅路徑），代碼同名稱永唔會同時入欄
- [x] Commit 7：歷史 K 線預設深度 **300 → 1000 根**（`config.py` default + `.env.example`）
- [x] Commit 8：**K 線圖 X/Y 軸縮放 + 手勢 + 左右平移**——互動視圖狀態（X=(可見根數,右偏移)、Y=手動範圍|auto-fit）+ 五個純函數 pan/zoom（游標錨定、邊界 clamp）；wheel/Ctrl+wheel/左鍵拖曳/右鍵拖曳/雙擊 reset

### 下一步（Step 2 後續候選，未定範圍）
- ICT 指標 overlay：經 `CandleChart.add_overlay()` 加 FVG / Order Block / Kill Zone 圖層
- 切換歷史記錄 / 多標的並排顯示（視需要）

## Features（Step 1 + Step 2）

- **全屏幕終端**：PySide6/Qt6 全屏幕窗口，F11 切換全屏幕，Esc 關閉。
- **運行時切換標的與週期**：頂部 control bar 輸入股票編號（`HK.XXXXX` / `US.XXX`，格式校驗 + 自動 uppercase；大小寫敏感特例如 `HK.HSImain` 經 `_CODE_ALIASES` 自動映返正規形式）+ K 線週期按鍵組（9 個 checkable button，QButtonGroup exclusive），點擊即切——engine worker thread 做 unsubscribe → fetch+seed → subscribe，全部驗證通過先 swap；失敗自動 rollback 返舊標的（圖表唔會斷）。
- **輸入欄只收純編號 + 存在性驗證**：TEXT FIELD 永遠只持有純編號——**onChange guard**（`textChanged` handler）一偵測到欄位出現「code + 名稱」（含空白，例 completer `setCompletion()` 喺 activated 前寫入嘅完整 display_text）即刻剝離返第一 token 純 code；目錄載入後經 `StockCatalog.canonical_code()` 驗證編號存在並正規化嚴格大小寫（`hk.00700` → `HK.00700`），未知編號直接報錯唔切換（唔會打到 OpenD）；目錄未載入時放行俾 engine/OpenD 最終校驗。
- **獨立名稱 LABEL**：control bar 輸入欄旁嘅 `QLabel` 顯示當前標的嘅中英文名（新純函數 `name_text()`），目錄載入 / dropdown 選中 / 手動切換時同步更新——名稱永遠唔會入 TEXT FIELD。
- **模糊輸入自動補全**：股票編號欄支持中英文名 + 簡體/繁體中文模糊匹配（例：`騰訊`、`AAPL`、`hsimain`），dropdown 結果 rank-based（精確 > prefix > substring > typo fuzzy）；**dropdown popup 顯示完整 `display_text`（code + 中英文名）**，選中後輸入欄 TEXT FIELD **只留 code**——經 `code_from_completion()` 還原嚴格大小寫 canonical code（mapping hit → canonical、miss → 第一 token 兜底），名稱唔會入輸入欄。目錄由 `get_stock_basicinfo`（HK+US，~17k 隻）載入，主力連續合約經 seed 補返。
- **富途 K 線資料源**：本地 OpenD（預設 `127.0.0.1:11111`），預設標的 `HK.HSImain`（恒指期貨主連），預設週期 1 分鐘，歷史深度預設 1000 根。
- **實時報價回調更新**：訂閱 QUOTE → `_QuoteHandler(StockQuoteHandlerBase).on_recv_rsp()`；tick 即時聚合入當前蠟燭（close=最新價、high/low=max/min、volume=日累計成交量 delta）。
- **紅漲綠跌（港股慣例）**：`.env` 可切 `CONVENTION=INTL`（綠漲紅跌）或用 `COLOR_UP` / `COLOR_DOWN` 手動 override。
- **深色主題圖表**：蠟燭 + last-price dashed line 同右軸 tag + OHLCV readout + volume subpane + crosshair。
- **X/Y 軸縮放 + 手勢 + 左右平移**：互動視圖狀態（X = (可見根數, 右偏移)——右偏移 0 = 右 pin 跟隨 live；Y = 手動價格範圍，None=auto-fit）。手勢：**wheel = X 軸縮放**（游標錨定、每 notch ×/÷1.25）、**Ctrl/Shift + wheel = Y 軸縮放**（游標錨定）、**左鍵拖曳 = 左右平移**、**右鍵拖曳 = 垂直平移**、**雙擊 = `reset_view()` 重置**。所有 pan/zoom 數學喺純函數（`visible_window`/`zoom_x`/`pan_x`/`zoom_y`/`pan_y`，邊界 clamp + 可獨立單測）；切換標的自動 reset view。
- **Overlay 擴展點**：`CandleChart.add_overlay()` 預留俾日後 ICT FVG / Order Block / Kill Zone 圖層（Step 1 零 overlay）。

## Architecture

### 文件結構

```
D:\coding\ICT_v1\
├─ main.py                     # ✅ entry：Config → QApplication + MainWindow(showFullScreen)；SIGINT 排程 quit；finally clean shutdown
├─ config.py                   # ✅ frozen dataclass Config.from_env()，純 stdlib+dotenv，無 Qt/futu import；公開 KLINE_TYPES / kline_period_minutes()
├─ engine\                     # ✅ timeutil / candle_aggregator（純類）/ stock_catalog（StockEntry + fuzzy 搜尋，OpenCC 簡繁轉換；`display_text()` dropdown 行、`name_text()` 名稱 LABEL、`canonical_code()` 存在性驗證）/ futu_engine（QObject：OpenD 連線 + seed + QUOTE 回調聚合 + switch 運行時切換 + get_stock_basicinfo 目錄 fetch）
├─ ui\                         # ✅ main_window（control bar：標的輸入欄（**只收純編號**——onChange guard `textChanged` 剝離「code + 名稱」、`canonical_code()` 驗證存在 + 正規化大小寫，fuzzy autocomplete dropdown 選中後只留 code）+ **獨立名稱 LABEL**（`name_text()` 顯示中英文名）+ K 線週期按鍵組（checkable QButtonGroup exclusive）→ engine.switch()）/ stock_completer（StockCompleter matching 委派 StockCatalog + `code_from_completion()` 純函數還原 canonical code + `catalog()` accessor）/ candle_chart（純 QPainter；backpressure coalesce repaint；volume 填充矩形同 body 等寬；**互動視圖狀態 X=(可見根數,右偏移)/Y=手動範圍 + 五個 pan/zoom 純函數（wheel/Ctrl+wheel/拖曳/雙擊 reset）**；add_overlay 擴展點）
├─ tests\                      # test_config.py ✅；test_timeutil.py ✅；test_aggregator.py ✅；test_futu_engine.py ✅（mock ctx，零真實連線；含 switch/_reconfigure/rollback/market tz/catalog fetch + seed）；test_stock_catalog.py ✅（fuzzy 搜尋 + name_text）；test_stock_completer.py ✅（offscreen Qt）；test_main_window.py ✅（offscreen Qt + fake engine：onChange guard 剝離 code+名稱 / 存在性檢查 / 名稱 LABEL）；test_candle_chart.py ✅
├─ .env                        # gitignored；唯一事實來源（host/port/標的/週期/convention）
├─ .env.example                # ✅ commit 嘅配置文檔（複製做 .env）
└─ requirements.txt            # pip freeze 輸出（PySide6==6.11.2、futu_api==10.5.6508…）
```

### Threading & Signal 模型

- futu-api **每個 context 只有一條 callback thread** → `on_recv_rsp` 必須快，唔做重活/阻塞。
- `request_history_kline` 係同步阻塞 → 放獨立 setup daemon thread（唔係 GUI thread）。
- **運行時切換**：`switch()` 每次 spawn 一個 daemon worker thread 跑 `_reconfigure()`（unsubscribe → fetch+seed → subscribe）；`stop()` join 晒所有 worker。
- **股票目錄 fetch**：`get_stock_basicinfo` 係同步阻塞 → 喺 setup thread 內、subscribe 成功後執行，獨立 try/except——失敗唔影響主流程、唔 close ctx；結果經 `catalog_ready(tuple[StockEntry])` signal auto-queue 去 GUI build autocomplete dropdown。
- **聚合喺 callback thread 做**；GUI 只負責 render。跨線程傳 **immutable tuple-of-tuples snapshot**（bar = `(time_key, open, high, low, close, volume)`），經 `pyqtSignal` queued 過 GUI——無共享可變狀態、無鎖。
- **Backpressure**：chart widget 用 dirty flag + singleShot `QTimer(30ms)` coalesce repaint → tick burst 都最多 ~30fps redraw，永遠 render 最新 snapshot。

### 運行時切換一致性（`_State` atomic swap）

Engine 只持一個 immutable `_State(aggregator, code, kline_type, anchor_date)` reference；切換 = 一次過 swap reference：

1. worker **先驗證後 swap**：fetch 失敗 / seed 0 根 / subscribe 失敗 → rollback（resubscribe 舊標的 + error signal），state 保持唔變、圖表繼續 live。
2. handler 每 batch load 一次 state + per-row `row.code != state.code → skip`——unsubscribe **唔係硬停**（OpenD 實測：訂閱未滿 1 分鐘 unsubscribe 會失敗），in-flight / 殘留 push 一律 filter 掉。
3. emit 前 identity check（`state is eng._state`）→ batch 中途 state 被 swap 走，呢批 discard，唔會用舊 aggregator 嘅 snapshot 覆蓋新圖。
4. `switch()` guard：setup/switch 進行中 → reject + status 提示；校驗（code 格式 `^(HK|US)\.\w+$`、週期名）失敗 → error signal。Code 經 `_normalize_code()` normalize（strip + uppercase，再將大小寫敏感特例如 `HK.HSImain` 經 `_CODE_ALIASES` 映返正規形式——OpenD 拒收全 upper 嘅 `HSIMAIN`）。

### 歷史 K 線取得（實測驗證行為）

- **必須明確窗口**：`request_history_kline` 唔帶 start/end 對 HK.HSImain 會返回一年前舊數據 → `history_window()` 用 now() 計算保守窗口（覆蓋夜期 ~834 min/日）。
- **返回頭 N 根而非最近 N 根**：window + max_count 返回時間序頭 N 根 → `page_req_key` 分頁攞晒（1000 根/頁）再 tail `history_count` 根。
- **按欄位名提取**：DataFrame 欄位順序係 open/close/high/low（唔係 OHLC）→ 一律 `df[["time_key","open","high","low","close","volume"]]`。
- **Live tick data_time 係 time-only**（'HH:mm:ss.SSS'，無日期）→ `resolve_tick_datetime()` 補 date = max(anchor, market_today)；anchor = seed 最後一根 bar 嘅日期（處理夜期跨午夜 + clock skew）；market_today 用 `_fallback_date()` 以**市場自己時區**（zoneinfo：HK=Asia/Hong_Kong / US=America/New_York，未知 prefix 回落 HK）計算——美股喺 HKT 機上「今日」會同 machine-local 差一日。
- **`unsubscribe()` 訂閱未滿 1 分鐘會失敗**（實測錯誤訊息「Basic訂閱時間過短」）→ 切換流程唔阻擋，殘留 push 由 handler code filter 兜底（見上節）。

### 時區鐵律

Quote `data_time` 同 kline `time_key` 對 HK.HSImain 都係 **HKT naive string** → parse naive、floor 到週期邊界、**永遠唔好 astimezone / 加 tzinfo**。呢個係 live bar key 同歷史 bar key 對得上嘅前提。

已知近似：期貨夜期嘅「交易日」界線未必等於日曆午夜，rollover volume reset 係合理近似（跨界嗰根 bar volume 可能微差）。

## Tech Stack

- Python 3.12（Windows 11 / Ubuntu；純 Python + Qt6，無平台特定代碼）
- PySide6（Qt6，LGPL）——pin `>=6.7,<6.12`，現裝 6.11.2
- futu-api ≥ 10.4.6408（現裝 10.5.6508）
- opencc-python-reimplemented —— 簡體/繁體中文轉換（fuzzy 搜尋 t2s 正規化，lazy init + identity fallback）
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
| `HISTORY_COUNT` | `1000` | 歷史 K 線根數（≥1） |
| `VISIBLE_BARS` | `120` | 圖表初始/預設可見蠟燭數（≥1；wheel 縮放可即時改，雙擊 reset 返呢個值） |
| `CONVENTION` | `HK` | 蠟燭顏色慣例：`HK`=紅漲綠跌 / `INTL`=綠漲紅跌；未知值回落 HK |
| `COLOR_UP` / `COLOR_DOWN` | （空=跟隨慣例） | 手動 override 色值，如 `#FF4D4F` |
| `BG_COLOR` / `GRID_COLOR` / `TEXT_COLOR` / `AXIS_TEXT_COLOR` / `LAST_PRICE_COLOR` | 深色主題預設 | 圖表配色，可覆蓋 |
| `DEBUG` | `false` | tick log 等除錯輸出（`1/true/yes/on` 為真） |

> 已存在嘅程序環境變數優先於 `.env` 檔案（`load_dotenv(override=False)`），方便測試與部署時臨時覆蓋。
