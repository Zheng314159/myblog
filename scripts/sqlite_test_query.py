import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

DATABASE_URL = "sqlite+aiosqlite:///blog.db"

async def test_query():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with AsyncSession(engine) as session:
        result = await session.execute(text("SELECT * FROM articles_fts LIMIT 5"))
        for row in result.fetchall():
            print(row)

asyncio.run(test_query())
