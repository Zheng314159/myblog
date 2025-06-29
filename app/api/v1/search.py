from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.search import FTSSearch
from app.schemas.article import ArticleListResponse
from app.models.article import ArticleStatus

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=List[ArticleListResponse])
async def search_articles(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(..., description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    status: Optional[ArticleStatus] = Query(None, description="文章状态过滤"),
    author: Optional[str] = Query(None, description="作者用户名过滤")
):
    """全文搜索文章
    
    基于 SQLite FTS5 全文索引搜索文章标题和内容
    如果FTS索引不可用，则使用简单的LIKE搜索作为备选
    """
    try:
        # 首先尝试使用FTS搜索
        results = await FTSSearch.search_articles(
            db=db,
            query=q,
            skip=skip,
            limit=limit,
            status=status,
            author=author
        )
        
        # 如果FTS搜索返回结果，直接返回
        if results:
            return results
            
        # 如果FTS搜索没有结果，使用简单的LIKE搜索作为备选
        print(f"FTS搜索无结果，使用LIKE搜索备选方案")
        return await search_articles_fallback(db, q, skip, limit, status, author)
        
    except Exception as e:
        print(f"FTS搜索失败，使用LIKE搜索备选方案: {e}")
        return await search_articles_fallback(db, q, skip, limit, status, author)


async def search_articles_fallback(
    db: AsyncSession,
    query: str,
    skip: int = 0,
    limit: int = 10,
    status: Optional[ArticleStatus] = None,
    author: Optional[str] = None
) -> List[ArticleListResponse]:
    """备选搜索方案：使用简单的LIKE搜索"""
    from app.models.article import Article
    from app.models.tag import ArticleTag, Tag
    from app.models.user import User
    from app.schemas.article import UserBasicInfo, TagInfo
    
    # 构建查询
    search_query = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.tags).selectinload(ArticleTag.tag),
        selectinload(Article.comments)
    ).where(
        (Article.title.contains(query) | Article.content.contains(query)) &
        (Article.status == ArticleStatus.PUBLISHED)
    )
    
    # 添加作者过滤
    if author:
        search_query = search_query.join(User).where(User.username == author)
    
    search_query = search_query.order_by(Article.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(search_query)
    articles = result.scalars().all()
    
    # 构建响应
    responses = []
    for article in articles:
        author_info = UserBasicInfo.model_validate(article.author)
        tag_infos = [TagInfo.model_validate(at.tag) for at in article.tags if at.tag is not None]
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
            view_count=0,
            comment_count=comment_count
        )
        responses.append(response)
    
    return responses


@router.get("/suggestions")
async def get_search_suggestions(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20, description="建议数量")
):
    """获取搜索建议
    
    基于当前搜索词提供相关建议
    """
    suggestions = await FTSSearch.get_search_suggestions(
        db=db,
        query=q,
        limit=limit
    )
    return {
        "query": q,
        "suggestions": suggestions,
        "count": len(suggestions)
    }


@router.get("/popular")
async def get_popular_searches(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50, description="热门搜索词数量")
):
    """获取热门搜索词
    
    基于文章标题中的关键词统计热门搜索词
    """
    popular_words = await FTSSearch.get_popular_searches(
        db=db,
        limit=limit
    )
    return {
        "popular_searches": popular_words,
        "count": len(popular_words)
    }


@router.post("/init")
async def initialize_search_index(db: Annotated[AsyncSession, Depends(get_db)]):
    """初始化搜索索引
    
    创建 FTS5 虚拟表和触发器，并填充现有数据
    """
    try:
        # 先删除已存在的表和触发器
        await FTSSearch.drop_fts_table(db)
        
        # 创建 FTS5 表
        await FTSSearch.create_fts_table(db)
        
        # 填充数据
        await FTSSearch.populate_fts_table(db)
        
        return {
            "message": "搜索索引初始化成功",
            "status": "completed"
        }
    except Exception as e:
        return {
            "message": f"搜索索引初始化失败: {str(e)}",
            "status": "error"
        }


@router.get("/stats")
async def get_search_stats(db: Annotated[AsyncSession, Depends(get_db)]):
    """获取搜索统计信息"""
    # 获取 FTS5 表统计信息
    result = await db.execute(text("SELECT COUNT(*) FROM articles_fts"))
    fts_count = result.scalar()
    
    # 获取文章总数 - 使用大写的PUBLISHED状态
    result = await db.execute(text("SELECT COUNT(*) FROM article WHERE status = 'PUBLISHED'"))
    article_count = result.scalar()
    
    return {
        "fts_indexed_articles": fts_count,
        "total_published_articles": article_count,
        "index_coverage": fts_count / article_count if article_count > 0 else 0
    } 