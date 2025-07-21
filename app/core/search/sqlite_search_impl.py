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


class SQLiteFTSSearch(BaseFTSSearch):
    @staticmethod
    async def drop_fts_table(db: AsyncSession):
        async with db.begin():
            await db.execute(text("DROP TRIGGER IF EXISTS articles_ai"))
            await db.execute(text("DROP TRIGGER IF EXISTS articles_ad"))
            await db.execute(text("DROP TRIGGER IF EXISTS articles_au"))
            await db.execute(text("DROP TABLE IF EXISTS articles_fts"))

    @staticmethod
    async def create_fts_table(db: AsyncSession):
        await SQLiteFTSSearch.drop_fts_table(db)
        async with db.begin():
            await db.execute(text("""
                CREATE VIRTUAL TABLE articles_fts USING fts5(
                    id UNINDEXED,
                    title,
                    content,
                    summary,
                    author_id UNINDEXED,
                    status UNINDEXED,
                    created_at UNINDEXED,
                    updated_at UNINDEXED
                )
            """))
            await db.execute(text("""
                CREATE TRIGGER articles_ai AFTER INSERT ON article BEGIN
                    INSERT INTO articles_fts(id, title, content, summary, author_id, status, created_at, updated_at)
                    VALUES (new.id, new.title, new.content, new.summary, new.author_id, new.status, new.created_at, new.updated_at);
                END
            """))
            await db.execute(text("""
                CREATE TRIGGER articles_ad AFTER DELETE ON article BEGIN
                    DELETE FROM articles_fts WHERE id = old.id;
                END
            """))
            await db.execute(text("""
                CREATE TRIGGER articles_au AFTER UPDATE ON article BEGIN
                    UPDATE articles_fts SET
                        title = new.title,
                        content = new.content,
                        summary = new.summary,
                        author_id = new.author_id,
                        status = new.status,
                        updated_at = new.updated_at
                    WHERE id = new.id;
                END
            """))

    @staticmethod
    async def populate_fts_table(db: AsyncSession):
        async with db.begin():
            await db.execute(text("DELETE FROM articles_fts"))
            await db.execute(text("""
                INSERT INTO articles_fts(id, title, content, summary, author_id, status, created_at, updated_at)
                SELECT id, title, content, summary, author_id, status, created_at, updated_at
                FROM article WHERE status = 'PUBLISHED'
            """))

    @staticmethod
    def build_search_query(search_term: str) -> str:
        """构建搜索查询：分词并前缀匹配"""
        search_term = re.sub(r'[^\w\s]', ' ', search_term).strip()
        if not search_term:
            return ""
        words = search_term.split()
        query_parts = [f'"{word}"*' for word in words if len(word) >= 2]
        return " AND ".join(query_parts)

    @staticmethod
    async def search_articles(
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[ArticleStatus] = None,
        author: Optional[str] = None
    ) -> List[ArticleListResponse]:
        fts_query = SQLiteFTSSearch.build_search_query(query)
        if not fts_query:
            return []

        sql = """
            SELECT a.id FROM articles_fts fts
            JOIN article a ON fts.id = a.id
            WHERE fts MATCH :query
        """
        params = {"query": fts_query}

        if status:
            sql += " AND a.status = :status"
            params["status"] = status.value
        else:
            sql += " AND a.status = 'PUBLISHED'"

        if author:
            sql += ' AND a.author_id IN (SELECT id FROM "user" WHERE username = :author)'
            params["author"] = author

        sql += " ORDER BY bm25(fts) DESC, a.created_at DESC LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip

        result = await db.execute(text(sql), params)
        article_ids = [row[0] for row in result.fetchall()]
        if not article_ids:
            return []

        result = await db.execute(
            select(Article).options(
                selectinload(Article.author),
                selectinload(Article.tags).selectinload(ArticleTag.tag),
                selectinload(Article.comments)
            ).where(Article.id.in_(article_ids))
        )
        articles = result.scalars().all()
        article_map = {a.id: a for a in articles}
        sorted_articles = [article_map[i] for i in article_ids if i in article_map]

        return [
            ArticleListResponse(
                id=a.id,
                title=a.title,
                summary=a.summary,
                status=a.status,
                author=UserBasicInfo.model_validate(a.author),
                tags=[TagInfo.model_validate(at.tag) for at in a.tags if at.tag],
                created_at=a.created_at,
                updated_at=a.updated_at,
                view_count=0,
                comment_count=len(a.comments or [])
            ) for a in sorted_articles
        ]

    @staticmethod
    async def get_search_suggestions(db: AsyncSession, query: str, limit: int = 5) -> List[str]:
        fts_query = SQLiteFTSSearch.build_search_query(query)
        if not fts_query:
            return []

        sql = """
            SELECT DISTINCT title FROM articles_fts fts
            WHERE fts MATCH :query
            ORDER BY bm25(fts) DESC
            LIMIT :limit
        """
        result = await db.execute(text(sql), {"query": fts_query, "limit": limit})
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def get_popular_searches(db: AsyncSession, limit: int = 10) -> List[dict]:
        result = await db.execute(select(Article.title).where(Article.status == ArticleStatus.PUBLISHED))
        titles = [row[0] for row in result.fetchall() if row[0]]
        words = []
        for title in titles:
            words += [w.lower() for w in re.split(r'[\s\-_,\.|/:;，。！？、]+', title) if len(w.strip()) > 1]
        counter = Counter(words)
        return [{"word": w, "frequency": f} for w, f in counter.most_common(limit)]
