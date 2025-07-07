import threading
import time
from typing import Optional, Callable
import tkinter as tk
from tkinter import messagebox
try:
    import pystray
    from pystray import MenuItem as Item
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    pystray = None
    Item = None
    Image = None
    ImageDraw = None


class SystemTray:
    """系统托盘管理器"""
    
    def __init__(self, app_instance=None):
        self.app = app_instance
        self.icon = None
        self.running = False
        self.callbacks = {}
        
        if not PYSTRAY_AVAILABLE:
            print("警告: pystray 库未安装，系统托盘功能不可用")
            print("请运行: pip install pystray pillow")
    
    def create_icon_image(self) -> Optional[Image.Image]:
        """创建托盘图标"""
        if not PYSTRAY_AVAILABLE:
            return None
            
        try:
            # 尝试加载图标文件
            try:
                return Image.open("assets/icon.ico")
            except:
                pass
            
            # 如果没有图标文件，创建一个简单的图标
            width = height = 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 绘制一个简单的剪贴板图标
            # 外框
            draw.rectangle([10, 8, 54, 56], outline='black', fill='white', width=2)
            
            # 夹子
            draw.rectangle([22, 4, 42, 12], outline='black', fill='silver', width=1)
            draw.rectangle([24, 6, 40, 10], outline='black', fill='white', width=1)
            
            # 文本线条
            draw.line([16, 20, 48, 20], fill='black', width=2)
            draw.line([16, 28, 45, 28], fill='black', width=2)
            draw.line([16, 36, 42, 36], fill='black', width=2)
            draw.line([16, 44, 38, 44], fill='black', width=2)
            
            return image
            
        except Exception as e:
            print(f"创建托盘图标失败: {e}")
            return None
    
    def create_menu(self):
        """创建托盘菜单"""
        if not PYSTRAY_AVAILABLE:
            return None
            
        menu_items = [
            Item('显示窗口', self.show_window, default=True),
            Item('隐藏窗口', self.hide_window),
            pystray.Menu.SEPARATOR,
            Item('打开设置', self.open_settings),
            Item('查看统计', self.show_statistics),
            pystray.Menu.SEPARATOR,
            Item('关于', self.show_about),
            Item('退出', self.quit_application)
        ]
        
        return pystray.Menu(*menu_items)
    
    def show_window(self, icon=None, item=None):
        """显示主窗口"""
        try:
            if self.app and hasattr(self.app, 'show_window'):
                self.app.show_window()
            elif hasattr(self, 'on_show_window') and self.callbacks.get('show_window'):
                self.callbacks['show_window']()
        except Exception as e:
            print(f"显示窗口失败: {e}")
    
    def hide_window(self, icon=None, item=None):
        """隐藏主窗口"""
        try:
            if self.app and hasattr(self.app, 'hide_window'):
                self.app.hide_window()
            elif self.callbacks.get('hide_window'):
                self.callbacks['hide_window']()
        except Exception as e:
            print(f"隐藏窗口失败: {e}")
    
    def open_settings(self, icon=None, item=None):
        """打开设置窗口"""
        try:
            if self.callbacks.get('open_settings'):
                self.callbacks['open_settings']()
            else:
                # 简单的设置对话框
                self.show_simple_message("设置", "设置功能正在开发中...")
        except Exception as e:
            print(f"打开设置失败: {e}")
    
    def show_statistics(self, icon=None, item=None):
        """显示统计信息"""
        try:
            if self.app and hasattr(self.app, 'storage'):
                stats = self.app.storage.get_statistics()
                stats_text = f"""剪贴板管理器统计信息

总记录数: {stats.get('total_count', 0)}
收藏记录数: {stats.get('favorite_count', 0)}
今日记录数: {stats.get('today_count', 0)}
数据库大小: {stats.get('db_size_mb', 0)} MB
"""
                self.show_simple_message("统计信息", stats_text)
            else:
                self.show_simple_message("统计信息", "无法获取统计信息")
        except Exception as e:
            print(f"显示统计信息失败: {e}")
    
    def show_about(self, icon=None, item=None):
        """显示关于信息"""
        about_text = """剪贴板管理器 v1.0

一个轻量级的 Windows 剪贴板历史记录管理工具

功能特性:
• 实时监听剪贴板变化
• 历史记录持久化存储
• 搜索和过滤功能
• 收藏功能
• 系统托盘集成
• 数据导出功能

开发: Claude AI Assistant
"""
        self.show_simple_message("关于", about_text)
    
    def quit_application(self, icon=None, item=None):
        """退出应用程序"""
        try:
            if self.callbacks.get('quit_application'):
                self.callbacks['quit_application']()
            elif self.app and hasattr(self.app, 'shutdown'):
                self.app.shutdown()
            else:
                self.stop()
        except Exception as e:
            print(f"退出应用程序失败: {e}")
    
    def show_simple_message(self, title: str, message: str):
        """显示简单消息对话框"""
        try:
            # 创建临时窗口显示消息
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showinfo(title, message)
            root.destroy()
        except Exception as e:
            print(f"显示消息失败: {e}")
    
    def show_notification(self, title: str, message: str, timeout: int = 3):
        """显示系统通知"""
        if not PYSTRAY_AVAILABLE or not self.icon:
            print(f"通知: {title} - {message}")
            return
            
        try:
            self.icon.notify(message, title)
        except Exception as e:
            print(f"显示通知失败: {e}")
    
    def on_double_click(self, icon, item):
        """托盘图标双击事件"""
        self.show_window()
    
    def start(self) -> bool:
        """启动系统托盘"""
        if not PYSTRAY_AVAILABLE:
            print("系统托盘不可用")
            return False
            
        try:
            # 创建图标
            icon_image = self.create_icon_image()
            if not icon_image:
                print("无法创建托盘图标")
                return False
            
            # 创建菜单
            menu = self.create_menu()
            
            # 创建托盘图标
            self.icon = pystray.Icon(
                "ClipboardManager",
                icon_image,
                "剪贴板管理器",
                menu
            )
            
            # 设置双击事件
            self.icon.on_double_click = self.on_double_click
            
            # 在单独的线程中运行托盘
            self.running = True
            tray_thread = threading.Thread(target=self._run_tray, daemon=True)
            tray_thread.start()
            
            print("系统托盘已启动")
            return True
            
        except Exception as e:
            print(f"启动系统托盘失败: {e}")
            return False
    
    def _run_tray(self):
        """在单独线程中运行系统托盘"""
        try:
            if self.icon:
                self.icon.run()
        except Exception as e:
            print(f"系统托盘运行出错: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """停止系统托盘"""
        try:
            self.running = False
            if self.icon:
                self.icon.stop()
                self.icon = None
            print("系统托盘已停止")
        except Exception as e:
            print(f"停止系统托盘失败: {e}")
    
    def is_running(self) -> bool:
        """检查系统托盘是否运行中"""
        return self.running and self.icon is not None
    
    def set_callbacks(self, **callbacks):
        """设置回调函数"""
        self.callbacks.update(callbacks)
    
    def update_tooltip(self, text: str):
        """更新托盘图标提示文本"""
        try:
            if self.icon:
                self.icon.title = text
        except Exception as e:
            print(f"更新提示文本失败: {e}")


def test_system_tray():
    """测试系统托盘功能"""
    print("测试系统托盘功能...")
    
    if not PYSTRAY_AVAILABLE:
        print("pystray 库未安装，无法测试系统托盘功能")
        return
    
    def on_show():
        print("显示窗口回调")
    
    def on_hide():
        print("隐藏窗口回调")
    
    def on_quit():
        print("退出应用程序回调")
        tray.stop()
    
    # 创建系统托盘
    tray = SystemTray()
    
    # 设置回调函数
    tray.set_callbacks(
        show_window=on_show,
        hide_window=on_hide,
        quit_application=on_quit
    )
    
    # 启动托盘
    if tray.start():
        print("系统托盘测试启动成功")
        print("请在系统托盘中查看图标")
        print("右键点击图标查看菜单")
        print("双击图标测试显示窗口功能")
        
        try:
            # 保持运行
            while tray.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            print("收到中断信号")
        finally:
            tray.stop()
    else:
        print("系统托盘测试启动失败")


if __name__ == "__main__":
    test_system_tray()