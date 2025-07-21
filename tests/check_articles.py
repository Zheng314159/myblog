import asyncio
import sqlite3
from pathlib import Path

async def check_articles():
    """检查数据库中的文章状态"""
    db_path = Path("blog.db")
    if not db_path.exists():
        print("数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查所有文章
    cursor.execute("SELECT id, title, status FROM article")
    articles = cursor.fetchall()
    
    print(f"数据库中共有 {len(articles)} 篇文章:")
    for article in articles:
        print(f"  ID: {article[0]}, 标题: '{article[1]}', 状态: '{article[2]}'")
    
    # 检查不同状态的文章数量
    cursor.execute("SELECT status, COUNT(*) FROM article GROUP BY status")
    status_counts = cursor.fetchall()
    
    print(f"\n各状态文章数量:")
    for status, count in status_counts:
        print(f"  {status}: {count} 篇")
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(check_articles()) 