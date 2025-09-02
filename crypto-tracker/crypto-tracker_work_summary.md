📑 Crypto Tracker 專案工作交接文件
1. 專案背景

這是一個 加密貨幣投資追蹤網站，主要功能是顯示加密貨幣的實時價格與市場數據。
之前遇到的問題是使用 CoinGecko API 會被限流（429 Too Many Requests），導致顯示的價格不是真實的。
因此已經改為使用使用者自己寫的 CryptoAPIs 抓取服務（getCryptoPrice.py），並加入 30 秒快取機制 來節省昂貴的 API 成本。

目前進展：

後端 已完成：

使用 CryptoAPIs 抓取真實價格。

增加快取（30 秒只打一次 API）。

增加備援機制（API 失敗時回退舊方式）。

支援 Mock data（方便開發 UI 階段）。

前端 已完成：

與後端連接，取得 Mock data。

基本 UI 實作（但目前是條列式，不夠專業）。

初步加入 Glassmorphism、主題切換、響應式設計。

2. 已完成的優化

API 整合：整合 CryptoAPIs，確保數據真實性。

成本控制：快取機制避免頻繁呼叫。

數據豐富化：包含 symbol、name、logo、price、change1h、change24h、change7d。

UI 改良方向：已研究 CoinMarketCap / CoinGecko / COIN360 的排版。

Mock Data 支援：開發階段不會消耗 API。

3. 下一步工作（主要任務）
🔹 前端程式碼重構

目前的 App.js 超過 1200 行，是一個大型單體，需要拆成可復用的元件。

建議拆分元件

Header

負責網站標題、主題切換、導航列。

MarketOverview

負責整體市場數據顯示（例如總市值、24h 交易量）。

CryptoCard

單個加密貨幣資訊卡片（名稱、logo、當前價格、漲跌幅）。

RecommendationCard

投資建議或 AI 推薦展示區。

NewsCard

顯示最新的加密貨幣新聞。

UpdateIndicator

顯示最後更新時間，提醒數據刷新狀態。

🔹 公用工具

建立 utils/ 資料夾，抽離以下邏輯：

formatPrice()

formatChange()

formatDate()

WebSocket 管理工具

4. 技術細節

後端

FastAPI (main.py)

getCryptoPrice.py 使用 aiohttp 抓取 CryptoAPIs

Cache 機制（30 秒 TTL）

目前 Mock data 模式開啟（避免 API 花費）

前端

React + WebSocket

CSS：Glassmorphism、Light/Dark mode

App.js 需重構為模組化元件

5. 待辦清單（TODO）

 拆分 App.js 成獨立元件（Header、CryptoCard、MarketOverview、NewsCard、RecommendationCard、UpdateIndicator）

 抽離共用工具至 utils/

 保持 WebSocket 實時更新 功能

 保持 主題切換 功能

 保持 快取數據顯示邏輯

 UI 優化：對齊 CoinMarketCap/Gecko 的專業水準

✅ 目標：
完成重構後，前端程式碼將更具模組化、易於維護，並保持既有功能（即時更新、快取、主題切換）。