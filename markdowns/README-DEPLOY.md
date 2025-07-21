# 博客系统部署指南

## 项目概述

这是一个基于FastAPI + React + SQLite + Redis的现代化博客系统，支持：

- 📝 文章管理（Markdown编辑器）
- 👥 用户认证（JWT + OAuth）
- 💬 评论系统
- 🏷️ 标签管理
- 📤 文件上传
- 💰 捐赠功能
- 🔍 全文搜索
- 📧 邮件通知
- 🔐 管理后台

## 部署方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Docker Compose** | 简单快速，环境一致 | 需要Docker环境 | 开发/测试/小规模生产 |
| **传统服务器** | 完全控制，成本低 | 配置复杂，维护困难 | 有运维经验的中小项目 |
| **云平台** | 弹性扩展，管理简单 | 成本较高 | 大规模生产环境 |

## 方案一：Docker Compose部署（推荐）

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ 内存
- 10GB+ 磁盘空间

### 快速启动
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/myblog.git
cd myblog

# 2. 运行启动脚本
chmod +x start-docker.sh
./start-docker.sh
```

### 手动部署
```bash
# 1. 创建环境变量文件
cp .env.example .env
# 编辑.env文件，配置数据库、Redis等

# 2. 构建并启动
docker-compose up -d --build

# 3. 查看状态
docker-compose ps
```

### 访问地址
- 前端：https://localhost
- 后端API：https://localhost/api
- 管理后台：https://localhost/admin
- 健康检查：https://localhost/health

## 方案二：传统服务器部署

### 系统要求
- Ubuntu 20.04+ / CentOS 8+
- 2GB+ 内存
- 20GB+ 磁盘空间
- Python 3.9+
- Node.js 16+
- Redis 6.0+

### 部署步骤
```bash
# 1. 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/myblog/main/deploy.sh

# 2. 运行部署脚本
chmod +x deploy.sh
sudo ./deploy.sh
```

### 配置说明
部署脚本会自动：
- 安装系统依赖
- 配置Python虚拟环境
- 构建前端项目
- 配置Nginx反向代理
- 设置systemd服务
- 启动Redis服务

## 方案三：云平台部署

### 阿里云ECS部署
1. 购买ECS实例（2核4GB）
2. 安装Docker和Docker Compose
3. 运行Docker Compose部署方案

### 腾讯云云开发
1. 创建云开发环境
2. 使用云函数部署后端
3. 使用静态网站托管前端

### 华为云部署
1. 购买弹性云服务器
2. 运行传统服务器部署方案

## 环境配置

### 必需配置
```bash
# .env文件
DATABASE_URL=sqlite:///./blog.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

### 可选配置
```bash
# 邮件服务
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# OAuth登录
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# 支付功能
ALIPAY_APP_ID=your-alipay-app-id
WECHAT_MCH_ID=your-wechat-mch-id
PAYPAL_CLIENT_ID=your-paypal-client-id
```

## 数据库初始化

### 首次部署
```bash
# 使用Docker
docker-compose exec backend python -c "
from app.core.database import create_db_and_tables
import asyncio
asyncio.run(create_db_and_tables())
"

# 使用传统部署
cd /opt/myblog
source venv/bin/activate
python -c "
from app.core.database import create_db_and_tables
import asyncio
asyncio.run(create_db_and_tables())
"
```

### 创建管理员账户
```bash
# 使用Docker
docker-compose exec backend python create_admin.py

# 使用传统部署
cd /opt/myblog
source venv/bin/activate
python create_admin.py
```

## 备份和恢复

### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp blog.db $BACKUP_DIR/blog_$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# 删除7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 设置定时备份
```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点备份）
0 2 * * * /opt/myblog/backup.sh
```

## 监控和维护

### 服务状态检查
```bash
# Docker方式
docker-compose ps
docker-compose logs -f

# 传统部署方式
systemctl status myblog nginx redis-server
journalctl -u myblog -f
```

### 性能监控
```bash
# 查看资源使用
htop
df -h
free -h

# 查看网络连接
netstat -tulpn
ss -tulpn
```

### 日志管理
```bash
# 查看Nginx访问日志
tail -f /var/log/nginx/access.log

# 查看应用日志
docker-compose logs -f backend
# 或
journalctl -u myblog -f
```

## 安全配置

### 安全检查
```bash
# 运行安全检查脚本
chmod +x security-check.sh
./security-check.sh
```

### 防火墙设置
```bash
# Ubuntu
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable

# CentOS
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload
```

### SSL证书配置

#### 开发环境（自签名证书）
```bash
# 生成自签名证书
chmod +x generate-ssl.sh
./generate-ssl.sh
```

#### 生产环境（Let's Encrypt证书）
```bash
# 配置Let's Encrypt证书
chmod +x setup-letsencrypt.sh
sudo ./setup-letsencrypt.sh your-domain.com
```

#### 手动配置
```bash
# 安装Certbot
apt-get install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期
crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8000
   
   # 检查日志
   docker-compose logs backend
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库文件权限
   ls -la blog.db
   
   # 重新初始化数据库
   docker-compose exec backend python -c "
   from app.core.database import create_db_and_tables
   import asyncio
   asyncio.run(create_db_and_tables())
   "
   ```

3. **Redis连接失败**
   ```bash
   # 检查Redis服务状态
   docker-compose logs redis
   # 或
   systemctl status redis-server
   ```

4. **前端无法访问**
   ```bash
   # 检查Nginx配置
   nginx -t
   
   # 检查前端构建
   ls -la frontend/dist/
   ```

## 更新部署

### 代码更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose up -d --build
```

### 配置更新
```bash
# 修改.env文件后重启
docker-compose restart backend
```

## 性能优化

### 数据库优化
- 定期清理日志表
- 优化查询索引
- 考虑迁移到PostgreSQL（大规模应用）

### 缓存优化
- 配置Redis持久化
- 增加缓存命中率
- 使用CDN加速静态资源

### 服务器优化
- 调整Nginx worker进程数
- 配置gzip压缩
- 启用HTTP/2

## 联系支持

如果遇到部署问题，请：

1. 查看日志文件
2. 检查配置文件
3. 确认系统要求
4. 提交Issue到GitHub

---

**注意**：生产环境部署前，请务必：
- 修改默认密码
- 配置SSL证书
- 设置防火墙规则
- 定期备份数据
- 监控系统资源 