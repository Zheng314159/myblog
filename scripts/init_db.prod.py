import os
import sys
import time
import asyncio
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
import psycopg2
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine

# 设置 PYTHONPATH，确保项目目录被识别
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ 加载 models，确保 SQLModel.metadata 有内容（必须在 load_dotenv 之后）
from app.models import __all_models__  # noqa: F401

# ==== 环境变量加载 ====
ENV_FILE = os.getenv("ENV_FILE", ".env.production")
env_path = Path(ENV_FILE)
if env_path.exists():
    print(f"📦 正在加载环境变量文件: {ENV_FILE}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"⚠️ 未找到 {ENV_FILE}，将使用系统环境变量")

# ==== 数据库连接 ====
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ 环境变量 DATABASE_URL 未设置")
    sys.exit(1)

# ==== PostgreSQL 启动检测 ====
def wait_for_postgres(timeout=30):
    parsed = urlparse(database_url.replace("+asyncpg", ""))
    db_name = parsed.path.lstrip("/")
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432

    print("⏳ 等待 PostgreSQL 启动...")
    for i in range(timeout):
        try:
            conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
            conn.close()
            print("✅ PostgreSQL 已就绪")
            return
        except Exception:
            time.sleep(1)
    print("❌ PostgreSQL 启动超时")
    sys.exit(1)

# ==== 检查并创建数据库 ====
def create_database_if_not_exists():
    parsed = urlparse(database_url.replace("+asyncpg", ""))
    db_name = parsed.path.lstrip("/")
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432

    try:
        conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
        if not cur.fetchone():
            print(f"🛠️ 创建数据库 {db_name}...")
            cur.execute(f"CREATE DATABASE {db_name};")
        else:
            print(f"✅ 数据库 {db_name} 已存在")
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ 数据库创建失败：", e)
        sys.exit(1)

# ==== Alembic 操作 ====
def alembic_stamp_head():
    print("📌 Alembic: 设置当前数据库状态为 head")
    try:
        subprocess.run(["alembic", "stamp", "head"], check=True)
    except subprocess.CalledProcessError as e:
        print("⚠️ Alembic stamp head 失败：", e)
        sys.exit(1)

def alembic_upgrade():
    print("🚀 执行 Alembic 数据迁移")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ 数据迁移成功")
    except subprocess.CalledProcessError as e:
        print("❌ 数据迁移失败：", e)
        sys.exit(1)

# ==== SQLModel 建表备选方案 ====
async def create_tables():
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✅ SQLModel 表结构删除并重建完成")

# ==== 主执行流程 ====
if __name__ == "__main__":
    wait_for_postgres()
    create_database_if_not_exists()

    # 建议只用 Alembic 迁移，除非你明知 metadata 中定义未同步
    asyncio.run(create_tables())
    alembic_stamp_head()
    alembic_upgrade()

    # 如 Alembic 无法识别模型，可用 SQLModel 手动创建（调试时再启用）

    print("🎉 数据库初始化完成（生产环境）")
