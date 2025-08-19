#!/bin/bash
# ====================================================
# 一键安装 Google Cloud CLI (tar.gz方式) 并自动登录
# 适用于 WSL / Ubuntu / 国内网络
# ====================================================

set -e

echo "🚀 开始安装 Google Cloud CLI (tar.gz方式)..."

# 检查 gcloud 是否已安装
if command -v gcloud &> /dev/null; then
    echo "✅ gcloud 已安装，版本：$(gcloud version)"
else
    TMP_DIR=$(mktemp -d)
    cd $TMP_DIR
    echo "💡 下载 Google Cloud CLI 压缩包..."
    
    # 如果 curl 被墙，可换用代理或手动下载到 TMP_DIR
    curl -LO https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-530.0.0-linux-x86_64.tar.gz

    echo "💡 解压并安装..."
    tar -xf google-cloud-cli-530.0.0-linux-x86_64.tar.gz
    ./google-cloud-sdk/install.sh --quiet

    echo "💡 添加 gcloud 到 PATH..."
    if ! grep -q 'google-cloud-sdk/bin' ~/.bashrc; then
        echo 'export PATH=$PATH:$HOME/google-cloud-sdk/bin' >> ~/.bashrc
    fi
    source ~/.bashrc
fi

# 确认 gcloud 可用
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud 安装失败，请手动检查"
    exit 1
fi

echo "🎉 gcloud 安装完成，版本：$(gcloud version)"

# =============================
# 自动执行 gcloud auth login
# =============================
echo "🌐 开始 Google 登录..."
echo "请在浏览器中完成登录授权，授权完成后按回车继续..."
gcloud auth login

echo "✅ gcloud 已登录完成，可以在 VS Code Gemini Code Assist 使用！"
