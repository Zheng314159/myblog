# app/core/search/base.py

from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.article import ArticleStatus
from app.schemas.article import ArticleListResponse


class BaseFTSSearch(ABC):
    """全文搜索接口统一规范"""

    @staticmethod
    @abstractmethod
    async def create_fts_table(db: AsyncSession):
        """创建搜索索引表（FTS5 / tsvector）"""
        pass

    @staticmethod
    @abstractmethod
    async def drop_fts_table(db: AsyncSession):
        """删除搜索索引表（FTS5 / tsvector）"""
        pass

    @staticmethod
    @abstractmethod
    async def populate_fts_table(db: AsyncSession):
        """填充搜索索引数据"""
        pass

    @staticmethod
    @abstractmethod
    async def search_articles(
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[ArticleStatus] = None,
        author: Optional[str] = None,
    ) -> List[ArticleListResponse]:
        """执行搜索文章"""
        pass

    @staticmethod
    @abstractmethod
    async def get_search_suggestions(
        db: AsyncSession,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """返回搜索建议（如标题）"""
        pass

    @staticmethod
    @abstractmethod
    async def get_popular_searches(
        db: AsyncSession,
        limit: int = 10
    ) -> List[dict]:
        """返回热门搜索词"""
        pass
