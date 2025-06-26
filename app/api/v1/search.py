from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

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
    status: Optional[ArticleStatus] = Query(None, description="文章状态过滤")
):
    """全文搜索文章
    
    基于 SQLite FTS5 全文索引搜索文章标题和内容
    """
    results = await FTSSearch.search_articles(
        db=db,
        query=q,
        skip=skip,
        limit=limit,
        status=status
    )
    return results


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
    from sqlalchemy import text
    
    # 获取 FTS5 表统计信息
    result = await db.execute(text("SELECT COUNT(*) FROM articles_fts"))
    fts_count = result.scalar()
    
    # 获取文章总数
    result = await db.execute(text("SELECT COUNT(*) FROM article WHERE status = 'PUBLISHED'"))
    article_count = result.scalar()
    
    return {
        "fts_indexed_articles": fts_count,
        "total_published_articles": article_count,
        "index_coverage": fts_count / article_count if article_count > 0 else 0
    } 