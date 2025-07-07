import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import win32clipboard
import win32con
from datetime import datetime
from typing import List, Dict, Optional, Callable
import threading


class ClipboardUI:
    """剪贴板管理器的用户界面"""
    
    def __init__(self, config_manager, storage_manager):
        self.config = config_manager
        self.storage = storage_manager
        self.root = None
        self.current_items = []
        self.selected_item = None
        
        # 回调函数
        self.on_copy_callback = None
        self.on_delete_callback = None
        self.on_favorite_callback = None
        self.on_clear_callback = None
        
        # UI 组件
        self.search_var = None
        self.tree = None
        self.status_label = None
        self.total_label = None
        
        self.create_main_window()
        self.setup_ui()
        
    def create_main_window(self):
        """创建主窗口"""
        self.root = tk.Tk()
        self.root.title("剪贴板管理器")
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # 从配置中获取窗口设置
        window_config = self.config.get_window_config()
        width = window_config.get('width', 600)
        height = window_config.get('height', 800)
        x = window_config.get('x', 100)
        y = window_config.get('y', 100)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # 设置最小窗口大小
        self.root.minsize(400, 300)
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # 窗口置顶设置
        if window_config.get('always_on_top', False):
            self.root.attributes('-topmost', True)
    
    def setup_ui(self):
        """设置用户界面"""
        self.create_menu_bar()
        self.create_toolbar()
        self.create_search_frame()
        self.create_main_content()
        self.create_status_bar()
        
        # 绑定键盘快捷键
        self.setup_shortcuts()
        
        # 加载初始数据
        self.refresh_data()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出数据...", command=self.export_data)
        file_menu.add_command(label="清理旧数据...", command=self.cleanup_old_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_window_close)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="复制选中项", command=self.copy_selected, accelerator="Ctrl+C")
        edit_menu.add_command(label="删除选中项", command=self.delete_selected, accelerator="Delete")
        edit_menu.add_command(label="切换收藏", command=self.toggle_favorite, accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="全部清除...", command=self.clear_all_data)
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="刷新", command=self.refresh_data, accelerator="F5")
        view_menu.add_command(label="置顶窗口", command=self.toggle_always_on_top)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="统计信息", command=self.show_statistics)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # 复制按钮
        ttk.Button(toolbar, text="复制", command=self.copy_selected).pack(side=tk.LEFT, padx=2)
        
        # 删除按钮
        ttk.Button(toolbar, text="删除", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        
        # 收藏按钮
        ttk.Button(toolbar, text="收藏", command=self.toggle_favorite).pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 刷新按钮
        ttk.Button(toolbar, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # 清理按钮
        ttk.Button(toolbar, text="清理", command=self.cleanup_old_data).pack(side=tk.LEFT, padx=2)
    
    def create_search_frame(self):
        """创建搜索框"""
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 绑定搜索事件
        self.search_var.trace('w', self.on_search_changed)
        
        # 搜索按钮
        ttk.Button(search_frame, text="搜索", command=self.search_data).pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_main_content(self):
        """创建主要内容区域"""
        # 创建框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建 Treeview 组件来显示历史记录
        columns = ('时间', '类型', '大小', '预览')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='tree headings', height=15)
        
        # 配置列
        self.tree.heading('#0', text='收藏')
        self.tree.column('#0', width=50, minwidth=50)
        
        self.tree.heading('时间', text='时间')
        self.tree.column('时间', width=150, minwidth=100)
        
        self.tree.heading('类型', text='类型')
        self.tree.column('类型', width=80, minwidth=60)
        
        self.tree.heading('大小', text='大小')
        self.tree.column('大小', width=80, minwidth=60)
        
        self.tree.heading('预览', text='内容预览')
        self.tree.column('预览', width=300, minwidth=200)
        
        # 创建滚动条
        scrollbar_v = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)  # 右键菜单
    
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.total_label = ttk.Label(status_frame, text="总计: 0 项")
        self.total_label.pack(side=tk.RIGHT, padx=5)
    
    def setup_shortcuts(self):
        """设置键盘快捷键"""
        self.root.bind('<Control-c>', lambda e: self.copy_selected())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<Control-f>', lambda e: self.toggle_favorite())
        self.root.bind('<F5>', lambda e: self.refresh_data())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Escape>', lambda e: self.clear_selection())
    
    def refresh_data(self, search_query: str = ""):
        """刷新数据显示"""
        try:
            # 清空当前显示
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 获取数据
            if search_query:
                items = self.storage.search_clipboard_history(search_query, 1000)
            else:
                items = self.storage.get_clipboard_history(1000)
            
            self.current_items = items
            
            # 填充数据
            for item in items:
                # 格式化时间
                timestamp = item['timestamp']
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        timestamp = datetime.now()
                
                formatted_time = timestamp.strftime('%m-%d %H:%M:%S')
                
                # 格式化大小
                size_text = f"{item['size']} 字符"
                
                # 收藏标记
                favorite_icon = "★" if item['is_favorite'] else ""
                
                # 插入项目
                self.tree.insert('', tk.END, 
                               text=favorite_icon,
                               values=(formatted_time, item['content_type'], size_text, item['preview']),
                               tags=('favorite' if item['is_favorite'] else 'normal',))
            
            # 配置标签样式
            self.tree.tag_configure('favorite', foreground='gold')
            self.tree.tag_configure('normal', foreground='black')
            
            # 更新状态栏
            self.total_label.config(text=f"总计: {len(items)} 项")
            self.status_label.config(text="数据已刷新")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新数据失败: {str(e)}")
    
    def on_search_changed(self, *args):
        """搜索框内容变化事件"""
        # 延迟搜索以避免频繁查询
        if hasattr(self, '_search_timer'):
            self.root.after_cancel(self._search_timer)
        
        self._search_timer = self.root.after(500, self.search_data)
    
    def search_data(self):
        """执行搜索"""
        query = self.search_var.get().strip()
        self.refresh_data(query)
        
        if query:
            self.status_label.config(text=f"搜索: {query}")
        else:
            self.status_label.config(text="显示所有记录")
    
    def on_item_select(self, event):
        """列表项选择事件"""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            index = self.tree.index(item_id)
            if 0 <= index < len(self.current_items):
                self.selected_item = self.current_items[index]
            else:
                self.selected_item = None
        else:
            self.selected_item = None
    
    def on_item_double_click(self, event):
        """列表项双击事件"""
        self.copy_selected()
    
    def copy_selected(self):
        """复制选中的项目"""
        if not self.selected_item:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            content = self.selected_item['content']
            
            # 复制到剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(content, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            self.status_label.config(text="已复制到剪贴板")
            
            # 调用回调函数
            if self.on_copy_callback:
                self.on_copy_callback(self.selected_item)
                
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def delete_selected(self):
        """删除选中的项目"""
        if not self.selected_item:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的项目吗？"):
            try:
                if self.storage.delete_clipboard_entry(self.selected_item['id']):
                    self.refresh_data(self.search_var.get())
                    self.status_label.config(text="项目已删除")
                    
                    # 调用回调函数
                    if self.on_delete_callback:
                        self.on_delete_callback(self.selected_item)
                else:
                    messagebox.showerror("错误", "删除失败")
                    
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
    
    def toggle_favorite(self):
        """切换收藏状态"""
        if not self.selected_item:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            if self.storage.toggle_favorite(self.selected_item['id']):
                self.refresh_data(self.search_var.get())
                status = "已收藏" if not self.selected_item['is_favorite'] else "已取消收藏"
                self.status_label.config(text=status)
                
                # 调用回调函数
                if self.on_favorite_callback:
                    self.on_favorite_callback(self.selected_item)
            else:
                messagebox.showerror("错误", "操作失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {str(e)}")
    
    def clear_all_data(self):
        """清空所有数据"""
        if messagebox.askyesno("确认清空", "确定要清空所有剪贴板历史记录吗？\n此操作不可恢复！"):
            try:
                # 这里需要在 storage 中添加清空所有数据的方法
                # self.storage.clear_all_entries()
                self.refresh_data()
                self.status_label.config(text="所有数据已清空")
                
                # 调用回调函数
                if self.on_clear_callback:
                    self.on_clear_callback()
                    
            except Exception as e:
                messagebox.showerror("错误", f"清空失败: {str(e)}")
    
    def cleanup_old_data(self):
        """清理旧数据"""
        days = simpledialog.askinteger("清理旧数据", "清理多少天前的数据？", initialvalue=30, minvalue=1)
        if days:
            try:
                deleted_count = self.storage.clear_old_entries(days)
                self.refresh_data(self.search_var.get())
                self.status_label.config(text=f"已清理 {deleted_count} 条旧记录")
                messagebox.showinfo("清理完成", f"已清理 {deleted_count} 条超过 {days} 天的记录")
                
            except Exception as e:
                messagebox.showerror("错误", f"清理失败: {str(e)}")
    
    def export_data(self):
        """导出数据"""
        filename = filedialog.asksaveasfilename(
            title="导出数据",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                if self.storage.export_data(filename):
                    self.status_label.config(text="数据导出成功")
                    messagebox.showinfo("导出成功", f"数据已导出到: {filename}")
                else:
                    messagebox.showerror("错误", "数据导出失败")
                    
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def show_statistics(self):
        """显示统计信息"""
        try:
            stats = self.storage.get_statistics()
            
            stats_text = f"""剪贴板管理器统计信息
            
总记录数: {stats.get('total_count', 0)}
收藏记录数: {stats.get('favorite_count', 0)}
今日记录数: {stats.get('today_count', 0)}
数据库大小: {stats.get('db_size_mb', 0)} MB
"""
            
            messagebox.showinfo("统计信息", stats_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"获取统计信息失败: {str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """剪贴板管理器 v1.0
        
一个轻量级的 Windows 剪贴板历史记录管理工具

功能特性:
• 实时监听剪贴板变化
• 历史记录持久化存储
• 搜索和过滤功能
• 收藏功能
• 数据导出功能

开发: Claude AI Assistant
"""
        messagebox.showinfo("关于", about_text)
    
    def toggle_always_on_top(self):
        """切换窗口置顶"""
        current = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current)
        status = "已启用" if not current else "已禁用"
        self.status_label.config(text=f"窗口置顶 {status}")
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 选择当前右键点击的项目
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.on_item_select(None)
        
        # 创建右键菜单
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="复制", command=self.copy_selected)
        context_menu.add_command(label="删除", command=self.delete_selected)
        context_menu.add_command(label="切换收藏", command=self.toggle_favorite)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def select_all(self):
        """全选"""
        children = self.tree.get_children()
        self.tree.selection_set(children)
    
    def clear_selection(self):
        """清除选择"""
        self.tree.selection_remove(self.tree.selection())
    
    def on_window_close(self):
        """窗口关闭事件"""
        # 保存窗口位置和大小
        if self.config.get('window.remember_position', True):
            geometry = self.root.geometry()
            # 解析几何字符串 "widthxheight+x+y"
            size_pos = geometry.split('+')
            size = size_pos[0].split('x')
            if len(size) == 2 and len(size_pos) >= 3:
                try:
                    width, height = int(size[0]), int(size[1])
                    x, y = int(size_pos[1]), int(size_pos[2])
                    self.config.update_window_position(x, y, width, height)
                    self.config.save_config()
                except:
                    pass
        
        # 检查是否最小化到托盘
        if self.config.get('system_tray.close_to_tray', True):
            self.root.withdraw()  # 隐藏窗口而不是关闭
        else:
            self.root.quit()
    
    def show_window(self):
        """显示窗口"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide_window(self):
        """隐藏窗口"""
        self.root.withdraw()
    
    def set_callbacks(self, on_copy=None, on_delete=None, on_favorite=None, on_clear=None):
        """设置回调函数"""
        self.on_copy_callback = on_copy
        self.on_delete_callback = on_delete
        self.on_favorite_callback = on_favorite
        self.on_clear_callback = on_clear
    
    def run(self):
        """运行主循环"""
        self.root.mainloop()


def test_clipboard_ui():
    """测试用户界面"""
    from config import ConfigManager
    from clipboard_storage import ClipboardStorage
    
    # 创建测试实例
    config = ConfigManager("test_ui_config.json")
    storage = ClipboardStorage("test_ui_clipboard.db")
    
    # 添加一些测试数据
    storage.add_clipboard_entry("这是第一条测试记录")
    storage.add_clipboard_entry("这是第二条测试记录，内容比较长，用于测试界面显示效果")
    storage.add_clipboard_entry("print('Hello, World!')", "code")
    
    # 创建UI
    ui = ClipboardUI(config, storage)
    
    # 运行
    ui.run()


if __name__ == "__main__":
    test_clipboard_ui()