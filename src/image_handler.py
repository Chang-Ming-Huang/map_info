#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps 評論圖片處理模組
功能: 處理評論中的圖片展開、提取和下載
"""

import os
import time
import requests
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
from urllib.parse import urlparse, parse_qs
import re

class ReviewImageHandler:
    def __init__(self, driver, wait_timeout=10):
        """初始化圖片處理器"""
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.session = requests.Session()
        
        # 設定 requests session 的 headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
    
    
    def extract_image_urls(self, review_element):
        """從評論元素中提取所有圖片 URL（點擊縮圖按鈕展開大圖）"""
        try:
            print("正在尋找評論中的圖片按鈕...")
            
            # 根據您提供的HTML，尋找真正的圖片按鈕
            photo_button_selectors = [
                ".//button[@class='Tya61d']",                           # 主要的圖片按鈕
                ".//button[contains(@jsaction, 'openPhoto')]",          # 包含openPhoto的按鈕
                ".//button[@data-photo-index]",                        # 有photo-index的按鈕
                ".//button[contains(@aria-label, '張相片')]"             # aria-label包含"張相片"
            ]
            
            photo_buttons = []
            
            # 尋找所有圖片按鈕
            for selector in photo_button_selectors:
                try:
                    buttons = review_element.find_elements(By.XPATH, selector)
                    
                    for button in buttons:
                        try:
                            # 檢查是否有背景圖片
                            style = button.get_attribute('style')
                            if style and 'background-image' in style and 'geougc' in style:
                                photo_buttons.append(button)
                                
                                # 提取背景圖片URL用於驗證
                                import re
                                url_match = re.search(r'url\("([^"]+)"\)', style)
                                if url_match:
                                    bg_url = url_match.group(1)
                                    print(f"找到圖片按鈕，背景URL: {bg_url[:60]}...")
                        
                        except Exception as e:
                            print(f"檢查按鈕時發生錯誤: {e}")
                            continue
                            
                except Exception as e:
                    print(f"使用選擇器 {selector} 時發生錯誤: {e}")
                    continue
            
            if not photo_buttons:
                print("未找到圖片按鈕")
                return []
            
            print(f"找到 {len(photo_buttons)} 個圖片按鈕")
            
            # 簡化版本：直接從前3個按鈕提取background-image URL
            print("\n=== 直接提取前3張圖片的URL ===")
            
            # 過濾出有效的圖片按鈕（不包含展開按鈕）
            valid_buttons = []
            for button in photo_buttons:
                try:
                    jsaction = button.get_attribute('jsaction')
                    style = button.get_attribute('style')
                    
                    # 只要真正的圖片按鈕（不是展開按鈕）
                    if (jsaction and 'openPhoto' in jsaction and 'showMorePhotos' not in jsaction and
                        style and 'background-image' in style and 'geougc' in style):
                        valid_buttons.append(button)
                except:
                    continue
            
            print(f"過濾後找到 {len(valid_buttons)} 個有效圖片按鈕")
            
            # 只處理前3個有效按鈕
            image_urls = []
            max_images = min(3, len(valid_buttons))
            print(f"將提取前 {max_images} 張圖片")
            
            for i in range(max_images):
                try:
                    button = valid_buttons[i]
                    
                    # 提取 background-image URL
                    style = button.get_attribute('style')
                    data_photo_index = button.get_attribute('data-photo-index')
                    aria_label = button.get_attribute('aria-label')
                    
                    print(f"\n--- 處理第 {i+1} 張圖片 ---")
                    print(f"按鈕索引: {data_photo_index}")
                    print(f"按鈕標籤: {aria_label}")
                    
                    # 使用正則表達式提取 background-image URL
                    import re
                    url_match = re.search(r'background-image:\s*url\("([^"]+)"\)', style)
                    if url_match:
                        bg_url = url_match.group(1)
                        
                        # 轉換為高解析度URL
                        high_res_url = self.convert_to_high_res_url(bg_url)
                        image_urls.append(high_res_url)
                        
                        print(f"✅ 成功提取圖片 URL")
                        print(f"   原始: {bg_url[:80]}...")
                        print(f"   高解析度: {high_res_url[:80]}...")
                    else:
                        print(f"❌ 無法從 style 中提取 URL")
                        print(f"   Style: {style[:100]}...")
                
                except Exception as e:
                    print(f"處理第 {i+1} 張圖片時發生錯誤: {e}")
                    continue
            
            print(f"總共提取到 {len(image_urls)} 個圖片 URL")
            return image_urls
            
        except Exception as e:
            print(f"提取圖片 URL 時發生錯誤: {e}")
            return []
    
    def convert_to_high_res_url(self, original_url):
        """將縮圖 URL 轉換為高解析度 URL"""
        try:
            if not original_url or 'googleusercontent' not in original_url:
                return original_url
            
            # Google 圖片 URL 通常包含尺寸參數，我們可以移除或修改這些參數
            # 例如: =s120-c0x00ffffff-no-rj 改為 =s0 (原始大小)
            
            # 移除尺寸限制參數
            patterns_to_remove = [
                r'=s\d+-.*',  # 移除 =s120-c0x00ffffff-no-rj 這類參數
                r'=w\d+-.*',  # 移除寬度限制
                r'=h\d+-.*'   # 移除高度限制
            ]
            
            high_res_url = original_url
            for pattern in patterns_to_remove:
                high_res_url = re.sub(pattern, '=s0', high_res_url)
            
            # 如果URL沒有尺寸參數，嘗試加上 =s0
            if '=s' not in high_res_url and 'googleusercontent' in high_res_url:
                if '?' in high_res_url:
                    high_res_url += '&s=0'
                else:
                    high_res_url += '=s0'
            
            return high_res_url
            
        except Exception as e:
            print(f"轉換高解析度 URL 時發生錯誤: {e}")
            return original_url
    
    def is_avatar_image(self, img_url):
        """判斷圖片是否為頭像"""
        try:
            # 頭像圖片的特徵
            avatar_patterns = [
                '/a/',                                    # 用戶頭像路徑
                'googleusercontent.com/a/',               # 完整頭像路徑
                'googleusercontent.com/a-/',              # 另一種頭像路徑
                '=c0x00ffffff-no-rj',                    # 頭像參數
                'photo.jpg',                             # 頭像檔名
                'photo',                                 # 頭像關鍵字
            ]
            
            # 檢查 URL 是否包含頭像特徵
            for pattern in avatar_patterns:
                if pattern in img_url:
                    return True
            
            # 額外檢查：頭像通常尺寸較小
            if 's120' in img_url or 's64' in img_url or 's32' in img_url:
                return True
            
            return False
            
        except Exception as e:
            print(f"判斷頭像時發生錯誤: {e}")
            return False
    
    
    
    
    def download_images(self, image_urls, save_dir, review_id, url_cache=None, max_retries=3):
        """下載圖片到指定目錄（支持URL去重）"""
        try:
            # 建立保存目錄
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"已建立圖片目錄: {save_dir}")
            
            downloaded_files = []
            duplicate_count = 0
            
            for i, url in enumerate(image_urls, 1):
                try:
                    # 檢查URL是否已經下載過
                    if url_cache is not None and url in url_cache:
                        existing_file = url_cache[url]
                        # 生成目前評論的檔名
                        filename = f"review_{review_id:03d}_img_{i:02d}.jpg"
                        filepath = os.path.join(save_dir, filename)
                        
                        # 複製已存在的檔案
                        if os.path.exists(existing_file):
                            import shutil
                            shutil.copy2(existing_file, filepath)
                            downloaded_files.append(filename)
                            duplicate_count += 1
                            print(f"圖片 {filename} 複製自已下載的檔案 (去重)")
                            continue
                        else:
                            # 如果原檔案不存在，從快取中移除這個URL
                            del url_cache[url]
                    
                    # 生成檔名
                    filename = f"review_{review_id:03d}_img_{i:02d}.jpg"
                    filepath = os.path.join(save_dir, filename)
                    
                    # 如果檔案已存在，跳過
                    if os.path.exists(filepath):
                        print(f"圖片 {filename} 已存在，跳過下載")
                        downloaded_files.append(filename)
                        continue
                    
                    print(f"正在下載圖片 {i}/{len(image_urls)}: {filename}")
                    
                    # 下載圖片
                    success = self.download_single_image(url, filepath, max_retries)
                    
                    if success:
                        downloaded_files.append(filename)
                        print(f"圖片下載成功: {filename}")
                        # 將URL和檔案路徑添加到快取中
                        if url_cache is not None:
                            url_cache[url] = filepath
                    else:
                        print(f"圖片下載失敗: {filename}")
                    
                    # 隨機延遲避免被封鎖
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"下載圖片 {i} 時發生錯誤: {e}")
                    continue
            
            print(f"圖片處理完成，成功獲取 {len(downloaded_files)} 張圖片")
            if duplicate_count > 0:
                print(f"其中 {duplicate_count} 張圖片通過去重複製獲得")
            return downloaded_files
            
        except Exception as e:
            print(f"下載圖片時發生錯誤: {e}")
            return []
    
    def download_single_image(self, url, filepath, max_retries=3):
        """下載單張圖片"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # 檢查是否為有效的圖片內容
                if 'image' not in response.headers.get('content-type', ''):
                    print(f"URL 不是有效的圖片: {url[:80]}...")
                    return False
                
                # 保存圖片
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # 驗證圖片檔案
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                    return True
                except:
                    print(f"下載的圖片檔案損壞: {filepath}")
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return False
                
            except Exception as e:
                print(f"下載嘗試 {attempt + 1}/{max_retries} 失敗: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指數退避
                continue
        
        return False
    
    def process_review_images(self, review_element, review_id, save_dir, url_cache=None):
        """處理單則評論的所有圖片（提取 + 下載）"""
        try:
            print(f"\n--- 處理評論 {review_id} 的圖片 ---")
            
            # 提取前3張圖片 URL
            image_urls = self.extract_image_urls(review_element)
            
            if not image_urls:
                print(f"評論 {review_id} 沒有找到圖片")
                return []
            
            # 下載圖片（傳遞URL快取）
            downloaded_files = self.download_images(image_urls, save_dir, review_id, url_cache)
            
            return downloaded_files
            
        except Exception as e:
            print(f"處理評論 {review_id} 的圖片時發生錯誤: {e}")
            return []