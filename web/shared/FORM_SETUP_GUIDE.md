# 預約諮詢表單設置指南

本指南將引導您完成預約諮詢表單與 Google Sheets 整合的完整設置過程。

## 📋 概述

這個解決方案使用 Google Apps Script 作為免費的後端服務，將網站表單提交的資料自動存儲到 Google Sheets 中。完全免費且適合靜態網站使用。

## 🚀 設置步驟

### 第一步：建立 Google Sheets

1. **開啟 Google Sheets**
   - 前往 [sheets.google.com](https://sheets.google.com)
   - 點擊「建立新的空白試算表」

2. **設置表頭**
   - 在第一行輸入以下欄位標題：
     ```
     A1: Name
     B1: Phone
     C1: Message
     D1: Timestamp
     ```

3. **美化表頭（可選）**
   - 選取第一行
   - 設置背景色為藍色 (#4285f4)
   - 設置文字顏色為白色
   - 設置字體為粗體

4. **記錄試算表 ID**
   - 複製瀏覽器網址列中的 ID
   - 範例：`https://docs.google.com/spreadsheets/d/`**`1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`**`/edit`
   - 紅色部分就是試算表 ID

### 第二步：建立 Google Apps Script

1. **開啟 Apps Script**
   - 在 Google Sheets 中，點擊「擴充功能」→「Apps Script」
   - 或直接前往 [script.google.com](https://script.google.com)

2. **建立新專案**
   - 如果是全新專案，會自動建立
   - 專案名稱設為：「築宜系統傢俱-預約表單處理」

3. **貼上程式碼**
   - 刪除預設的 `myFunction()` 函數
   - 將 `google-apps-script.js` 檔案中的完整程式碼複製貼上

4. **修改設置**
   ```javascript
   // 將您的試算表 ID 貼在這裡
   const SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms';

   // 可選：設置通知郵件地址
   const NOTIFICATION_EMAIL = 'your-email@example.com';
   ```

### 第三步：測試 Apps Script

1. **執行測試函數**
   - 在編輯器中選擇 `testFormSubmission` 函數
   - 點擊「執行」按鈕
   - 第一次執行需要授權權限

2. **授權權限**
   - 點擊「審查權限」
   - 選擇您的 Google 帳戶
   - 點擊「進階」→「前往築宜系統傢俱-預約表單處理（不安全）」
   - 點擊「允許」

3. **檢查測試結果**
   - 返回 Google Sheets
   - 應該會看到一筆測試資料
   - 檢查執行記錄是否顯示「✅ 測試成功」

### 第四步：部署為 Web App

1. **部署設置**
   - 點擊「部署」→「新增部署作業」
   - 類型選擇「網頁應用程式」
   - 說明填寫：「築宜預約表單處理 v1.0」

2. **執行身分設置**
   - 「執行身分」選擇：**我**
   - 「具有存取權限的使用者」選擇：**任何人**

3. **完成部署**
   - 點擊「部署」
   - 複製「網頁應用程式 URL」
   - 範例：`https://script.google.com/macros/s/AKfycby.../exec`

### 第五步：更新網站設定

1. **修改 HTML 檔案**
   - 開啟 `web/style-dark-blue/index.html`
   - 找到第 695 行左右的這段程式碼：
   ```javascript
   this.SCRIPT_URL = 'YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE';
   ```

2. **替換 URL**
   - 將 `YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE` 替換為您的 Web App URL
   ```javascript
   this.SCRIPT_URL = 'https://script.google.com/macros/s/AKfycby.../exec';
   ```

3. **保存並部署**
   - 保存 HTML 檔案
   - 推送到 GitHub Pages

## 🧪 測試功能

### 本地測試
1. 用瀏覽器開啟 `web/style-dark-blue/index.html`
2. 滾動到「預約諮詢」區塊
3. 填寫測試資料並提交
4. 檢查 Google Sheets 是否收到資料

### 線上測試
1. 訪問您的 GitHub Pages 網站
2. 測試表單提交功能
3. 檢查各種情況：
   - 正常提交
   - 必填欄位驗證
   - 電話號碼格式驗證
   - 網路錯誤處理

## 🔧 常見問題與解決方案

### Q1: 提交後顯示「請先設置 Google Apps Script Web App URL」
**解決方案：**
- 檢查 HTML 檔案第 695 行的 `SCRIPT_URL` 是否正確設置
- 確保已將預設文字替換為實際的 Web App URL

### Q2: 表單提交後顯示錯誤
**可能原因：**
- Apps Script 部署設置錯誤
- 試算表權限問題
- 網路連線問題

**解決步驟：**
1. 檢查 Apps Script 執行記錄
2. 確認試算表 ID 正確
3. 重新部署 Web App

### Q3: 收不到資料但沒有錯誤訊息
**檢查項目：**
1. Apps Script 的 `SPREADSHEET_ID` 是否正確
2. 工作表名稱是否為 `Form Responses`
3. Google Sheets 權限是否正確

### Q4: CORS 跨域錯誤
**解決方案：**
- 確保 Apps Script 中的 CORS 設置正確
- 重新部署 Web App
- 檢查 `doOptions()` 函數是否存在

## 📧 進階功能

### 啟用郵件通知
1. 修改 Apps Script 中的 `NOTIFICATION_EMAIL`
2. 設置為您要接收通知的郵件地址
3. 重新部署 Web App

### 自訂表單欄位
如需添加新欄位：
1. 修改 Google Sheets 表頭
2. 更新 Apps Script 的資料處理邏輯
3. 修改 HTML 表單和 JavaScript 驗證

### Google Analytics 追蹤
表單已支援 GA 事件追蹤，確保網站已載入 GA 追蹤碼。

## 🛡️ 安全性說明

- Apps Script 運行在 Google 的安全環境中
- 所有資料傳輸都經過加密
- 僅有您能存取試算表資料
- Web App URL 可設為僅限特定網域存取

## 📞 技術支援

如遇到問題，請檢查：
1. 瀏覽器開發者工具的 Console 錯誤訊息
2. Apps Script 執行記錄
3. Google Sheets 權限設定

---

完成設置後，您的預約諮詢表單就能自動將客戶資料記錄到 Google Sheets 中了！