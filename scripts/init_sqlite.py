# scripts/init_sqlite.py
import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
from dotenv import load_dotenv

load_dotenv(".env.sqlite")  # 记得这里配置的是 SQLite 的连接字符串

sqlite_url = "sqlite+aiosqlite:///./blog.db"
engine = create_async_engine(sqlite_url, echo=True)

from app.models import *  # 导入所有模型类以触发表注册

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
