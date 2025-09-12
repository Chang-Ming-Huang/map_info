#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps 評論爬蟲
功能: 爬取指定商家的 Google Maps 評論
目標: 築宜系統傢俱-桃園店
"""

from enum import Enum
import time
import json
import pandas as pd
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import random
import os
from image_handler import ReviewImageHandler

class UserConfig(Enum):
    """用戶層配置 - 簡單直觀"""
    WANTED_REVIEWS = 30      # 期望的評論數量
    ENABLE_IMAGES = False      # 是否下載圖片

class ScrapingConfig(Enum):
    """技術層設定參數"""
    MAX_SCROLLS = 15          # 最大滾動次數 (影響評論數量: 約 5-10則/次滾動)
    HEADLESS_MODE = False     # 是否無頭模式 (True=背景執行, False=顯示瀏覽器)
    DOWNLOAD_IMAGES = True    # 是否下載圖片 (True=下載前3張圖片, False=僅文字)
    SCROLL_DELAY = (1, 2)     # 滾動延遲秒數範圍 (min, max)
    SCROLL_DISTANCE = 300     # 每次滾動距離 (像素)

class ScrapingMode:
    """爬取模式配置"""
    def __init__(self):
        self.mode = 0  # 預設模式
        self.filter_keyword = ""  # 過濾關鍵字
        
    def select_mode(self):
        """互動式選擇爬取模式"""
        print("\n" + "="*50)
        print("🚀 Google Maps 評論爬蟲 - 模式選擇")
        print("="*50)
        print("可用模式：")
        print("  0 - 預設模式（按照設定抓取指定數量的評論）")
        print("  1 - 關鍵字過濾模式（只抓取包含特定字串的評論）")
        print("-"*50)
        
        while True:
            try:
                user_input = input("請選擇模式 (0 或 1，直接按 Enter 使用預設模式): ").strip()
                
                if user_input == "" or user_input == "0":
                    self.mode = 0
                    print(f"✅ 已選擇預設模式，將抓取 {UserConfig.WANTED_REVIEWS.value} 則評論")
                    break
                elif user_input == "1":
                    self.mode = 1
                    self._setup_keyword_filter()
                    break
                else:
                    print("❌ 無效輸入，請輸入 0 或 1")
            except KeyboardInterrupt:
                print("\n程式已取消")
                exit(0)
        
        print("="*50)
        return self.mode
    
    def _setup_keyword_filter(self):
        """設定關鍵字過濾"""
        print("\n📝 關鍵字過濾模式設定")
        print("-"*30)
        
        while True:
            keyword = input("請輸入要搜尋的關鍵字（評論內容必須包含此字串）: ").strip()
            if keyword:
                self.filter_keyword = keyword
                print(f"✅ 已設定關鍵字過濾：'{keyword}'")
                print("📌 注意：中文將進行精確比對，英文將忽略大小寫")
                break
            else:
                print("❌ 關鍵字不能為空，請重新輸入")
    
    def should_include_review(self, review_text):
        """判斷評論是否符合過濾條件"""
        if self.mode == 0:
            return True  # 預設模式：包含所有評論
        
        if self.mode == 1:
            return self._match_keyword(review_text, self.filter_keyword)
        
        return True
    
    def _match_keyword(self, text, keyword):
        """字串比對功能"""
        if not text or not keyword:
            return False
        
        # 檢查是否包含中文字符
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', keyword))
        
        if has_chinese:
            # 中文：精確比對
            return keyword in text
        else:
            # 英文：忽略大小寫比對
            return keyword.lower() in text.lower()

class GoogleReviewsScraper:
    def __init__(self, headless=None, download_images=None, scraping_mode=None):
        """初始化爬蟲"""
        self.headless = headless if headless is not None else ScrapingConfig.HEADLESS_MODE.value
        self.download_images = download_images if download_images is not None else UserConfig.ENABLE_IMAGES.value
        self.driver = None
        self.reviews_data = []
        self.image_handler = None
        self.processed_reviews = set()  # 用於去重的集合
        self.downloaded_images = {}  # URL -> 檔案路徑的映射，用於圖片去重
        self.scraping_mode = scraping_mode if scraping_mode is not None else ScrapingMode()  # 爬取模式
        
    def setup_driver(self):
        """設定 Chrome WebDriver"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # 隨機 User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # 初始化圖片處理器
        if self.download_images:
            self.image_handler = ReviewImageHandler(self.driver)
        
    def navigate_to_main_page(self, url):
        """導航到主頁面（不跳轉到評論頁面）"""
        try:
            print(f"正在打開主頁面: {url}")
            self.driver.get(url)
            
            # 等待頁面載入
            time.sleep(5)
            print("主頁面載入完成")
            
            return True
            
        except Exception as e:
            print(f"導航到主頁面時發生錯誤: {e}")
            return False
    
    def scroll_left_panel_to_load_reviews(self, target_reviews=None, max_scrolls=None):
        """滾動左側面板載入更多評論（以評論數量為目標）"""
        if target_reviews is None:
            target_reviews = UserConfig.WANTED_REVIEWS.value
        if max_scrolls is None:
            max_scrolls = ScrapingConfig.MAX_SCROLLS.value
            
        print(f"開始滾動左側面板載入評論，目標: {target_reviews} 則評論...")
        
        try:
            # 等待頁面完全載入
            time.sleep(3)
            
            # 尋找可滾動的評論容器，嘗試更多選擇器
            scrollable_selectors = [
                "div[role='main']",                    # Google Maps 主要內容區域
                ".m6QErb .DxyBCb",                    # 評論列表容器
                ".section-scrollbox",                  # 捲動區塊
                ".siAUzd",                            # 側邊欄內容
                ".m6QErb",                            # 整個左側面板
                "div[data-value='Sort']",             # 包含評論的區域
                ".TFQHme",                            # 另一個可能的容器
                "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"     # 具體的評論容器
            ]
            
            scrollable_element = None
            for selector in scrollable_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # 檢查元素是否真的可滾動
                        elem = elements[0]
                        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", elem)
                        client_height = self.driver.execute_script("return arguments[0].clientHeight", elem)
                        
                        if scroll_height > client_height:
                            scrollable_element = elem
                            print(f"找到可滾動元素: {selector} (scrollHeight: {scroll_height}, clientHeight: {client_height})")
                            break
                        else:
                            print(f"元素 {selector} 不可滾動 (scrollHeight: {scroll_height}, clientHeight: {client_height})")
                except Exception as e:
                    print(f"檢查選擇器 {selector} 時出錯: {e}")
                    continue
            
            if not scrollable_element:
                print("未找到特定滾動容器，使用整個頁面")
                scrollable_element = self.driver.find_element(By.TAG_NAME, "body")
            
            # 獲取初始評論數量
            initial_review_count = self.get_current_review_count()
            print(f"滾動前評論數量: {initial_review_count}")
            
            # 執行滾動並檢測評論數量變化
            scroll_count = 0
            no_new_content_count = 0  # 連續沒有新內容的次數
            last_review_count = initial_review_count
            
            while scroll_count < max_scrolls:
                # 記錄滾動前的評論數量
                before_scroll_count = self.get_current_review_count()
                
                print(f"\n=== 滾動第 {scroll_count + 1} 次 ===")
                
                # 嘗試多種滾動方式
                scroll_success = False
                
                # 方法1: 元素內部滾動
                try:
                    old_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scrollable_element)
                    self.driver.execute_script(f"arguments[0].scrollTop += {ScrapingConfig.SCROLL_DISTANCE.value}", scrollable_element)
                    time.sleep(1)
                    new_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scrollable_element)
                    
                    if new_scroll_top != old_scroll_top:
                        print(f"✅ 元素內滾動成功: {old_scroll_top} -> {new_scroll_top}")
                        scroll_success = True
                    else:
                        print(f"❌ 元素內滾動失敗: 位置未改變 ({old_scroll_top})")
                except Exception as e:
                    print(f"❌ 元素內滾動異常: {e}")
                
                # 方法2: 整頁滾動（如果元素滾動失敗）
                if not scroll_success:
                    try:
                        old_page_scroll = self.driver.execute_script("return window.pageYOffset")
                        self.driver.execute_script(f"window.scrollBy(0, {ScrapingConfig.SCROLL_DISTANCE.value})")
                        time.sleep(1)
                        new_page_scroll = self.driver.execute_script("return window.pageYOffset")
                        
                        if new_page_scroll != old_page_scroll:
                            print(f"✅ 整頁滾動成功: {old_page_scroll} -> {new_page_scroll}")
                            scroll_success = True
                        else:
                            print(f"❌ 整頁滾動失敗: 位置未改變 ({old_page_scroll})")
                    except Exception as e:
                        print(f"❌ 整頁滾動異常: {e}")
                
                # 方法3: 鍵盤滾動
                if not scroll_success:
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(scrollable_element)
                        actions.send_keys(Keys.PAGE_DOWN)
                        actions.perform()
                        print("✅ 使用鍵盤 PAGE_DOWN")
                        scroll_success = True
                    except Exception as e:
                        print(f"❌ 鍵盤滾動異常: {e}")
                
                # 等待新內容載入
                delay_range = ScrapingConfig.SCROLL_DELAY.value
                sleep_time = random.uniform(delay_range[0], delay_range[1])
                print(f"等待 {sleep_time:.1f} 秒載入新內容...")
                time.sleep(sleep_time)
                
                # 檢查評論數量變化
                after_scroll_count = self.get_current_review_count()
                new_reviews_loaded = after_scroll_count - before_scroll_count
                
                print(f"滾動結果: {before_scroll_count} -> {after_scroll_count} (+{new_reviews_loaded})")
                
                if new_reviews_loaded == 0:
                    no_new_content_count += 1
                    print(f"⚠️  無新評論載入，連續無效次數={no_new_content_count}")
                    
                    # 連續3次沒有新內容才停止
                    if no_new_content_count >= 3:
                        print(f"🛑 連續 {no_new_content_count} 次滾動沒有新內容，停止滾動")
                        break
                else:
                    no_new_content_count = 0  # 重置計數器
                    print(f"🎉 載入 {new_reviews_loaded} 個新評論，總評論數: {after_scroll_count}")
                    
                    # 檢查是否已達到目標評論數量
                    if after_scroll_count >= target_reviews:
                        print(f"🎯 已達到目標評論數量 {target_reviews}，停止滾動")
                        break
                
                scroll_count += 1
                
        except Exception as e:
            print(f"滾動左側面板時發生錯誤: {e}")
            import traceback
            print(f"詳細錯誤: {traceback.format_exc()}")
    
    def get_current_review_count(self):
        """獲取當前頁面上的評論數量"""
        try:
            review_selectors = [
                "div[data-review-id]",
                "div[jsaction*='review']", 
                ".jftiEf"
            ]
            
            for selector in review_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        return len(elements)
                except:
                    continue
            
            return 0
        except Exception as e:
            print(f"獲取評論數量時發生錯誤: {e}")
            return 0
    
    def click_more_buttons(self):
        """點擊所有的 '更多' 按鈕來展開完整評論"""
        print("正在展開所有評論...")
        
        more_button_selectors = [
            "button[jsaction*='review.expandReview']",
            ".w8nwRe",
            "button[aria-label*='更多']",
            "button[aria-label*='More']",
            "button:contains('更多')",
            "span:contains('更多')"
        ]
        
        for selector in more_button_selectors:
            try:
                if 'contains' in selector:
                    # 使用 XPath 處理 contains
                    if '更多' in selector:
                        buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '更多')] | //span[contains(text(), '更多')]")
                    else:
                        buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), 'More')] | //span[contains(text(), 'More')]")
                else:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if buttons:
                    print(f"找到 {len(buttons)} 個更多按鈕 (使用選擇器: {selector})")
                    for i, button in enumerate(buttons):
                        try:
                            # 滾動到按鈕位置
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(0.5)
                            
                            # 點擊按鈕
                            button.click()
                            print(f"已點擊第 {i+1} 個更多按鈕")
                            time.sleep(0.5)
                        except Exception as e:
                            print(f"點擊第 {i+1} 個更多按鈕時發生錯誤: {e}")
                    break
                    
            except Exception as e:
                print(f"尋找更多按鈕時發生錯誤 (選擇器: {selector}): {e}")
                continue
    
    def extract_reviews(self, target_reviews=None):
        """提取評論數據（主頁面版本）"""
        if target_reviews is None:
            target_reviews = UserConfig.WANTED_REVIEWS.value
            
        print(f"正在提取主頁面評論數據，目標: {target_reviews} 則評論...")
        
        # 主頁面的評論容器選擇器
        review_selectors = [
            "div[data-review-id]",     # 主頁面的評論容器
            "div[jsaction*='review']", # 包含評論操作的容器
            ".jftiEf",                 # 通用評論容器
            ".fontBodyMedium"          # 可能的評論文字容器
        ]
        
        reviews = []
        for selector in review_selectors:
            try:
                review_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if review_elements:
                    print(f"使用選擇器 {selector} 找到 {len(review_elements)} 個評論元素")
                    reviews = review_elements
                    break
            except:
                continue
        
        if not reviews:
            print("未找到評論元素，嘗試其他方法...")
            return []
        
        extracted_reviews = []
        total_reviews = len(reviews)
        duplicate_count = 0
        
        for i in range(total_reviews):
            try:
                # 每次重新搜索評論元素，避免stale element問題
                current_reviews = []
                for selector in review_selectors:
                    try:
                        found_reviews = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if found_reviews:
                            current_reviews = found_reviews
                            break
                    except:
                        continue
                
                if i >= len(current_reviews):
                    print(f"第 {i+1} 個評論元素已不存在，跳過")
                    continue
                
                review = current_reviews[i]
                
                # 檢查評論唯一性
                review_id = self.get_review_unique_id(review)
                if review_id in self.processed_reviews:
                    duplicate_count += 1
                    print(f"跳過重複評論: {review_id[:50]}...")
                    continue
                
                # 添加到已處理集合
                self.processed_reviews.add(review_id)
                
                review_data = {}
                
                # 提取評論者姓名
                try:
                    name_selectors = [".d4r55", ".X43Kjb", "div[data-attrid='Name']", ".reviewer-name"]
                    for sel in name_selectors:
                        try:
                            name_element = review.find_element(By.CSS_SELECTOR, sel)
                            review_data['reviewer_name'] = name_element.text.strip()
                            break
                        except:
                            continue
                    
                    if 'reviewer_name' not in review_data:
                        review_data['reviewer_name'] = "Unknown"
                        
                except Exception as e:
                    review_data['reviewer_name'] = "Unknown"
                
                # 提取評分
                try:
                    rating_selectors = [
                        "span[aria-label*='星']",
                        "span[aria-label*='star']", 
                        ".kvMYJc",
                        "div[role='img'][aria-label*='星']"
                    ]
                    
                    for sel in rating_selectors:
                        try:
                            rating_element = review.find_element(By.CSS_SELECTOR, sel)
                            aria_label = rating_element.get_attribute('aria-label')
                            if aria_label:
                                # 從 aria-label 中提取數字
                                import re
                                rating_match = re.search(r'(\d+)', aria_label)
                                if rating_match:
                                    review_data['rating'] = int(rating_match.group(1))
                                    break
                        except:
                            continue
                    
                    if 'rating' not in review_data:
                        review_data['rating'] = None
                        
                except Exception as e:
                    review_data['rating'] = None
                
                # 提取評論文字
                try:
                    text_selectors = [".MyEned", ".wiI7pd", ".review-text", "span[jsaction*='review']"]
                    for sel in text_selectors:
                        try:
                            text_element = review.find_element(By.CSS_SELECTOR, sel)
                            review_data['review_text'] = text_element.text.strip()
                            break
                        except:
                            continue
                    
                    if 'review_text' not in review_data:
                        review_data['review_text'] = ""
                        
                except Exception as e:
                    review_data['review_text'] = ""
                
                # 提取日期
                try:
                    date_selectors = [".rsqaWe", ".review-date", "span[aria-label*='ago']"]
                    for sel in date_selectors:
                        try:
                            date_element = review.find_element(By.CSS_SELECTOR, sel)
                            review_data['review_date'] = date_element.text.strip()
                            break
                        except:
                            continue
                    
                    if 'review_date' not in review_data:
                        review_data['review_date'] = ""
                        
                except Exception as e:
                    review_data['review_date'] = ""
                
                # 添加時間戳和 ID
                review_data['scraped_at'] = datetime.now().isoformat()
                review_data['review_id'] = i + 1
                
                # 處理圖片（如果啟用）
                review_data['images'] = []
                review_data['total_images'] = 0
                review_data['images_downloaded'] = False
                
                if self.download_images and self.image_handler:
                    try:
                        # 建立圖片儲存目錄
                        timestamp = datetime.now().strftime("%Y%m%d")
                        image_dir = f"images/築宜系統傢俱_桃園店_{timestamp}"
                        
                        # 處理這則評論的圖片，傳遞URL快取進行去重
                        downloaded_files = self.image_handler.process_review_images(
                            review, i + 1, image_dir, self.downloaded_images
                        )
                        
                        if downloaded_files:
                            review_data['images'] = downloaded_files
                            review_data['total_images'] = len(downloaded_files)
                            review_data['images_downloaded'] = True
                            review_data['image_directory'] = image_dir
                            print(f"評論 {i+1} 成功下載 {len(downloaded_files)} 張圖片")
                        
                    except Exception as e:
                        print(f"處理評論 {i+1} 圖片時發生錯誤: {e}")
                        review_data['images_error'] = str(e)
                
                extracted_reviews.append(review_data)
                
                print(f"已提取第 {len(extracted_reviews)}/{target_reviews} 個評論: {review_data['reviewer_name']}")
                
                # 檢查是否已達到目標數量
                if len(extracted_reviews) >= target_reviews:
                    print(f"✅ 已達到目標評論數量 {target_reviews}，停止提取")
                    break
                
            except Exception as e:
                print(f"提取第 {i+1} 個評論時發生錯誤: {e}")
                continue
        
        print(f"成功提取 {len(extracted_reviews)} 個評論")
        print(f"跳過重複評論: {duplicate_count} 個")
        print(f"實際處理評論: {len(extracted_reviews)} 個")
        return extracted_reviews
    
    def get_review_unique_id(self, review_element):
        """獲取評論的唯一標識符"""
        try:
            # 優先使用 data-review-id
            review_id = review_element.get_attribute('data-review-id')
            if review_id:
                return f"review_id_{review_id}"
            
            # 次選：評論者姓名 + 評論文字前50字
            reviewer_name = ""
            review_text = ""
            
            # 提取評論者姓名
            name_selectors = [".d4r55", ".X43Kjb", "div[data-attrid='Name']", ".reviewer-name"]
            for sel in name_selectors:
                try:
                    name_element = review_element.find_element(By.CSS_SELECTOR, sel)
                    reviewer_name = name_element.text.strip()
                    break
                except:
                    continue
            
            # 提取評論文字
            text_selectors = [".MyEned", ".wiI7pd", ".review-text", "span[jsaction*='review']"]
            for sel in text_selectors:
                try:
                    text_element = review_element.find_element(By.CSS_SELECTOR, sel)
                    review_text = text_element.text.strip()[:50]  # 取前50字
                    break
                except:
                    continue
            
            # 組合成唯一ID
            unique_id = f"{reviewer_name}_{review_text}".replace(" ", "_").replace("\n", "_")
            return unique_id
            
        except Exception as e:
            print(f"獲取評論唯一ID時發生錯誤: {e}")
            # 使用元素的位置作為備用ID
            return f"element_{hash(str(review_element))}"
    
    def save_to_json(self, reviews, filename):
        """保存為 JSON 格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            print(f"評論已保存到 {filename}")
        except Exception as e:
            print(f"保存 JSON 檔案時發生錯誤: {e}")
    
    
    def scrape_reviews(self, url):
        """主要爬蟲流程（新的循環邏輯）"""
        try:
            # 設定 WebDriver
            self.setup_driver()
            
            # 導航到主頁面
            if not self.navigate_to_main_page(url):
                return []
            
            # 執行新的循環式爬取邏輯
            reviews = self.scrape_with_scroll_and_download_loop()
            
            return reviews
            
        except Exception as e:
            print(f"爬蟲過程發生錯誤: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("已關閉瀏覽器")
    
    def scrape_with_scroll_and_download_loop(self):
        """新的循環邏輯：滾動→檢查→下載→判斷"""
        target_reviews = UserConfig.WANTED_REVIEWS.value
        max_no_new_reviews = 20  # 連續無新評論的最大次數
        no_new_reviews_counter = 0
        downloaded_reviews = []
        processed_review_ids = set()
        scroll_count = 0
        max_total_scrolls = 50  # 總滾動次數上限
        
        print(f"開始循環式爬取，目標: {target_reviews} 則評論")
        print(f"無新評論觸底判斷: 連續 {max_no_new_reviews} 次無新評論則停止")
        
        # 等待頁面載入
        time.sleep(3)
        
        # 前置作業：先滾動左側區塊20次
        print("前置作業：開始滾動左側區塊20次")
        self.pre_scroll_left_panel()
        
        # 步驟0：點擊「更多評論」按鈕展開所有評論
        print("步驟0：嘗試點擊「更多評論」按鈕展開所有評論")
        self.click_show_more_reviews_button()
        
        # 找到可滾動元素
        scrollable_element = self.find_scrollable_element()
        if not scrollable_element:
            print("❌ 無法找到可滾動元素")
            return []
        
        while len(downloaded_reviews) < target_reviews and scroll_count < max_total_scrolls:
            cycle_start_count = len(downloaded_reviews)
            scroll_count += 1
            
            print(f"\n=== 循環第 {scroll_count} 次 ===")
            print(f"目前已下載: {len(downloaded_reviews)}/{target_reviews} 則評論")
            
            # 步驟一：滾動頁面
            print("步驟一：滾動頁面載入更多內容")
            scroll_success = self.perform_scroll(scrollable_element, scroll_count)
            
            # 步驟二：檢查目前頁面上有多少評論
            print("步驟二：檢查頁面上的評論數量")
            current_review_elements = self.get_current_review_elements()
            print(f"頁面上發現 {len(current_review_elements)} 個評論元素")
            
            # 步驟三：處理尚未下載的評論
            print("步驟三：處理尚未下載的評論")
            new_reviews_in_cycle = self.process_new_reviews(
                current_review_elements, 
                processed_review_ids, 
                target_reviews - len(downloaded_reviews)
            )
            
            downloaded_reviews.extend(new_reviews_in_cycle)
            print(f"本次循環新增 {len(new_reviews_in_cycle)} 則評論")
            
            # 步驟四：判斷是否繼續
            print("步驟四：判斷是否繼續滾動")
            if len(new_reviews_in_cycle) == 0:
                no_new_reviews_counter += 1
                print(f"⚠️  本次循環無新評論，連續無效次數: {no_new_reviews_counter}/{max_no_new_reviews}")
                
                if no_new_reviews_counter >= max_no_new_reviews:
                    print(f"🛑 連續 {max_no_new_reviews} 次循環無新評論，判定已觸底，停止爬取")
                    break
            else:
                no_new_reviews_counter = 0  # 重置計數器
                print(f"✅ 有新評論，重置無效計數器")
                
                # 檢查是否已達到目標
                if len(downloaded_reviews) >= target_reviews:
                    print(f"🎯 已達到目標評論數量 {target_reviews}，停止爬取")
                    break
        
        print(f"\n爬取完成！共獲得 {len(downloaded_reviews)} 則評論")
        return downloaded_reviews[:target_reviews]  # 確保不超過目標數量
    
    def pre_scroll_left_panel(self):
        """前置作業：滾動左側區塊30次，每次滾動後檢查並點擊「更多評論」按鈕"""
        try:
            print("正在執行前置滾動作業...")
            
            # 找到可滾動的左側面板元素
            scrollable_selectors = [
                "div[role='main']",                    # Google Maps 主要內容區域
                ".m6QErb .DxyBCb",                    # 評論列表容器
                ".section-scrollbox",                  # 捲動區塊
                ".siAUzd",                            # 側邊欄內容
                ".m6QErb",                            # 整個左側面板
                "div[data-value='Sort']",             # 包含評論的區域
                ".TFQHme",                            # 另一個可能的容器
                "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"     # 具體的評論容器
            ]
            
            scrollable_element = None
            for selector in scrollable_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elem = elements[0]
                        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", elem)
                        client_height = self.driver.execute_script("return arguments[0].clientHeight", elem)
                        
                        if scroll_height > client_height:
                            scrollable_element = elem
                            print(f"找到可滾動的左側面板: {selector}")
                            break
                except Exception as e:
                    continue
            
            if not scrollable_element:
                print("⚠️  未找到可滾動的左側面板，使用整個頁面")
                scrollable_element = self.driver.find_element(By.TAG_NAME, "body")
            
            # 執行30次滾動，每次滾動後檢查「更多評論」按鈕
            scroll_distance = 300  # 每次滾動距離
            more_button_clicks = 0  # 記錄點擊「更多評論」按鈕的次數
            
            for i in range(30):
                try:
                    print(f"前置滾動 {i+1}/30")
                    
                    # 記錄滾動前位置
                    old_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scrollable_element)
                    
                    # 執行滾動
                    self.driver.execute_script(f"arguments[0].scrollTop += {scroll_distance}", scrollable_element)
                    
                    # 等待內容載入
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # 檢查滾動是否成功
                    new_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scrollable_element)
                    
                    if new_scroll_top != old_scroll_top:
                        print(f"✅ 滾動成功: {old_scroll_top} -> {new_scroll_top}")
                    else:
                        print(f"⚠️  滾動位置未改變，可能已到底部")
                    
                    # 每次滾動後檢查是否有「更多評論」按鈕
                    print(f"  檢查是否有「更多評論」按鈕...")
                    button_found = self.check_and_click_more_reviews_button()
                    if button_found:
                        more_button_clicks += 1
                        print(f"  ✅ 找到並點擊「更多評論」按鈕 (第{more_button_clicks}次)")
                    else:
                        print(f"  ❌ 未找到「更多評論」按鈕")
                        
                except Exception as e:
                    print(f"前置滾動第 {i+1} 次時發生錯誤: {e}")
                    continue
            
            print(f"✅ 前置滾動作業完成，已滾動30次，點擊「更多評論」按鈕{more_button_clicks}次")
            
            # 等待頁面穩定
            time.sleep(2)
            
        except Exception as e:
            print(f"前置滾動作業發生錯誤: {e}")
            print("繼續執行後續步驟...")
    
    def check_and_click_more_reviews_button(self):
        """檢查並點擊「更多評論」按鈕，返回是否找到並點擊成功"""
        try:
            # 「更多評論」按鈕的選擇器
            more_reviews_selectors = [
                "button[aria-label*='更多評論']",                      # 主要選擇器
                "button[aria-label*='More reviews']",                 # 英文版本
                ".m6QErb .j3fM2b button[aria-label*='更多']",         # 更具體的路徑
                ".m6QErb .j3fM2b button.M77dve",                     # 使用class
                "button.M77dve[aria-label*='更多評論']",               # 組合選擇器
                "button[jsaction*='pane.wfvdle67']",                 # 使用jsaction
            ]
            
            for selector in more_reviews_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if buttons:
                        button = buttons[0]
                        
                        # 檢查按鈕是否可見和可點擊
                        if button.is_displayed() and button.is_enabled():
                            # 滾動到按鈕位置
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(0.5)
                            
                            # 點擊按鈕
                            button.click()
                            
                            # 等待頁面載入更多評論
                            time.sleep(1.5)
                            return True
                    
                except Exception as e:
                    continue
            
            # 備用方案：使用XPath尋找包含「更多評論」文字的按鈕
            try:
                xpath_selectors = [
                    "//span[@class='wNNZR' and contains(text(), '更多評論')]/../..",
                    "//button[contains(@aria-label, '更多評論')]",
                    "//button[contains(text(), '更多評論')]"
                ]
                
                for xpath in xpath_selectors:
                    buttons = self.driver.find_elements(By.XPATH, xpath)
                    if buttons:
                        button = buttons[0]
                        if button.is_displayed() and button.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(0.5)
                            button.click()
                            time.sleep(1.5)
                            return True
            except:
                pass
            
            return False
            
        except Exception as e:
            return False

    def click_show_more_reviews_button(self):
        """點擊「更多評論」按鈕展開所有評論"""
        try:
            # 根據您提供的HTML結構，尋找「更多評論」按鈕
            more_reviews_selectors = [
                "button[aria-label*='更多評論']",                      # 主要選擇器
                "button[aria-label*='More reviews']",                 # 英文版本
                ".m6QErb .j3fM2b button[aria-label*='更多']",         # 更具體的路徑
                ".m6QErb .j3fM2b button.M77dve",                     # 使用class
                "button.M77dve[aria-label*='更多評論']",               # 組合選擇器
                "button[jsaction*='pane.wfvdle67']",                 # 使用jsaction
                ".BgrMEd .wNNZR:contains('更多評論')"                 # 包含文字的span
            ]
            
            button_found = False
            
            for selector in more_reviews_selectors:
                try:
                    if 'contains' in selector:
                        # 使用XPath處理contains
                        buttons = self.driver.find_elements(By.XPATH, "//span[@class='wNNZR' and contains(text(), '更多評論')]/../..")
                    else:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if buttons:
                        button = buttons[0]
                        
                        # 檢查按鈕是否可見和可點擊
                        if button.is_displayed() and button.is_enabled():
                            # 滾動到按鈕位置
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(1)
                            
                            # 獲取按鈕的aria-label或文字內容用於確認
                            aria_label = button.get_attribute('aria-label')
                            button_text = button.text
                            
                            print(f"找到「更多評論」按鈕: {aria_label or button_text}")
                            
                            # 點擊按鈕
                            button.click()
                            print("✅ 成功點擊「更多評論」按鈕")
                            
                            # 等待頁面載入更多評論
                            time.sleep(3)
                            button_found = True
                            break
                        else:
                            print(f"找到按鈕但無法點擊: {selector}")
                    
                except Exception as e:
                    print(f"使用選擇器 {selector} 時發生錯誤: {e}")
                    continue
            
            if not button_found:
                print("⚠️  未找到「更多評論」按鈕，可能已經顯示所有評論")
                
                # 備用方案：尋找任何包含「更多」或「評論」的按鈕
                try:
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in all_buttons:
                        button_text = button.text.lower()
                        aria_label = (button.get_attribute('aria-label') or '').lower()
                        
                        if ('更多' in button_text or '更多' in aria_label) and ('評論' in button_text or '評論' in aria_label):
                            print(f"備用方案找到按鈕: {button_text} / {aria_label}")
                            button.click()
                            print("✅ 使用備用方案成功點擊按鈕")
                            time.sleep(3)
                            button_found = True
                            break
                except Exception as e:
                    print(f"備用方案失敗: {e}")
            
            return button_found
            
        except Exception as e:
            print(f"點擊「更多評論」按鈕時發生錯誤: {e}")
            return False
    
    def find_scrollable_element(self):
        """找到可滾動的評論容器元素"""
        scrollable_selectors = [
            "div[role='main']",                    # Google Maps 主要內容區域
            ".m6QErb .DxyBCb",                    # 評論列表容器
            ".section-scrollbox",                  # 捲動區塊
            ".siAUzd",                            # 側邊欄內容
            ".m6QErb",                            # 整個左側面板
            "div[data-value='Sort']",             # 包含評論的區域
            ".TFQHme",                            # 另一個可能的容器
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"     # 具體的評論容器
        ]
        
        for selector in scrollable_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    elem = elements[0]
                    scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", elem)
                    client_height = self.driver.execute_script("return arguments[0].clientHeight", elem)
                    
                    if scroll_height > client_height:
                        print(f"✅ 找到可滾動元素: {selector} (scrollHeight: {scroll_height}, clientHeight: {client_height})")
                        return elem
                    else:
                        print(f"元素 {selector} 不可滾動 (scrollHeight: {scroll_height}, clientHeight: {client_height})")
            except Exception as e:
                print(f"檢查選擇器 {selector} 時出錯: {e}")
                continue
        
        print("未找到特定滾動容器，使用整個頁面")
        return self.driver.find_element(By.TAG_NAME, "body")
    
    def perform_scroll(self, scrollable_element, scroll_count):
        """執行滾動操作"""
        try:
            # 記錄滾動前位置
            old_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scrollable_element)
            
            # 滾動
            self.driver.execute_script(f"arguments[0].scrollTop += {ScrapingConfig.SCROLL_DISTANCE.value}", scrollable_element)
            
            # 等待載入
            delay_range = ScrapingConfig.SCROLL_DELAY.value
            sleep_time = random.uniform(delay_range[0], delay_range[1])
            print(f"滾動完成，等待 {sleep_time:.1f} 秒載入新內容...")
            time.sleep(sleep_time)
            
            # 檢查滾動是否成功
            new_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scrollable_element)
            
            if new_scroll_top != old_scroll_top:
                print(f"✅ 滾動成功: {old_scroll_top} -> {new_scroll_top}")
                return True
            else:
                print(f"❌ 滾動失敗: 位置未改變 ({old_scroll_top})")
                return False
                
        except Exception as e:
            print(f"滾動執行異常: {e}")
            return False
    
    def get_current_review_elements(self):
        """獲取當前頁面上的所有評論元素"""
        review_selectors = [
            "div[data-review-id]",
            "div[jsaction*='review']", 
            ".jftiEf"
        ]
        
        for selector in review_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用選擇器 {selector} 找到 {len(elements)} 個評論元素")
                    return elements
            except:
                continue
        
        print("❌ 未找到任何評論元素")
        return []
    
    def process_new_reviews(self, review_elements, processed_review_ids, remaining_target):
        """處理頁面上尚未下載的新評論"""
        new_reviews = []
        
        for i, review_element in enumerate(review_elements):
            if len(new_reviews) >= remaining_target:
                print(f"已達到剩餘目標數量 {remaining_target}，停止處理新評論")
                break
                
            try:
                # 生成評論ID用於去重
                review_id = self.generate_review_id(review_element)
                if review_id in processed_review_ids:
                    continue  # 跳過已處理的評論
                
                # 展開評論（如果需要）
                self.expand_review_if_needed(review_element)
                
                # 提取評論資料
                review_data = self.extract_single_review_data(review_element, len(new_reviews) + 1)
                if review_data:
                    # 檢查是否符合過濾條件
                    if self.scraping_mode.should_include_review(review_data['review_text']):
                        processed_review_ids.add(review_id)
                        new_reviews.append(review_data)
                        print(f"✅ 已處理第 {len(new_reviews)} 則新評論: {review_data['reviewer_name']}")
                    else:
                        processed_review_ids.add(review_id)  # 標記為已處理但不加入結果
                        print(f"⏭️  評論不符合過濾條件，跳過: {review_data['reviewer_name']}")
                
            except Exception as e:
                print(f"處理評論 {i+1} 時發生錯誤: {e}")
                continue
        
        return new_reviews
    
    def generate_review_id(self, review_element):
        """生成評論的唯一ID用於去重"""
        try:
            # 嘗試從data-review-id屬性獲取
            review_id = review_element.get_attribute('data-review-id')
            if review_id:
                return f"review_id_{review_id}"
            
            # 備用方案：使用評論文字的hash
            review_text = review_element.text[:100] if review_element.text else ""
            return f"review_hash_{hash(review_text)}"
            
        except:
            return f"review_fallback_{random.randint(10000, 99999)}"
    
    def expand_review_if_needed(self, review_element):
        """展開評論（點擊更多按鈕）"""
        try:
            more_button_selectors = [
                ".//button[contains(@jsaction, 'expandReview')]",
                ".//button[contains(@aria-label, '更多')]",
                ".//button[contains(@aria-label, 'More')]",
                ".//span[contains(text(), '更多')]"
            ]
            
            for selector in more_button_selectors:
                try:
                    buttons = review_element.find_elements(By.XPATH, selector)
                    if buttons:
                        button = buttons[0]
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.3)
                        button.click()
                        time.sleep(0.3)
                        break
                except:
                    continue
        except:
            pass  # 如果展開失敗也不影響整體流程
    
    def extract_single_review_data(self, review_element, review_sequence):
        """從單個評論元素中提取數據並下載圖片"""
        try:
            # 提取基本評論資訊
            reviewer_name = self.extract_reviewer_name(review_element)
            if not reviewer_name:
                return None
            
            rating = self.extract_rating(review_element) 
            review_text = self.extract_review_text(review_element)
            review_date = self.extract_review_date(review_element)
            
            # 處理圖片
            image_files = []
            total_images = 0
            images_downloaded = False
            image_directory = ""
            
            if UserConfig.ENABLE_IMAGES.value:
                business_name = "築宜系統傢俱_桃園店"  # 固定店名
                image_directory = f"images/{business_name}_{datetime.now().strftime('%Y%m%d')}"
                
                # 提取圖片URL並下載
                image_handler = ReviewImageHandler(self.driver)
                # 初始化 downloaded_images 快取如果不存在
                if not hasattr(self, 'downloaded_images'):
                    self.downloaded_images = {}
                
                downloaded_files = image_handler.process_review_images(
                    review_element, review_sequence, image_directory, self.downloaded_images
                )
                
                if downloaded_files:
                    image_files = downloaded_files
                    total_images = len(downloaded_files)
                    images_downloaded = True
            
            # 組裝評論資料
            review_data = {
                'reviewer_name': reviewer_name,
                'rating': rating,
                'review_text': review_text,
                'review_date': review_date,
                'scraped_at': datetime.now().isoformat(),
                'review_id': review_sequence,
                'images': image_files,
                'total_images': total_images,
                'images_downloaded': images_downloaded,
                'image_directory': image_directory
            }
            
            return review_data
            
        except Exception as e:
            print(f"提取評論數據時發生錯誤: {e}")
            return None
    
    def extract_reviewer_name(self, review_element):
        """提取評論者姓名"""
        name_selectors = [
            ".d4r55",
            "[data-value='Name']",
            ".a-profile-name",
            ".TSUbDb",
            "div[style*='16px'] > div",
            "a[data-value]",
            "button[data-value]"
        ]
        
        for selector in name_selectors:
            try:
                elements = review_element.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    name = elements[0].text.strip()
                    if name and len(name) > 0:
                        return name
            except:
                continue
        
        # 備用方案：尋找第一個可點擊的文字元素
        try:
            clickable_elements = review_element.find_elements(By.XPATH, ".//button | .//a")
            for element in clickable_elements:
                text = element.text.strip()
                if text and len(text) > 0 and len(text) < 50:  # 姓名不會太長
                    return text
        except:
            pass
        
        return "Unknown Reviewer"
    
    def extract_rating(self, review_element):
        """提取評分"""
        rating_selectors = [
            "[role='img'][aria-label*='星']",
            "[aria-label*='star']",
            ".kvMYJc",
            "span[role='img']",
            "[title*='星']"
        ]
        
        for selector in rating_selectors:
            try:
                elements = review_element.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    aria_label = elements[0].get_attribute('aria-label')
                    title = elements[0].get_attribute('title')
                    
                    # 從 aria-label 或 title 中提取評分
                    text = aria_label or title or ""
                    if "星" in text:
                        import re
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            return int(numbers[0])
            except:
                continue
        
        return 5  # 預設5星
    
    def extract_review_text(self, review_element):
        """提取評論內容"""
        text_selectors = [
            ".wiI7pd",
            "[data-expandable-section]",
            ".MyEned",
            ".rsqaWe",
            "span[jsaction*='JIbuQc']",
            ".review-full-text"
        ]
        
        for selector in text_selectors:
            try:
                elements = review_element.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text.strip()
                    if text and len(text) > 10:  # 過濾太短的文字
                        return text
            except:
                continue
        
        # 備用方案：提取所有文字內容並過濾
        try:
            all_text = review_element.text
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            # 尋找最長的文字行作為評論內容
            longest_line = ""
            for line in lines:
                if len(line) > len(longest_line) and len(line) > 20:
                    longest_line = line
            
            return longest_line if longest_line else "無評論內容"
        except:
            return "無評論內容"
    
    def extract_review_date(self, review_element):
        """提取評論日期"""
        date_selectors = [
            ".rsqaWe",
            ".DU9Pgb",
            "span[style*='color']",
            "[data-value='Date']"
        ]
        
        for selector in date_selectors:
            try:
                elements = review_element.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    # 檢查是否包含日期相關關鍵字
                    if any(keyword in text for keyword in ['前', '週', '月', '年', 'ago', 'week', 'month', 'year']):
                        return text
            except:
                continue
        
        return "未知日期"

def main():
    """主程式"""
    # 築宜系統傢俱-桃園店的 Google Maps URL
    url = "https://www.google.com/maps/place/%E7%AF%89%E5%AE%9C%E7%B3%BB%E7%B5%B1%E5%82%A2%E4%BF%B1-%E6%A1%83%E5%9C%92%E5%BA%97/@24.9948316,121.2836128,3a,75y,90t/data=!3m8!1e2!3m6!1sCIHM0ogKEICAgMDI_JbaNw!2e10!3e12!6shttps:%2F%2Flh3.googleusercontent.com%2Fgeougc-cs%2FAB3l90BQ0Z3Ft45dwrZpZ3dAesq9EZc92j1JF1ZzwDmybfFROE6vD1Xva0dZiFykQOuB_p46fUs8_g5LWTN_7q90gQPktgMXn3038OwdnbxfL6oxG7jLtM6LxBJViBJPhsUdjZhLhe2z!7i1477!8i1108!4m8!3m7!1s0x34681f295669592d:0xd8650cf553030107!8m2!3d24.9948316!4d121.2836128!9m1!1b1!16s%2Fg%2F11rb4r3796?entry=ttu&g_ep=EgoyMDI1MDkwOS4wIKXMDSoASAFQAw%3D%3D"
    
    # 創建並設定爬取模式
    scraping_mode = ScrapingMode()
    selected_mode = scraping_mode.select_mode()
    
    # 創建爬蟲實例（使用 ENUM 預設值和選定的模式）
    scraper = GoogleReviewsScraper(scraping_mode=scraping_mode)
    
    print(f"\n開始爬取築宜系統傢俱-桃園店的 Google Maps 評論")
    if selected_mode == 0:
        print(f"🎯 模式: 預設模式 - 期望 {UserConfig.WANTED_REVIEWS.value} 則評論")
    else:
        print(f"🎯 模式: 關鍵字過濾模式 - 搜尋包含 '{scraping_mode.filter_keyword}' 的評論")
    print(f"📷 下載圖片: {UserConfig.ENABLE_IMAGES.value}")
    
    # 記錄開始時間
    start_time = datetime.now()
    
    # 執行爬蟲（使用 UserConfig 設定）
    reviews = scraper.scrape_reviews(url)
    
    # 計算執行時間
    end_time = datetime.now()
    execution_time = end_time - start_time
    
    if reviews:
        print(f"\n成功爬取 {len(reviews)} 個評論!")
        
        # 統計去重和圖片下載結果
        total_images = sum(r['total_images'] for r in reviews)
        reviews_with_images = sum(1 for r in reviews if r['total_images'] > 0)
        processed_reviews_count = len(scraper.processed_reviews)
        downloaded_images_count = len(scraper.downloaded_images)
        
        print(f"\n=== 爬取統計結果 ===")
        print(f"執行時間: {execution_time}")
        print(f"成功爬取評論: {len(reviews)} 則")
        print(f"處理過的評論總數（含重複）: {processed_reviews_count}")
        print(f"去重評論: {processed_reviews_count - len(reviews)} 則")
        
        print(f"\n圖片下載統計:")
        print(f"總共獲取圖片: {total_images} 張")
        print(f"唯一圖片URL: {downloaded_images_count} 個")
        print(f"包含圖片的評論: {reviews_with_images} 則")
        
        # 顯示部分結果
        print("\n前 3 個評論預覽:")
        for i, review in enumerate(reviews[:3]):
            print(f"\n評論 {i+1}:")
            print(f"姓名: {review['reviewer_name']}")
            print(f"評分: {review['rating']}")
            print(f"日期: {review['review_date']}")
            print(f"圖片數: {review['total_images']} 張")
            print(f"內容: {review['review_text'][:100]}...")
        
        # 保存JSON結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"築宜系統傢俱_桃園店_評論_{timestamp}.json"
        
        print(f"\n正在保存結果到: {json_filename}")
        scraper.save_to_json(reviews, json_filename)
        print(f"✅ 爬取任務完成！")
        
    else:
        print("❌ 未能成功爬取評論，請檢查網路連線或頁面結構是否改變")
        print(f"執行時間: {execution_time}")
        
        # 即使沒有評論，也檢查是否有其他統計信息
        if hasattr(scraper, 'processed_reviews'):
            processed_count = len(scraper.processed_reviews)
            if processed_count > 0:
                print(f"處理了 {processed_count} 個元素，但未能成功提取評論數據")

if __name__ == "__main__":
    main()