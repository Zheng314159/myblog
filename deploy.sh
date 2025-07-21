#!/bin/bash

# 博客系统部署脚本
# 适用于Ubuntu/CentOS服务器

set -e

echo "开始部署博客系统..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 更新系统
echo "更新系统包..."
apt-get update
apt-get upgrade -y

# 安装基础依赖
echo "安装基础依赖..."
apt-get install -y curl wget git nginx redis-server python3 python3-pip python3-venv nodejs npm

# 安装pnpm
echo "安装pnpm..."
npm install -g pnpm

# 创建应用目录
APP_DIR="/opt/myblog"
echo "创建应用目录: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# 克隆代码（如果是从Git仓库）
# git clone https://github.com/your-repo/myblog.git .

# 或者直接复制文件到服务器
# 这里假设文件已经在服务器上

# 创建Python虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 安装前端依赖并构建
echo "构建前端..."
cd frontend
pnpm install
pnpm build
cd ..

# 创建uploads目录
mkdir -p uploads

# 设置文件权限
echo "设置文件权限..."
chown -R www-data:www-data uploads
chmod -R 755 uploads

# 配置Redis
echo "配置Redis..."
systemctl enable redis-server
systemctl start redis-server

# 配置Nginx
echo "配置Nginx..."
cat > /etc/nginx/sites-available/myblog << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    # 前端静态文件
    location / {
        root /opt/myblog/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存设置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 上传文件
    location /uploads/ {
        alias /opt/myblog/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # API代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 管理后台
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/myblog /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx

# 创建systemd服务文件
echo "创建systemd服务..."
cat > /etc/systemd/system/myblog.service << 'EOF'
[Unit]
Description=MyBlog FastAPI Application
After=network.target redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/myblog
Environment=PATH=/opt/myblog/venv/bin
ExecStart=/opt/myblog/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd并启动服务
systemctl daemon-reload
systemctl enable myblog
systemctl start myblog

# 检查服务状态
echo "检查服务状态..."
systemctl status myblog --no-pager
systemctl status nginx --no-pager
systemctl status redis-server --no-pager

echo "部署完成！"
echo "访问地址: http://your-domain.com"
echo "管理后台: http://your-domain.com/admin"
echo ""
echo "常用命令:"
echo "  查看日志: journalctl -u myblog -f"
echo "  重启服务: systemctl restart myblog"
echo "  停止服务: systemctl stop myblog" 