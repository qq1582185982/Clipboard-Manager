@echo off
echo ================================================
echo              剪贴板管理器启动器
echo ================================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 当前Python版本:
python --version
echo.

REM 切换到脚本目录
cd /d "%~dp0"

echo 正在启动剪贴板管理器...
echo.

REM 启动应用程序
python run_app.py

echo.
echo 应用程序已退出
pause