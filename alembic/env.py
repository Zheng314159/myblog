from logging.config import fileConfig
from pathlib import Path
from alembic import context
from dotenv import load_dotenv
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.base import BaseModelMixin

import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import create_async_engine  # ✅ 注意


# 添加项目根目录
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 动态加载 .env 或 .env.{ENVIRONMENT}
env = os.getenv("ENVIRONMENT", "development").lower()
env_file = Path(".") / f".env.{env}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(Path(".") / ".env")

# ✅ 导入你的 config
from app.core.config import settings
from app.models import __all_models__  # 自动引入所有 SQLModel 模型

print(f"📦 当前使用数据库: {settings.database_url}")
# Alembic config
config = context.config
fileConfig(config.config_file_name, encoding=settings.python_io_encoding)

# 设置 sqlalchemy.url（即使是 asyncpg，也需要设为 sync URL 用于 Alembic 的兼容处理）
# config.set_main_option("sqlalchemy.url", settings.database_url.replace("asyncpg", "psycopg2"))

# 自动根据数据库类型设置 sync URL
def get_sync_url() -> str:
    url = settings.database_url
    if url.startswith("sqlite+aiosqlite"):
        return url.replace("sqlite+aiosqlite", "sqlite")
    elif url.startswith("postgresql+asyncpg"):
        return url.replace("postgresql+asyncpg", "postgresql+psycopg2")
    else:
        raise ValueError(f"❌ 不支持的数据库类型: {url}")

config.set_main_option("sqlalchemy.url", get_sync_url())


target_metadata = BaseModelMixin.metadata

def include_object(object, name, type_, reflected, compare_to):
    if name and name.startswith("articles_fts"):
        return False
    return True

def run_migrations_offline():
    """离线迁移：不连接数据库"""

    if context.is_offline_mode():
        context.configure(
            url=settings.database_url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()
    else:
        context.configure(
            url=settings.database_url,
            target_metadata=target_metadata,
            dialect_opts={"paramstyle": "named"},
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
        )
        context.run_migrations()

def do_run_migrations(connection):
    """同步迁移逻辑"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

async def check_db_connection(engine: AsyncEngine):
    """检测数据库连接是否正常"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: None)  # 简单执行一条无操作语句
        print("✅ 数据库连接成功")
    except OperationalError as e:
        print("❌ 数据库连接失败:", str(e))
        sys.exit(1)

async def print_current_tables(engine: AsyncEngine):
    """打印当前数据库中所有表名"""
    try:
        async with engine.connect() as conn:
            def get_tables(sync_conn):
                return list(sync_conn.dialect.get_table_names(sync_conn)) 
                # return list(inspect(sync_conn).get_table_names())

            tables = await conn.run_sync(get_tables)
            print("📄 当前数据库中的所有表：")
            for table in tables:
                print(f"   - {table}")
    except Exception as e:
        print(f"⚠️ 获取表失败: {e}")

async def run_migrations_online():
    """在线迁移"""
    engine = create_async_engine(settings.database_url, echo=False)  # ✅ 动态创建
    # ✅ 检查数据库连接
    await check_db_connection(engine)
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)
    # ✅ 迁移后打印所有表名
    await print_current_tables(engine)

import sys

# 判断当前 Alembic 命令，revision/autogenerate 时不运行任何迁移逻辑（让 Alembic 自己处理）
is_revision_cmd = any(cmd in " ".join(sys.argv).lower() for cmd in ["revision", "autogenerate"])

if is_revision_cmd and not context.is_offline_mode():
    # revision/autogenerate 阶段（非 offline）不运行任何迁移逻辑，直接 return
    pass
elif context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
