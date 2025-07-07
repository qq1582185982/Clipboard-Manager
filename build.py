#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序打包脚本
使用 PyInstaller 将应用程序打包成独立的 exe 文件
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path


def check_pyinstaller():
    """检查 PyInstaller 是否安装"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller 版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理 .pyc 文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))


def create_icon():
    """创建应用图标（如果不存在）"""
    icon_path = Path('assets') / 'icon.ico'
    
    if not icon_path.exists():
        print("创建默认应用图标...")
        
        # 确保 assets 目录存在
        icon_path.parent.mkdir(exist_ok=True)
        
        try:
            from PIL import Image, ImageDraw
            
            # 创建简单的图标
            size = (64, 64)
            image = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 绘制剪贴板图标
            # 外框
            draw.rectangle([8, 6, 56, 58], outline='black', fill='white', width=2)
            # 夹子
            draw.rectangle([20, 2, 44, 10], outline='black', fill='silver', width=1)
            draw.rectangle([22, 4, 42, 8], outline='black', fill='white', width=1)
            # 文本线条
            draw.line([14, 18, 50, 18], fill='black', width=2)
            draw.line([14, 26, 47, 26], fill='black', width=2)
            draw.line([14, 34, 44, 34], fill='black', width=2)
            draw.line([14, 42, 40, 42], fill='black', width=2)
            
            # 保存为 ICO 格式
            image.save(icon_path, format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
            print(f"✓ 图标已创建: {icon_path}")
            
        except ImportError:
            print("! 无法创建图标，PIL 库未安装")
        except Exception as e:
            print(f"! 创建图标失败: {e}")


def build_exe():
    """构建 exe 文件"""
    print("开始构建 exe 文件...")
    
    try:
        # 使用 spec 文件构建
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'clipboard_manager.spec'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✓ 构建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def create_portable_package():
    """创建便携版压缩包"""
    exe_path = Path('dist') / 'ClipboardManager.exe'
    
    if not exe_path.exists():
        print("✗ 未找到构建的 exe 文件")
        return False
    
    print("创建便携版压缩包...")
    
    package_dir = Path('dist') / 'ClipboardManager_Portable'
    package_dir.mkdir(exist_ok=True)
    
    # 复制主要文件
    files_to_copy = [
        ('dist/ClipboardManager.exe', 'ClipboardManager.exe'),
        ('README.md', 'README.md'),
        ('start.bat', 'start.bat'),
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        if src_path.exists():
            shutil.copy2(src_path, package_dir / dst)
            print(f"✓ 复制: {src} -> {dst}")
    
    # 创建启动脚本
    portable_bat = package_dir / 'ClipboardManager.bat'
    with open(portable_bat, 'w', encoding='utf-8') as f:
        f.write('''@echo off
echo 启动剪贴板管理器...
ClipboardManager.exe
pause
''')
    
    # 创建压缩包
    zip_path = Path('dist') / 'ClipboardManager_v1.0_Portable.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
                print(f"添加到压缩包: {arcname}")
    
    print(f"✓ 便携版创建完成: {zip_path}")
    
    # 清理临时目录
    shutil.rmtree(package_dir)
    
    return True


def show_build_info():
    """显示构建信息"""
    print("\n" + "=" * 50)
    print("构建信息")
    print("=" * 50)
    
    exe_path = Path('dist') / 'ClipboardManager.exe'
    zip_path = Path('dist') / 'ClipboardManager_v1.0_Portable.zip'
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ 主程序: {exe_path} ({size_mb:.1f} MB)")
    
    if zip_path.exists():
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"✓ 便携版: {zip_path} ({size_mb:.1f} MB)")
    
    print("\n使用说明:")
    print("1. 双击 ClipboardManager.exe 直接运行")
    print("2. 解压便携版到任意目录使用")
    print("3. 首次运行会自动创建配置文件")


def main():
    """主函数"""
    print("=" * 50)
    print("剪贴板管理器打包工具")
    print("=" * 50)
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        return
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建图标
    create_icon()
    
    # 构建 exe
    if not build_exe():
        print("构建失败，请检查错误信息")
        return
    
    # 创建便携版
    create_portable_package()
    
    # 显示构建信息
    show_build_info()
    
    print("\n🎉 打包完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n打包被用户中断")
    except Exception as e:
        print(f"\n打包过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")