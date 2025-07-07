#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序启动脚本
用于在 Windows 环境中启动剪贴板管理器
"""

import sys
import os
import subprocess

def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要 Python 3.7 或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_platform():
    """检查平台"""
    if sys.platform != 'win32':
        print("警告: 此应用程序主要为 Windows 平台设计")
        print(f"当前平台: {sys.platform}")
        response = input("是否继续运行？(y/N): ").lower()
        return response in ['y', 'yes']
    return True

def install_dependencies():
    """安装依赖"""
    print("正在检查并安装依赖...")
    
    try:
        # 尝试安装所有依赖
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False
    except FileNotFoundError:
        print("错误: 找不到 requirements.txt 文件")
        return False

def check_dependencies():
    """检查必要的依赖"""
    required_modules = ['win32clipboard', 'tkinter']
    optional_modules = ['pystray', 'PIL']
    
    missing_required = []
    missing_optional = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_required.append(module)
    
    for module in optional_modules:
        try:
            __import__(module)
        except ImportError:
            missing_optional.append(module)
    
    if missing_required:
        print(f"缺少必需依赖: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"缺少可选依赖: {', '.join(missing_optional)}")
        print("某些功能可能不可用")
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("剪贴板管理器启动器")
    print("=" * 50)
    
    # 检查 Python 版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查平台
    if not check_platform():
        input("按回车键退出...")
        return
    
    # 检查依赖
    if not check_dependencies():
        print("\n尝试自动安装依赖...")
        if not install_dependencies():
            print("依赖安装失败，请手动运行:")
            print("pip install -r requirements.txt")
            input("按回车键退出...")
            return
        
        # 重新检查依赖
        if not check_dependencies():
            print("依赖安装后仍有问题，请检查错误信息")
            input("按回车键退出...")
            return
    
    print("所有检查通过，正在启动应用程序...")
    
    try:
        # 导入并运行主应用程序
        from main import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\n应用程序被用户中断")
    except Exception as e:
        print(f"\n启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()