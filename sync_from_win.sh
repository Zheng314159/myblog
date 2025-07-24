#!/bin/bash

SRC="/mnt/f/myblog"
DEST="$HOME/projects/myblog"

echo "📥 正在将 Windows 项目 $SRC 同步到 WSL 本地 $DEST..."

mkdir -p "$DEST"

rsync -avh --progress \
  --exclude '.venv/' \
  --exclude 'frontend/node_modules/' \
  --exclude 'frontend/dist/' \
  --exclude 'alembic/versions/' \
  --exclude 'myblogenv/' \
  --exclude '__pycache__/' \
  --exclude '.git/' \
  --exclude '*.pyc' \
  "$SRC/" "$DEST/"

echo "✅ 同步完成！"
du -sh "$DEST"
