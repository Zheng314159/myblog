#!/bin/bash

set -e

echo "🚀 开始安装 Docker 和 docker-compose ..."

# Step 1: 安装必要依赖
echo "📦 安装依赖包 ..."
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Step 2: 添加 Docker 官方 GPG 密钥
echo "🔐 添加 Docker GPG 密钥 ..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Step 3: 添加 Docker 仓库
echo "🌐 添加 Docker 官方仓库 ..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Step 4: 安装 Docker Engine 和 Compose 插件
echo "⚙️ 安装 Docker 引擎和 Compose 插件 ..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Step 5: 将当前用户加入 docker 组
echo "👤 添加用户到 docker 组 ..."
sudo usermod -aG docker $USER

echo "✅ 安装完成，请运行以下命令以生效 docker 用户权限："
echo
echo "👉 运行：newgrp docker"
echo "👉 然后测试：docker run hello-world"
echo "👉 测试 compose：docker compose version"
