import threading
import time
import win32clipboard
import win32con
import win32api
from datetime import datetime
from typing import Callable, Optional, Any


class ClipboardMonitor:
    """剪贴板监听器类，负责监听系统剪贴板变化"""
    
    def __init__(self, callback: Optional[Callable[[str, Any], None]] = None):
        self.callback = callback
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_clipboard_content = None
        self.sequence_number = 0
        
    def set_callback(self, callback: Callable[[str, Any], None]):
        """设置剪贴板变化时的回调函数"""
        self.callback = callback
        
    def get_clipboard_text(self) -> Optional[str]:
        """获取剪贴板中的文本内容"""
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return text
            elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                return text.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"获取剪贴板文本失败: {e}")
            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        return None
    
    def get_clipboard_sequence_number(self) -> int:
        """获取剪贴板序列号，用于检测变化"""
        try:
            return win32clipboard.GetClipboardSequenceNumber()
        except Exception:
            return 0
    
    def check_clipboard_change(self):
        """检查剪贴板是否发生变化"""
        current_sequence = self.get_clipboard_sequence_number()
        
        if current_sequence != self.sequence_number:
            self.sequence_number = current_sequence
            current_content = self.get_clipboard_text()
            
            # 检查内容是否真的改变了（有时序列号变化但内容相同）
            if current_content and current_content != self.last_clipboard_content:
                self.last_clipboard_content = current_content
                
                # 创建剪贴板数据对象
                clipboard_data = {
                    'type': 'text',
                    'content': current_content,
                    'timestamp': datetime.now(),
                    'size': len(current_content)
                }
                
                # 调用回调函数
                if self.callback:
                    try:
                        self.callback('clipboard_changed', clipboard_data)
                    except Exception as e:
                        print(f"回调函数执行失败: {e}")
    
    def _monitor_loop(self):
        """监听循环，在后台线程中运行"""
        # 初始化当前剪贴板状态
        self.sequence_number = self.get_clipboard_sequence_number()
        self.last_clipboard_content = self.get_clipboard_text()
        
        while self.is_monitoring:
            try:
                self.check_clipboard_change()
                time.sleep(0.5)  # 每500ms检查一次
            except Exception as e:
                print(f"监听循环出错: {e}")
                time.sleep(1)  # 出错时等待更长时间
    
    def start_monitoring(self):
        """开始监听剪贴板"""
        if self.is_monitoring:
            print("剪贴板监听已经在运行中")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("剪贴板监听已启动")
    
    def stop_monitoring(self):
        """停止监听剪贴板"""
        if not self.is_monitoring:
            print("剪贴板监听未在运行")
            return
            
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("剪贴板监听已停止")
    
    def is_running(self) -> bool:
        """检查监听器是否正在运行"""
        return self.is_monitoring and self.monitor_thread and self.monitor_thread.is_alive()


def test_clipboard_monitor():
    """测试剪贴板监听器功能"""
    
    def on_clipboard_change(event_type: str, data: dict):
        print(f"剪贴板变化检测到:")
        print(f"  时间: {data['timestamp']}")
        print(f"  类型: {data['type']}")
        print(f"  大小: {data['size']} 字符")
        print(f"  内容预览: {data['content'][:100]}...")
        print("-" * 50)
    
    monitor = ClipboardMonitor(on_clipboard_change)
    
    try:
        print("开始测试剪贴板监听器...")
        print("请复制一些文本到剪贴板进行测试")
        print("按 Ctrl+C 停止测试")
        
        monitor.start_monitoring()
        
        # 保持运行直到用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n停止测试...")
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    test_clipboard_monitor()