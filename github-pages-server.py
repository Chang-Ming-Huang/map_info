#!/usr/bin/env python3
"""
GitHub Pages 測試服務器
用於模擬不同的 GitHub Pages 部署配置，測試路徑和 CORS 問題

使用方法：
python3 github-pages-server.py --mode=repo-root    # 整個倉庫為根目錄（預設）
python3 github-pages-server.py --mode=docs         # 模擬 docs/ 目錄部署
python3 github-pages-server.py --mode=flat         # 扁平結構部署
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import argparse
import shutil
import tempfile
from pathlib import Path

PORT = 8003

class GitHubPagesHandler(http.server.SimpleHTTPRequestHandler):
    """自定義處理器，模擬 GitHub Pages 行為"""

    def end_headers(self):
        # 添加 CORS 頭，允許跨域請求（模擬 GitHub Pages）
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def log_message(self, format, *args):
        """自定義日誌格式"""
        print(f"[{self.date_time_string()}] {format % args}")

def setup_repo_root_mode():
    """配置 A: 整個倉庫為根目錄"""
    print("🔧 設定模式：整個倉庫為根目錄")
    print("   - 服務器根目錄：專案根目錄")
    print("   - 測試 URL：/web/shared/test-dataapi.html")
    print("   - 樣式頁面：/web/style-dark-blue/index.html")
    return os.getcwd()

def setup_docs_mode():
    """配置 B: 模擬 docs/ 目錄部署"""
    print("🔧 設定模式：docs/ 目錄部署")
    print("   - 服務器根目錄：web/ 目錄（模擬 docs/）")
    print("   - 測試 URL：/shared/test-dataapi.html")
    print("   - 樣式頁面：/style-dark-blue/index.html")
    web_dir = os.path.join(os.getcwd(), 'web')
    if not os.path.exists(web_dir):
        print("❌ 錯誤：web/ 目錄不存在")
        sys.exit(1)
    return web_dir

def setup_flat_mode():
    """配置 C: 扁平結構部署（創建臨時目錄結構）"""
    print("🔧 設定模式：扁平結構部署")
    print("   - 正在創建臨時扁平結構...")

    # 創建臨時目錄
    temp_dir = tempfile.mkdtemp(prefix="github_pages_test_")
    web_dir = os.path.join(os.getcwd(), 'web')

    if not os.path.exists(web_dir):
        print("❌ 錯誤：web/ 目錄不存在")
        sys.exit(1)

    try:
        # 複製 web/ 目錄內容到臨時目錄
        for item in os.listdir(web_dir):
            src = os.path.join(web_dir, item)
            dst = os.path.join(temp_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        print(f"   - 臨時目錄：{temp_dir}")
        print("   - 測試 URL：/shared/test-dataapi.html")
        print("   - 樣式頁面：/style-dark-blue/index.html")
        print("   ⚠️  注意：服務器停止時會自動清理臨時目錄")

        return temp_dir

    except Exception as e:
        print(f"❌ 創建臨時結構失敗：{e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)

def print_test_urls(mode, port):
    """打印測試 URL"""
    base_url = f"http://localhost:{port}"

    print("\n🧪 測試 URL 列表：")

    if mode == "repo-root":
        urls = [
            f"{base_url}/web/shared/test-dataapi.html",
            f"{base_url}/web/shared/reviews.html",
            f"{base_url}/web/style-dark-blue/index.html",
            f"{base_url}/web/style-dark-blue/index_optimized.html",
        ]
    else:  # docs 或 flat 模式
        urls = [
            f"{base_url}/shared/test-dataapi.html",
            f"{base_url}/shared/reviews.html",
            f"{base_url}/style-dark-blue/index.html",
            f"{base_url}/style-dark-blue/index_optimized.html",
        ]

    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")

def run_tests(mode, port):
    """執行自動化測試"""
    print(f"\n🧪 執行 {mode} 模式測試...")

    import requests
    import time

    # 等待服務器啟動
    time.sleep(2)

    base_url = f"http://localhost:{port}"
    test_results = []

    # 定義測試 URL
    if mode == "repo-root":
        test_urls = {
            "測試頁面": "/web/shared/test-dataapi.html",
            "DataAPI": "/web/shared/dataAPI.js",
            "Utils": "/web/shared/utils.js",
            "JSON數據": "/web/data/20250914_115841.json",
            "圖片": "/web/images/20250914_115841/review_002_img_01.jpg",
        }
    else:
        test_urls = {
            "測試頁面": "/shared/test-dataapi.html",
            "DataAPI": "/shared/dataAPI.js",
            "Utils": "/shared/utils.js",
            "JSON數據": "/data/20250914_115841.json",
            "圖片": "/images/20250914_115841/review_002_img_01.jpg",
        }

    # 執行測試
    for name, path in test_urls.items():
        try:
            response = requests.get(f"{base_url}{path}", timeout=5)
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            test_results.append(f"   {name}: {status}")
        except Exception as e:
            test_results.append(f"   {name}: ❌ FAIL ({e})")

    # 顯示結果
    print("\n📊 測試結果：")
    for result in test_results:
        print(result)

def main():
    parser = argparse.ArgumentParser(description='GitHub Pages 測試服務器')
    parser.add_argument('--mode', choices=['repo-root', 'docs', 'flat'],
                       default='repo-root', help='測試模式')
    parser.add_argument('--port', type=int, default=PORT, help='服務器端口')
    parser.add_argument('--no-browser', action='store_true', help='不自動打開瀏覽器')
    parser.add_argument('--test-only', action='store_true', help='只執行測試，不啟動互動式服務器')

    args = parser.parse_args()

    print("🚀 GitHub Pages 測試服務器")
    print("=" * 50)

    # 設定工作目錄
    temp_dir = None
    try:
        if args.mode == "repo-root":
            work_dir = setup_repo_root_mode()
        elif args.mode == "docs":
            work_dir = setup_docs_mode()
        elif args.mode == "flat":
            work_dir = setup_flat_mode()
            temp_dir = work_dir

        os.chdir(work_dir)

        # 打印測試 URL
        print_test_urls(args.mode, args.port)

        # 啟動服務器
        with socketserver.TCPServer(("", args.port), GitHubPagesHandler) as httpd:
            print(f"\n📡 服務器啟動成功！")
            print(f"   - 模式：{args.mode}")
            print(f"   - 地址：http://localhost:{args.port}")
            print(f"   - 根目錄：{work_dir}")
            print("✋ 按 Ctrl+C 停止服務器")

            if not args.no_browser and args.mode == "repo-root":
                webbrowser.open(f'http://localhost:{args.port}/web/shared/test-dataapi.html')
            elif not args.no_browser:
                webbrowser.open(f'http://localhost:{args.port}/shared/test-dataapi.html')

            if args.test_only:
                # 只執行測試
                import threading
                server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
                server_thread.start()
                run_tests(args.mode, args.port)
                httpd.shutdown()
            else:
                # 互動式服務器
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\n👋 服務器已停止")

    except Exception as e:
        print(f"❌ 服務器啟動失敗：{e}")
        return 1

    finally:
        # 清理臨時目錄
        if temp_dir and os.path.exists(temp_dir):
            print("🧹 清理臨時目錄...")
            shutil.rmtree(temp_dir, ignore_errors=True)

    return 0

if __name__ == "__main__":
    sys.exit(main())