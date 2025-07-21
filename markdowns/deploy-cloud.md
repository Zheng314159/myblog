# 云平台部署指南

## 1. 阿里云/腾讯云部署

### 使用ECS + 云数据库Redis

1. **购买ECS实例**
   - 推荐配置：2核4GB内存，50GB系统盘
   - 操作系统：Ubuntu 20.04 LTS
   - 带宽：5Mbps起步

2. **购买云数据库Redis**
   - 选择Redis 6.0版本
   - 内存：1GB起步
   - 网络类型：内网访问

3. **部署步骤**
   ```bash
   # 连接到ECS
   ssh root@your-server-ip
   
   # 运行部署脚本
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **配置环境变量**
   ```bash
   # 编辑.env文件
   nano /opt/myblog/.env
   
   # 添加以下配置
   REDIS_URL=redis://your-redis-endpoint:6379
   DATABASE_URL=sqlite:///./blog.db
   SECRET_KEY=your-secret-key
   ENVIRONMENT=production
   ```

## 2. 腾讯云云开发部署

### 使用云函数 + 云数据库

1. **创建云开发环境**
   - 登录腾讯云控制台
   - 创建云开发环境

2. **部署后端API**
   ```bash
   # 安装云开发CLI
   npm install -g @cloudbase/cli
   
   # 登录
   tcb login
   
   # 部署云函数
   tcb fn deploy myblog-api
   ```

3. **配置云数据库**
   - 创建Redis实例
   - 创建MySQL实例（可选，替换SQLite）

## 3. 阿里云函数计算部署

### 使用函数计算 + 表格存储

1. **创建函数计算服务**
   ```bash
   # 安装fun工具
   npm install -g @alicloud/fun
   
   # 初始化项目
   fun init
   ```

2. **配置template.yml**
   ```yaml
   ROSTemplateFormatVersion: '2015-09-01'
   Transform: 'Aliyun::Serverless-2018-04-03'
   Resources:
     myblog:
       Type: 'Aliyun::Serverless::Service'
       Properties:
         Description: 'MyBlog API Service'
       myblog-api:
         Type: 'Aliyun::Serverless::Function'
         Properties:
           Handler: app.main:app
           Runtime: python3.9
           CodeUri: ./
           EnvironmentVariables:
             REDIS_URL: your-redis-url
             DATABASE_URL: your-database-url
   ```

## 4. 华为云部署

### 使用弹性云服务器

1. **购买弹性云服务器**
   - 规格：2核4GB
   - 镜像：Ubuntu 20.04
   - 带宽：5Mbps

2. **部署步骤**
   ```bash
   # 连接服务器
   ssh root@your-server-ip
   
   # 运行部署脚本
   ./deploy.sh
   ```

## 5. 容器云平台部署

### 使用阿里云容器服务ACK

1. **创建Kubernetes集群**
   - 选择托管版Kubernetes
   - 节点配置：2核4GB，3个节点

2. **部署应用**
   ```bash
   # 构建镜像
   docker build -f Dockerfile.backend -t myblog-backend .
   docker build -f frontend/Dockerfile.frontend -t myblog-frontend .
   
   # 推送到镜像仓库
   docker tag myblog-backend registry.cn-hangzhou.aliyuncs.com/your-namespace/myblog-backend
   docker push registry.cn-hangzhou.aliyuncs.com/your-namespace/myblog-backend
   
   # 部署到Kubernetes
   kubectl apply -f k8s/
   ```

3. **创建k8s配置文件**
   ```yaml
   # k8s/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: myblog-backend
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: myblog-backend
     template:
       metadata:
         labels:
           app: myblog-backend
       spec:
         containers:
         - name: backend
           image: registry.cn-hangzhou.aliyuncs.com/your-namespace/myblog-backend
           ports:
           - containerPort: 8000
           env:
           - name: REDIS_URL
             value: "redis://redis-service:6379"
   ```

## 6. 成本对比

| 部署方案 | 月成本 | 适用场景 |
|---------|--------|----------|
| ECS + 云数据库 | ¥200-500 | 中小型项目 |
| 云函数 | ¥50-200 | 低流量项目 |
| 容器服务 | ¥500-1000 | 大型项目 |
| 传统服务器 | ¥100-300 | 自建机房 |

## 7. 监控和维护

### 基础监控
```bash
# 查看服务状态
systemctl status myblog nginx redis-server

# 查看日志
journalctl -u myblog -f
tail -f /var/log/nginx/access.log

# 查看资源使用
htop
df -h
free -h
```

### 备份策略
```bash
# 数据库备份
cp blog.db blog.db.backup.$(date +%Y%m%d)

# 上传文件备份
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/

# 自动备份脚本
crontab -e
# 添加：0 2 * * * /opt/myblog/backup.sh
```

### 安全配置
```bash
# 配置防火墙
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable

# 配置SSL证书
certbot --nginx -d your-domain.com
``` 