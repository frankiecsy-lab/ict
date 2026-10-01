# ICT TRADER

跨平台（Windows 11 / Ubuntu）全屏幕 K 線終端，基於 Inner Circle Trader (ICT) 方法論。Step 1 目標：透過本地富途 OpenD（`futu-api`）取得歷史 K 線，並用**實時報價回調**（subclass `StockQuoteHandlerBase`、覆蓋 `on_recv_rsp(self, rsp_pb)`）驅動當前蠟燭即時更新——唔係 polling、唔係 K 線 push。

## 📍 最新進度 / 發佈日誌

| 日期 | 階段 | 更新摘要 |
|---|---|---|
| 2026-10-01 | Step 2 · Commit 15 | **ICT 指標開關：Order Blocks + FVG Confluence**：新增 `engine/indicators.py`（純 stdlib、零 Qt/futu 依賴）——`Zone(kind, side, start_idx, end_idx, top, bottom)` frozen dataclass + 三個 O(n) 純函數：`detect_fvg()`（三根 K 線失衡：bullish = c1.high < c3.low → gap `[c1.high, c3.low]`、bearish 對稱；矩形自第三根向右延伸直到**完全填補**→ end_idx 記錄填補位置，未填補 = None 畫到右緣）、`detect_order_blocks()`（強線 BOS 觸發：body ≥ range/2 且 close 突破 prior high/low → 向前掃最近一根反向線 j → OB 矩形 = 該線 open–close body；doji skip、同 origin dedup、後續 bar close 跌穿 body 界失效）、`confluence_zones()`（同向 OB ∩ FVG 價格重疊帶 `[max(bottoms), min(tops)]` × 時間交集）。UI：control bar「指標」區 checkable 開關按鍵——**模組化註冊表 `INDICATOR_TOGGLES`（加新指標 = 加一行）**→ 全部 4 pane 同步；`CandleChart.set_indicator()` 立即重算 + repaint timer coalesce tick 重算；paintEvent 蠟燭之後畫價格錨定矩形（fvg 虛線邊框 alpha≈45 / ob 實線邊框 alpha≈80 / confluence 紫色 `#B388FF` 最上層），視窗外 / Y 範圍外 zone skip。28 項新單測（全套 **371 passed**） |
| 2026-10-01 | Step 2 · Commit 14 | **多 pane 圖表 + 時間軸同步**：UI 由單圖表改為 **1/2/4 pane layout 按鍵組**（QButtonGroup exclusive）+ 每個 pane 頂部獨立 K 線週期 combo（9 種，預設 K_1M/K_3M/K_5M/K_15M）。Engine 重構：單一 QUOTE 訂閱 → **N aggregator fan-out**——`_State(code, anchor_date, periods: frozenset, aggregators: dict)` 每週期一個 `CandleAggregator`，tick 分發入所有活躍週期；`switch(code=None, periods=None)` 差集處理（同 code 未變嘅週期沿用舊 aggregator 保留 live bars、唔重新 fetch；code 變先 unsubscribe/subscribe + 全部重建）；signals 改 **per-period** `(period, bars)`，GUI 按 pane combo 路由。時間軸同步：用戶喺任何 pane pan/zoom → 廣播時間視窗 `(start_dt, end_dt)` 去其他可見 pane（`time_window_indices()` span-overlap——不同週期 bar 數自然對齊同一時間跨度）；放大/縮小按鍵改做**全部可見 pane 統一時間空間縮放**（中心錨定 ×/÷1.25）。4 pane 週期與可見性無關常駐活躍（OpenD 額度零額外成本、layout 切換即時有數據）。38 項新單測（全套 **343 passed**） |
| 2026-10-01 | Step 2 · Commit 13 | **SQLite 訂閱帳本 + 自動清理 reconcile（杜絕訂閱洩漏）**：根因係切換標的時 `unsubscribe` 舊 code，但 OpenD 規則「同一 code 訂閱未滿 1 分鐘就 unsubscribe 會被拒」（實測「Basic訂閱時間過短」）→ 舊訂閱實際未移除、持續佔用額度（快速切換多隻股票會累積一堆清唔到嘅洩漏）。新增 `engine/subscription_store.py`（純 stdlib sqlite3，零 Qt/futu 依賴）——記錄每筆活躍 QUOTE 訂閱 `(code, subtype, subscribed_at)`；DB 路徑跟 `.env` 同邏輯（開發=專案根目錄、frozen=exe 旁邊）。`FutuEngine` 整合：subscribe/rollback 成功 → `store.add()`；unsubscribe 成功 → `store.remove()`、失敗（未滿 1min）→ **保留 pending**；定時 `_reconcile_subscriptions()`（30s，獨立 daemon thread）對「已不活躍且 age≥75s」嘅洩漏訂閱重試 unsubscribe + remove；開機經 `query_subscription()` 對帳自癒上次 crash 殘留（OpenD 端有、帳本冇、非當前 state → 直接清）。26 項新單測（全套 **302 passed**） |
| 2026-09-30 | Step 2 · Commit 12 | **雙平台執行檔建置（Windows / Ubuntu x86-64，PyInstaller onedir）**：新增 `scripts/build_exe.py`（Windows → `dist/ICT-Trader-win/ICT-Trader.exe`）+ `scripts/build_ubuntu.sh`（WSL Ubuntu native build → `dist/ICT-Trader-ubuntu/ict-trader`；venv + apt tzdata/libgl1，唔需要 Docker daemon）。**frozen 模式支援**：`.env` 改讀 **exe 旁邊**（`config.py::_default_env_path()`——唔係 `_MEIPASS` temp dir，用戶部署可改）+ windowed build 配置錯誤彈 `QMessageBox`（`main.py::_report_config_error()`）。新增 `scripts/smoke_test.py` offscreen smoke。6 項新單測（全套 **276 passed**） |
| 2026-09-30 | Step 2 · Commit 11 | **月K（K_MON）切換失敗修復**（live 使用發現：撳 K_MON 按鍵圖表冇更新、仲係顯示舊週期數據）：根因係 `history_window()` 為大週期 × 大 count 算出過長窗口——`K_MON`(43200min)×1000 ≈ **123 年**跨度，超過 OpenD `request_history_kline` 嘅 ~55 年臨界點（實測邊界：55yr OK / 60yr → `ret=-1 F3CNN返回错误`）→ fetch raise → `_reconfigure()` rollback → 圖表保持舊數據。修復：新增 `_MAX_WINDOW_DAYS=40*365` clamp——窗口寬度上限 **40 年**（遠低於臨界點、留 ~15 年安全餘量，且已覆蓋 HK.HSImain 全部可用歷史 ~21 年）。實測 K_MON 由 `ret=-1` → **`ret=0 / 256 根`**（全部月線）、K_WEEK 照常 1000 根。2 項回歸單測（全套 **270 passed**） |
| 2026-09-30 | Step 2 · Commit 10 | **last-price 水平線跟隨「真正最新一根 bar」**（live 使用發現：pan 左走後虛線顯示嘅係可見視窗最右邊嗰根 K 線嘅 close，唔係真實最新價）：`paintEvent` 由 `bars[-1]`（visible_window slice）改用 `self._bars[-1]`——無論 pan/zoom 到咩位置，虛線 + 右軸 tag 永遠顯示數據尾部真正最新一根 bar 嘅 close；加 bounds-check（同 gridline 一樣）：最新價超出當前 Y 範圍（auto-fit 只 fit 可見 bars / 手動 Y zoom/pan）→ 整條線 + tag 唔畫，避免繪製出界。2 項 pixel 級回歸單測（offscreen render + `#FFB020` 精確色計數：tag 必須喺 y(真正最新價) 而唔係 y(可見視窗最右 close)；超範圍時全圖零 last-price 像素）。全套 **268 passed** |
| 2026-09-30 | Step 2 · Commit 9 | **K 線圖多段式縮放 + 放大/縮小按鍵**（live 使用發現「只有兩段」bug）：根因係 Windows wheel 每物理 notch 報 `angleDelta.y()=±120°`，未正規化會令單 notch 變 `1.25**120 ≈ 3e13` → X 軸縮放直接 clamp 去 min(5)/max(2000) 極限（放大即跳到 5 根超大蠟燭）。修復：新增純函數 `wheel_notches()`（±120° → ±1 階）+ `wheelEvent` 改用正規化 delta——**每物理 notch / 按鍵點擊 = 一階 ×/÷1.25**；control bar 右側新增**放大/縮小按鍵**→ `CandleChart.zoom_in()/zoom_out()`（中心錨定、無數據 no-op）。踩坑：PySide6 `clicked` 有 `(bool)` 重載會令直接 connect 變 no-op → lambda 包零參數調用。14 項新單測（全套 **266 passed**） |
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
- [x] Commit 9：**K 線圖多段式縮放 + 放大/縮小按鍵**——`wheel_notches()` 將 Windows ±120° wheel delta 正規化返每 notch 一階 ×/÷1.25（修「只有兩段」bug：未正規化單 notch 直跳 min/max 極限）；control bar 右側放大/縮小按鍵 → `zoom_in()/zoom_out()`（中心錨定分步縮放）
- [x] Commit 10：**last-price 水平線跟隨真正最新一根 bar**——`paintEvent` 由可見視窗 slice 改用 `self._bars[-1]`（pan 左走後仍顯示真實最新價）+ bounds-check（最新價超出當前 Y 範圍 → 整條線 + tag 唔畫）
- [x] Commit 11：**月K（K_MON）切換失敗修復**——`history_window()` 大週期 × 大 count 算出過長窗口（K_MON×1000 ≈ 123 年 > OpenD ~55 年臨界點 → `ret=-1` → rollback）→ 加 `_MAX_WINDOW_DAYS=40*365` clamp
- [x] Commit 12：**雙平台執行檔建置**——PyInstaller onedir（Windows `scripts/build_exe.py` / Ubuntu WSL native `scripts/build_ubuntu.sh`）+ frozen 模式 `.env` 讀 exe 旁邊 + windowed 配置錯誤彈框 + offscreen smoke test
- [x] Commit 13：**SQLite 訂閱帳本 + 自動清理 reconcile**——`engine/subscription_store.py`（純 stdlib sqlite3）記錄每筆活躍 QUOTE 訂閱；切換時 unsubscribe 失敗（未滿 1min）→ 保留 pending，定時 `_reconcile_subscriptions()` 重試清理洩漏；開機 `query_subscription()` 對帳自癒殘留
- [x] Commit 14：**多 pane 圖表 + 時間軸同步**——1/2/4 layout 按鍵組（QButtonGroup exclusive）+ 每 pane 頂部獨立 K 線週期 combo；engine 重構為單一 QUOTE 訂閱 → N aggregator fan-out（`_State(code, anchor_date, periods: frozenset, aggregators: dict)`、`switch(code=None, periods=None)` 差集處理——同 code 未變嘅週期沿用舊 aggregator 保留 live bars、per-period signals `(period, bars)`）；用戶喺任何 pane pan/zoom → 廣播時間視窗去其他可見 pane（span-overlap 跨週期對齊）；放大/縮小按鍵 = 全部可見 pane 統一時間空間縮放
- [x] Commit 15：**ICT 指標開關：Order Blocks + FVG Confluence**——`engine/indicators.py` 純邏輯層（FVG 三根 K 線失衡 / OB 強線 BOS 觸發 + 最近反向線 body / confluence 同向重疊帶）+ control bar「指標」區 checkable 開關按鍵（`INDICATOR_TOGGLES` 模組化註冊表，加新指標 = 加一行）→ 全部 pane 同步；`CandleChart.set_indicator()` 立即重算 + paintEvent 價格錨定矩形層（fvg 虛線 / ob 實線 / confluence 紫色高亮最上層）

### 下一步（Step 2 後續候選，未定範圍）
- ICT 指標 overlay：**Order Blocks + FVG Confluence 已完成**（Commit 15，control bar「指標」區開關）；Kill Zone 圖層留待後續
- 切換歷史記錄 / 多標的並排顯示（視需要）

## Features（Step 1 + Step 2）

- **全屏幕終端**：PySide6/Qt6 全屏幕窗口，F11 切換全屏幕，Esc 關閉。
- **運行時切換標的與週期**：頂部 control bar 輸入股票編號（`HK.XXXXX` / `US.XXX`，格式校驗 + 自動 uppercase；大小寫敏感特例如 `HK.HSImain` 經 `_CODE_ALIASES` 自動映返正規形式）+ **1/2/4 pane layout 按鍵組**（checkable QButtonGroup exclusive）與每 pane 頂部獨立 K 線週期 combo（9 種），點擊即切——engine worker thread 差集處理（code 變先 unsubscribe/subscribe；週期逐個 fetch+seed，未變嘅沿用舊 aggregator），全部驗證通過先 swap；失敗自動 rollback（圖表唔會斷）。
- **多 pane 圖表 + 時間軸同步**：1/2/4 pane layout（QGridLayout，pane 數據保留、切換 layout 唔重建）；每個 pane 頂部獨立 K 線週期 combo——engine 以「全 pane combo union」為目標活躍週期集合（與可見性無關：layout 切換即時有數據），單一 QUOTE 訂閱 → N `CandleAggregator` fan-out（OpenD 額度零額外成本）。**時間軸同步**：用戶喺任何 pane pan/zoom → 廣播時間視窗 `(start_dt, end_dt)` 去其他可見 pane，經 `time_window_indices()` span-overlap 對齊——不同週期 bar 數自然對應同一時間跨度；放大/縮小按鍵 = **全部可見 pane 統一時間空間縮放**（中心錨定 ×/÷1.25）。
- **訂閱洩漏自動清理**：切換時 `unsubscribe` 舊 code 若因「訂閱未滿 1 分鐘」被 OpenD 拒收，該筆訂閱會實際殘留、持續佔用額度——SQLite 訂閱帳本記錄每筆活躍訂閱 + 定時 reconcile（30s）對已不活躍且滿 75s 嘅洩漏訂閱重試清理；開機經 `query_subscription()` 對帳自癒上次 crash 殘留。快速切換多隻股票唔會累積清唔到嘅訂閱。
- **輸入欄只收純編號 + 存在性驗證**：TEXT FIELD 永遠只持有純編號——**onChange guard**（`textChanged` handler）一偵測到欄位出現「code + 名稱」（含空白，例 completer `setCompletion()` 喺 activated 前寫入嘅完整 display_text）即刻剝離返第一 token 純 code；目錄載入後經 `StockCatalog.canonical_code()` 驗證編號存在並正規化嚴格大小寫（`hk.00700` → `HK.00700`），未知編號直接報錯唔切換（唔會打到 OpenD）；目錄未載入時放行俾 engine/OpenD 最終校驗。
- **獨立名稱 LABEL**：control bar 輸入欄旁嘅 `QLabel` 顯示當前標的嘅中英文名（新純函數 `name_text()`），目錄載入 / dropdown 選中 / 手動切換時同步更新——名稱永遠唔會入 TEXT FIELD。
- **模糊輸入自動補全**：股票編號欄支持中英文名 + 簡體/繁體中文模糊匹配（例：`騰訊`、`AAPL`、`hsimain`），dropdown 結果 rank-based（精確 > prefix > substring > typo fuzzy）；**dropdown popup 顯示完整 `display_text`（code + 中英文名）**，選中後輸入欄 TEXT FIELD **只留 code**——經 `code_from_completion()` 還原嚴格大小寫 canonical code（mapping hit → canonical、miss → 第一 token 兜底），名稱唔會入輸入欄。目錄由 `get_stock_basicinfo`（HK+US，~17k 隻）載入，主力連續合約經 seed 補返。
- **富途 K 線資料源**：本地 OpenD（預設 `127.0.0.1:11111`），預設標的 `HK.HSImain`（恒指期貨主連）；pane 0 預設週期跟 `.env kline_type`（K_1M）、其餘 pane 錯開 K_3M/K_5M/K_15M，歷史深度預設 1000 根。
- **實時報價回調更新**：訂閱 QUOTE → `_QuoteHandler(StockQuoteHandlerBase).on_recv_rsp()`；tick 分發入**所有活躍週期嘅 `CandleAggregator`**（每 aggregator 各自聚合：close=最新價、high/low=max/min、volume=日累計成交量 delta），per-period signal `(period, bars)` 路由去對應 pane。
- **紅漲綠跌（港股慣例）**：`.env` 可切 `CONVENTION=INTL`（綠漲紅跌）或用 `COLOR_UP` / `COLOR_DOWN` 手動 override。
- **深色主題圖表**：蠟燭 + last-price dashed line 同右軸 tag（跟隨「真正最新一根 bar」`self._bars[-1]`——pan/zoom 到咩位置都顯示真實最新價，唔係可見視窗最右邊嗰根；最新價超出當前 Y 範圍時整條隱藏）+ OHLCV readout + volume subpane + crosshair。
- **X/Y 軸縮放 + 手勢 + 左右平移**：互動視圖狀態（X = (可見根數, 右偏移)——右偏移 0 = 右 pin 跟隨 live；Y = 手動價格範圍，None=auto-fit）。**多段式縮放**：每個物理 wheel notch / 按鍵點擊 = **一階 ×/÷1.25**（`wheel_notches()` 將 Windows ±120° `angleDelta` 正規化返 ±1 階——唔正規化會單 notch 直跳 min(5)/max(2000) 極限，表現成「只有兩段」）。手勢：**wheel = X 軸縮放**（游標錨定）、**Ctrl/Shift + wheel = Y 軸縮放**（游標錨定）、**左鍵拖曳 = 左右平移**、**右鍵拖曳 = 垂直平移**、**雙擊 = `reset_view()` 重置**；control bar 右側**放大/縮小按鍵** → `zoom_in()/zoom_out()`（中心錨定分步縮放，無數據 no-op）。所有 pan/zoom 數學喺純函數（`visible_window`/`zoom_x`/`pan_x`/`zoom_y`/`pan_y`/`wheel_notches`，邊界 clamp + 可獨立單測）；切換標的自動 reset view。
- **ICT 指標開關（Order Blocks + FVG Confluence）**：control bar「指標」區 checkable 開關按鍵——**模組化註冊表 `INDICATOR_TOGGLES`（加新指標 = 喺註冊表加一行，control bar 自動生成對應按鍵）**；偵測邏輯係 `engine/indicators.py` 純函數：**FVG**（三根 K 線失衡：bullish = c1.high < c3.low → gap 矩形自第三根向右延伸直到完全填補）、**Order Block**（強線 BOS 觸發 body ≥ range/2 + close 突破 prior high/low → 最近一根反向線嘅 open–close body 矩形；doji skip、同 origin dedup、close 跌穿 body 界失效）；兩開關同時開啟自動派生 **Confluence 共鳴層**（同向 OB ∩ FVG 價格重疊帶紫色 `#B388FF` 高亮）。`set_indicator()` 立即重算 + repaint timer coalesce tick 重算；paintEvent 喺蠟燭之後畫價格錨定矩形（fvg 虛線邊框 / ob 實線邊框 / confluence 最上層），完全喺可見視窗或 Y 範圍外嘅 zone skip。
- **Overlay 擴展點**：`CandleChart.add_overlay()` 保留作通用 hook；ICT FVG / Order Block / Confluence 已係一級指標層（`set_indicator()`，見上條），Kill Zone 留待後續。

## Architecture

### 文件結構

```
D:\coding\ICT_v1\
├─ main.py                     # ✅ entry：Config → QApplication + MainWindow(showFullScreen)；SIGINT 排程 quit；finally clean shutdown；windowed build（frozen + 無 console）配置錯誤彈 QMessageBox
├─ config.py                   # ✅ frozen dataclass Config.from_env()，純 stdlib+dotenv，無 Qt/futu import；公開 KLINE_TYPES / kline_period_minutes()；`_default_env_path()`——frozen 時 .env 讀 exe 旁邊（開發模式 = 專案根目錄）
├─ engine\                     # ✅ timeutil / candle_aggregator（純類）/ indicators（**ICT 指標純邏輯層**：`Zone` frozen dataclass + `detect_fvg()` / `detect_order_blocks()` / `confluence_zones()` O(n) 純函數，零 Qt/futu 依賴）/ stock_catalog（StockEntry + fuzzy 搜尋，OpenCC 簡繁轉換；`display_text()` dropdown 行、`name_text()` 名稱 LABEL、`canonical_code()` 存在性驗證）/ subscription_store（**SQLite 訂閱帳本**：純 stdlib sqlite3，記錄每筆活躍 QUOTE 訂閱 `(code,subtype,subscribed_at)` + `due_for_cleanup()`；DB 路徑跟 .env 同邏輯——開發=專案根目錄、frozen=exe 旁邊）/ futu_engine（QObject：OpenD 連線 + seed + **單一 QUOTE 訂閱 → N aggregator fan-out**（`_State(code, anchor_date, periods: frozenset, aggregators: dict)`、per-period signals `(period, bars)`）+ `switch(code=None, periods=None)` 差集處理運行時切換 + get_stock_basicinfo 目錄 fetch + **訂閱帳本 reconcile 自動清理洩漏**）
├─ ui\                         # ✅ main_window（control bar：標的輸入欄（**只收純編號**——onChange guard `textChanged` 剝離「code + 名稱」、`canonical_code()` 驗證存在 + 正規化大小寫，fuzzy autocomplete dropdown 選中後只留 code）+ **獨立名稱 LABEL**（`name_text()` 顯示中英文名）+ **1/2/4 pane layout 按鍵組** + **指標開關按鍵**（`INDICATOR_TOGGLES` 模組化註冊表 → 全部 pane `set_indicator()` 同步）→ engine.switch(code, periods)；**多 pane 圖表區**：每 pane = 頂部週期 combo + CandleChart（per-period signal 路由、pan/zoom 時間視窗廣播同步、放大/縮小 = 全部可見 pane 統一時間空間縮放））/ stock_completer（StockCompleter matching 委派 StockCatalog + `code_from_completion()` 純函數還原 canonical code + `catalog()` accessor）/ candle_chart（純 QPainter；backpressure coalesce repaint；volume 填充矩形同 body 等寬；**互動視圖狀態 X=(可見根數,右偏移)/Y=手動範圍 + 五個 pan/zoom 純函數（wheel/Ctrl+wheel/拖曳/雙擊 reset）**；**ICT 指標層**：`set_indicator()` + `_recompute_zones()`（OB/FVG/confluence 價格錨定矩形——fvg 虛線 / ob 實線 / confluence 紫色最上層、視窗外 skip）+ add_overlay 通用 hook）
├─ scripts\                    # ✅ build_exe.py（Windows PyInstaller onedir → dist/ICT-Trader-win/）/ build_ubuntu.sh（WSL Ubuntu native build → dist/ICT-Trader-ubuntu/）/ smoke_test.py（offscreen 啟動 + clean shutdown smoke）
├─ tests\                      # test_config.py ✅；test_indicators.py ✅（**ICT 指標純邏輯**：FVG/OB/confluence 偵測 + fill/失效/dedup/doji/邊界）；test_timeutil.py ✅；test_aggregator.py ✅；test_futu_engine.py ✅（mock ctx，零真實連線；含 switch/_reconfigure/rollback/market tz/catalog fetch + seed + **訂閱帳本 reconcile / pending / query_subscription 對帳**）；test_subscription_store.py ✅（SQLite 帳本 CRUD + due_for_cleanup + frozen/dev DB 路徑 + 併發 add）；test_stock_catalog.py ✅（fuzzy 搜尋 + name_text）；test_stock_completer.py ✅（offscreen Qt）；test_main_window.py ✅（offscreen Qt + fake engine：onChange guard 剝離 code+名稱 / 存在性檢查 / 名稱 LABEL / **多 pane 時間視窗廣播同步 + per-period signal 路由 + active snapshot push** + 指標開關按鍵全 pane 同步）；test_candle_chart_widget.py ✅（offscreen Qt：CandleChart 互動視圖 + 時間視窗 `set_time_window`/`time_window` + **ICT 指標層 set_indicator 立即重算 + pixel 級 render 驗證**）；test_candle_chart.py ✅；test_frozen.py ✅（frozen .env 路徑 + windowed 配置錯誤彈框）
├─ .env                        # gitignored；唯一事實來源（host/port/標的/週期/convention）
├─ .env.example                # ✅ commit 嘅配置文檔（複製做 .env；build 腳本自動生成入產物夾）
└─ requirements.txt            # pip freeze 輸出（PySide6==6.11.2、futu_api==10.5.6508…）
```

### Threading & Signal 模型

- futu-api **每個 context 只有一條 callback thread** → `on_recv_rsp` 必須快，唔做重活/阻塞。
- `request_history_kline` 係同步阻塞 → 放獨立 setup daemon thread（唔係 GUI thread）。
- **運行時切換**：`switch(code=None, periods=None)` 每次 spawn 一個 daemon worker thread 跑 `_reconfigure()`——code 變先 unsubscribe/subscribe，週期差集逐個 fetch+seed（同 code 未變嘅週期沿用舊 aggregator、保留 live bars）；`stop()` join 晒所有 worker。
- **股票目錄 fetch**：`get_stock_basicinfo` 係同步阻塞 → 喺 setup thread 內、subscribe 成功後執行，獨立 try/except——失敗唔影響主流程、唔 close ctx；結果經 `catalog_ready(tuple[StockEntry])` signal auto-queue 去 GUI build autocomplete dropdown。
- **訂閱帳本 reconcile**：`_reconcile_subscriptions()` 喺獨立 daemon thread（`threading.Timer`，30s 間隔）跑——對「已不活躍且訂閱滿 75s」嘅洩漏訂閱重試 `unsubscribe`；`query_subscription()` / `unsubscribe` 都係同步阻塞 → 唔好占 callback / switch worker thread。SQLite 帳本 per-call connection（天然 thread-safe，見下節）。
- **聚合喺 callback thread 做**；GUI 只負責 render。跨線程傳 **immutable tuple-of-tuples snapshot**（bar = `(time_key, open, high, low, close, volume)`），經 `pyqtSignal` queued 過 GUI——無共享可變狀態、無鎖。
- **Backpressure**：chart widget 用 dirty flag + singleShot `QTimer(30ms)` coalesce repaint → tick burst 都最多 ~30fps redraw，永遠 render 最新 snapshot。

### 運行時切換一致性（`_State` atomic swap）

Engine 只持一個 immutable `_State(code, anchor_date, periods: frozenset[str], aggregators: dict[str, CandleAggregator])` reference（每週期一個 aggregator）；切換 = 一次過 swap reference：

1. worker **先驗證後 swap**：fetch 失敗 / seed 0 根 / subscribe 失敗 → rollback（code 變先 resubscribe 舊標的 + error signal），state 保持唔變、圖表繼續 live。
2. handler 每 batch load 一次 state + per-row `row.code != state.code → skip`——unsubscribe **唔係硬停**（OpenD 實測：訂閱未滿 1 分鐘 unsubscribe 會失敗），in-flight / 殘留 push 一律 filter 掉；**洩漏訂閱由 SQLite 帳本 reconcile 兜底清理**（見下節）。
3. emit 前 identity check（`state is eng._state`）→ batch 中途 state 被 swap 走，呢批 discard，唔會用舊 aggregator 嘅 snapshot 覆蓋新圖。
4. `switch()` guard：setup/switch 進行中 → reject + status 提示；校驗（code 格式 `^(HK|US)\.\w+$`、週期名）失敗 → error signal。Code 經 `_normalize_code()` normalize（strip + uppercase，再將大小寫敏感特例如 `HK.HSImain` 經 `_CODE_ALIASES` 映返正規形式——OpenD 拒收全 upper 嘅 `HSIMAIN`）。

### 歷史 K 線取得（實測驗證行為）

- **必須明確窗口**：`request_history_kline` 唔帶 start/end 對 HK.HSImain 會返回一年前舊數據 → `history_window()` 用 now() 計算保守窗口（覆蓋夜期 ~834 min/日）。
- **窗口寬度上限 clamp**：OpenD 對過長窗口會拒收——實測 K_MON 跨度 >~55 年 → `ret=-1 F3CNN返回错误`。大週期 × 大 count 算出嘅理論窗口可達百多年（K_MON×1000 ≈ 123 年）→ `history_window()` 將窗口寬度 clamp 到 `_MAX_WINDOW_DAYS=40*365`（遠低於臨界點、留 ~15 年安全餘量，且已覆蓋 HK.HSImain 全部可用歷史 ~21 年）。
- **返回頭 N 根而非最近 N 根**：window + max_count 返回時間序頭 N 根 → `page_req_key` 分頁攞晒（1000 根/頁）再 tail `history_count` 根。
- **按欄位名提取**：DataFrame 欄位順序係 open/close/high/low（唔係 OHLC）→ 一律 `df[["time_key","open","high","low","close","volume"]]`。
- **Live tick data_time 係 time-only**（'HH:mm:ss.SSS'，無日期）→ `resolve_tick_datetime()` 補 date = max(anchor, market_today)；anchor = seed 最後一根 bar 嘅日期（處理夜期跨午夜 + clock skew）；market_today 用 `_fallback_date()` 以**市場自己時區**（zoneinfo：HK=Asia/Hong_Kong / US=America/New_York，未知 prefix 回落 HK）計算——美股喺 HKT 機上「今日」會同 machine-local 差一日。
- **`unsubscribe()` 訂閱未滿 1 分鐘會失敗**（實測錯誤訊息「Basic訂閱時間過短」）→ 切換流程唔阻擋，殘留 push 由 handler code filter 兜底；**洩漏訂閱由 SQLite 帳本 reconcile 清理**（見下節）。

### 訂閱帳本與自動清理（SQLite reconcile）

**問題**：切換標的時 `unsubscribe` 舊 code，但 OpenD 規則「同一 code 訂閱未滿 1 分鐘就 unsubscribe 會被拒」→ 快速切換時舊訂閱實際未移除、持續佔用額度（洩漏）。純靠 handler code filter 只係過濾 push，**唔會清走 OpenD 端嗰筆訂閱**。

**方案**：`engine/subscription_store.py`（純 stdlib sqlite3）做訂閱帳本 + `FutuEngine` 定時 reconcile：

- **帳本**：每筆活躍 QUOTE 訂閱 = `(code, subtype, subscribed_at)`，主鍵 `(code, subtype)`。subscribe / rollback resubscribe 成功 → `add()`（re-subscribe 同 code → `INSERT OR REPLACE` 重新計時）；unsubscribe 成功 → `remove()`。**DB 路徑跟 `.env` 同邏輯**：開發 = 專案根目錄、frozen = exe 旁邊（`default_db_path()`）。
- **pending 標記**：`_reconfigure()` unsubscribe 舊 code 失敗（未滿 1min）→ **唔 remove，保留喺帳本**做 pending；subscribe 新 code 成功 → `add(新)` + `_schedule_reconcile()`。
- **定時 reconcile**（30s，獨立 daemon thread）：`query_subscription()` 攞 OpenD 端實際訂閱 code → 對「已不活躍（≠ 當前 state.code）且 age ≥ `MIN_SUBSCRIBE_SECONDS`(75s)」嘅帳本條目重試 `unsubscribe` + `remove`；失敗（仲未滿 1min）→ 保留，下輪再試。
- **開機對帳自癒**：setup subscribe 成功後排程 reconcile——`query_subscription()` 攞到「OpenD 端有、但帳本完全冇記錄」嘅 code（上次 crash 前嘅訂閱殘留）→ 直接 `unsubscribe`（唔入帳本，清完即止）。
- **冪等 + 安全**：每輪重讀帳本；無 due → no-op。`query_subscription()` 失敗 → 跳過該輪（唔改帳本、避免誤刪）。residual 判斷用 loop 前 ledger snapshot 排除「已喺帳本」嘅 code，避免同 due-loop 重複 unsub。
- **Thread safety**：store per-call connection（每次操作開自己 connection + commit/close）→ 唔共享 connection object，天然 thread-safe；SQLite file locking 處理 reconcile worker 同 switch worker 嘅低頻併發寫入。

### 時區鐵律

Quote `data_time` 同 kline `time_key` 對 HK.HSImain 都係 **HKT naive string** → parse naive、floor 到週期邊界、**永遠唔好 astimezone / 加 tzinfo**。呢個係 live bar key 同歷史 bar key 對得上嘅前提。

已知近似：期貨夜期嘅「交易日」界線未必等於日曆午夜，rollover volume reset 係合理近似（跨界嗰根 bar volume 可能微差）。

## Tech Stack

- Python 3.12（Windows 11 / Ubuntu；純 Python + Qt6，無平台特定代碼）
- PySide6（Qt6，LGPL）——pin `>=6.7,<6.12`，現裝 6.11.2
- futu-api ≥ 10.4.6408（現裝 10.5.6508）
- opencc-python-reimplemented —— 簡體/繁體中文轉換（fuzzy 搜尋 t2s 正規化，lazy init + identity fallback）
- python-dotenv —— `.env` 讀取
- sqlite3（**Python stdlib**，無額外依賴）—— 訂閱帳本 `subscriptions.db`（記錄活躍 QUOTE 訂閱 + reconcile 清理洩漏；DB 檔 gitignored）
- pytest —— 單測

## How to Run

```bash
python -m pip install -r requirements.txt
copy .env.example .env    # Windows；Ubuntu: cp .env.example .env
# 按下方表格填 FUTU_OPEND_HOST / FUTU_OPEND_PORT 等（全部可選，預設已可用）
python main.py            # 全屏幕啟動；F11 切換全屏幕、Esc 關閉、Ctrl+C clean exit
```

> 前提：本地富途 OpenD 已開（預設 `127.0.0.1:11111`）。連唔到時窗口會照開，status bar 顯示錯誤訊息。

## Build Executables（雙平台執行檔）

PyInstaller **onedir** build（windowed、無 console）；產物係一個資料夾（exe + `_internal/`），整夾 zip / tar.gz 分發。**`.env` 唔會打包**——部署時放喺 exe 旁邊（build 腳本已自動由 `.env.example` 生成一份預設）。

| 平台 | 指令（喺 repo root） | 產物 |
|---|---|---|
| Windows x86-64 | `python scripts\build_exe.py [--clean]` | `dist/ICT-Trader-win/ICT-Trader.exe` |
| Ubuntu x86-64 | WSL：`wsl -d Ubuntu -- bash -lc "cd /mnt/d/coding/ICT_v1 && bash scripts/build_ubuntu.sh"` | `dist/ICT-Trader-ubuntu/ict-trader` |

- **frozen 模式 `.env`**：`config.py::_default_env_path()`——frozen 時讀 **exe 旁邊**（唔係 `_MEIPASS` temp dir，用戶改咗先要重開 app）；開發模式照舊讀專案根目錄。
- **windowed build 配置錯誤**：無 console → `QMessageBox.critical` 彈出（console / 開發模式照舊 stderr）。
- **乾淨 venv build**：兩邊都用獨立 venv（`.venv-win` / `.venv-ubuntu`，只 pin 必要依賴）——global Python 裝咗 torch/cv2 等無關套件時，PyInstaller `hook-pandas.py` 會將 pandas optional deps 全部打入產物（實測 1.5GB vs ~300MB）。
- **Ubuntu build**：WSL Ubuntu native + apt `tzdata libgl1 libegl1`——唔需要 Docker daemon；首次跑會自動裝依賴。
- **Smoke test**：`QT_QPA_PLATFORM=offscreen python scripts/smoke_test.py [timeout]`——驗證入口可啟動、event loop 行得、clean shutdown（連唔到 OpenD 係預期行為，engine error signal 唔算失敗）。

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
