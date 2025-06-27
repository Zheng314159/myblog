import asyncio
import sqlite3
from pathlib import Path

async def debug_search():
    """调试搜索索引问题"""
    db_path = Path("blog.db")
    if not db_path.exists():
        print("数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 检查数据库表结构 ===")
    
    # 检查FTS表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles_fts'")
    fts_exists = cursor.fetchone()
    print(f"FTS表存在: {fts_exists is not None}")
    
    if fts_exists:
        # 检查FTS表结构
        cursor.execute("PRAGMA table_info(articles_fts)")
        columns = cursor.fetchall()
        print("FTS表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 检查FTS表数据
        cursor.execute("SELECT COUNT(*) FROM articles_fts")
        fts_count = cursor.fetchone()[0]
        print(f"FTS表中的记录数: {fts_count}")
        
        if fts_count > 0:
            cursor.execute("SELECT id, title FROM articles_fts LIMIT 3")
            fts_articles = cursor.fetchall()
            print("FTS表中的前3篇文章:")
            for article in fts_articles:
                print(f"  ID: {article[0]}, 标题: '{article[1]}'")
    
    print("\n=== 检查文章表 ===")
    
    # 检查文章表结构
    cursor.execute("PRAGMA table_info(article)")
    columns = cursor.fetchall()
    print("文章表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 检查所有文章
    cursor.execute("SELECT id, title, status FROM article")
    articles = cursor.fetchall()
    print(f"\n文章表中的记录数: {len(articles)}")
    
    for article in articles:
        print(f"  ID: {article[0]}, 标题: '{article[1]}', 状态: '{article[2]}'")
    
    # 检查PUBLISHED状态的文章
    cursor.execute("SELECT id, title FROM article WHERE status = 'PUBLISHED'")
    published_articles = cursor.fetchall()
    print(f"\nPUBLISHED状态的文章数: {len(published_articles)}")
    
    for article in published_articles:
        print(f"  ID: {article[0]}, 标题: '{article[1]}'")
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(debug_search()) 