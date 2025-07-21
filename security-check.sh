#!/bin/bash

# 安全配置检查脚本

echo "🔒 检查安全配置..."

# 检查SSL证书
echo "📋 检查SSL证书..."
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo "✅ SSL证书存在"
    echo "证书有效期："
    openssl x509 -in ssl/cert.pem -noout -dates
else
    echo "❌ SSL证书不存在，请运行 ./generate-ssl.sh"
fi

# 检查环境变量
echo ""
echo "📋 检查环境变量..."
if [ -f ".env" ]; then
    echo "✅ .env文件存在"
    
    # 检查SECRET_KEY
    if grep -q "SECRET_KEY=your-secret-key" .env; then
        echo "⚠️  警告：SECRET_KEY使用默认值，请修改"
    else
        echo "✅ SECRET_KEY已配置"
    fi
    
    # 检查ENVIRONMENT
    if grep -q "ENVIRONMENT=production" .env; then
        echo "✅ 环境设置为production"
    else
        echo "⚠️  警告：环境未设置为production"
    fi
else
    echo "❌ .env文件不存在"
fi

# 检查Docker服务状态
echo ""
echo "📋 检查Docker服务状态..."
if command -v docker-compose &> /dev/null; then
    if [ -f "docker-compose.yml" ]; then
        echo "✅ docker-compose.yml存在"
        
        # 检查服务是否运行
        if docker-compose ps | grep -q "Up"; then
            echo "✅ 服务正在运行"
        else
            echo "⚠️  服务未运行，请执行 docker-compose up -d"
        fi
    else
        echo "❌ docker-compose.yml不存在"
    fi
else
    echo "❌ docker-compose未安装"
fi

# 检查端口占用
echo ""
echo "📋 检查端口占用..."
if command -v netstat &> /dev/null; then
    if netstat -tulpn 2>/dev/null | grep -q ":80 "; then
        echo "✅ 端口80被占用"
    else
        echo "❌ 端口80未被占用"
    fi
    
    if netstat -tulpn 2>/dev/null | grep -q ":443 "; then
        echo "✅ 端口443被占用"
    else
        echo "❌ 端口443未被占用"
    fi
fi

# 检查防火墙
echo ""
echo "📋 检查防火墙..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo "✅ 防火墙已启用"
        echo "防火墙规则："
        ufw status numbered
    else
        echo "⚠️  防火墙未启用"
    fi
elif command -v firewall-cmd &> /dev/null; then
    if firewall-cmd --state | grep -q "running"; then
        echo "✅ 防火墙已启用"
        echo "防火墙规则："
        firewall-cmd --list-all
    else
        echo "⚠️  防火墙未启用"
    fi
else
    echo "⚠️  未检测到防火墙"
fi

# 检查Nginx配置
echo ""
echo "📋 检查Nginx配置..."
if [ -f "nginx.conf" ]; then
    echo "✅ nginx.conf存在"
    
    # 检查HTTPS配置
    if grep -q "listen 443 ssl" nginx.conf; then
        echo "✅ HTTPS配置存在"
    else
        echo "❌ HTTPS配置不存在"
    fi
    
    # 检查安全头
    if grep -q "Strict-Transport-Security" nginx.conf; then
        echo "✅ HSTS头已配置"
    else
        echo "❌ HSTS头未配置"
    fi
    
    if grep -q "X-Frame-Options" nginx.conf; then
        echo "✅ X-Frame-Options头已配置"
    else
        echo "❌ X-Frame-Options头未配置"
    fi
else
    echo "❌ nginx.conf不存在"
fi

# 检查文件权限
echo ""
echo "📋 检查文件权限..."
if [ -f "ssl/key.pem" ]; then
    perms=$(stat -c %a ssl/key.pem)
    if [ "$perms" = "600" ]; then
        echo "✅ SSL私钥权限正确 (600)"
    else
        echo "⚠️  SSL私钥权限不正确: $perms (应为600)"
    fi
fi

# 安全建议
echo ""
echo "🔒 安全建议："
echo "   1. 修改.env文件中的SECRET_KEY"
echo "   2. 配置防火墙规则"
echo "   3. 定期更新SSL证书"
echo "   4. 启用日志监控"
echo "   5. 定期备份数据"
echo "   6. 使用强密码"
echo "   7. 限制管理后台访问IP"
echo "   8. 配置fail2ban防止暴力破解"

echo ""
echo "✅ 安全检查完成！" 