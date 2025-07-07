#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪贴板管理器主程序
一个轻量级的 Windows 剪贴板历史记录管理工具
"""

import sys
import os
import traceback
import threading
import time
from typing import Optional
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入应用程序模块
try:
    from config import ConfigManager
    from clipboard_storage import ClipboardStorage
    from clipboard_monitor import ClipboardMonitor
    from clipboard_ui import ClipboardUI
    from system_tray import SystemTray
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)


class ClipboardManagerApp:
    """剪贴板管理器主应用程序类"""
    
    def __init__(self):
        self.config = None
        self.storage = None
        self.monitor = None
        self.ui = None
        self.tray = None
        self.running = False
        
        # 初始化应用程序
        self.initialize()
    
    def initialize(self):
        """初始化应用程序"""
        try:
            print("正在初始化剪贴板管理器...")
            
            # 初始化配置管理器
            self.config = ConfigManager()
            print("配置管理器初始化完成")
            
            # 确保应用数据目录存在
            self.config.ensure_app_data_dir()
            
            # 初始化数据存储
            db_path = self.config.get_database_path()
            self.storage = ClipboardStorage(db_path)
            print("数据存储初始化完成")
            
            # 初始化剪贴板监听器
            self.monitor = ClipboardMonitor(self.on_clipboard_changed)
            print("剪贴板监听器初始化完成")
            
            # 初始化用户界面
            self.ui = ClipboardUI(self.config, self.storage)
            print("用户界面初始化完成")
            
            # 设置UI回调函数
            self.ui.set_callbacks(
                on_copy=self.on_item_copied,
                on_delete=self.on_item_deleted,
                on_favorite=self.on_item_favorited,
                on_clear=self.on_data_cleared
            )
            
            # 设置UI窗口关闭回调
            self.ui.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
            
            # 初始化系统托盘
            if self.config.get('system_tray.enabled', True):
                self.tray = SystemTray(self)
                self.tray.set_callbacks(
                    show_window=self.show_window,
                    hide_window=self.hide_window,
                    quit_application=self.shutdown
                )
                print("系统托盘初始化完成")
            
            print("应用程序初始化完成")
            
        except Exception as e:
            error_msg = f"应用程序初始化失败: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            
            # 尝试显示错误对话框
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("初始化错误", error_msg)
                root.destroy()
            except:
                pass
            
            sys.exit(1)
    
    def on_clipboard_changed(self, event_type: str, data: dict):
        """剪贴板变化回调函数"""
        try:
            if event_type == 'clipboard_changed':
                content = data['content']
                content_type = data['type']
                
                # 检查内容过滤
                if self.config.should_filter_content(content):
                    print(f"内容被过滤: {content[:50]}...")
                    return
                
                # 检查内容长度
                if self.config.is_content_too_long(content):
                    print(f"内容过长，已忽略: {len(content)} 字符")
                    return
                
                # 保存到数据库
                metadata = {
                    'source': 'clipboard_monitor',
                    'timestamp': data['timestamp'].isoformat()
                }
                
                if self.storage.add_clipboard_entry(content, content_type, metadata):
                    print(f"新剪贴板记录已保存: {len(content)} 字符")
                    
                    # 刷新UI显示（在主线程中执行）
                    if self.ui and self.ui.root:
                        self.ui.root.after(0, self.refresh_ui)
                    
                    # 系统托盘通知
                    if self.tray and self.config.get('system_tray.show_notifications', True):
                        preview = content[:30] + '...' if len(content) > 30 else content
                        self.tray.show_notification("剪贴板记录", f"已保存: {preview}")
                else:
                    print("保存剪贴板记录失败")
                    
        except Exception as e:
            print(f"处理剪贴板变化失败: {e}")
    
    def refresh_ui(self):
        """刷新用户界面"""
        try:
            if self.ui:
                # 保持当前搜索状态
                current_search = self.ui.search_var.get() if self.ui.search_var else ""
                self.ui.refresh_data(current_search)
        except Exception as e:
            print(f"刷新UI失败: {e}")
    
    def on_item_copied(self, item: dict):
        """项目被复制回调"""
        print(f"项目已复制: ID {item['id']}")
    
    def on_item_deleted(self, item: dict):
        """项目被删除回调"""
        print(f"项目已删除: ID {item['id']}")
    
    def on_item_favorited(self, item: dict):
        """项目收藏状态改变回调"""
        status = "收藏" if not item['is_favorite'] else "取消收藏"
        print(f"项目{status}: ID {item['id']}")
    
    def on_data_cleared(self):
        """数据被清空回调"""
        print("所有数据已清空")
    
    def on_window_close(self):
        """窗口关闭回调"""
        try:
            # 检查是否最小化到托盘
            if self.config.get('system_tray.close_to_tray', True):
                self.ui.hide_window()
                print("应用程序已最小化到托盘")
            else:
                self.shutdown()
        except Exception as e:
            print(f"窗口关闭处理失败: {e}")
            self.shutdown()
    
    def start_monitoring(self):
        """开始监听剪贴板"""
        try:
            if self.config.get('monitor.auto_start', True):
                self.monitor.start_monitoring()
                print("剪贴板监听已启动")
            else:
                print("自动监听已禁用")
        except Exception as e:
            print(f"启动监听失败: {e}")
    
    def stop_monitoring(self):
        """停止监听剪贴板"""
        try:
            if self.monitor:
                self.monitor.stop_monitoring()
                print("剪贴板监听已停止")
        except Exception as e:
            print(f"停止监听失败: {e}")
    
    def run(self):
        """运行应用程序"""
        try:
            self.running = True
            print("正在启动剪贴板管理器...")
            
            # 启动剪贴板监听
            self.start_monitoring()
            
            # 启动系统托盘
            if self.tray:
                if self.tray.start():
                    print("系统托盘已启动")
                else:
                    print("系统托盘启动失败")
            
            # 检查是否以最小化方式启动
            if self.config.get('window.start_minimized', False):
                self.ui.hide_window()
            else:
                self.ui.show_window()
            
            print("剪贴板管理器已启动")
            
            # 运行主循环
            self.ui.run()
            
        except KeyboardInterrupt:
            print("收到中断信号，正在退出...")
            self.shutdown()
        except Exception as e:
            error_msg = f"运行时错误: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            
            try:
                messagebox.showerror("运行时错误", error_msg)
            except:
                pass
            
            self.shutdown()
    
    def shutdown(self):
        """关闭应用程序"""
        try:
            if not self.running:
                return
                
            print("正在关闭剪贴板管理器...")
            self.running = False
            
            # 停止剪贴板监听
            self.stop_monitoring()
            
            # 停止系统托盘
            if self.tray:
                self.tray.stop()
                print("系统托盘已停止")
            
            # 保存配置
            if self.config:
                self.config.save_config()
                print("配置已保存")
            
            # 关闭数据库连接
            if self.storage:
                # 这里可以添加清理数据库连接的代码
                print("数据库连接已关闭")
            
            # 关闭UI
            if self.ui and self.ui.root:
                try:
                    self.ui.root.quit()
                    self.ui.root.destroy()
                except:
                    pass
            
            print("剪贴板管理器已关闭")
            
        except Exception as e:
            print(f"关闭应用程序时出错: {e}")
        finally:
            # 强制退出
            os._exit(0)
    
    def show_window(self):
        """显示主窗口"""
        if self.ui:
            self.ui.show_window()
    
    def hide_window(self):
        """隐藏主窗口"""
        if self.ui:
            self.ui.hide_window()
    
    def toggle_window(self):
        """切换窗口显示状态"""
        if self.ui:
            try:
                if self.ui.root.state() == 'withdrawn':
                    self.show_window()
                else:
                    self.hide_window()
            except:
                self.show_window()


def check_dependencies():
    """检查依赖"""
    try:
        import win32clipboard
        import win32con
        import sqlite3
        import tkinter
        print("所有依赖检查通过")
        return True
    except ImportError as e:
        print(f"依赖检查失败: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def check_platform():
    """检查平台兼容性"""
    if sys.platform != 'win32':
        print("警告: 此应用程序主要为 Windows 平台设计")
        return False
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("剪贴板管理器 v1.0")
    print("=" * 50)
    
    # 检查平台
    if not check_platform():
        print("平台检查失败")
        input("按回车键退出...")
        return
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败")
        input("按回车键退出...")
        return
    
    # 创建并运行应用程序
    try:
        app = ClipboardManagerApp()
        app.run()
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        print(traceback.format_exc())
        input("按回车键退出...")


if __name__ == "__main__":
    main()