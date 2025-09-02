# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這個專案是一個加密貨幣追蹤和投資諮詢的 Web 應用程式。專案的目標是為主流加密貨幣（BTC、ETH、BNB）提供數據驅動的投資建議，涵蓋短期（1-7 天）、中期（1-3 個月）和長期（6 個月以上）的投資期間。

## 專案結構

專案採用前後端分離架構：

```
crypto-tracker/
├── backend/                 # Python FastAPI 後端
│   ├── main.py             # 主應用程式入口
│   ├── models.py           # 資料模型
│   ├── requirements.txt    # Python 依賴
│   └── venv/              # Python 虛擬環境
├── frontend/              # React 前端
│   ├── src/              
│   │   ├── App.js        # 主應用程式組件
│   │   ├── App.css       # 應用程式樣式
│   │   └── index.js      # React 入口點
│   ├── package.json      # Node.js 依賴和腳本
│   └── public/           # 靜態資源
├── database/             # 資料庫相關檔案
├── docs/                # 文檔
└── scripts/             # 腳本檔案

.claude/
└── agents/              # Claude Code 專用代理人配置
    ├── ml-evaluation-architect.md
    ├── backend-engineer.md
    ├── frontend-engineer.md
    ├── ui-ux-designer.md
    └── [其他代理人配置...]
```

## 開發命令

### 後端 (FastAPI)
```bash
cd crypto-tracker/backend

# 安裝依賴
pip install -r requirements.txt

# 啟動開發伺服器
python main.py
# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 運行測試
pytest
```

### 前端 (React)
```bash
cd crypto-tracker/frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm start

# 建置生產版本
npm run build

# 運行測試
npm test
```

## 技術架構

### 後端 (Python/FastAPI)
- **框架**: FastAPI 0.104.1
- **ASGI 伺服器**: Uvicorn
- **資料庫**: PostgreSQL (透過 SQLAlchemy 2.0.23 和 Alembic)
- **數據分析**: Pandas, NumPy, TA-Lib 用於技術分析
- **外部 API**: 
  - yfinance 0.2.28 用於金融數據
  - python-telegram-bot 20.6 用於 Telegram 整合
- **背景任務**: Celery 5.3.4 配合 Redis
- **HTTP 客戶端**: httpx 0.25.1

### 前端 (React)
- **框架**: React 18.2.0
- **UI 庫**: Ant Design 5.11.0
- **圖表**: Recharts 2.8.0
- **HTTP 客戶端**: Axios 1.6.0
- **路由**: React Router DOM 6.17.0
- **樣式**: Styled Components 6.1.0
- **日期處理**: Moment.js 2.29.4

### 核心功能架構
1. **數據收集層**: 實時加密貨幣價格、市場指標和新聞情感分析
2. **分析引擎**: 技術指標（RSI、MACD、移動平均線）、情感評分、風險評估
3. **投資諮詢系統**: 針對不同時間範圍的演算法驅動建議
4. **用戶介面**: 投資組合追蹤和個人化洞察的儀表板
5. **訂閱系統**: 具有分層功能的免費增值模式

## MCP 工具整合

專案已配置以下 MCP (Model Context Protocol) 伺服器：

- **exa**: Web 搜尋和內容發現
- **upstash-context-7-mcp**: 上下文管理和儲存  
- **wonderwhy-er-desktop-commander**: 桌面自動化功能
- **hwangwoohyun-nav-yahoo-finance-mcp**: Yahoo Finance 數據整合
- **falahgs-flux-imagegen-mcp-server**: AI 圖像生成
- **maxvint-mcp-crypto-research**: 加密貨幣研究和分析
- **martin-songzy-coin-mcp-server**: 硬幣價格和市場數據

## 環境配置

關鍵環境變數配置在 `.env`：
- `TELEGRAM_BOT_TOKEN`: Telegram 機器人整合
- `TELEGRAM_CHAT_ID`: 通知目標聊天室
- `GOOGLE_API_KEY`: Google 服務整合
- `SMITHERY_API_KEY`: Smithery MCP 伺服器存取

## 專業代理人

專案使用位於 `.claude/agents/` 的專業 Claude Code 代理人：

- **ml-evaluation-architect**: 建立全面的 ML 評估框架
- **backend-engineer**: API 和基礎架構開發
- **frontend-engineer**: UI 和用戶體驗實作
- **ui-ux-designer**: 用戶介面設計和體驗優化
- **applied-ml-engineer**: ML 模型部署和整合
- **product-manager**: 功能優先順序和業務對齊
- **tech-lead**: 架構決策和技術監督

## 開發工作流程
1. 優先調用agents 進行工作
2. 使用 `ml-evaluation-architect` 代理人建立評估框架和數據管道設計
3. 利用 `backend-engineer` 進行 API 開發和數據處理服務  
4. 使用 `frontend-engineer` 開發儀表板和用戶介面組件
5. 利用 `ui-ux-designer` 進行用戶體驗優化和設計系統開發
6. 使用可用的 MCP 工具進行數據收集和外部服務整合
7. 遵循評估優先的方法，建立全面的測試和基準

## 重要注意事項

- 專注於主流加密貨幣（BTC、ETH、ADA）的初始實作
- 對金融數據實施適當的數據驗證和錯誤處理
- 確保 ML 管道具有版本控制的可重現性
- 為可擴展性和實時數據處理要求而設計
- 維護金融應用程式的安全最佳實踐
- 在開始工作前檢查是否有上一份總結報告以便快速了解當前狀況
- 若快要達到使用上限請使用/compact 指令對當前的工作作出總結