#!/usr/bin/env python3
"""
强制清理FTS5相关表和触发器
"""
import sqlite3
import os

def force_clean_fts5():
    """强制清理FTS5相关对象"""
    db_path = "blog.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    print("开始强制清理FTS5相关对象...")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 先检查现有的触发器和表
        print("\n=== 检查现有对象 ===")
        
        # 检查触发器
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE '%articles%'")
        triggers = cursor.fetchall()
        print(f"现有文章相关触发器: {[t[0] for t in triggers]}")
        
        # 检查FTS5相关表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")
        fts_tables = cursor.fetchall()
        print(f"现有FTS5相关表: {[t[0] for t in fts_tables]}")
        
        # 2. 强制删除所有触发器
        print("\n=== 删除触发器 ===")
        triggers_to_drop = [
            "articles_ai",
            "articles_ad", 
            "articles_au"
        ]
        
        for trigger in triggers_to_drop:
            try:
                cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
                print(f"✓ 删除触发器 {trigger}")
            except Exception as e:
                print(f"✗ 删除触发器 {trigger} 失败: {e}")
        
        # 3. 强制删除FTS5表（使用VACUUM清理）
        print("\n=== 删除FTS5表 ===")
        fts_tables_to_drop = [
            "articles_fts",
            "articles_fts_config",
            "articles_fts_data", 
            "articles_fts_docsize",
            "articles_fts_content",
            "articles_fts_idx"
        ]
        
        for table in fts_tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"✓ 删除表 {table}")
            except Exception as e:
                print(f"✗ 删除表 {table} 失败: {e}")
        
        # 4. 执行VACUUM清理数据库
        print("\n=== 执行VACUUM清理 ===")
        try:
            cursor.execute("VACUUM")
            print("✓ VACUUM清理完成")
        except Exception as e:
            print(f"✗ VACUUM清理失败: {e}")
        
        # 5. 提交更改
        conn.commit()
        print("\n=== 提交更改 ===")
        print("✓ 数据库更改已提交")
        
        # 6. 验证清理结果
        print("\n=== 验证清理结果 ===")
        
        # 检查触发器
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE '%articles%'")
        remaining_triggers = cursor.fetchall()
        if remaining_triggers:
            print(f"⚠️  仍有触发器存在: {[t[0] for t in remaining_triggers]}")
        else:
            print("✓ 所有文章相关触发器已清理")
        
        # 检查FTS5表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")
        remaining_fts = cursor.fetchall()
        if remaining_fts:
            print(f"⚠️  仍有FTS5相关表存在: {[t[0] for t in remaining_fts]}")
        else:
            print("✓ 所有FTS5相关表已清理")
        
        # 7. 检查数据库完整性
        print("\n=== 检查数据库完整性 ===")
        try:
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            if integrity_result and integrity_result[0] == "ok":
                print("✓ 数据库完整性检查通过")
            else:
                print(f"⚠️  数据库完整性检查结果: {integrity_result}")
        except Exception as e:
            print(f"✗ 数据库完整性检查失败: {e}")
        
        conn.close()
        print("\n=== 清理完成 ===")
        print("数据库连接已关闭")
        
    except Exception as e:
        print(f"清理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_clean_fts5() 