#!/bin/bash

# Let's Encrypt证书配置脚本
# 用于生产环境配置免费SSL证书

echo "🔐 配置Let's Encrypt证书..."

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 请提供域名参数"
    echo "用法: $0 your-domain.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

echo "域名: $DOMAIN"
echo "邮箱: $EMAIL"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 检查域名解析
echo "📋 检查域名解析..."
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    echo "❌ 域名 $DOMAIN 无法解析，请检查DNS配置"
    exit 1
fi

# 安装certbot
echo "📦 安装certbot..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum install -y certbot python3-certbot-nginx
else
    echo "❌ 不支持的包管理器"
    exit 1
fi

# 检查Nginx配置
if [ ! -f "/etc/nginx/sites-available/myblog" ]; then
    echo "📝 创建Nginx配置..."
    cat > /etc/nginx/sites-available/myblog << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN;  # 将被替换

    location / {
        root /opt/myblog/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /uploads/ {
        alias /opt/myblog/uploads/;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

    # 替换域名
    sed -i "s/YOUR_DOMAIN/$DOMAIN/g" /etc/nginx/sites-available/myblog
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/myblog /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    systemctl restart nginx
fi

# 申请证书
echo "🔐 申请Let's Encrypt证书..."
certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

# 检查证书状态
echo "📋 检查证书状态..."
if certbot certificates | grep -q "$DOMAIN"; then
    echo "✅ 证书申请成功！"
    
    # 显示证书信息
    echo "证书信息："
    certbot certificates | grep -A 10 "$DOMAIN"
    
    # 设置自动续期
    echo "🔄 设置自动续期..."
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    echo ""
    echo "🎉 Let's Encrypt证书配置完成！"
    echo "访问地址: https://$DOMAIN"
    echo "证书将自动续期"
    
else
    echo "❌ 证书申请失败"
    echo "请检查："
    echo "1. 域名是否正确解析到服务器"
    echo "2. 防火墙是否开放80和443端口"
    echo "3. Nginx是否正常运行"
fi 