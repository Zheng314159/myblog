import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload

from app.models.article import Article, ArticleStatus
from app.models.tag import Tag, ArticleTag
from app.schemas.article import ArticleListResponse, UserBasicInfo, TagInfo


class FTSSearch:
    """基于 SQLite FTS5 的全文搜索"""
    
    @staticmethod
    async def drop_fts_table(db: AsyncSession):
        """删除 FTS5 虚拟表和触发器"""
        # 删除触发器
        await db.execute(text("DROP TRIGGER IF EXISTS articles_ai"))
        await db.execute(text("DROP TRIGGER IF EXISTS articles_ad"))
        await db.execute(text("DROP TRIGGER IF EXISTS articles_au"))
        
        # 删除 FTS5 表
        await db.execute(text("DROP TABLE IF EXISTS articles_fts"))
        
        await db.commit()
    
    @staticmethod
    async def create_fts_table(db: AsyncSession):
        """创建 FTS5 虚拟表"""
        try:
            # 首先删除可能存在的表和触发器
            await FTSSearch.drop_fts_table(db)
            
            # 创建 FTS5 虚拟表
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
            
            # 创建触发器
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
            
            await db.commit()
            print("FTS5 table and triggers created successfully")
            
        except Exception as e:
            await db.rollback()
            print(f"Error creating FTS5 table: {e}")
            raise
    
    @staticmethod
    async def populate_fts_table(db: AsyncSession):
        """填充 FTS5 表数据"""
        try:
            # 检查表是否存在
            result = await db.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='articles_fts'
            """))
            if not result.fetchone():
                print("FTS5 table does not exist, skipping population")
                return
            
            # 清空现有数据
            await db.execute(text("DELETE FROM articles_fts"))
            
            # 获取所有已发布的文章
            result = await db.execute(
                select(Article).where(Article.status == ArticleStatus.PUBLISHED)
            )
            articles = result.scalars().all()
            
            if not articles:
                print("No published articles found for FTS5 population")
                await db.commit()
                return
            
            # 批量插入到 FTS5 表
            for article in articles:
                await db.execute(text("""
                    INSERT INTO articles_fts(id, title, content, summary, author_id, status, created_at, updated_at)
                    VALUES (:id, :title, :content, :summary, :author_id, :status, :created_at, :updated_at)
                """), {
                    "id": article.id,
                    "title": article.title,
                    "content": article.content,
                    "summary": article.summary or "",
                    "author_id": article.author_id,
                    "status": article.status.value,
                    "created_at": article.created_at.isoformat(),
                    "updated_at": article.updated_at.isoformat()
                })
            
            await db.commit()
            print(f"FTS5 table populated with {len(articles)} articles")
            
        except Exception as e:
            await db.rollback()
            print(f"Error populating FTS5 table: {e}")
    
    @staticmethod
    def build_search_query(search_term: str) -> str:
        """构建搜索查询"""
        # 清理搜索词
        search_term = re.sub(r'[^\w\s]', ' ', search_term).strip()
        
        if not search_term:
            return ""
        
        # 分词并构建 FTS5 查询
        words = search_term.split()
        query_parts = []
        
        for word in words:
            if len(word) >= 2:  # 忽略太短的词
                # 支持前缀匹配
                query_parts.append(f'"{word}"*')
        
        return " AND ".join(query_parts) if query_parts else ""
    
    @staticmethod
    async def search_articles(
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[ArticleStatus] = None
    ) -> List[ArticleListResponse]:
        """搜索文章"""
        if not query.strip():
            return []
        
        # 构建 FTS5 查询
        fts_query = FTSSearch.build_search_query(query)
        if not fts_query:
            return []
        
        # 构建 SQL 查询
        sql = """
            SELECT 
                a.id,
                a.title,
                a.content,
                a.summary,
                a.status,
                a.author_id,
                a.created_at,
                a.updated_at,
                fts.rank as search_rank
            FROM articles_fts fts
            JOIN article a ON fts.id = a.id
            WHERE articles_fts MATCH :query
        """
        
        params = {"query": fts_query}
        
        # 添加状态过滤
        if status:
            sql += " AND a.status = :status"
            params["status"] = status.value
        
        # 添加排序和分页
        sql += " ORDER BY search_rank DESC, a.created_at DESC LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip
        
        # 执行查询
        result = await db.execute(text(sql), params)
        rows = result.fetchall()
        
        if not rows:
            return []
        
        # 获取文章ID列表
        article_ids = [row[0] for row in rows]
        
        # 获取完整的文章信息（包括作者和标签）
        articles_result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.author),
                selectinload(Article.tags).selectinload(ArticleTag.tag),
                selectinload(Article.comments)
            )
            .where(Article.id.in_(article_ids))
        )
        articles = articles_result.scalars().all()
        
        # 按搜索排名排序
        article_dict = {article.id: article for article in articles}
        sorted_articles = []
        for row in rows:
            article_id = row[0]
            if article_id in article_dict:
                sorted_articles.append(article_dict[article_id])
        
        # 构建响应
        responses = []
        for article in sorted_articles:
            # 构建作者信息
            author_info = UserBasicInfo.model_validate(article.author)
            
            # 构建标签信息
            tag_infos = [TagInfo.model_validate(at.tag) for at in article.tags if at.tag is not None]
            
            # 计算评论数量
            comment_count = len(article.comments) if article.comments else 0
            
            response = ArticleListResponse(
                id=article.id,
                title=article.title,
                summary=article.summary,
                status=article.status,
                author=author_info,
                tags=tag_infos,
                created_at=article.created_at,
                updated_at=article.updated_at,
                view_count=0,  # 默认值，因为数据库中没有这个字段
                comment_count=comment_count
            )
            responses.append(response)
        
        return responses
    
    @staticmethod
    async def get_search_suggestions(db: AsyncSession, query: str, limit: int = 5) -> List[str]:
        """获取搜索建议"""
        if not query.strip():
            return []
        
        # 使用 FTS5 的 highlight 功能获取建议
        fts_query = FTSSearch.build_search_query(query)
        if not fts_query:
            return []
        
        sql = """
            SELECT DISTINCT title
            FROM articles_fts
            WHERE articles_fts MATCH :query
            ORDER BY rank DESC
            LIMIT :limit
        """
        
        result = await db.execute(text(sql), {"query": fts_query, "limit": limit})
        suggestions = [row[0] for row in result.fetchall()]
        
        return suggestions
    
    @staticmethod
    async def get_popular_searches(db: AsyncSession, limit: int = 10) -> List[dict]:
        """获取热门搜索词（基于文章标题中的关键词，兼容所有 SQLite 环境）"""
        # 查询所有已发布文章标题
        result = await db.execute(
            select(Article.title).where(Article.status == ArticleStatus.PUBLISHED)
        )
        titles = [row[0] for row in result.fetchall() if row[0]]

        # 拆分标题为词，统计词频
        from collections import Counter
        import re
        words = []
        for title in titles:
            # 用空格、-、_、,、.、|、/、:、;、中文逗号等分割
            split_words = re.split(r'[\s\-_,\.|/:;，。！？、]+', title)
            words.extend([w.lower().strip() for w in split_words if len(w.strip()) > 1])
        counter = Counter(words)
        popular = counter.most_common(limit)
        return [{"word": w, "frequency": f} for w, f in popular] 