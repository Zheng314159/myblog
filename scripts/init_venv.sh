#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
NC='\033[0m'

sudo apt update && sudo apt upgrade -y
sudo apt install python3.12-venv

echo -e "${GREEN}🔧 创建 Python 虚拟环境 .venv...${NC}"
python3 -m venv .venv || { echo "❌ 创建失败"; exit 1; }

echo -e "${GREEN}✅ 激活虚拟环境...${NC}"
source .venv/bin/activate

echo -e "${GREEN}📦 安装依赖项...${NC}"
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 所有依赖已安装完成${NC}"
else
    echo -e "${GREEN}⚠️ 未检测到 requirements.txt，跳过依赖安装${NC}"
fi

echo -e "${GREEN}🎉 虚拟环境准备完成！${NC}"
