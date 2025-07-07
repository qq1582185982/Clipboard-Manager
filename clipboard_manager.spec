# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# 应用程序信息
app_name = 'ClipboardManager'
version = '1.0.0'
description = 'Windows 剪贴板历史记录管理工具'

# 入口点
main_script = 'main.py'

# 数据文件
datas = [
    ('assets', 'assets'),  # 包含图标等资源文件（如果存在）
]

# 隐藏导入（PyInstaller 可能无法自动检测的模块）
hiddenimports = [
    'win32clipboard',
    'win32con', 
    'win32api',
    'win32gui',
    'pywintypes',
    'win32event',
    'win32process',
    'pystray',
    'pystray._win32',
    'pystray.util',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'tkinter.filedialog',
    'sqlite3',
    'json',
    'threading',
    'datetime',
    'hashlib',
    'pathlib',
    'typing',
    'pkg_resources.py2_warn',
]

# 排除的模块（减小文件大小）
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'django',
    'flask',
    'tornado',
    'notebook',
    'IPython',
]

# 分析阶段
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 打包阶段
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设为 False 以隐藏控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version_file='version_info.txt' if os.path.exists('version_info.txt') else None,
)

# 可选：创建目录分发（如果需要多文件分发，取消注释以下代码）
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name=app_name,
# )