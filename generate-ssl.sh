#!/bin/bash

# SSL证书生成脚本
# 用于生成自签名证书或配置Let's Encrypt证书

echo "🔐 生成SSL证书..."

# 创建SSL目录
mkdir -p ssl

# 检查是否已有证书
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo "✅ SSL证书已存在"
    echo "证书信息："
    openssl x509 -in ssl/cert.pem -text -noout | grep -E "(Subject:|Not After|DNS:)"
    exit 0
fi

# 生成自签名证书
echo "🔨 生成自签名证书..."

# 生成私钥
openssl genrsa -out ssl/key.pem 2048

# 生成证书签名请求
openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=CN/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# 生成自签名证书
openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem

# 清理临时文件
rm ssl/cert.csr

# 设置权限
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "✅ 自签名证书生成完成！"
echo ""
echo "📋 证书信息："
openssl x509 -in ssl/cert.pem -text -noout | grep -E "(Subject:|Not After)"

echo ""
echo "⚠️  注意："
echo "   1. 这是自签名证书，浏览器会显示安全警告"
echo "   2. 生产环境请使用Let's Encrypt或商业证书"
echo "   3. 证书有效期为365天"
echo ""
echo "🔧 使用Let's Encrypt证书："
echo "   1. 确保有域名和公网IP"
echo "   2. 运行: certbot --nginx -d your-domain.com"
echo "   3. 证书会自动配置到Nginx" 