# projects/myblog/scripts/init_db.py
import os
import sys
import time
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import psycopg2
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from app.core.base import BaseModelMixin

# 👇 把项目根目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import __all_models__  # noqa: F401

# ==== 加载 .env 配置 ====
env = os.getenv("ENVIRONMENT", "development").lower()
env_file = Path(".") / f".env.{env}"
load_dotenv(env_file if env_file.exists() else Path(".") / ".env")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL 未设置")
    sys.exit(1)

is_sqlite = database_url.startswith("sqlite")

# ==== PostgreSQL 初始化 ====
if not is_sqlite:
    parsed = urlparse(database_url.replace("+asyncpg", ""))
    db_name = parsed.path.lstrip("/")
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432

    def wait_for_postgres(timeout=30):
        print("⏳ 等待 PostgreSQL 启动...")
        for _ in range(timeout):
            try:
                conn = psycopg2.connect(
                    dbname="postgres", user=user, password=password, host=host, port=port
                )
                conn.close()
                print("✅ PostgreSQL 已就绪")
                return
            except Exception:
                time.sleep(1)
        print("❌ PostgreSQL 启动超时")
        sys.exit(1)

    def create_database_if_not_exists():
        try:
            conn = psycopg2.connect(
                dbname="postgres", user=user, password=password, host=host, port=port
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
            if not cur.fetchone():
                print(f"🛠️ 正在创建数据库 {db_name}...")
                cur.execute(f"CREATE DATABASE {db_name};")
            else:
                print(f"✅ 数据库 {db_name} 已存在")
            cur.close()
            conn.close()
        except Exception as e:
            print("❌ 数据库连接或创建失败：", e)
            sys.exit(1)

    wait_for_postgres()
    create_database_if_not_exists()

# ==== 创建表结构 ====
async def create_pg_tables():
    try:
        print("📦 正在使用 SQLModel 创建表结构（如未使用 Alembic，可启用）...")
        assert database_url is not None
        engine = create_async_engine(database_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(BaseModelMixin.metadata.drop_all)
            await conn.run_sync(BaseModelMixin.metadata.create_all)
        print("✅ SQLModel 表结构删除并重建完成")
    except Exception as e:
        print("❌ SQLModel 表结构创建失败：", e)
        sys.exit(1)

# ==== 打印表结构信息 ====
async def show_tables():
    assert database_url is not None 
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        tables = [row[0] for row in result.fetchall()]
        print(f"📂 当前数据库表：{tables}")

async def print_table_schemas():
    assert database_url is not None
    engine = create_async_engine(database_url, echo=False)
    async with engine.connect() as conn:
        def inspect_tables(sync_conn: Connection):
            inspector = inspect(sync_conn)
            for table_name in inspector.get_table_names():
                print(f"\n📘 表: {table_name}")
                for col in inspector.get_columns(table_name):
                    print(f"   ├─ {col['name']} ({col['type']}) NULL: {col['nullable']} DEFAULT: {col.get('default')}")
                pk = inspector.get_pk_constraint(table_name)
                if pk and pk.get("constrained_columns"):
                    print(f"   🔑 主键: {', '.join(pk['constrained_columns'])}")
                for fk in inspector.get_foreign_keys(table_name):
                    print(f"   🔗 外键: {fk['constrained_columns']} → {fk['referred_table']}({fk['referred_columns']})")
                for uq in inspector.get_unique_constraints(table_name):
                    print(f"   🧷 唯一约束: {uq['column_names']}")
                for idx in inspector.get_indexes(table_name):
                    print(f"   📍 索引: {idx['name']} ({idx.get('column_names', [])})")
        await conn.run_sync(inspect_tables)

# ==== Alembic 自动初始化 ====
def ensure_alembic_ready():
    if not Path("alembic").exists():
        print("🚧 未检测到 Alembic 初始化目录，正在初始化...")
        subprocess.run(["alembic", "init", "alembic"], check=True)

def run_alembic_stamp_base():
    print("📌 Alembic: 记录当前数据库状态为 base")
    subprocess.run(["alembic", "stamp", "base"], check=True)

def fix_alembic_version():
    from sqlalchemy import text
    import asyncio
    from app.core.database import engine

    async def _run():
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

    asyncio.run(_run())

def run_alembic_stamp_head():
    print("📌 Alembic: 记录当前数据库状态为 head")
    try:
        subprocess.run(["alembic", "stamp", "head"], check=True)
    except subprocess.CalledProcessError:
        print("⚠️ Alembic 状态异常，尝试清除 alembic_version 表后重新 stamp")
        fix_alembic_version()
        subprocess.run(["alembic", "stamp", "head"], check=True)


def run_alembic_autogenerate():
    print("🧬 正在根据模型生成 Alembic migration 脚本...")
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "initial migration"], check=True)

def run_alembic_upgrade():
    print("🚀 正在运行 Alembic 升级...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Alembic 迁移完成")
    except subprocess.CalledProcessError as e:
        print("❌ Alembic 执行失败：", e)
        sys.exit(1)

# ==== 主入口 ====
if __name__ == "__main__":
    ensure_alembic_ready()

    # 可选：首次用 create_all() 建表，然后 stamp 为 base 状态
    if not is_sqlite:
        asyncio.run(create_pg_tables())  # 第一次创建
        run_alembic_stamp_base()         # stamp base
        run_alembic_stamp_head()          # stamp head
        # run_alembic_autogenerate()       # 自动生成脚本
        run_alembic_upgrade()            # 正式迁移
        # asyncio.run(show_tables())
        asyncio.run(print_table_schemas())
    else:
        asyncio.run(print_table_schemas())
        print("📝 SQLite 环境，仅本地开发使用")

    print("🎉 数据库初始化完成")
