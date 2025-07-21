#!/bin/bash

# Docker快速启动脚本

echo "🚀 启动博客系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建.env文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建.env文件..."
    cat > .env << 'EOF'
# 数据库配置
DATABASE_URL=sqlite:///./blog.db

# Redis配置
REDIS_URL=redis://redis:6379

# 安全配置
SECRET_KEY=your-secret-key-change-this-in-production

# 环境配置
ENVIRONMENT=production

# 邮件配置（可选）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# OAuth配置（可选）
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# 支付配置（可选）
ALIPAY_APP_ID=your-alipay-app-id
ALIPAY_PRIVATE_KEY=your-alipay-private-key
WECHAT_MCH_ID=your-wechat-mch-id
WECHAT_API_KEY=your-wechat-api-key
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
EOF
    echo "✅ .env文件已创建，请根据需要修改配置"
fi

# 创建uploads目录
mkdir -p uploads

# 生成SSL证书
echo "🔐 生成SSL证书..."
chmod +x generate-ssl.sh
./generate-ssl.sh

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "🎉 部署完成！"
echo ""
echo "📱 访问地址:"
echo "   前端: http://localhost"
echo "   后端API: http://localhost:8000"
echo "   管理后台: http://localhost/admin"
echo "   健康检查: http://localhost/health"
echo ""
echo "🔧 常用命令:"
echo "   查看日志: docker-compose logs -f"
echo "   重启服务: docker-compose restart"
echo "   停止服务: docker-compose down"
echo "   更新代码: docker-compose up -d --build"
echo ""
echo "📝 注意事项:"
echo "   1. 首次访问需要创建管理员账户"
echo "   2. 请修改.env文件中的SECRET_KEY"
echo "   3. 生产环境请配置SSL证书"
echo "   4. 定期备份数据库和上传文件" 