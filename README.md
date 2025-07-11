# 剪贴板管理器

一个轻量级的 Windows 剪贴板历史记录管理工具，帮您跟踪和管理复制的所有内容。

## 🌟 功能特性

- **实时监听** - 自动捕获剪贴板变化
- **历史记录** - 持久化存储所有复制内容
- **智能搜索** - 快速查找历史记录
- **收藏功能** - 标记重要的剪贴板内容
- **系统托盘** - 最小化到系统托盘运行
- **数据管理** - 支持清理、导出等功能
- **简洁界面** - 直观易用的 GUI 界面

## 📋 系统要求

- **操作系统**: Windows 7/8/10/11
- **Python**: 3.7 或更高版本
- **内存**: 至少 100MB 可用内存
- **磁盘**: 至少 50MB 可用空间

## 🚀 快速开始

### 方法1: 下载预编译版本（推荐）

1. 访问项目的 [GitHub Releases](../../releases) 页面
2. 下载最新版本的 `ClipboardManager-v*.exe`
3. 双击运行，无需安装任何依赖
4. 首次运行会自动创建配置文件

### 方法2: GitHub Actions自动构建

1. Fork或上传代码到GitHub仓库
2. GitHub会自动构建Windows exe文件
3. 在Actions页面下载构建产物
4. 详见 [GitHub Actions构建指南](GITHUB_ACTIONS_GUIDE.md)

### 方法3: 源码运行（开发者）

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动应用程序**
   ```bash
   python main.py
   ```

## 📦 依赖包说明

### 必需依赖
- `pywin32` - Windows API 支持
- `tkinter` - GUI 界面（Python 内置）
- `sqlite3` - 数据库支持（Python 内置）

### 可选依赖
- `pystray` - 系统托盘支持
- `Pillow` - 图像处理支持

## 🎯 使用说明

### 基本操作

1. **启动应用程序**
   - 运行后会出现主窗口
   - 应用程序自动开始监听剪贴板

2. **查看历史记录**
   - 主界面显示所有剪贴板历史
   - 双击任意记录可复制到剪贴板

3. **搜索内容**
   - 在搜索框中输入关键词
   - 支持实时搜索过滤

4. **管理记录**
   - 右键点击记录显示操作菜单
   - 支持复制、删除、收藏等操作

### 高级功能

1. **系统托盘**
   - 关闭窗口时最小化到托盘
   - 右键托盘图标查看功能菜单
   - 双击托盘图标显示主窗口

2. **数据管理**
   - 菜单栏 -> 文件 -> 导出数据
   - 菜单栏 -> 文件 -> 清理旧数据
   - 自动清理超过30天的记录

3. **个性化设置**
   - 窗口置顶功能
   - 启动时最小化选项
   - 自定义清理规则

## ⚙️ 配置文件

应用程序会自动创建 `config.json` 配置文件，主要配置项：

```json
{
  "database": {
    "path": "clipboard_history.db",
    "auto_cleanup_days": 30,
    "max_entries": 10000
  },
  "window": {
    "width": 600,
    "height": 800,
    "always_on_top": false,
    "start_minimized": false
  },
  "system_tray": {
    "enabled": true,
    "close_to_tray": true,
    "show_notifications": true
  }
}
```

## 🔧 故障排除

### 常见问题

1. **应用程序无法启动**
   - 检查 Python 版本是否为 3.7+
   - 运行 `python test_modules.py` 检查依赖

2. **剪贴板监听不工作**
   - 确保在 Windows 环境下运行
   - 检查是否有其他程序占用剪贴板

3. **系统托盘不显示**
   - 安装 pystray: `pip install pystray`
   - 检查系统托盘设置

4. **数据库错误**
   - 删除 `clipboard_history.db` 重新开始
   - 检查磁盘空间是否充足

### 调试模式

运行测试脚本检查问题：
```bash
python test_modules.py
```

## 📁 文件结构

```
clipboard_manager/
├── main.py                 # 主程序入口
├── clipboard_monitor.py    # 剪贴板监听模块
├── clipboard_storage.py    # 数据存储模块
├── clipboard_ui.py         # 用户界面模块
├── system_tray.py         # 系统托盘模块
├── config.py              # 配置管理模块
├── run_app.py             # 启动脚本
├── test_modules.py        # 测试脚本
├── requirements.txt       # 依赖列表
├── README.md             # 说明文档
├── config.json           # 配置文件（自动生成）
├── clipboard_history.db  # 数据库文件（自动生成）
└── assets/               # 资源文件
    └── icon.ico          # 应用图标（可选）
```

## 🎮 快捷键

- `Ctrl+C` - 复制选中记录
- `Delete` - 删除选中记录
- `Ctrl+F` - 切换收藏状态
- `F5` - 刷新记录列表
- `Ctrl+A` - 全选记录
- `Esc` - 清除选择

## 🔒 隐私说明

- 所有数据存储在本地 SQLite 数据库中
- 不会上传任何数据到网络
- 支持敏感内容过滤（如密码等）
- 可以随时清理或导出数据

## 📊 性能说明

- 内存占用: 约 30-50MB
- CPU 占用: 极低（监听时约 0.1%）
- 数据库大小: 每1000条记录约 1-2MB
- 启动时间: 约 2-3 秒

## 🤝 技术支持

如果遇到问题：

1. 查看本文档的故障排除部分
2. 运行 `test_modules.py` 进行诊断
3. 检查 `config.json` 配置是否正确
4. 尝试删除数据库文件重新开始

## 📄 许可证

本项目为个人使用工具，仅供学习和个人使用。

## 🔄 版本历史

### v1.0 (2024)
- 初始版本
- 基本剪贴板监听功能
- GUI 界面
- 数据存储和搜索
- 系统托盘集成
- 配置管理

---

**享受您的剪贴板管理体验！** 📋✨