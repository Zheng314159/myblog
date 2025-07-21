#!/usr/bin/env python3
"""
Debug script to test search functionality
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.core.search import FTSSearch
from app.models.article import Article, ArticleStatus
from sqlalchemy import select, text

async def test_search_functionality():
    """Test search functionality"""
    print("=== Search Debug Test ===")
    
    async for db in get_db():
        try:
            # 1. 检查FTS表是否存在
            print("\n1. 检查FTS表状态...")
            result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='articles_fts'"))
            fts_exists = result.scalar()
            print(f"FTS表存在: {fts_exists}")
            
            if fts_exists:
                # 检查FTS表中的数据
                result = await db.execute(text("SELECT COUNT(*) FROM articles_fts"))
                fts_count = result.scalar()
                print(f"FTS表中的记录数: {fts_count}")
                
                # 显示FTS表中的一些数据
                result = await db.execute(text("SELECT id, title, content FROM articles_fts LIMIT 3"))
                fts_data = result.fetchall()
                print("FTS表中的数据示例:")
                for row in fts_data:
                    print(f"  ID: {row[0]}, Title: {row[1][:50]}..., Content: {row[2][:50]}...")
            
            # 2. 检查文章表中的数据
            print("\n2. 检查文章表数据...")
            result = await db.execute(select(Article).where(Article.status == ArticleStatus.PUBLISHED))
            articles = result.scalars().all()
            print(f"已发布的文章数量: {len(articles)}")
            
            for article in articles:
                print(f"  文章ID: {article.id}, 标题: {article.title}")
                if "数学" in article.content:
                    print(f"    -> 内容包含'数学'字样")
            
            # 3. 测试搜索功能
            print("\n3. 测试搜索功能...")
            
            # 测试搜索"数学"
            print("搜索关键词: '数学'")
            search_results = await FTSSearch.search_articles(db, "数学", limit=10)
            print(f"FTS搜索结果数量: {len(search_results)}")
            
            for result in search_results:
                print(f"  找到文章: {result.title}")
            
            # 4. 如果FTS搜索没有结果，测试备选搜索
            if not search_results:
                print("\n4. FTS搜索无结果，测试备选搜索...")
                from app.api.v1.search import search_articles_fallback
                fallback_results = await search_articles_fallback(db, "数学", limit=10)
                print(f"备选搜索结果数量: {len(fallback_results)}")
                
                for result in fallback_results:
                    print(f"  找到文章: {result.title}")
            
            # 5. 检查搜索索引状态
            print("\n5. 检查搜索索引状态...")
            try:
                result = await db.execute(text("SELECT COUNT(*) FROM articles_fts"))
                indexed_count = result.scalar()
                
                result = await db.execute(select(Article).where(Article.status == ArticleStatus.PUBLISHED))
                published_count = len(result.scalars().all())
                
                coverage = indexed_count / published_count if published_count > 0 else 0
                print(f"索引覆盖率: {coverage:.2%} ({indexed_count}/{published_count})")
                
                if coverage < 0.8:
                    print("警告: 索引覆盖率较低，建议重新初始化搜索索引")
                    
            except Exception as e:
                print(f"检查索引状态失败: {e}")
            
        except Exception as e:
            print(f"测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

async def reinitialize_search_index():
    """重新初始化搜索索引"""
    print("=== 重新初始化搜索索引 ===")
    
    async for db in get_db():
        try:
            # 删除现有索引
            await FTSSearch.drop_fts_table(db)
            print("已删除现有FTS表")
            
            # 创建新索引
            await FTSSearch.create_fts_table(db)
            print("已创建新FTS表")
            
            # 填充数据
            await FTSSearch.populate_fts_table(db)
            print("已填充FTS表数据")
            
            # 验证结果
            result = await db.execute(text("SELECT COUNT(*) FROM articles_fts"))
            count = result.scalar()
            print(f"FTS表最终记录数: {count}")
            
        except Exception as e:
            print(f"重新初始化失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reinit":
        asyncio.run(reinitialize_search_index())
    else:
        asyncio.run(test_search_functionality()) 