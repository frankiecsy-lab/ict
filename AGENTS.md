# AI 自動進度管理、記憶與 Git 全自動版本控制規範 (`AGENTS.md`)

本檔案定義了所有 AI 編碼代理（AI Coding Agent）必須嚴格遵守的強制性工作流規則、專案標準與開發約束。**在修改任何代碼或執行 Git 操作之前，你必須完整閱讀並嚴格執行這些規則。**

---

## 1. 核心開發環境與溝通語言
*   **開發環境**：Windows 11 + PyCharm + Claude Code。
*   **溝通語言**：在開發、日誌記錄與對話過程中，**全程必須使用繁體中文**與開發者溝通。
*   **環境相容性**：所有腳本與指令編寫必須原生支援 Windows 11 環境，檔案路徑處理優先使用相容性工具（如 Python `pathlib`）。

---

## 2. 🚨 核心工作流約束：同步重構與更新 `README.md`
為了確保專案進度與架構設計「事實來源唯一」，任何涉及功能增刪或技術調整的任務，必須在**同一次迭代/提交**中同步重構 `README.md`。

### 📄 更新觸發條件
只要你的任務或程式碼變更涉及以下任一項，你**必須**立即開啟並重構更新 `README.md`：
*   ✨ **新功能**：新增了應用程式介面（API）端點、使用者介面（UI）模組、核心業務邏輯或用戶流程。
*   🗑️ **刪減功能 / 棄用**：刪除或棄用了某些功能、清成了過時的路由、或移除了不再使用的設定參數。
*   🏗️ **方案架構與原理**：系統拓撲、資料流向、背景任務、快取策略、設計模式、或核心演算法有任何調整。
*   🛠️ **技術棧與依賴**：升級、新增或移除了關鍵第三方依賴、配置檔結構變更、或改變了底層實現技術。

### 🔄 標準更新與重構流程
1.  **計畫階段核對**：在修改代碼前，先評估本次改動會影響 `README.md` 的哪些章節（如功能特性、系統架構、技術棧）。
2.  **置頂進度更新**：將本次的更新摘要，以「最新進度/發佈日誌」的形式置頂寫入 `README.md`，讓 GitHub 專案首頁能即時反映最新狀態。
3.  **內文深度重構**：除了置頂摘要外，必須**同步修改 `README.md` 對應的章節內文**（例如刪減了 A 功能，就必須把 `README.md` 內文中的 A 功能介紹或架構圖說明一併剔除/修正），確保文件內容與代碼庫當前狀態 100% 精準吻合。
4.  **發佈日誌同步**：每完成一個核心功能，須同步在 `CHANGELOG.md` 記載更新摘要，方便追蹤。
5.  **無縫接手目標**：確保任何全新、獨立的 AI 代理在讀取 these `.md` 文檔後，都能**無時差馬上接手**，並完全掌握最新功能的開發進度與業務邏輯。

---

## 3. 🚨 核心工具鏈約束：全自動切片讀入機制（防止快取抖動死循環）
為了防止本地模型在處理大型檔案時，因為上下文空間暴增而引發無限自動壓縮與失憶報錯，你**必須強制讓工具呼叫進入全自動切片模式**。

### 🛠️ 關鍵權杖與檔案處理硬性規則：
- **全自動追加行數限制**：當你需要讀取、分析或檢視專案內任何檔案（特別是位於 `tests/` 目錄下的測試檔案如 `test_futu_engine.py`，或任何超過 200 行的程式碼檔案）時，你被**硬性禁止**直接讀取整個檔案的完整內容！
- **剛性限制參數**：你在呼叫 `view_file` 或 `read` 工具時，**必須全自動、強制地在 JSON 參數內加上行數限制**。單次工具呼叫所抓取的程式碼**嚴禁超過 100 行**！正確的自動化切片呼叫範例如下：
  ```json
  { "path": "檔案路徑", "limit": 100 }
  ```
  或者在需要閱讀後續內容時自動遞增偏移量：
  ```json
  { "path": "檔案路徑", "offset": 101, "limit": 100 }
  ```
- **禁止無意義重複讀取**：一旦某個切片區間的程式碼被讀入快取，你必須立刻使用 `edit_file` 工具執行修改任務。絕對不准重複呼叫讀取工具去重新載入無關或重複的程式碼。
- **安全退路機制**：萬一遇到「檔案尚未被讀取」或「自動壓縮陷入死循環」等工具鏈中斷錯誤，**請立即停止呼叫所有檔案相關工具**，並禮貌地請使用者直接將特定的程式碼片段複製並貼上到對話視窗中。

---

## 4. 測試與錯誤自救機制
*   **先測試後提交**：執行 Git 提交前，必須自動運行專案的測試指令。測試通過後方可觸發自動推送（PUSH）；若測試失敗，則自動進入修復流程。
*   **防無效循環死鎖**：方針針對同一錯誤連續修復超過 **3 次**仍告失敗時，AI 必須立即停止自動修改，盤點已嘗試的方案，並向開發者回報尋求引導。
*   **安全還原**：若修改導致系統崩潰或大規模功能退化，須善用 Git 工具將代碼還原至健康狀態，嚴禁將崩潰代碼推送遠端。
*   **測試環境清理**：
    *   當所有功能測試完成、準備進行 Git 提交前，**必須自動清理環境**。
    *   凡是為了本次測試而臨時建立的虛擬資料、臨時測試腳本（例如 `test_tmp.py`、`dummy_data.json` 等臨時檔案），**必須一律徹底刪除**，嚴禁將測試廢料提交進代碼庫。
    *   **【核心禁令】嚴禁刪除本地的 `venv` 虛擬環境資料夾！** 
    *   **【依賴維護】** 若測試與開發期間有新增、變更或移除 Python 第三方套件，必須在清理階段自動執行 `pip freeze > requirements.txt`，以動態同步並清理專案的依賴套件清單。

---

## 5. Git 全自動版控與部署規範
*   **原子化提交**：每當完成**一個獨立功能**或**一個修復步驟**，必須即時執行 Git 流程。
*   **【版控前置置頂動作】**：在執行 `git add .` 之前，AI **必須確保已完成 `README.md`、`CHANGELOG.md` 文件的進度更新與深度重構**，嚴禁提交未同步進度與架構說明的代碼。
*   **全自動自動化**：自動執行 `git add .`、`git commit` 並且 `git push` 到遠端代碼庫。
*   **日誌規範**：
    *   必須使用**繁體中文**編寫變更日誌（Commit Message）。
    *   內容必須詳細記載本次提交的修改內容、流程邏輯以及對整體專案的影響。
*   **遠端安全外殼協定（SSH）自動部署規範**：
    *   每次本地成功推送遠端代碼庫後，AI 必須**立刻自動執行部署指令**。
    *   必須利用 Windows 11 本地的 SSH 工具，依據 `.env` 設定的伺服器資料連線至遠端伺服器。
    *   自動在遠端伺 sensory 對應的網站資料夾執行部署流程（例如：`git pull`、重新安裝依賴、重啟服務、或清除伺服器快取）。
    *   部署完成後，必須自動檢查伺服器狀態（如透過網路傳輸工具 `curl` 測試網站狀態碼），確認遠端網站更新成功且運行正常後，方可結束任務。
*   **工作匯報規範**：
    *   每次功能製作、修改或修復完成，並**成功自動部署至伺服器後**，在對話視窗內**必須使用繁體中文**向開發者進行簡短匯報。
    *   匯報內容必須清晰拆解：**【製作原理】**（背後使用了什麼技術、設計模式、底層邏輯或核心演算法）以及**【代碼運行流程與部署狀態】**（從頭到尾資料是怎樣流動的、遠端部署與運行是否一切正常）。

---

## 6. 機密資料與環境變數管理
*   **唯一事實來源**：專案運作與部署所需的所有伺服器 IP、SSH 帳號密碼、API 網址、模型上下文協議（MCP）參數、密碼、金鑰（包括 TTLOCK、富途等）等敏感資料，**必須優先讀取 `.env` 檔案**。
*   **動態更新機制**：如果使用者在對話視窗中提供了新的密碼、權杖（Token）或金鑰，AI 必須在驗證該資料有效及可用後，**第一時間自動更新或寫入 `.env` 檔案**。
*   **安全防护**：嚴禁將 `.env` 檔案或任何明文密碼提交至 Git 倉庫（必須在 `.gitignore` 中將其忽略）。

---

## 7. 開發知識庫與踩坑記錄
*   **經驗動態沉澱**：開發過程中凡是發現**重要技術限制**（如 API 頻率限制、硬體瓶頸）、**關鍵說明書/官方文檔網址**、或**耗時很久才解開的特殊錯誤（Bug）**，必須馬上寫入專案知識庫。
*   **記錄存放位置**：
    *   如果是全域或跨模組的重大限制，直接更新在本 `AGENTS.md` 的最底部 [附錄：開發知識庫]。
    *   如果是特定模組的細節，則在該模組目錄下建立或更新 `README.md`。
*   **記錄格式規範**：必須用簡潔的繁體中文列明：
    *   **【問題/限制】**：簡述遇到了什麼（例如：某 API 每分鐘限制 60 次）。
    *   **【正確資源】**：附上好不容易找到的官方正確說明書連結（例如：[官方說明書網址]）。
    *   **【解決/避坑方案】**：AI 與開發者最終採用的應對程式碼邏輯或策略，確保下次遇到時能直接秒殺。

---

## 附錄：開發知識庫（隨時動態追加）

### 📌 核心 API 說明書與文件速查表

#### 1. 🥈 輔助對照：富途 Futu 官方 API (FutuOpenD)
*   **【名稱】**：富途命令行 OpenD 啟動與參數配置規範
*   **【正確資源】**：https://futunn.com
*   **【備註說明】**：此網址**僅作為輔助參考與功能對照用途**。當開發港量（HKQuant）相關功能遇到邏輯不清晰（例如：搶行情權限、特定 K 線參數、到價提醒回呼函式）時，可閱此官方文件的底層邏輯進行代碼設計。

#### 2. 🥉 PySide6/Qt：QStandardItem Display/Edit role 耦合（無法雙 role）
*   **【問題/限制】**：喺本專案嘅 PySide6 6.11.2 / Qt6 版本，`QStandardItem` **唔支持獨立嘅 `DisplayRole` 同 `EditRole`**——兩者係耦合嘅，最後 set 嗰個 role 會連帶覆蓋另一個。實測：constructor 設 full text 再 `setData(code, EditRole)` → Display/Edit 都變 code；反之先 `setData(EditRole)` 再 `setData(DisplayRole)=full` → 兩個都變 full。所以「dropdown popup 顯示完整名稱、輸入欄只寫入 code」嘅雙 role 方案**行唔通**。
*   **【正確資源】**：PySide6 / Qt `QStandardItemModel` 官方文檔（role 機制）；本專案實測 probe（offscreen）。
*   **【解決/避坑方案】**：要「dropdown 顯示 A、輸入欄寫入 B」時，**唔好靠 model role**——model item 用完整顯示字串（dropdown 顯示），喺 `QCompleter.activated` handler 內用純函數還原目標字串後 `setText()` 強制覆蓋。本專案即係 `ui/stock_completer.py::code_from_completion(text, mapping)`：mapping hit → canonical code、miss → 取 display_text 第一 whitespace token（code 永遠係第一 token）兜底，`_on_code_activated` 一律 `setText(code)`。另注意：offscreen QPA **無法驅動 completer popup 嘅鍵盤/滑鼠選中**（`setCompletion()` 喺 PySide6 未 expose、`activated.overloads()` 亦唔可用），所以「選中後寫入輸入欄」呢條路徑只能靠純邏輯 + handler 強制覆蓋保證，唔好期望 offscreen 實測到。

#### 3. 🥉 PySide6/Qt：QCompleter `setCompletion()` 喺 `activated` **之前**將完整 display_text 寫入輸入欄
*   **【問題/限制】**：popup 開住撳 Enter（或 mouse click 選中）時，Qt 內部 `QCompleter::complete()` / `setCompletion()` 會**先**將選中 item 嘅完整文字（本專案 = `display_text`「code + 中文名 + 英文名」雙空格 join）寫入 QLineEdit，**然後**先 emit `activated` signal。即係話：淨係靠 `activated` handler 做 `setText(code)` 強制覆蓋，喺 signal 觸發前嗰一瞬間輸入欄會短暫持有「code + 名稱」——live 使用時肉眼可見（欄位閃一下完整字串先變返 code）。
*   **【正確資源】**：Qt `QCompleter` 官方文檔（completion flow）；本專案 live 實測。
*   **【解決/避坑方案】**：**加 onChange guard**——接 QLineEdit `textChanged`，欄位一出現空白字符（= code + 名稱混入）即刻取第一 whitespace token 剝離返純 code。本專案即係 `ui/main_window.py::_on_code_text_changed()`：`blockSignals(True)` 包 `setText(code)` 避免多餘 round-trip；剝離後無空白 → 再觸發嘅 textChanged 自然 no-op，**唔會死循環**。呢個 guard 兜晒所有寫入路徑（手動輸入 / dropdown Enter / activated），比淨係靠 activated handler 強制覆蓋更穩。注意：guard 用 `textChanged`（唔係 `textEdited`）——`textEdited` 只捕獲用戶鍵盤輸入，捕唔到 completer 程序化 `setText()`；要攔截 completer 寫入必須用 `textChanged`。

#### 4. 🥉 PySide6/Qt：`QPushButton.clicked` 有 `(bool checked)` 重載——直接 connect 可選參數方法會靜默綁定 bool 版（no-op bug）
*   **【問題/限制】**：PySide6 6.11.2 / Qt6 嘅 `QAbstractButton.clicked` signal **同時 expose 兩個 overload**：無參數版同 `(bool checked)` 版。當 connect 嘅 Python slot 簽名「可以接受一個可選參數」（例如 `def zoom_in(self, steps: int = 1)`），PySide6 會綁定到 **`(bool checked)` 版**——click 時實際調用 `zoom_in(False)`，`steps=False` → `+False == 0` → guard `delta == 0` no-op。**表面完全冇報錯、signal 有 emit、方法有被 call，但行為係靜默無效**（本專案實測：offscreen probe 打 log 見到 `zoom_in called!` 但 `_view_count` 唔變）。
*   **【正確資源】**：PySide6 signal overload 綁定機制；本專案 offscreen probe 實測（click → slot 收到 `False`）。
*   **【解決/避坑方案】**：**用 lambda 包零參數調用**——`btn.clicked.connect(lambda: self.chart.zoom_in())`，lambda 無參數 → PySide6 只能綁定無參數 overload，永遠傳唔到 bool。本專案即係 `ui/main_window.py::_build_control_bar()` 嘅放大/縮小按鍵接線。通用規則：connect 任何**帶可選參數**嘅方法去 Qt signal 前，先確認該 signal 有冇多 overload（`clicked`、`activated`、`pressed` 等 button/completer signal 都有）；唔確定就一律 lambda 包零參數調用。另注意：offscreen QPA 下 `btn.click()` 可以正常驅動 signal（同 completer popup 唔同），所以呢類接線 bug **可以**用 offscreen widget 單測抓到——本專案即係 `tests/test_main_window.py::test_zoom_buttons_wired_to_chart`。

#### 5. 🥉 Futu OpenD：`request_history_kline` 窗口寬度上限（~55 年）——過長會 `ret=-1 F3CNN返回错误`
*   **【問題/限制】**：OpenD `request_history_kline` 對**過長嘅 start/end 窗口**會拒收。實測邊界（HK.HSImain K_MON）：50yr / 55yr OK、60yr → `ret=-1 F3CNN返回错误，可能是参数错误或者断线`。本專案 `history_window()` 原公式對大週期 × 大 count 會算出百多年窗口（K_MON=43200min × count=1000 ≈ **123 年**）→ fetch raise → `_reconfigure()` rollback → **圖表靜默保持舊數據**（表現成「撳月K冇反應、仲係顯示週K」——唔會報錯，好難察覺）。
*   **【正確資源】**：本專案 live probe 實測（逐段試窗口跨度搵臨界點）；futu-api `request_history_kline` 文檔。
*   **【解決/避坑方案】**：`engine/timeutil.py::history_window()` 加 `_MAX_WINDOW_DAYS=40*365` clamp——窗口寬度上限 **40 年**（遠低於 ~55 年臨界點、留 ~15 年安全餘量，且已覆蓋 HK.HSImain 全部可用歷史 ~21 年）。通用規則：任何「按週期 × count 估算窗口」嘅邏輯都要 clamp 上限；大週期（K_MON/K_QUARTER/K_YEAR）尤其要防。另注意：clamp 後 K_MON 返回 **256 根**（= 全部可用月線，少於 history_count），分頁 tail 邏輯天然處理——唔會報錯、只係拿晒有嘅數據。

#### 6. 🥉 PyInstaller：`--collect-submodules PySide6` 令 build 極慢（~10min+）；futu data files 要明確 `--collect-data futu`
*   **【問題/限制】**：(1) `--collect-submodules PySide6` 會分析 **全部** PySide6 submodules（QtWebEngineCore / Qt3D / QtCharts…），Windows build 實測 >10 分鐘（background task 直接 timeout）——完全唔需要，因為 PyInstaller 內置 `hook-PySide6.py` 已經用 `pyside6_library_info.collect_extra_binaries()` 自動收集晒所有 Qt binaries + plugins（platforms/qoffscreen、styles、imageformats…）。(2) `futu/__init__.py:117` import 時讀取 package 內 data file `VERSION.txt`——PyInstaller **唔會**自動收集第三方 package 嘅 data files → frozen binary 啟動即 crash：`FileNotFoundError: .../_internal/futu/VERSION.txt`。
*   **【正確資源】**：PyInstaller 官方文檔（hooks / collect-data）；本專案實測（Windows + WSL Ubuntu）。
*   **【解決/避坑方案】**：build flags 淨係 `--collect-data futu`（收集 VERSION.txt / proto 等 data files，唔會分析多餘 submodules）——見 `scripts/build_exe.py` / `scripts/build_ubuntu.sh`。通用規則：frozen app 啟動 crash 喺第三方 package import 時讀 file → 90% 係漏咗 `--collect-data <pkg>`；Qt bindings 唔好手動 collect submodules（內置 hook 已處理）。另注意：PyInstaller onedir 產物目錄名 = `--name` 值（`dist/ICT-Trader/`、`dist/ict-trader/`），build 腳本要 rename 做平台標識名；Windows filesystem case-insensitive——`dist/ICT-Trader` 同 `dist/ict-trader` 係同一個目錄，雙平台 build 唔好同時喺同一 repo 跑。
*   **【補充（產物膨脹）】**：用**裝晒成百套件嘅 global Python** build 會令 PyInstaller `hook-pandas.py` 將 pandas optional deps（torch/cv2/transformers/scipy…，只要 site-packages 有就收集）全部打入產物——本專案實測 **1.5GB vs 乾淨 venv ~300MB**。兩邊 build 腳本都改用**獨立乾淨 venv**（`.venv-win` / `.venv-ubuntu`，只 pin requirements.txt 必要依賴）。

#### 7. 🥉 PyInstaller frozen：`.env` 要讀 exe 旁邊（唔係 `_MEIPASS`）+ windowed build 冇 console
*   **【問題/限制】**：frozen onedir 模式下 `sys._MEIPASS` 係 temp dir（啟動時解壓、退出即刪），用戶改唔到；而 `Path(__file__)` 喺 frozen 後指向 `_internal/` 內——兩者都唔適合放用戶可編輯嘅 `.env`。另外 `--windowed` build **冇 console**：`sys.stdout/stderr is None`，配置錯誤如果淨係 `print(..., file=sys.stderr)` → 用戶完全無從得知點解 app 即刻退出（靜默閃退）。
*   **【正確資源】**：PyInstaller 官方文檔（Runtime Temporary Folder / Windows GUI apps）；本專案實測。
*   **【解決/避坑方案】**：`config.py::_default_env_path()`——frozen 時 `.env` = `Path(sys.executable).with_name(".env")`（exe 旁邊，用戶部署可改、改完重開 app 生效），開發模式照舊專案根目錄；build 腳本自動由 `.env.example` 生成預設 `.env` 入產物夾。`main.py::_report_config_error()`——frozen + `sys.stdout is None`（windowed）→ `QMessageBox.critical` 彈出，否則 stderr。通用規則：任何「用戶可編輯配置」喺 frozen app 都要放 exe 旁邊或 `%APPDATA%`，唔好放 `_MEIPASS`；windowed build 嘅所有錯誤回報都要有 GUI fallback。

#### 8. 🥉 Futu OpenD：`query_subscription()` 係訂閱狀態唯一權威來源 + 「帳本+定時重試」清理洩漏模式
*   **【問題/限制】**：OpenD `unsubscribe()` 對「同一 code 訂閱未滿 1 分鐘」會拒收（實測「Basic訂閱時間過短」）→ 切換標的時舊訂閱**實際未移除、持續佔用額度**（洩漏）。純靠 handler per-row code filter 只係過濾 push，**清唔走 OpenD 端嗰筆訂閱**。另外 `unsubscribe` 失敗後冇任何 API 直接話你邊啲 code 仲訂閱緊——本地記錄會同 OpenD 實際狀態漂移。
*   **【正確資源】**：futu-api `query_subscription(is_all_conn)` 文檔（返回 dict：`total_used/own_used/remain/sub_list{subtype:[codes]}`）；本專案實測。
*   **【解決/避坑方案】**：**SQLite 訂閱帳本 + 定時 reconcile**——(1) 每筆 subscribe/rollback resubscribe 成功 → `store.add(code, ts)`（re-subscribe 同 code → `INSERT OR REPLACE` 重新計時）；unsubscribe 成功 → `remove()`、失敗 → **保留 pending**。(2) 定時 `_reconcile_subscriptions()`（30s daemon thread）：先 `query_subscription(is_all_conn=False)` 攞 OpenD 端**實際**訂閱 code（呢個係唯一權威來源，本地帳本只係輔助計時），再對「已不活躍且 age≥75s」嘅帳本條目重試 unsubscribe + remove；失敗保留下輪再試。(3) **開機自癒**：query 到但帳本冇記錄、非當前 state 的 code（上次 crash 殘留）→ 直接清。通用規則：任何「操作有頻率/時間限制、失敗唔會自動重試」嘅外部資源管理，都應該 (a) 持久化本地狀態 + (b) 用 API 查真實狀態做對帳錨點 + (c) 定時冪等 reconcile——唔好淨係靠「操作當下成功」。另注意：residual 判斷要用 loop **前**嘅 ledger snapshot（`open - active - ledger_before`），避免同 due-loop 重複 unsub 同一 code；query 失敗要跳過該輪（唔改帳本、避免誤刪）。本專案即係 `engine/subscription_store.py` + `futu_engine.py::_reconcile_subscriptions()`。

#### 9. 🥉 ICT Order Block 有效性標準 + OB+FVG confluence（VOB 三重過濾 proxy）
*   **【問題/限制】**：唔係每個 Order Block 都有效——ICT 社群共識「What Makes One Valid」四條件：① **前置流動性掃蕩**（最重要，「No sweep, no order block」：bullish OB 前價格必須先跌破明顯低點再反轉；bearish 對稱）；② 真位移（大實體細影 / FVG 驗證——移動強到喺前後 K 線影之間留下 FVG 先算機構級）；③ **未失效（Unmitigated）**：只有 **body close 穿過 zone 邊界**先算完全失效（wick 唔算），首次回訪剩餘訂單最濃；④ HTF 對齊 + 首次回訪。單週期圖表層只能實作前三個——條件 ④ 要跨時間框架判斷，超出單週期 zone 標記層範圍。
*   **【正確資源】**：[ictkillzone.com ICT Order Block](https://www.ictkillzone.com/ict-order-block)（四條件 + OB+FVG confluence =「最高概率 setup」）；[smartmoneytrader.co OB+FVG Confluence ICT](https://www.smartmoneytrader.co/blog/order-block-fvg-confluence-ict)（獨立佐證：OB unmitigated / FVG unfilled / overlap confirmed checklist）。
*   **【解決/避坑方案】**：本專案 `engine/indicators.py::detect_valid_order_blocks()` = **三重過濾全部通過**：① `_has_liquidity_sweep(bars, j, side, lookback=20)` proxy——窗口 [max(0,j-lookback)..j] 內存在 s<j，其 low（bullish）/ high（bearish）**創下窗口極值**（跌破之前結構）且**到 origin j 為止再冇被跌穿**（終端極值；s==win 起點無 prior 結構可比 → 唔計）；② `ob.end_idx is None`（未失效——現有 OB body-close 失效邏輯已吻合 ICT 規則，wick 唔算）；③ 同方向 FVG 與 OB body **嚴格價格重疊**（`lo=max(bottoms), hi=min(tops), hi>lo`，重用 `confluence_zones()` 公式）。畫**完整 OB body**（唔係重疊帶）做錨點、`end_idx = _min_end(ob.end, min(匹配 FVG ends))`（OB 失效或 FVG 填補都截斷）、每個 OB 最多一個 vob zone。VOB 自含 recompute——內部自算 OB+FVG，**獨立於 ob/fvg 開關狀態**。HTF 對齊 / LTF CISD 計時留待用戶目測（文件註明）。

#### 10. 🥉 ICT Liquidity Levels：BSL/SSL = equal highs/lows 流動性池（pivot swing + 價格聚類）
*   **【問題/限制】**：唔係每個 high/low 都係「流動性」——ICT 概念 **BSL（Buy-Side Liquidity）**= 價格上方嘅 **equal highs**（同一價位被多個 swing high 觸及）→ buy-stop 訂單聚集喺呢度 → **阻力**；**SSL（Sell-Side Liquidity）**= 下方 equal lows → sell-stop 聚集 → **支撐**。機構常「掃」（sweep）呢啲池先反轉。要偵測「equal」需要 (a) 搵出 swing high/low（pivot）、(b) 將相近價位聚類做 pool、(c) 只保留相對於最新價未失效嘅池。
*   **【正確資源】**：ICT 社群共識（BSL/SSL = equal highs/lows liquidity pools）；本專案實測。
*   **【解決/避坑方案】**：`engine/indicators.py::detect_liquidity_levels(bars, pivot=3, min_touches=2, tol_frac=0.002)`——(1) `_swing_points(bars, k, which)` 搵 pivot swing high/low（bar i 嘅 high/low 嚴格極於前後各 k 根；boundary skip，O(n·k)）；(2) `_cluster_by_price(points, tol_frac)` greedy 價格聚類（同 cluster price 差 ≤ `tol_frac × ref` → 同一 pool、price = cluster mean）；(3) 只保留 **≥min_touches** 個 pivot 觸及嘅 cluster（equal highs/lows），再按最新 close 過濾：BSL 要 `price > last_close`（上方）、SSL 要 `price < last_close`（下方）——已穿過嘅池唔畫。線段由首次觸及 bar 畫到右緣（end=None）。繪製 = BSL 粉紅 `#FF80AB` / SSL 深紫 `#7C4DFF` **虛線**（未觸及前係「潛在」位）+ kind label，palette 唯一色。通用規則：任何「equal highs/lows」偵測都要 (a) pivot swing + (b) 價格容差聚類 + (c) 相對最新價過濾——淨係搵局部極值唔夠（要「重複觸及同一價位」先算流動性池）。

#### 11. 🥉 ICT Structure Breaks：BOS vs CHoCH + 「consume pivot after one break」防 spam 模型
*   **【問題/限制】**：**BOS（Break of Structure）**= 順趨勢方向嘅結構突破（continuation）；**CHoCH（Change of Character）**= **首次逆勢**突破 = 反轉訊號。兩者觸發條件完全一樣——「close 穿過最近已確認 pivot swing high/low」，分別只喺方向相對於當前趨勢（順 → BOS、逆 → CHoCH + 翻轉 direction）。兩個坑：(1) **pivot 要 k bars 先確認**——bar s 嘅 high/low 係咪 swing，要等之後 k 根 bar 都唔創新高/新低先至確定（`_is_swing_high/_is_swing_low` boundary → False），所以 marker 天然滯後 k bars；(2) **naive「每根 close 穿過 reference 都標記」會喺單邊市炸彈式刷屏**——穩態趨勢每一根 bar 都 close > last_sh，會每根都畫 BOS。
*   **【正確資源】**：ICT 社群共識（BOS = continuation / CHoCH = reversal）；本專案實測。
*   **【解決/避坑方案】**：`engine/indicators.py::detect_structure_breaks(bars, k=2)`——**趨勢方向 state machine**：`direction ∈ {None,"up","down"}` + `last_sh`/`last_sl`（最近已確認未 break 嘅 swing high/low `(price, idx)`）。逐 bar i：先檢查 close 穿過 last_sh / last_sl → 順勢 BOS、逆勢 CHoCH（翻 direction）；**break 後將該 pivot set None（consume）**→ 同一個 pivot 只觸發一次，之後要等下一個新確認 pivot 先至再有 marker。之後確認 `s=i-k` 係咪新 swing high/low → 更新 last_sh / last_sl。**「consume after one break」模型**係關鍵——避免 spam。繪製 = 每個 marker 喺該 bar 中心 x 畫小三角：direction "up" → high 上方指上、「down」→ low 下方指下（方向用**三角形朝向**編碼、唔係顏色）；BOS 橙 `#FF9100` / CHoCH 品紅 `#E040FB`（palette 唯一色）。通用規則：任何「結構突破」偵測都要 (a) pivot swing k-bar 確認 + (b) 趨勢方向 state machine 分 BOS/CHoCH + (c) consume-after-break 防 spam——淨係比 close vs reference 會刷屏。

#### 12. 🥉 SQLite「單行 JSON blob」持久化模式——UI 狀態記憶（schema 演化 + 原子快照）
*   **【問題/限制】**：要持久化一組**會持續增長嘅 UI 偏好**（標的 / pane 佈局 / per-pane 週期 / 指標開關，日後可能再加 zoom level、主題等），若用「每個字段一欄」嘅 schema，每加一個新字段就要 `ALTER TABLE` + 遷移邏輯；而且多欄寫入唔係原子——崩潰喺中途會留半套狀態（例如 pane_count=4 但 periods 仲係舊值）。
*   **【正確資源】**：本專案實測（純 stdlib sqlite3，零 Qt/futu）；SQLite `INSERT ... ON CONFLICT DO UPDATE`（upsert）文檔。
*   **【解決/避坑方案】**：**單行 JSON blob**——表 `ui_state(key TEXT PRIMARY KEY, value TEXT NOT NULL)`、固定 key='main'，value = 完整狀態 dict 嘅 `json.dumps()`。(1) **schema 演化穩健**：加新字段只改 Python dict，DB schema 完全唔變（無 ALTER TABLE）；(2) **原子語義**：一次 save = 一條 `INSERT INTO ui_state(key,value) VALUES('main',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value`——唔會寫到一半。API：`save(dict)` / `load() -> dict|None`（無記錄 / JSON parse 失敗 / 合法 JSON 但非 dict → **一律 None**，呼叫方 fallback 預設值、唔 crash）/ `clear()`。**健壯性鐵律**：`load()` 必須 try/except `ValueError`(JSON decode) + `TypeError` + `isinstance(dict)` 三重檢查——任何損壞都當「無記憶」而非崩潰。本專案即係 `engine/ui_state_store.py::UIStateStore`。**Thread safety**：per-call connection（每次 save/load 開自己 connection + commit/close，`_tx()` contextmanager）→ 唔共享 connection object、天然 thread-safe；低頻極小寫入唔使 WAL。通用規則：任何「一組會增長嘅偏好/狀態快照」持久化都應該用單行 JSON blob（schema 演化 + 原子），而唔係拆多欄——除非需要按字段 query/index（本專案 UI 狀態永遠整包讀寫、無此需求）。另注意：DB 路徑跟 `.env`/`subscriptions.db` 同邏輯（開發=專案根目錄、frozen=exe 旁邊**唔係 `_MEIPASS`**），gitignored `*.db`。

#### 13. 🥉 ICT Premium/Discount + OTE：dealing range equilibrium split + Fibonacci golden pocket 62%–79%
*   **【問題/限制】**：**Premium/Discount**——唔係每個價位都「中性」，ICT 將 dealing range（一段行情嘅 max high / min low）以 **equilibrium=(hi+lo)/2** 分兩半：premium `[eq,hi]`「貴」（偏空、等回調入 discount 先買）、discount `[lo,eq]`「賤」（偏多）。**OTE（Optimal Trade Entry）**——唔係每個回撤都係好入場位，ICT 共識機構常喺 **Fibonacci golden pocket 62%–79%** 區間掛單（0.618–0.79 之間），呢個帶先算高概率入場。兩個坑：(1) dealing range 要用**有限 lookback 窗口**（唔係全部歷史）——用全數據會令 hi/lo 被很久以前嘅極值拉走、equilibrium 失去「當前行情」意義；(2) OTE 要**最近 pivot swing high/low**做錨點（唔係任意 bar），且 bullish/bearish 方向對稱——淨係比一個固定百分比會漏咗方向性。
*   **【正確資源】**：ICT 社群共識（Premium/Discount = dealing range equilibrium split；OTE = Fibonacci golden pocket 62%–79%）；本專案實測。
*   **【解決/避坑方案】**：`engine/indicators.py::detect_premium_discount(bars, lookback=50)`——win=bars[-lookback:]、hi=max high / lo=min low，len<2 或 hi<=lo → `()`；否則 `(Zone("premium","bearish",0,None,hi,eq), Zone("discount","bullish",0,None,eq,lo))`（start=0/end=None = **全寬背景帶**、唔係價格錨定矩形——PD 係「區域」概念）。`detect_ote_zones(bars, k=3)`——重用 `_swing_points()`：最近 pivot swing high H + 之前 swing low L → bullish OTE `[H−0.79×span, H−0.62×span]`（start_idx=hi_idx）、bearish 對稱（最近 swing low L' + 之前 swing high H'）；len<2k+1 → `()`。繪製：PD = **全寬背景帶**（premium 紅 `#F23645` / discount 綠 `#089981` fill alpha 18 + equilibrium 線 `#CFD8DC` 實線 width 1 + "EQ" label，clip 入 price_r）；OTE = 價格錨定矩形（金黃 `#FFC400`、fill alpha 50、**2px 邊框**——同 vob 一層級視覺優先級）。通用規則：任何「dealing range / equilibrium」類指標都要 (a) 有限 lookback 窗口（唔係全歷史）+ (b) hi/lo 極值 + (c) midpoint split；任何「Fibonacci 回撤入場位」都要 (a) pivot swing high/low 做錨點 + (b) golden pocket 62%–79% 帶 + (c) bullish/bearish 方向對稱。

#### 14. 🥉 ICT Session High/Low：per-day 交易日 high/low 範圍線（`_date_groups()` 共用分組）
*   **【問題/限制】**：**Session High/Low** = 每個交易日嘅最高 high / 最低 low——當日實際成交範圍上下界。兩個坑：(1) **線段要 per-day 跨當日 bar 範圍（start/end = 當日 first/last idx），唔係全寬**——全寬會喺多日圖表上令每日 sh/sl 互相重疊成一片、失去「邊個 session」嘅意義；呢點同 Daily ref lines 嘅 Prev Day High/Low/Close（嗰啲先係全寬 end=None）刻意區分。(2) **日期分組邏輯唔好重複寫**——`daily_reference_lines()` 原本自己內聯做「按 time_key[:10] 分組」，加 Session High/Low 時若再抄一份會令兩處行為漂移（改邊漏邊）。
*   **【正確資源】**：ICT 社群共識（Session High/Low = per-day high/low range）；本專案實測。
*   **【解決/避坑方案】**：抽出共用 helper `engine/indicators.py::_date_groups(bars) -> [(first_idx, last_idx), ...]`（按 time_key[:10] 分組、O(n)、月線 key len<10 → 空）——`daily_reference_lines()` **同**新函數 `detect_session_high_low(bars)` 都調用佢（DRY，行為不變、原 daily-ref 測試全綠）。`detect_session_high_low()`：對每個 group `(s,e)` → `sh=max(high[s..e])` / `sl=min(low[s..e])` → `RefLine("sh", sh, s, e)` + `RefLine("sl", sl, s, e)`（start/end = 當日範圍）。繪製：SH 深橙 `#FF6E40` / SL 青檸綠 `#9CCC65` **實線**（當日實際範圍已成交、唔係「潛在」位——同 Liquidity Levels 嘅虛線語義相反）+ kind label，畫喺 ref-lines block 之後。通用規則：任何「按日期分組」嘅指標都應該共用同一個 `_date_groups()` helper；per-day 範圍線段用 start/end = 當日 idx（唔係全寬），先至同「全寬參考線」（Prev Day H/L/C）視覺區分開。

*(此處留空，供 AI 在後續開發中自動填入發現的頻率限制、新官方文檔網址等珍貴經驗)*
