#!/bin/bash

# 脚本作用：用于 WSL 中模拟部署 FastAPI 项目为生产环境
# 请确保此脚本在项目根目录中运行

set -e

echo "🔧 正在进入项目根目录..."
cd "$(dirname "$0")/.."

echo "🟡 正在创建 Python 虚拟环境..."
python3 -m venv .venv
source .venv/bin/activate

echo "📦 正在安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 正在设置环境变量..."
export ENVIRONMENT=production
export $(cat .env.production | grep -v '^#' | xargs)

echo "🗃️ 启动 PostgreSQL 数据库服务（如果使用）..."
sudo service postgresql start

echo "🛠️ 正在运行 Alembic 数据迁移..."
alembic upgrade head

echo "🔥 启动 FastAPI 应用（Gunicorn + Uvicorn workers）..."
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --workers 4 \
  --log-level info \
  --timeout 60 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
