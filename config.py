import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigManager:
    """配置管理器，负责应用程序配置的读取、保存和管理"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 数据库配置
        "database": {
            "path": "clipboard_history.db",
            "auto_cleanup_days": 30,
            "max_entries": 10000
        },
        
        # 监听配置
        "monitor": {
            "check_interval": 0.5,  # 监听间隔（秒）
            "auto_start": True,
            "ignore_duplicates": True
        },
        
        # 窗口配置
        "window": {
            "width": 600,
            "height": 800,
            "x": 100,
            "y": 100,
            "always_on_top": False,
            "start_minimized": False,
            "remember_position": True
        },
        
        # 显示配置
        "display": {
            "max_preview_length": 100,
            "show_timestamps": True,
            "date_format": "%Y-%m-%d %H:%M:%S",
            "items_per_page": 50
        },
        
        # 系统托盘配置
        "system_tray": {
            "enabled": True,
            "minimize_to_tray": True,
            "close_to_tray": True,
            "show_notifications": True
        },
        
        # 快捷键配置
        "hotkeys": {
            "show_hide_window": "Ctrl+Alt+V",
            "quick_paste": "Ctrl+Shift+V"
        },
        
        # 数据管理配置
        "data_management": {
            "auto_backup": True,
            "backup_interval_days": 7,
            "export_format": "json"
        },
        
        # 安全配置
        "security": {
            "max_content_length": 1000000,  # 最大内容长度（字符）
            "filter_passwords": True,
            "exclude_patterns": ["password", "passwd", "secret", "token"]
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> bool:
        """从配置文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                # 深度合并配置
                self.config = self._merge_configs(self.DEFAULT_CONFIG, user_config)
                print(f"配置加载成功: {self.config_file}")
                return True
            else:
                print(f"配置文件不存在，使用默认配置: {self.config_file}")
                self.save_config()  # 创建默认配置文件
                return True
                
        except Exception as e:
            print(f"配置加载失败: {e}")
            print("使用默认配置")
            return False
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"配置保存成功: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """深度合并配置字典"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的路径"""
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
                    
            return value
            
        except Exception:
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """设置配置值，支持点号分隔的路径"""
        try:
            keys = key_path.split('.')
            config = self.config
            
            # 导航到最后一级
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 设置值
            config[keys[-1]] = value
            return True
            
        except Exception as e:
            print(f"设置配置失败: {e}")
            return False
    
    def get_database_path(self) -> str:
        """获取数据库路径"""
        return self.get('database.path', 'clipboard_history.db')
    
    def get_window_config(self) -> Dict:
        """获取窗口配置"""
        return self.get('window', {})
    
    def get_monitor_config(self) -> Dict:
        """获取监听配置"""
        return self.get('monitor', {})
    
    def get_display_config(self) -> Dict:
        """获取显示配置"""
        return self.get('display', {})
    
    def get_system_tray_config(self) -> Dict:
        """获取系统托盘配置"""
        return self.get('system_tray', {})
    
    def should_filter_content(self, content: str) -> bool:
        """检查内容是否应该被过滤"""
        if not self.get('security.filter_passwords', True):
            return False
            
        content_lower = content.lower()
        patterns = self.get('security.exclude_patterns', [])
        
        for pattern in patterns:
            if pattern.lower() in content_lower:
                return True
                
        return False
    
    def is_content_too_long(self, content: str) -> bool:
        """检查内容是否过长"""
        max_length = self.get('security.max_content_length', 1000000)
        return len(content) > max_length
    
    def update_window_position(self, x: int, y: int, width: int, height: int):
        """更新窗口位置和大小"""
        if self.get('window.remember_position', True):
            self.set('window.x', x)
            self.set('window.y', y)
            self.set('window.width', width)
            self.set('window.height', height)
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            self.config = self.DEFAULT_CONFIG.copy()
            return self.save_config()
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """导出配置到指定路径"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"配置导出成功: {export_path}")
            return True
        except Exception as e:
            print(f"配置导出失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """从指定路径导入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                
            # 验证配置格式
            if not isinstance(imported_config, dict):
                raise ValueError("配置格式无效")
                
            # 合并配置
            self.config = self._merge_configs(self.DEFAULT_CONFIG, imported_config)
            
            # 保存到当前配置文件
            self.save_config()
            print(f"配置导入成功: {import_path}")
            return True
            
        except Exception as e:
            print(f"配置导入失败: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """验证配置的有效性，返回错误信息列表"""
        errors = []
        
        # 验证数据库配置
        if not isinstance(self.get('database.path'), str):
            errors.append("数据库路径必须是字符串")
            
        # 验证监听间隔
        interval = self.get('monitor.check_interval')
        if not isinstance(interval, (int, float)) or interval <= 0:
            errors.append("监听间隔必须是正数")
            
        # 验证窗口大小
        width = self.get('window.width')
        height = self.get('window.height')
        if not isinstance(width, int) or width < 100:
            errors.append("窗口宽度必须是大于100的整数")
        if not isinstance(height, int) or height < 100:
            errors.append("窗口高度必须是大于100的整数")
            
        return errors
    
    def get_app_data_dir(self) -> str:
        """获取应用数据目录"""
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA', '')
            return os.path.join(app_data, 'ClipboardManager')
        else:  # Linux/Unix
            home = os.path.expanduser('~')
            return os.path.join(home, '.clipboard-manager')
    
    def ensure_app_data_dir(self) -> bool:
        """确保应用数据目录存在"""
        try:
            app_dir = self.get_app_data_dir()
            os.makedirs(app_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建应用数据目录失败: {e}")
            return False


def test_config_manager():
    """测试配置管理器功能"""
    
    # 创建测试配置文件
    test_config_file = "test_config.json"
    
    print("测试配置管理器...")
    
    # 创建配置管理器
    config = ConfigManager(test_config_file)
    
    # 测试获取配置
    print(f"数据库路径: {config.get_database_path()}")
    print(f"窗口配置: {config.get_window_config()}")
    print(f"监听间隔: {config.get('monitor.check_interval')}")
    
    # 测试设置配置
    config.set('window.width', 800)
    config.set('window.height', 600)
    config.set('test.new_setting', 'test_value')
    
    # 测试保存配置
    config.save_config()
    
    # 测试加载配置
    config2 = ConfigManager(test_config_file)
    print(f"重新加载后的窗口宽度: {config2.get('window.width')}")
    
    # 测试过滤功能
    print(f"是否过滤密码内容: {config.should_filter_content('my password is 123')}")
    print(f"是否过滤普通内容: {config.should_filter_content('hello world')}")
    
    # 测试配置验证
    errors = config.validate_config()
    print(f"配置验证错误: {errors}")
    
    # 清理测试文件
    if os.path.exists(test_config_file):
        os.remove(test_config_file)
    
    print("配置管理器测试完成")


if __name__ == "__main__":
    test_config_manager()