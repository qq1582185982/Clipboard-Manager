# Windows 系统快速设置指南

由于您的Windows系统没有Python环境，这里提供几种获取可执行文件的方法。

## 🚀 方法1: 快速安装Python并打包（推荐）

### 第一步：安装Python
1. 访问 https://www.python.org/downloads/
2. 点击 "Download Python 3.x.x" 下载最新版本
3. 运行安装程序，**务必勾选 "Add Python to PATH"**
4. 点击 "Install Now" 完成安装

### 第二步：验证安装
按 `Win + R` 键，输入 `cmd` 回车，然后输入：
```cmd
python --version
```
如果显示版本号，说明安装成功。

### 第三步：一键打包
1. 将项目文件复制到Windows系统
2. 双击 `build.bat` 文件
3. 等待自动安装依赖和打包完成
4. 在 `dist` 文件夹中获取 `ClipboardManager.exe`

## 🌐 方法2: 使用GitHub在线构建

### 上传到GitHub
1. 在GitHub创建新仓库
2. 上传所有项目文件
3. GitHub会自动运行构建流程
4. 在Actions标签页下载生成的exe文件

### 本地使用Git（可选）
如果你有Git：
```cmd
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/clipboard-manager.git
git push -u origin main
```

## 💾 方法3: 使用便携版Python

### 下载便携版Python
1. 访问 https://www.python.org/downloads/windows/
2. 下载 "embeddable zip file" 版本
3. 解压到项目文件夹中
4. 使用相对路径运行

### 创建便携版构建脚本
将以下内容保存为 `portable_build.bat`：

```batch
@echo off
echo ================================================
echo          便携版Python构建脚本
echo ================================================

REM 检查便携版Python
if not exist "python-3.x.x-embed-amd64" (
    echo 请先下载便携版Python并解压到当前目录
    echo 下载地址: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

REM 设置Python路径
set PYTHON_PATH=%CD%\python-3.x.x-embed-amd64
set PATH=%PYTHON_PATH%;%PATH%

REM 安装pip
%PYTHON_PATH%\python.exe -m ensurepip

REM 安装依赖
%PYTHON_PATH%\python.exe -m pip install -r requirements.txt

REM 构建应用
%PYTHON_PATH%\python.exe build.py

echo 构建完成！
pause
```

## 🎯 方法4: 云端构建服务

### 使用GitHub Codespaces
1. 在GitHub仓库页面点击 "Code" -> "Codespaces"
2. 创建新的Codespace
3. 在云端运行构建命令
4. 下载生成的文件

### 使用在线IDE
- **Replit**: 导入项目，在线运行构建
- **CodeSandbox**: 支持Python项目构建
- **Gitpod**: 自动化构建环境

## 📋 所需文件清单

确保您有以下文件：
- ✅ `main.py` - 主程序
- ✅ `clipboard_monitor.py` - 监听模块
- ✅ `clipboard_storage.py` - 存储模块
- ✅ `clipboard_ui.py` - 界面模块
- ✅ `system_tray.py` - 托盘模块
- ✅ `config.py` - 配置模块
- ✅ `requirements.txt` - 依赖列表
- ✅ `clipboard_manager.spec` - 打包配置
- ✅ `version_info.txt` - 版本信息
- ✅ `build.py` - 构建脚本
- ✅ `build.bat` - Windows批处理脚本

## 💡 推荐流程

**最简单的方法**：
1. 安装Python（5分钟）
2. 双击 `build.bat`（自动完成）
3. 获得可执行文件

**如果不想安装Python**：
1. 使用GitHub在线构建
2. 下载预编译文件

## 🆘 需要帮助？

如果遇到问题：
1. 确保Python已正确安装并添加到PATH
2. 检查网络连接（下载依赖时需要）
3. 尝试以管理员身份运行批处理文件
4. 查看错误信息并反馈

---

**选择哪种方法？**
- 🚀 **推荐**: 方法1（安装Python）- 最可靠
- 🌐 **备选**: 方法2（GitHub构建）- 无需本地环境
- 💾 **高级**: 方法3（便携版）- 适合高级用户