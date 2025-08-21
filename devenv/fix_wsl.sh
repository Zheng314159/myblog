#!/bin/bash
set -e

# Step 0: 定义 HOME 目录（防止某些精简版 WSL 没有 $HOME）
if [ -z "$HOME" ]; then
    HOME="/home/$(whoami)"
    export HOME
fi
echo "📂 HOME 已设置为: $HOME"

# Step 0.5: 自动检测 Windows 主机 IP
WIN_IP=$(grep -m1 nameserver /etc/resolv.conf | awk '{print $2}')
if [ -z "$WIN_IP" ]; then
    echo "❌ 无法检测到 Windows 主机 IP，请检查 /etc/resolv.conf"
    exit 1
fi
echo "🖥️ 检测到 Windows 主机 IP: $WIN_IP"

echo "🔧 配置 WSL DNS 永久生效..."

# Step 1: 写入 /etc/wsl.conf
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[network]
generateResolvConf=false
generateHosts=false
EOF
echo "✅ 已写入 /etc/wsl.conf"

# Step 2: 删除 resolv.conf 软链接（如果存在）
if [ -L /etc/resolv.conf ]; then
    sudo rm /etc/resolv.conf
    echo "✅ 已删除 resolv.conf 软链接"
elif [ -f /etc/resolv.conf ]; then
    sudo mv /etc/resolv.conf /etc/resolv.conf.bak.$(date +%s)
    echo "✅ 已备份原 resolv.conf"
fi

# Step 3: 创建新的 resolv.conf
sudo tee /etc/resolv.conf >/dev/null <<'EOF'
nameserver 8.8.8.8
nameserver 1.1.1.1
EOF
echo "✅ 已创建新的 resolv.conf (DNS: 8.8.8.8, 1.1.1.1)"

# Step 4: 配置代理到用户的 ~/.bashrc
cat >> "$HOME/.bashrc" <<EOF

# Proxy settings (Auto-detected Windows IP)
export http_proxy="http://$WIN_IP:1081"
export https_proxy="http://$WIN_IP:1081"
export all_proxy="http://$WIN_IP:1081"
EOF
echo "✅ 已写入代理配置到 $HOME/.bashrc"

# Step 5: 立即生效
source "$HOME/.bashrc"
echo "✅ 代理配置已生效 (使用 Windows IP: $WIN_IP:1081)"

# Step 6: 测试网络连通性
echo "🌐 测试网络连通性..."
if curl -s --max-time 5 https://www.google.com >/dev/null; then
    echo "✅ 网络代理测试成功，可以访问 Google"
else
    echo "⚠️ 无法通过代理访问 Google，请检查 Windows 上的代理软件是否监听在 $WIN_IP:1081"
fi

echo
echo "🚀 完成！建议在 PowerShell/CMD 中运行 'wsl --shutdown' 然后重启 WSL"
