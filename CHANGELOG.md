# CHANGELOG

## [Unreleased] Step 2（2026-09-30）——運行時切換標的與 K 線週期 + 股票編號模糊自動補全

### Added
- （2026-09-30）`engine/futu_engine.py` 重構為 **immutable `_State(aggregator, code, kline_type, anchor_date)` reference**：engine 只持一個 state reference，切換 = atomic swap。新增 `switch(code, kline_type)`（校驗 code 格式 `^(HK|US)\.\w+$` + 週期名、guard setup/switch 進行中 → reject）+ `_reconfigure()` worker thread（unsubscribe 舊 → fetch+seed 新 → subscribe 新，**全部驗證通過先 swap**；任何失敗 `_rollback()` resubscribe 舊標的 + error signal，圖表保持 live）。
- （2026-09-30）handler 切換一致性：每 batch load 一次 state + per-row `row.code != state.code → skip`（unsubscribe 唔係硬停——OpenD 實測訂閱未滿 1 分鐘 unsubscribe 會失敗「Basic訂閱時間過短」，殘留 push 由 code filter 兜底）+ emit 前 identity check（batch 中途 swap → 呢批 discard）。
- （2026-09-30）time-only tick fallback date 升級為**市場時區感知**：`_fallback_date()` 用 zoneinfo（HK=Asia/Hong_Kong / US=America/New_York，未知 prefix 回落 HK；tzdata 缺失回落 machine-local）——美股喺 HKT 機上「今日」會同 machine-local 差一日。
- （2026-09-30）`config.py` 公開 `KLINE_TYPES`（tuple，insertion order = UI 顯示順序）+ `kline_period_minutes()` helper，UI combo / engine 校驗共用同一事實來源。
- （2026-09-30）`ui/main_window.py` 頂部 **control bar**：標的編號輸入欄（placeholder `HK.00700 / US.AAPL`、預設填 `.env` TRADING_CODE）+ K 線週期 combo（9 種，先 set items/index 再 connect 避免初始觸發 switch）；returnPressed / activated → `_do_switch()` 一次傳齊兩個值 → `engine.switch()`。深色主題跟 `.env` 配色；0 margin/spacing 保持全屏幕感。
- （2026-09-30）`tests/test_futu_engine.py` 遷移到 `_State` 架構 + 新增覆蓋：code filter（in-flight 舊標的 skip / mid-batch swap discard / state None 靜默）、`_fallback_date` 市場時區 7 項（含 NY 前一日 instant-based fake clock、tzdata 缺失 fallback）、switch 校驗 4 項、`_reconfigure` happy path + 3 種 rollback + unsubscribe 失敗唔阻擋 + closed 抑制 emit、真線程 guard（concurrent reject / 小寫 normalize / setup 進行中 reject）；全套 **160 passed**（+24）。
- （2026-09-30）**Live smoke test 實測通過**（offscreen + 真 OpenD `127.0.0.1:11111`）：HK.HSImain K_1M → `hk.00700` K_5M（小寫輸入自動 upper normalize）運行時切換成功——state swap、anchor=2026-09-30、300 bars；格式錯誤校驗（`AAPL` → error signal）正確；`stop()` 乾淨斷線（CallClose）。實測發現 `unsubscribe()` 訂閱未滿 1 分鐘失敗限制 → 已入 AGENTS.md 知識庫。
- （2026-09-30）**股票目錄 fuzzy autocomplete**：新增 `engine/stock_catalog.py`——`StockEntry(code, name_cn, name_en)` frozen dataclass + `display_text()`（code + 中文名 + 英文名）+ `register_code_aliases(entries, alias_map)`（純函數，mixed-case code 自動註冊入 engine `_CODE_ALIASES`）。`StockCatalog.search(query, limit=20)` rank-based 兩段評分：rank 0–7（code 精確 CI → suffix-only 精確 → code prefix → 英文名精確/prefix → 中文名簡繁正規化後精確/prefix → code substring ≥2 → 英文名 substring ≥3 → 中文名 substring）+ 第二段 difflib `SequenceMatcher` ratio ≥0.8 typo fuzzy（length-gap prefilter，只喺 rank≤7 零命中時行）。**簡體/繁體**：OpenCC t2s lazy init + identity fallback——query 每 keystroke 轉簡體、entry 名 index build 時預計算一次（API `name` 實測係簡體中文）；13k entries 搜尋 <2s。
- （2026-09-30）`engine/futu_engine.py::_fetch_catalog()`：`get_stock_basicinfo(Market.HK/US)` per-market try/except（單市場失敗唔阻另一邊）+ code dedup + `_cell_str()` NaN/None 防護；**live 實測限制**——API **冇 `english_name` 欄位**（17 欄，詳見 AGENTS.md 知識庫）、`name` 係簡體中文、**主力連續合約唔喺列表**（HK 3798 rows 冇 HSImain）→ `_SEED_ENTRIES = (StockEntry("HK.HSImain", "恒指期货主连", ""),)` seed 先入 + dedup skip。`_setup()` subscribe 成功後獨立 try/except fetch → `catalog_ready(tuple[StockEntry])` emit + status「股票目錄已載入 · N 隻」；失敗只 log，唔影響主流程、唔 close ctx。
- （2026-09-30）新增 `ui/stock_completer.py::StockCompleter(QCompleter)`：`UnfilteredPopupCompletion`（popup = `completionMatches()` rank-based 結果，Qt 唔再 filter）、matching 全委派 `StockCatalog.search()`；`set_catalog(entries)` rebuild QStandardItemModel + 返回 display_text → canonical code 映射。`ui/main_window.py` control bar 輸入欄接 dropdown：activated → 查 mapping 填返**嚴格大小寫** code（`HK.HSImain`）→ `engine.switch(code=...)`；returnPressed 保留 raw-text 路徑（OpenD 最終校驗）。
- （2026-09-30）新單測：`tests/test_stock_catalog.py`（24 項：rank 各層、t2s query「騰訊控股」→HK.00700、typo fuzzy「hhimain」、dedup、limit、13k entries perf <2s）+ `tests/test_stock_completer.py`（offscreen Qt，mapping 嚴格大小寫保留）+ `test_futu_engine.py::TestFetchCatalog`（8 項：欄位名提取、NaN/None 清理、dedup、單市場 exception、ret≠0、schema 差異、seed 補返 + seed dedup）；全套 **205 passed**。
- （2026-09-30）**Live smoke 實測**（真 OpenD `127.0.0.1:11111`）：HK ret=0 / 3798 rows、US ret=0 / 13111 rows；確認欄位清單冇 `english_name`、`name` 簡體中文（HK.00700 →「腾讯控股」）、HSI substring 搜尋 Market.HK 零命中（主力連續合約唔列出）→ seed 方案驗證。限制已入 AGENTS.md 知識庫。
- （2026-09-30）**K 線週期按鍵組**：`ui/main_window.py` control bar 嘅 K 線週期由 `QComboBox` 換做 **checkable QPushButton group**（`QButtonGroup.setExclusive(True)`，`:checked` 用 `cfg.last_price_color` 背景 + bold、hover 跟 grid 色）——一鍵直切唔使開 dropdown；新增 `current_period()`（checked button text，fallback `KLINE_TYPES[0]`），`_do_switch()` 一次傳齊 code+period → `engine.switch()`（returnPressed / buttonClicked 共用同一入口，避免連續兩次 switch）。
- （2026-09-30）**volume subpane 填充矩形**：`ui/candle_chart.py` volume bar 由 1px 細線改成同蠟燭 body 一樣寬嘅填充矩形（`body_w = max(1.0, slot * 0.7)`，紅漲綠跌跟 config），低成交量時 `max(1.0, h_px)` 保底可視。
- （2026-09-30）**seed 擴充至三隻 HK 指數期貨主連**：`engine/futu_engine.py::_SEED_ENTRIES` 加 `HK.HHImain`（国指期货主连）/ `HK.MHImain`（小恒指期货主连），`_CODE_ALIASES` 同步加 upper→canonical 映射；三隻均經 `get_market_snapshot` live 驗證。US/SG 指數期貨本帳號行情權限不足、官方名稱無法核實 → 暫唔 seed（避免 seed-first dedup 用錯名 shadow API 正確名）。
- （2026-09-30）新單測：`TestFetchCatalog` 8 項斷言更新為 3 seeds；全套 **205 passed**。

### Fixed
- （2026-09-30）**主力連續合約代碼大小寫敏感 bug**（live 使用發現）：`switch()` 嘅 `.strip().upper()` 會將 `hk.hsimain` 變 `HK.HSIMAIN`，OpenD 拒收（「未知股票 HSIMAIN」）→ 新增 `_CODE_ALIASES` + `_normalize_code()`（upper 後映返正規形式），switch 路徑同啟動 `.env` code 路徑一致應用；5 項新單測（全套 **165 passed**）。限制已入 AGENTS.md 知識庫。

### Next
- Step 2 後續候選：ICT 指標 overlay（FVG / Order Block / Kill Zone）、切換歷史記錄、多標的並排顯示

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
- （2026-09-30）`ui/candle_chart.py`：全屏幕深色主題蠟燭圖表（純 QPainter，零第三方圖表庫）——蠟燭 wick+body（紅漲綠跌跟 config 慣例/override）、volume subpane（plot 高度 22%）、nice-step（1/2/2.5/5×10^n）水平 grid + 右軸 price label、時間軸 label（~90px 間隔，intraday 顯示 HH:mm）、last-price dashed line + 右軸 tag、crosshair + OHLCV readout；**backpressure**：`update_bars()` 只記錄 immutable snapshot + singleShot `QTimer(30ms)` coalesce repaint（tick burst 最多 ~30fps，永遠 render 最新）；純 layout 函數（`visible_slice`/`price_range`/`volume_max`/`nice_step`/`time_label`/`fmt_price`）抽離可獨立單測；`add_overlay(fn)` 預留 ICT FVG / Order Block / Kill Zone 圖層擴展點。
- （2026-09-30）`ui/main_window.py`：全屏幕終端主窗口——CandleChart central widget + FutuEngine signal 接線（`history_ready`/`bars_changed` → `chart.update_bars`、`status`/`error` → status bar，callback thread emit 經 Qt auto-queue 過 GUI）、深色主題 stylesheet 跟 `.env` 配色、F11 全屏幕切換 / Esc 關閉、`shutdown()` clean stop（idempotent）。
- （2026-09-30）`tests/test_candle_chart.py`（20 項，零 Qt app 依賴）：visible_slice 右 pin/邊界、price_range 5% padding + flat fallback、volume_max 除零防護、nice_step mantissa 不變量、time_label intraday/day-week-month、fmt_price；全套 **136 passed**。
- （2026-09-30）`main.py`：應用入口——`Config.from_env()`（未知 KLINE_TYPE → stderr 報錯 exit(1)，唔開窗口）→ QApplication + MainWindow `showFullScreen()`；SIGINT（Ctrl+C）handler 排程 `QTimer.singleShot(0, app.quit)`（行完 event loop 先收，唔喺 signal context 做重活）；`exec()` 返回後 finally `window.shutdown()`（close OpenD ctx + join setup thread）。
- （2026-09-30）`.env.example`：全部配置鍵範本（預設值同 README 表格一致，繁中註釋），複製做 `.env` 即用。
- （2026-09-30）**Live smoke test 實測通過**（offscreen QApplication + 真 OpenD `127.0.0.1:11111`）：連線成功 → `history_ready` 300 根（HK.HSImain K_1M，夜期數據 `2026-09-29 22:01`→`2026-09-30 03:00`）→ QUOTE 訂閱成功 → `stop()` 乾淨斷線（CallClose）。全套 **136 passed**，**Step 1 完成**。

### Next
- （已完成）Step 2 · Commit 1：運行時切換標的與 K 線週期 → 見上方 [Unreleased] Step 2
