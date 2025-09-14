#!/usr/bin/env python3
"""
简单的本地 HTTP 服务器，用于测试 DataAPI 功能
使用方法：
1. 在终端中进入 web 目录
2. 运行：python start-server.py
3. 打开浏览器访问：http://localhost:8000
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加 CORS 头，允许跨域请求
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

if __name__ == "__main__":
    # 保持在 web 目录，这样 shared/ 下的文件可以直接访问
    # 同时通过相对路径访问上级目录的 data/ 和 images/

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 服务器启动成功！")
        print(f"📡 服务器地址: http://localhost:{PORT}")
        print(f"🧪 测试页面: http://localhost:{PORT}/shared/test-dataapi.html")
        print(f"🎨 样式页面:")

        # 列出所有样式页面
        style_dirs = [d for d in os.listdir('.') if d.startswith('style-') and os.path.isdir(d)]
        for style_dir in sorted(style_dirs):
            print(f"   - http://localhost:{PORT}/{style_dir}/")

        print(f"✋ 按 Ctrl+C 停止服务器")
        print(f"🔄 正在启动...")

        try:
            # 自动打开测试页面
            webbrowser.open(f'http://localhost:{PORT}/shared/test-dataapi.html')
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
            sys.exit(0)