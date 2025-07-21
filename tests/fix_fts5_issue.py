#!/usr/bin/env python3
"""
修复FTS5表问题
"""
import sqlite3
import os

def fix_fts5_issue():
    """修复FTS5表问题"""
    db_path = "blog.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    print("开始修复FTS5表问题...")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 删除所有FTS5相关的触发器
        triggers_to_drop = [
            "articles_ai",
            "articles_ad", 
            "articles_au"
        ]
        
        for trigger in triggers_to_drop:
            try:
                cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
                print(f"删除触发器 {trigger}")
            except Exception as e:
                print(f"删除触发器 {trigger} 失败: {e}")
        
        # 2. 删除FTS5表
        try:
            cursor.execute("DROP TABLE IF EXISTS articles_fts")
            print("删除FTS5表 articles_fts")
        except Exception as e:
            print(f"删除FTS5表失败: {e}")
        
        # 3. 删除其他FTS5相关表
        fts_tables = [
            "articles_fts_config",
            "articles_fts_data", 
            "articles_fts_docsize",
            "articles_fts_content",
            "articles_fts_idx"
        ]
        
        for table in fts_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"删除FTS5相关表 {table}")
            except Exception as e:
                print(f"删除表 {table} 失败: {e}")
        
        # 4. 提交更改
        conn.commit()
        print("FTS5表修复完成")
        
        # 5. 验证修复结果
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")
        remaining_fts = cursor.fetchall()
        
        if remaining_fts:
            print(f"警告：仍有FTS5相关表存在: {[row[0] for row in remaining_fts]}")
        else:
            print("所有FTS5相关表已清理完成")
        
        # 6. 检查触发器
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE '%articles%'")
        remaining_triggers = cursor.fetchall()
        
        if remaining_triggers:
            print(f"警告：仍有文章相关触发器存在: {[row[0] for row in remaining_triggers]}")
        else:
            print("所有文章相关触发器已清理完成")
        
        conn.close()
        print("数据库连接已关闭")
        
    except Exception as e:
        print(f"修复过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_fts5_issue() 