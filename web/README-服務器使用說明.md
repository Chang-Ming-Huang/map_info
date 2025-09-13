# 🌐 本地服務器使用說明

## 問題解決

您遇到的 CORS 錯誤和 JavaScript 重複聲明問題已經修復！

### 🐛 原始問題：
1. **CORS 錯誤**：`file://` 協議無法載入 JSON 文件
2. **重複聲明**：`ReviewManager` 類被重複定義

### ✅ 修復內容：
1. 創建了本地 HTTP 服務器，支持 CORS
2. 修復了 JavaScript 重複聲明問題
3. 提供了自動啟動和瀏覽器打開功能

## 🚀 啟動方法

### 方法一：使用 Python 腳本
在專案根目錄 (`map_info`) 下執行：
```bash
python web/start-server.py
```
腳本會自動在瀏覽器中打開測試頁面。

### 方法二：使用 Windows 批處理（推薦）
進入 `web` 目錄，然後雙擊運行 `start-server.bat`。

## 📱 訪問地址

服務器啟動後，可以訪問：

- **評論模組頁面**：http://localhost:8000/web/shared/reviews.html
- **各種風格頁面**：
  - http://localhost:8000/web/style-bauhaus/
  - http://localhost:8000/web/style-brutalist/
  - http://localhost:8000/web/style-creative/
  - http://localhost:8000/web/style-ethereal/
  - http://localhost:8000/web/style-fintech/
  - http://localhost:8000/web/style-industrial/
  - http://localhost:8000/web/style-volcanic/
  - http://localhost:8000/web/style-dark-blue/
  - http://localhost:8000/web/style-golden/
  - http://localhost:8000/web/style-warm/

## 🧪 評論模組功能

### 評論展示功能包含：
- ✅ JSON 文件自動檢測和載入最新評論數據
- ✅ 評論卡片顯示（姓名、評分、內容、日期）
- ✅ 圖片路徑解析和顯示（支援 Lightbox 檢視）
- ✅ 評論文字截斷和展開功能
- ✅ 「顯示更多評論」分頁功能
- ✅ 響應式設計和互動效果

### 預期結果：
- 自動載入最新的 JSON 評論數據
- 以卡片形式顯示評論文字、星級評分、發布日期
- 載入和顯示評論圖片（點擊放大檢視）
- 支援評論內容截斷和「看全文」展開

## ⚠️ 注意事項

1. **Python 版本**：需要 Python 3.x
2. **端口占用**：如果 8000 端口被占用，腳本會自動報錯
3. **文件路徑**：服務器會自動設置正確的根目錄
4. **停止服務器**：按 `Ctrl+C` 停止

## 🔧 故障排除

### 如果仍然出現 CORS 錯誤：
1. 確保使用 `http://localhost:8000` 而不是直接打開 HTML 文件
2. 檢查瀏覽器控制台是否還有其他錯誤

### 如果圖片無法顯示：
1. 檢查 `images/` 文件夾是否存在
2. 確認圖片路徑是否正確
3. 查看測試頁面的錯誤日誌

### 如果 JSON 數據無法載入：
1. 確認根目錄中有 `.json` 文件
2. 檢查文件名格式是否為 `YYYYMMDD_HHMMSS.json`
3. 查看控制台的詳細錯誤信息
