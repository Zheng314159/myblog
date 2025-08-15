import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from collections import Counter

from app.core.search.fts_base_interface import BaseFTSSearch
from app.models.article import Article, ArticleStatus
from app.models.tag import Tag, ArticleTag
from app.schemas.article import ArticleListResponse, UserBasicInfo, TagInfo


class PostgresFTSSearch(BaseFTSSearch):
    """基于 PostgreSQL tsvector 的全文搜索实现（支持中英文）"""

    @staticmethod
    async def drop_fts_table(db: AsyncSession):
        """删除全文索引和触发器（如果存在）"""
        drop_sqls = [
            "DROP TRIGGER IF EXISTS article_tsv_update ON article",
            "DROP FUNCTION IF EXISTS update_article_tsvector",
            "DROP INDEX IF EXISTS idx_article_tsv_zh",
            "DROP INDEX IF EXISTS idx_article_tsv_en"
        ]
        try:
            for sql in drop_sqls:
                await db.execute(text(sql))
            await db.commit()
            print("✅ 已删除 PostgreSQL FTS 结构")
        except Exception as e:
            await db.rollback()
            print(f"⚠️ Drop SQL 执行失败: {e}")

    @staticmethod
    async def create_fts_table(db: AsyncSession):
        """创建 GIN 索引和 tsvector 更新触发器（支持中英文）"""
        try:
            await PostgresFTSSearch.drop_fts_table(db)
            await db.execute(text("""
                CREATE OR REPLACE FUNCTION update_article_tsvector() RETURNS trigger AS $$
                BEGIN
                    NEW.tsv_zh := to_tsvector('simple', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '') || ' ' || coalesce(NEW.summary, ''));
                    NEW.tsv_en := to_tsvector('english', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '') || ' ' || coalesce(NEW.summary, ''));
                    RETURN NEW;
                END
                $$ LANGUAGE plpgsql;
            """))
            await db.execute(text("""
                CREATE TRIGGER article_tsv_update
                BEFORE INSERT OR UPDATE ON article
                FOR EACH ROW EXECUTE FUNCTION update_article_tsvector();
            """))
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_article_tsv_zh ON article USING GIN(tsv_zh);
            """))
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_article_tsv_en ON article USING GIN(tsv_en);
            """))
            await db.commit()
            print("✅ PostgreSQL FTS 结构创建成功")
        except Exception as e:
            await db.rollback()
            print(f"❌ 创建 PostgreSQL FTS 结构失败: {e}")

    @staticmethod
    async def populate_fts_table(db: AsyncSession):
        """手动触发更新所有现有数据的 tsvector"""
        try:
            await db.execute(text("UPDATE article SET title = title"))
            await db.commit()
            print("✅ 已更新所有文章的 tsvector 字段")
        except Exception as e:
            await db.rollback()
            print(f"❌ 更新 tsvector 失败: {e}")

    @staticmethod
    async def search_articles(
        db: AsyncSession,
        query: str|None,
        skip: int = 0,
        limit: int = 10,
        status: Optional[ArticleStatus] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[ArticleListResponse]:
        """使用 PostgreSQL FTS 查询文章（中英文支持）"""
        assert query is not None
        if not query.strip():
            return []

        ts_query = query.strip()
        sql = """
            SELECT  a.id
            FROM article a
            WHERE (
                a.tsv_zh @@ plainto_tsquery('simple', :query)
                OR a.tsv_en @@ plainto_tsquery('english', :query)
            )
        """
        params: dict[str, str | int] = {"query": ts_query}

        if status:
            sql += " AND a.status = :status"
            params["status"] = status.value.upper()
        else:
            sql += " AND a.status = 'PUBLISHED'"

        if author:
            sql += """
            AND a.author_id IN (
                SELECT id FROM "user" WHERE username = :author
            )
            """
            params["author"] = author
        # 标签过滤
        if tag is not None and tag.strip() != "":
            sql += """
                AND a.id IN (
                    SELECT DISTINCT at.article_id
                    FROM article_tag at
                    JOIN tag t ON at.tag_id = t.id
                    WHERE t.name = :tag
                )
            """
            params["tag"] = tag

        sql += " ORDER BY a.created_at DESC LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip

        try:
            result = await db.execute(text(sql), params)
            article_ids = [row[0] for row in result.fetchall()]
        except Exception as e:
            print(f"❌ PostgreSQL FTS 搜索失败，降级使用 LIKE: {e}")
            return []

        if not article_ids:
            return []

        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.author),
                selectinload(Article.tags).selectinload(ArticleTag.tag),
                selectinload(Article.comments)
            )
            .where(Article.id.in_(article_ids))
        )
        articles = result.scalars().all()

        article_dict = {a.id: a for a in articles}
        sorted_articles = [article_dict[aid] for aid in article_ids if aid in article_dict]

        return [
            ArticleListResponse(
                id=article.id,
                title=article.title,
                summary=article.summary,
                status=article.status,
                author=UserBasicInfo.model_validate(article.author),
                tags=[TagInfo.model_validate(at.tag) for at in article.tags if at.tag],
                created_at=article.created_at,
                updated_at=article.updated_at,
                view_count=0,
                comment_count=len(article.comments or [])
            )
            for article in sorted_articles
        ]

    @staticmethod
    async def get_search_suggestions(db: AsyncSession, query: str, limit: int = 5) -> List[str]:
        """返回匹配的标题建议（支持中英文）"""
        if not query.strip():
            return []

        try:
            result = await db.execute(text("""
                SELECT DISTINCT title FROM article
                WHERE (
                    tsv_zh @@ plainto_tsquery('simple', :query)
                    OR tsv_en @@ plainto_tsquery('english', :query)
                ) AND status = 'PUBLISHED'
                ORDER BY created_at DESC
                LIMIT :limit
            """), {"query": query.strip(), "limit": limit})
            return [row[0] for row in result.fetchall()]
        except Exception as e:
            print(f"❌ 获取搜索建议失败: {e}")
            return []

    @staticmethod
    async def get_popular_searches(db: AsyncSession, limit: int = 10) -> List[dict]:
        """返回热门搜索词（模拟）"""
        try:
            result = await db.execute(
                select(Article.title).where(Article.status == ArticleStatus.PUBLISHED)
            )
            titles = [row[0] for row in result.fetchall() if row[0]]
        except Exception as e:
            print(f"❌ 获取热门搜索词失败: {e}")
            return []

        words = []
        for title in titles:
            words += [w.lower() for w in re.split(r'[\s\-_,\.|/:;，。！？、]+', title) if len(w.strip()) > 1]

        counter = Counter(words)
        return [{"word": w, "frequency": f} for w, f in counter.most_common(limit)]
