#!/bin/bash

set -e

# ------------------------------
# 前端依赖初始化脚本（适用于 WSL Ubuntu）
# ------------------------------

echo "🔧 正在更新系统依赖..."
sudo apt update && sudo apt upgrade -y

echo "📦 安装 curl 和 build-essential..."
sudo apt install -y curl build-essential

echo "📥 安装 Node.js（v20）..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

echo "✅ Node.js 安装完成，版本："
node -v
npm -v

echo "📦 安装 corepack 并启用 pnpm..."
sudo corepack enable
sudo corepack prepare pnpm@latest --activate

echo "✅ pnpm 安装完成，版本："
pnpm -v

# 项目目录，默认是 frontend 文件夹
FRONTEND_DIR="./frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "❌ 目录 $FRONTEND_DIR 不存在，正在创建并初始化前端项目..."
  mkdir -p $FRONTEND_DIR
  cd $FRONTEND_DIR
  pnpm create vite
else
  cd $FRONTEND_DIR
fi

echo "📦 安装项目依赖（包括 esbuild）..."
pnpm install
pnpm add -D esbuild

echo "🎉 前端依赖安装完成。"
