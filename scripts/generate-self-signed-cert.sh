#!/bin/bash
set -e

# 证书目录
SSL_DIR="./ssl"

# 创建目录（如果不存在）
mkdir -p "${SSL_DIR}"

sudo chown $(whoami):$(whoami) ssl
chmod u+rwx ssl
# 生成自签名证书，参数可根据需求调整
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "${SSL_DIR}/key.pem" \
  -out "${SSL_DIR}/cert.pem" \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=Dev/OU=Local/CN=localhost"

echo "自签名证书已生成："
echo "  - 私钥路径: ${SSL_DIR}/key.pem"
echo "  - 证书路径: ${SSL_DIR}/cert.pem"
echo ""

# 证书内容信息
echo "证书详细信息："
openssl x509 -in "${SSL_DIR}/cert.pem" -text -noout
echo ""

# 显示证书开头几行，方便快速确认格式是否正确
echo "证书文件开头（cert.pem）:"
head -n 10 "${SSL_DIR}/cert.pem"
echo ""

# 显示私钥开头几行
echo "私钥文件开头（key.pem）:"
head -n 10 "${SSL_DIR}/key.pem"
echo ""

echo "生成和验证完成。"
