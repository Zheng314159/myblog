from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

async def check_pg_fts_health(db: AsyncSession, test_query: Optional[str] = "test"):
    print("🔍 正在检查 PostgreSQL FTS 健康状况...\n")

    try:
        # 1. 检查 tsv_zh 字段是否存在及类型
        result = await db.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'article' AND column_name = 'tsv_zh';
        """))
        row = result.fetchone()
        if row and row[1] == "tsvector":
            print("✅ 字段 article.tsv_zh 存在，类型为 tsvector")
        else:
            print("❌ 字段 article.tsv_zh 不存在或类型错误")
            return

        # 1.2 检查 tsv_en 字段是否存在及类型
        result = await db.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'article' AND column_name = 'tsv_en';
        """))
        row = result.fetchone()
        if row and row[1] == "tsvector":
            print("✅ 字段 article.tsv_en 存在，类型为 tsvector")
        else:
            print("❌ 字段 article.tsv_en 不存在或类型错误")
            return

        # 2. 检查触发器是否存在
        result = await db.execute(text("""
            SELECT trigger_name
            FROM information_schema.triggers
            WHERE event_object_table = 'article'
              AND trigger_name = 'article_tsv_update';
        """))
        if result.fetchone():
            print("✅ 触发器 article_tsv_update 存在")
        else:
            print("❌ 触发器 article_tsv_update 不存在")

        # 3. 检查函数是否存在
        result = await db.execute(text("""
            SELECT proname
            FROM pg_proc
            WHERE proname = 'update_article_tsvector';
        """))
        if result.fetchone():
            print("✅ 函数 update_article_tsvector() 存在")
        else:
            print("❌ 函数 update_article_tsvector() 不存在")

        # 4. 检查 GIN 索引是否存在
        result = await db.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'article' AND indexname = 'idx_article_tsv_zh';
        """))
        if result.fetchone():
            print("✅ GIN 索引 idx_article_tsv_zh 存在")
        else:
            print("❌ GIN 索引 idx_article_tsv_zh 不存在")

        result = await db.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'article' AND indexname = 'idx_article_tsv_en';
        """))
        if result.fetchone():
            print("✅ GIN 索引 idx_article_tsv_en 存在")
        else:
            print("❌ GIN 索引 idx_article_tsv_en 不存在")

        # 5. 检查是否已有文章填充了 tsv_zh 字段
        result = await db.execute(text("""
            SELECT COUNT(*) FROM article WHERE tsv_zh IS NOT NULL AND tsv_zh != '';
        """))
        count_zh = result.scalar()
        if count_zh is not None and count_zh > 0:
            print(f"✅ 已有 {count_zh} 篇文章填充了 tsv_zh 字段")
        else:
            print("❌ 没有文章填充 tsv_zh 字段，可能未触发更新")

        # 5.2 检查是否已有文章填充了 tsv_en 字段
        result = await db.execute(text("""
            SELECT COUNT(*) FROM article WHERE tsv_en IS NOT NULL AND tsv_en != '';
        """))
        count_en = result.scalar()
        if count_en is not None and count_en > 0:
            print(f"✅ 已有 {count_en} 篇文章填充了 tsv_en 字段")
        else:
            print("❌ 没有文章填充 tsv_en 字段，可能未触发更新")

        # 6. 尝试执行 FTS 搜索（中英文）
        try:
            result = await db.execute(text("""
                SELECT id FROM article
                WHERE tsv_zh @@ plainto_tsquery('simple', :query)
                   OR tsv_en @@ plainto_tsquery('english', :query)
                LIMIT 5
            """), {"query": test_query})
            hits = result.fetchall()
            print(f"✅ FTS 搜索正常，返回 {len(hits)} 条结果")
        except Exception as e:
            print(f"❌ FTS 搜索失败: {e}")

        print("\n🔎 PostgreSQL FTS 健康检查完成\n")

    except Exception as e:
        print(f"❌ 检查过程中出现异常: {e}")

from app.core.database import async_session
import asyncio

async def run_check():
    async with async_session() as session:
        await check_pg_fts_health(session, test_query="ad")

if __name__ == "__main__":
    asyncio.run(run_check())

