import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json


class ClipboardStorage:
    """剪贴板数据存储管理器，使用SQLite数据库"""
    
    def __init__(self, db_path: str = "clipboard_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库，创建必要的表结构"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建剪贴板历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'text',
                    content_hash TEXT UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    size INTEGER DEFAULT 0,
                    is_favorite BOOLEAN DEFAULT 0,
                    metadata TEXT DEFAULT '{}'
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON clipboard_history(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_history(content_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_type ON clipboard_history(content_type)')
            
            conn.commit()
            conn.close()
            print(f"数据库初始化成功: {self.db_path}")
            
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            raise
    
    def get_content_hash(self, content: str) -> str:
        """计算内容的MD5哈希值，用于去重"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def add_clipboard_entry(self, content: str, content_type: str = 'text', metadata: dict = None) -> bool:
        """添加剪贴板记录到数据库"""
        if not content or not content.strip():
            return False
            
        content_hash = self.get_content_hash(content)
        metadata = metadata or {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否已存在相同内容
            cursor.execute(
                'SELECT id, timestamp FROM clipboard_history WHERE content_hash = ?',
                (content_hash,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # 如果已存在，更新时间戳
                cursor.execute(
                    'UPDATE clipboard_history SET timestamp = CURRENT_TIMESTAMP WHERE id = ?',
                    (existing[0],)
                )
                print(f"更新已存在记录的时间戳: ID {existing[0]}")
            else:
                # 添加新记录
                cursor.execute('''
                    INSERT INTO clipboard_history 
                    (content, content_type, content_hash, size, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    content,
                    content_type,
                    content_hash,
                    len(content),
                    json.dumps(metadata)
                ))
                print(f"添加新的剪贴板记录: {len(content)} 字符")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"添加剪贴板记录失败: {e}")
            return False
    
    def get_clipboard_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取剪贴板历史记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content, content_type, timestamp, size, is_favorite, metadata
                FROM clipboard_history
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'content': row[1],
                    'content_type': row[2],
                    'timestamp': row[3],
                    'size': row[4],
                    'is_favorite': bool(row[5]),
                    'metadata': json.loads(row[6]) if row[6] else {},
                    'preview': row[1][:100] + '...' if len(row[1]) > 100 else row[1]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []
    
    def search_clipboard_history(self, query: str, limit: int = 50) -> List[Dict]:
        """搜索剪贴板历史记录"""
        if not query.strip():
            return self.get_clipboard_history(limit)
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            search_pattern = f"%{query}%"
            cursor.execute('''
                SELECT id, content, content_type, timestamp, size, is_favorite, metadata
                FROM clipboard_history
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (search_pattern, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'content': row[1],
                    'content_type': row[2],
                    'timestamp': row[3],
                    'size': row[4],
                    'is_favorite': bool(row[5]),
                    'metadata': json.loads(row[6]) if row[6] else {},
                    'preview': row[1][:100] + '...' if len(row[1]) > 100 else row[1]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"搜索历史记录失败: {e}")
            return []
    
    def delete_clipboard_entry(self, entry_id: int) -> bool:
        """删除指定的剪贴板记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM clipboard_history WHERE id = ?', (entry_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"删除记录成功: ID {entry_id}")
                result = True
            else:
                print(f"未找到要删除的记录: ID {entry_id}")
                result = False
                
            conn.close()
            return result
            
        except Exception as e:
            print(f"删除记录失败: {e}")
            return False
    
    def toggle_favorite(self, entry_id: int) -> bool:
        """切换记录的收藏状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'UPDATE clipboard_history SET is_favorite = NOT is_favorite WHERE id = ?',
                (entry_id,)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"切换收藏状态成功: ID {entry_id}")
                result = True
            else:
                result = False
                
            conn.close()
            return result
            
        except Exception as e:
            print(f"切换收藏状态失败: {e}")
            return False
    
    def clear_old_entries(self, days: int = 30) -> int:
        """清理指定天数之前的记录（保留收藏的记录）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM clipboard_history 
                WHERE timestamp < ? AND is_favorite = 0
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"清理了 {deleted_count} 条超过 {days} 天的记录")
            return deleted_count
            
        except Exception as e:
            print(f"清理旧记录失败: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """获取数据库统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 总记录数
            cursor.execute('SELECT COUNT(*) FROM clipboard_history')
            total_count = cursor.fetchone()[0]
            
            # 收藏记录数
            cursor.execute('SELECT COUNT(*) FROM clipboard_history WHERE is_favorite = 1')
            favorite_count = cursor.fetchone()[0]
            
            # 今天的记录数
            today = datetime.now().date()
            cursor.execute(
                'SELECT COUNT(*) FROM clipboard_history WHERE DATE(timestamp) = ?',
                (today,)
            )
            today_count = cursor.fetchone()[0]
            
            # 数据库文件大小
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            conn.close()
            
            return {
                'total_count': total_count,
                'favorite_count': favorite_count,
                'today_count': today_count,
                'db_size': db_size,
                'db_size_mb': round(db_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}
    
    def export_data(self, output_file: str, format: str = 'json') -> bool:
        """导出数据到文件"""
        try:
            data = self.get_clipboard_history(limit=10000)  # 导出所有数据
            
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            else:
                print(f"不支持的导出格式: {format}")
                return False
                
            print(f"数据导出成功: {output_file}")
            return True
            
        except Exception as e:
            print(f"数据导出失败: {e}")
            return False


def test_clipboard_storage():
    """测试数据存储功能"""
    
    # 使用测试数据库
    storage = ClipboardStorage("test_clipboard.db")
    
    # 测试添加记录
    print("测试添加记录...")
    storage.add_clipboard_entry("这是第一条测试记录")
    storage.add_clipboard_entry("这是第二条测试记录，内容稍长一些，用于测试长文本的处理")
    storage.add_clipboard_entry("python code example: print('hello world')", "code")
    
    # 测试获取历史记录
    print("\n测试获取历史记录...")
    history = storage.get_clipboard_history(5)
    for item in history:
        print(f"ID: {item['id']}, 时间: {item['timestamp']}, 预览: {item['preview']}")
    
    # 测试搜索
    print("\n测试搜索功能...")
    results = storage.search_clipboard_history("测试")
    print(f"搜索 '测试' 找到 {len(results)} 条记录")
    
    # 测试统计信息
    print("\n测试统计信息...")
    stats = storage.get_statistics()
    print(f"统计信息: {stats}")
    
    # 清理测试数据库
    os.remove("test_clipboard.db")
    print("\n测试完成，清理测试数据库")


if __name__ == "__main__":
    test_clipboard_storage()