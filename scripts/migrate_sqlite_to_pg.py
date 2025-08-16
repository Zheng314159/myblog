# scripts/migrate_sqlite_to_pg.py

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Type
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import inspect, text
from app.models import __all_models__  # 自动引入所有模型

# ==== 环境变量加载 ====
ENV_FILE = os.getenv("ENV_FILE", ".env.production")
env_path = Path(ENV_FILE)
if env_path.exists():
    print(f"📦 正在加载环境变量文件: {ENV_FILE}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"⚠️ 未找到 {ENV_FILE}，将使用系统环境变量")

# SQLite & Postgres URL
sqlite_url = "sqlite+aiosqlite:///./blog.db"
postgres_url = os.getenv("DATABASE_URL")
if not postgres_url:
    raise ValueError("❌ DATABASE_URL 未设置")

# 创建异步引擎
sqlite_engine = create_async_engine(sqlite_url, echo=True)
postgres_engine = create_async_engine(postgres_url, echo=True)

# 创建 sessionmaker
AsyncSQLiteSessionMaker = async_sessionmaker(bind=sqlite_engine, expire_on_commit=False)
AsyncPostgresSessionMaker = async_sessionmaker(bind=postgres_engine, expire_on_commit=False)


async def migrate_data():
    # 按依赖顺序迁移表
    table_order = []
    for name in ["User", "OAuthAccount"]:
        for model in __all_models__:
            if model.__name__ == name:
                table_order.append(model)
    for model in __all_models__:
        if model not in table_order:
            table_order.append(model)

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

    async with AsyncSQLiteSessionMaker() as sqlite_session, AsyncPostgresSessionMaker() as pg_session:
        # 缓存 DonationGoal 的所有 id
        donationgoal_ids = set()
        for model in table_order:
            if model.__name__ == "DonationGoal":
                result = await sqlite_session.execute(select(model))
                records = result.scalars().all()
                donationgoal_ids = {getattr(r, "id") for r in records}
                break

        async def check_exists(model: Type[SQLModel], pk_field: str, pk_value):
            result = await pg_session.execute(select(model).where(getattr(model, pk_field) == pk_value))
            return result.scalars().first() is not None

        for model in table_order:
            try:
                result = await sqlite_session.execute(select(model))
                records = result.scalars().all()
                print(f"📦 {model.__name__}：准备迁移 {len(records)} 条记录")

                for record in records:
                    data = {c.key: getattr(record, c.key) for c in inspect(record).mapper.column_attrs}

                    # DonationRecord 的 goal_id 检查
                    if model.__name__ == "DonationRecord":
                        goal_id = data.get("goal_id")
                        if goal_id is not None and goal_id not in donationgoal_ids:
                            print(f"⚠️ 跳过 DonationRecord id={data.get('id')}，goal_id={goal_id} 不存在")
                            data["goal_id"] = None

                    # 主键存在检测
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

                # 修复序列，避免主键重复
                pk_field = pk_map.get(model.__name__)
                if pk_field:
                    table_name = model.__tablename__
                    stmt = text(f"""
                    SELECT setval(pg_get_serial_sequence('"{table_name}"', '{pk_field}'),
                                  COALESCE((SELECT MAX({pk_field}) FROM "{table_name}"), 0) + 1,
                                  false);
                    """)
                    await pg_session.execute(stmt)
                    await pg_session.commit()
                    print(f"🔧 {model.__name__} 序列已修复")

            except Exception as e:
                await pg_session.rollback()
                print(f"❌ {model.__name__} 数据迁移失败：{type(e).__name__} - {e}")
                raise


if __name__ == "__main__":
    asyncio.run(migrate_data())
