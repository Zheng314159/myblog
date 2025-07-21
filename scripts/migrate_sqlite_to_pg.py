# scripts/migrate_sqlite_to_pg.py

import asyncio
import os
from dotenv import load_dotenv
from typing import Type
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker  # ✅ Python 3.10+ 的推荐用法
from app.models import __all_models__  # ✅ 自动引入所有模型

# 加载环境变量
sqlite_url = "sqlite+aiosqlite:///./blog.db"

load_dotenv(".env.development")  # postgres 环境
postgres_url = os.getenv("DATABASE_URL")
if not postgres_url:
    raise ValueError("❌ DATABASE_URL 未设置")

# 创建两个异步数据库引擎
sqlite_engine = create_async_engine(sqlite_url, echo=True)
postgres_engine = create_async_engine(postgres_url, echo=True)

# 创建两个 sessionmaker（异步）
AsyncSQLiteSessionMaker = async_sessionmaker(bind=sqlite_engine, expire_on_commit=False)
AsyncPostgresSessionMaker = async_sessionmaker(bind=postgres_engine, expire_on_commit=False)



# 按依赖顺序迁移表，user -> oauthaccount -> 其他表
async def migrate_data():
    table_order = []
    # 你可以根据实际依赖顺序调整
    for name in ["User", "OAuthAccount"]:
        for model in __all_models__:
            if model.__name__ == name:
                table_order.append(model)
    for model in __all_models__:
        if model not in table_order:
            table_order.append(model)

    async with AsyncSQLiteSessionMaker() as sqlite_session, AsyncPostgresSessionMaker() as pg_session:
        donationgoal_ids = set()
        # 先缓存 donationgoal 的所有 id
        for model in table_order:
            if model.__name__ == "DonationGoal":
                result = await sqlite_session.execute(select(model))
                records = result.scalars().all()
                donationgoal_ids = {getattr(r, "id") for r in records}
                break

        # 优化：主键存在检测逻辑抽象
        pk_map = {
            "User": "id",
            "OAuthAccount": "id",
            "Article": "id",
            "Comment": "id",
            "Tag": "id",
            "ArticleTag": "id",
            "MediaFile": "id",
            "DonationConfig": "id",
            "DonationGoal": "id",
            "DonationRecord": "id",
            "SystemNotification": "id",
        }

        async def check_exists(model, pk_field, pk_value):
            exist = await pg_session.execute(select(model).where(getattr(model, pk_field) == pk_value))
            return exist.scalars().first() is not None

        for model in table_order:
            try:
                result = await sqlite_session.execute(select(model))
                records = result.scalars().all()
                print(f"📦 {model.__name__}：准备迁移 {len(records)} 条记录")

                for record in records:
                    data = record.model_dump()
                    # 针对 DonationRecord，goal_id 不存在则置为 None
                    if model.__name__ == "DonationRecord":
                        goal_id = data.get("goal_id")
                        if goal_id is not None and goal_id not in donationgoal_ids:
                            print(f"⚠️ 跳过 DonationRecord id={data.get('id')}，goal_id={goal_id} 不存在")
                            data["goal_id"] = None

                    # 通用主键存在检测
                    pk_field = pk_map.get(model.__name__)
                    if pk_field:
                        pk_value = data.get(pk_field)
                        if await check_exists(model, pk_field, pk_value):
                            print(f"⚠️ 跳过 {model.__name__} id={pk_value}，主键已存在")
                            continue

                    new_obj = model(**data)
                    pg_session.add(new_obj)

                await pg_session.commit()
                print(f"✅ {model.__name__} 数据迁移完成")
            except Exception as e:
                await pg_session.rollback()
                print(f"❌ {model.__name__} 数据迁移失败：{type(e).__name__} - {e}")
                raise


if __name__ == "__main__":
    asyncio.run(migrate_data())
