#!/bin/bash

# === 配置你的代理地址（根据你Clash显示的IPv4网关来改）===
WIN_GATEWAY="172.26.48.1"  # ← 可以改成你 WSL 的 Windows IP
HTTP_PORT="1081"
SOCKS_PORT="1080"

echo "✅ 设置环境变量..."
cat <<EOF >> ~/.bashrc

# === WSL Proxy 设置开始 ===
export http_proxy=http://$WIN_GATEWAY:$HTTP_PORT
export https_proxy=http://$WIN_GATEWAY:$HTTP_PORT
export all_proxy=socks5h://$WIN_GATEWAY:$SOCKS_PORT
# === WSL Proxy 设置结束 ===
EOF

source ~/.bashrc

echo "✅ 设置 DNS..."
sudo bash -c "echo -e 'nameserver 8.8.8.8\nnameserver 1.1.1.1' > /etc/resolv.conf"

echo "✅ 禁用 WSL 自动生成 resolv.conf..."
sudo bash -c "echo -e '[network]\ngenerateResolvConf=false' > /etc/wsl.conf"

echo "✅ 关闭并重启 WSL 网络..."
wsl.exe --shutdown

echo "⚠️ 请重新打开你的 WSL Ubuntu 终端，再执行以下命令测试连接："

echo -e "\n🚀 curl -x http://$WIN_GATEWAY:$HTTP_PORT https://www.google.com -I --connect-timeout 10"
echo -e "🚀 curl -x socks5h://$WIN_GATEWAY:$SOCKS_PORT https://ipinfo.io --connect-timeout 10\n"

echo "✅ 所有设置完成！如果仍无法访问，请确认 Clash 设置已开启「允许局域网连接」并监听 0.0.0.0"
