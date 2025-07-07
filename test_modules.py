#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块测试脚本
验证所有模块是否可以正确导入和初始化
"""

import sys
import os
import traceback

def test_imports():
    """测试模块导入"""
    print("=" * 50)
    print("测试模块导入")
    print("=" * 50)
    
    modules_to_test = [
        'config',
        'clipboard_storage',
        'clipboard_monitor',
        'clipboard_ui',
        'system_tray',
        'main'
    ]
    
    success_count = 0
    
    for module_name in modules_to_test:
        try:
            print(f"测试导入 {module_name}... ", end="")
            module = __import__(module_name)
            print("✓ 成功")
            success_count += 1
        except Exception as e:
            print(f"✗ 失败: {str(e)}")
    
    print(f"\n导入测试结果: {success_count}/{len(modules_to_test)} 成功")
    return success_count == len(modules_to_test)

def test_config_manager():
    """测试配置管理器"""
    print("\n" + "=" * 50)
    print("测试配置管理器")
    print("=" * 50)
    
    try:
        from config import ConfigManager
        
        # 创建测试配置文件
        config = ConfigManager("test_config.json")
        
        # 测试基本功能
        print("测试配置读取... ", end="")
        db_path = config.get_database_path()
        print(f"✓ 数据库路径: {db_path}")
        
        print("测试配置设置... ", end="")
        config.set('test.value', 'test_data')
        value = config.get('test.value')
        assert value == 'test_data'
        print("✓ 成功")
        
        print("测试配置保存... ", end="")
        result = config.save_config()
        print("✓ 成功" if result else "✗ 失败")
        
        # 清理测试文件
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置管理器测试失败: {str(e)}")
        return False

def test_clipboard_storage():
    """测试数据存储"""
    print("\n" + "=" * 50)
    print("测试数据存储")
    print("=" * 50)
    
    try:
        from clipboard_storage import ClipboardStorage
        
        # 创建测试数据库
        storage = ClipboardStorage("test_clipboard.db")
        
        print("测试添加记录... ", end="")
        result = storage.add_clipboard_entry("测试内容", "text")
        print("✓ 成功" if result else "✗ 失败")
        
        print("测试获取历史记录... ", end="")
        history = storage.get_clipboard_history(10)
        print(f"✓ 获取 {len(history)} 条记录")
        
        print("测试搜索功能... ", end="")
        results = storage.search_clipboard_history("测试")
        print(f"✓ 搜索到 {len(results)} 条记录")
        
        print("测试统计信息... ", end="")
        stats = storage.get_statistics()
        print(f"✓ 总记录数: {stats.get('total_count', 0)}")
        
        # 清理测试数据库
        if os.path.exists("test_clipboard.db"):
            os.remove("test_clipboard.db")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据存储测试失败: {str(e)}")
        return False

def test_clipboard_monitor():
    """测试剪贴板监听器（仅测试创建，不启动）"""
    print("\n" + "=" * 50)
    print("测试剪贴板监听器")
    print("=" * 50)
    
    try:
        from clipboard_monitor import ClipboardMonitor
        
        print("测试创建监听器... ", end="")
        monitor = ClipboardMonitor()
        print("✓ 成功")
        
        print("测试设置回调... ", end="")
        def test_callback(event_type, data):
            pass
        monitor.set_callback(test_callback)
        print("✓ 成功")
        
        # 注意：在非Windows环境中不启动实际监听
        if sys.platform == 'win32':
            print("测试获取剪贴板序列号... ", end="")
            seq = monitor.get_clipboard_sequence_number()
            print(f"✓ 序列号: {seq}")
        else:
            print("跳过Windows特定功能测试（非Windows环境）")
        
        return True
        
    except Exception as e:
        print(f"✗ 剪贴板监听器测试失败: {str(e)}")
        return False

def test_system_tray():
    """测试系统托盘"""
    print("\n" + "=" * 50)
    print("测试系统托盘")
    print("=" * 50)
    
    try:
        from system_tray import SystemTray
        
        print("测试创建系统托盘... ", end="")
        tray = SystemTray()
        print("✓ 成功")
        
        print("测试设置回调... ", end="")
        tray.set_callbacks(
            show_window=lambda: print("显示窗口"),
            hide_window=lambda: print("隐藏窗口"),
            quit_application=lambda: print("退出应用程序")
        )
        print("✓ 成功")
        
        print("测试创建图标... ", end="")
        icon = tray.create_icon_image()
        if icon:
            print("✓ 成功")
        else:
            print("! 警告: 无法创建图标（可能缺少依赖）")
        
        return True
        
    except Exception as e:
        print(f"✗ 系统托盘测试失败: {str(e)}")
        return False

def check_dependencies():
    """检查依赖"""
    print("\n" + "=" * 50)
    print("检查依赖")
    print("=" * 50)
    
    dependencies = [
        ('tkinter', 'GUI框架'),
        ('sqlite3', '数据库'),
        ('json', 'JSON处理'),
        ('threading', '多线程'),
        ('datetime', '日期时间'),
        ('hashlib', '哈希计算'),
        ('pathlib', '路径处理')
    ]
    
    if sys.platform == 'win32':
        dependencies.extend([
            ('win32clipboard', 'Windows剪贴板API'),
            ('win32con', 'Windows常量'),
            ('win32api', 'Windows API')
        ])
    
    optional_dependencies = [
        ('pystray', '系统托盘'),
        ('PIL', 'Python图像库')
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {module} ({description})")
            success_count += 1
        except ImportError:
            print(f"✗ {module} ({description}) - 缺失")
    
    print("\n可选依赖:")
    for module, description in optional_dependencies:
        try:
            __import__(module)
            print(f"✓ {module} ({description})")
        except ImportError:
            print(f"! {module} ({description}) - 可选，建议安装")
    
    print(f"\n依赖检查结果: {success_count}/{total_count} 必需依赖可用")
    return success_count == total_count

def run_all_tests():
    """运行所有测试"""
    print("开始模块测试")
    print("当前平台:", sys.platform)
    print("Python版本:", sys.version)
    
    test_results = []
    
    # 依赖检查
    test_results.append(("依赖检查", check_dependencies()))
    
    # 模块导入测试
    test_results.append(("模块导入", test_imports()))
    
    # 功能测试
    test_results.append(("配置管理器", test_config_manager()))
    test_results.append(("数据存储", test_clipboard_storage()))
    test_results.append(("剪贴板监听", test_clipboard_monitor()))
    test_results.append(("系统托盘", test_system_tray()))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(test_results)} 测试通过")
    
    if passed == len(test_results):
        print("🎉 所有测试通过！应用程序可以正常运行。")
    else:
        print("⚠️  部分测试失败，请检查相关问题。")
    
    return passed == len(test_results)

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        print(traceback.format_exc())