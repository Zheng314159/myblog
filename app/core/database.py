import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import SQLModel
from app.core.config import settings
from app.core.search import FTSSearch


class Base(DeclarativeBase):
    pass


# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# 创建会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session() as session:
        yield session


async def create_db_and_tables():
    """创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # 创建搜索索引
    async with async_session() as session:
        try:
            # 创建 FTS5 表
            await FTSSearch.create_fts_table(session)
            # 填充数据
            await FTSSearch.populate_fts_table(session)
            print("FTS5 search index setup completed successfully")
        except Exception as e:
            print(f"Warning: FTS5 setup failed: {e}")
            print("Application will continue without FTS5 search functionality")
            # 继续运行，不要让 FTS5 错误阻止应用启动 