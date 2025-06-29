import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import OperationalError

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
        # 幂等删除所有 FTS5 相关对象
        for sql in [
            "DROP TRIGGER IF EXISTS articles_ai",
            "DROP TRIGGER IF EXISTS articles_ad",
            "DROP TRIGGER IF EXISTS articles_au",
            "DROP TABLE IF EXISTS articles_fts"
        ]:
            try:
                await db.execute(text(sql))
                await db.commit()
            except Exception as e:
                print(f"Warning: {sql} failed: {e}")

        # 创建 FTS5 表
        try:
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
            await db.commit()
        except Exception as e:
            print(f"Warning: FTS5 table create failed: {e}")

        # 创建触发器
        trigger_sqls = [
            ("articles_ai", """
                CREATE TRIGGER articles_ai AFTER INSERT ON article BEGIN
                    INSERT INTO articles_fts(id, title, content, summary, author_id, status, created_at, updated_at)
                    VALUES (new.id, new.title, new.content, new.summary, new.author_id, new.status, new.created_at, new.updated_at);
                END
            """),
            ("articles_ad", """
                CREATE TRIGGER articles_ad AFTER DELETE ON article BEGIN
                    DELETE FROM articles_fts WHERE id = old.id;
                END
            """),
            ("articles_au", """
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
            """)
        ]
        for name, sql in trigger_sqls:
            try:
                await db.execute(text(sql))
                await db.commit()
            except Exception as e:
                if "already exists" in str(e):
                    print(f"Warning: FTS5 trigger {name} create failed: {e}")
                else:
                    print(f"Warning: FTS5 trigger {name} create failed: {e}")
    
    @staticmethod
    async def populate_fts_table(db: AsyncSession):
        """填充 FTS5 表数据"""
        print("开始填充FTS5表...")
        
        # 检查 FTS5 表是否存在
        try:
            result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='articles_fts'"))
            exists = result.scalar()
            if not exists:
                print("Warning: articles_fts table does not exist, skip population.")
                return
            print("FTS5表存在，继续填充...")
        except Exception as e:
            print(f"Warning: FTS5 table existence check failed: {e}")
            return
        
        # 清空 FTS5 表
        try:
            await db.execute(text("DELETE FROM articles_fts"))
            await db.commit()
            print("FTS5表清空成功")
        except Exception as e:
            print(f"Warning: FTS5 table clear failed: {e}")
        
        # 填充 FTS5 表
        try:
            # 首先检查所有文章的状态
            result = await db.execute(text("SELECT id, title, status FROM article"))
            all_articles = result.fetchall()
            print(f"数据库中共有 {len(all_articles)} 篇文章:")
            for article in all_articles:
                print(f"  Article {article[0]}: '{article[1]}' - status: '{article[2]}'")
            
            # 查询已发布的文章
            query = text("""
                SELECT article.id, article.title, article.content, article.summary, article.author_id, article.status, article.created_at, article.updated_at
                FROM article
                WHERE article.status = 'PUBLISHED'
            """)
            print(f"执行查询: {query}")
            
            result = await db.execute(query)
            rows = result.fetchall()
            print(f"找到 {len(rows)} 篇已发布的文章")
            
            if not rows:
                print("没有找到已发布的文章，跳过FTS5填充")
                return
            
            # 插入到FTS表
            inserted_count = 0
            for row in rows:
                try:
                    # 构建插入数据
                    insert_data = {
                        'id': row[0],
                        'title': row[1] or '',
                        'content': row[2] or '',
                        'summary': row[3] or '',
                        'author_id': row[4],
                        'status': row[5],
                        'created_at': row[6],
                        'updated_at': row[7]
                    }
                    
                    insert_query = text("""
                        INSERT INTO articles_fts(id, title, content, summary, author_id, status, created_at, updated_at)
                        VALUES (:id, :title, :content, :summary, :author_id, :status, :created_at, :updated_at)
                    """)
                    
                    await db.execute(insert_query, insert_data)
                    inserted_count += 1
                    print(f"成功插入文章 {row[0]}: '{row[1]}'")
                    
                except Exception as e:
                    print(f"插入文章 {row[0]} 失败: {e}")
                    print(f"文章数据: {dict(row)}")
            
            await db.commit()
            print(f"成功插入 {inserted_count} 篇文章到FTS5表")
            
            # 验证插入结果
            result = await db.execute(text("SELECT COUNT(*) FROM articles_fts"))
            final_count = result.scalar()
            print(f"FTS5表最终记录数: {final_count}")
            
        except Exception as e:
            print(f"FTS5填充过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
        
        print("FTS5搜索索引设置完成")
    
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
        status: Optional[ArticleStatus] = None,
        author: Optional[str] = None
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
        
        # 添加作者过滤
        if author:
            sql += " AND a.author_id IN (SELECT id FROM user WHERE username = :author)"
            params["author"] = author
        
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