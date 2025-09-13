@echo off
chcp 65001
echo.
echo 🚀 正在启动本地服务器...
echo.

cd /d "%~dp0"
python start-server.py

pause