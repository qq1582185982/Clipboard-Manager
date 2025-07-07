@echo off
echo ================================================
echo          Python 快速安装指导
echo ================================================
echo.
echo 检测到您的系统可能没有安装Python
echo.
echo 请按照以下步骤安装Python：
echo.
echo 1. 打开浏览器访问：https://www.python.org/downloads/
echo 2. 点击 "Download Python 3.x.x" 下载最新版本
echo 3. 运行下载的安装程序
echo 4. 重要：勾选 "Add Python to PATH" 选项
echo 5. 点击 "Install Now" 完成安装
echo.
echo 安装完成后，重新运行 build.bat 即可自动打包
echo.
echo 是否现在打开Python官网？
choice /c YN /m "按 Y 打开官网，按 N 退出"

if errorlevel 2 goto :end
if errorlevel 1 goto :open_website

:open_website
start https://www.python.org/downloads/
echo 已为您打开Python官网，请下载并安装
echo.

:end
echo.
echo 安装Python后，请：
echo 1. 重新打开命令提示符
echo 2. 运行 build.bat 开始打包
echo 3. 或运行 start.bat 直接启动应用
echo.
pause