# Google Maps 評論爬蟲專案

這是一個專門爬取 Google Maps 店家評論的 Python 專案，支援評論文字提取和圖片下載功能。

## 專案結構

- `google_reviews_scraper.py` - 主要爬蟲程式
- `image_handler.py` - 圖片處理模組
- `images/` - 圖片下載目錄
- `*.json` - 評論數據輸出檔案

## 主要功能

1. **評論提取**: 爬取指定店家的 Google Maps 評論
2. **圖片下載**: 自動下載評論中的圖片（每則評論最多3張）
3. **去重處理**: 自動跳過重複的評論和圖片
4. **用戶友好配置**: 簡單設定目標評論數量

## 使用方法

### 執行爬蟲
```bash
python3 google_reviews_scraper.py
```

### 配置設定
在 `google_reviews_scraper.py` 頂部的 `UserConfig` 調整設定：
```python
class UserConfig(Enum):
    WANTED_REVIEWS = 10       # 期望的評論數量
    ENABLE_IMAGES = True      # 是否下載圖片
```

## 技術特點

- 基於 Selenium 的網頁自動化
- 智能滾動載入更多評論
- CSS 背景圖片 URL 直接提取技術
- 圖片 URL 去重和快取機制
- 目標導向的資料收集邏輯

## 輸出格式

評論數據會保存為 JSON 檔案，包含：
- 評論者姓名、評分、日期
- 評論文字內容
- 圖片檔名和下載狀態
- 爬取時間戳記

## 依賴套件

- selenium
- requests
- PIL (Pillow)
- Chrome WebDriver

## 目前狀態

已完成核心功能開發和測試，程式可穩定運行並正確處理各種邊界條件。