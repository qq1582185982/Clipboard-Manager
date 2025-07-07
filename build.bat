@echo off
echo ================================================
echo            剪贴板管理器打包工具
echo ================================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo 当前Python版本:
python --version
echo.

REM 切换到脚本目录
cd /d "%~dp0"

REM 检查并安装依赖
echo 检查打包依赖...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 安装打包依赖...
    pip install pyinstaller
    if errorlevel 1 (
        echo 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

echo.
echo 开始打包应用程序...
echo.

REM 运行打包脚本
python build.py

echo.
echo 打包完成！
echo.
echo 生成的文件在 dist 目录中：
echo - ClipboardManager.exe (主程序)
echo - ClipboardManager_v1.0_Portable.zip (便携版)
echo.

pause