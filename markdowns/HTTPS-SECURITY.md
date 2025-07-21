# HTTPS安全配置指南

## 概述

本指南详细说明了如何为博客系统配置HTTPS安全连接，包括SSL证书生成、Nginx配置和安全头设置。

## 🔐 SSL证书配置

### 1. 开发环境（自签名证书）

#### Linux/macOS
```bash
# 生成自签名证书
chmod +x generate-ssl.sh
./generate-ssl.sh
```

#### Windows
```cmd
# 运行Windows脚本
setup-https.bat
```

### 2. 生产环境（Let's Encrypt证书）

```bash
# 配置Let's Encrypt证书
chmod +x setup-letsencrypt.sh
sudo ./setup-letsencrypt.sh your-domain.com
```

### 3. 手动配置

```bash
# 安装certbot
apt-get install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期
crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 🛡️ 安全头配置

Nginx配置中已包含以下安全头：

### 1. HSTS (HTTP Strict Transport Security)
```
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```
- 强制浏览器使用HTTPS连接
- 有效期1年
- 包含子域名

### 2. X-Frame-Options
```
add_header X-Frame-Options DENY always;
```
- 防止点击劫持攻击
- 禁止在iframe中嵌入

### 3. X-Content-Type-Options
```
add_header X-Content-Type-Options nosniff always;
```
- 防止MIME类型嗅探
- 强制浏览器使用声明的Content-Type

### 4. X-XSS-Protection
```
add_header X-XSS-Protection "1; mode=block" always;
```
- 启用浏览器XSS保护
- 检测到攻击时阻止页面加载

### 5. Referrer-Policy
```
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```
- 控制Referrer信息传递
- 跨域时只传递源信息

### 6. Content-Security-Policy
```
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:;" always;
```
- 防止XSS攻击
- 控制资源加载来源
- 允许WebSocket连接

## 🔒 SSL/TLS配置

### 1. 协议版本
```
ssl_protocols TLSv1.2 TLSv1.3;
```
- 只允许TLS 1.2和1.3
- 禁用不安全的TLS 1.0和1.1

### 2. 加密套件
```
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
```
- 使用强加密算法
- 支持前向保密

### 3. 会话缓存
```
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```
- 提高SSL握手性能
- 减少CPU使用

## 🔍 安全检查

### 1. 运行安全检查脚本
```bash
chmod +x security-check.sh
./security-check.sh
```

### 2. 在线安全检测
- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)
- [Mozilla Observatory](https://observatory.mozilla.org/)

### 3. 手动检查项目
- [ ] SSL证书有效期
- [ ] 安全头配置
- [ ] 防火墙规则
- [ ] 文件权限设置
- [ ] 环境变量安全
- [ ] 日志监控

## 🚀 快速部署

### Docker方式
```bash
# 1. 生成SSL证书
./generate-ssl.sh

# 2. 启动服务
./start-docker.sh

# 3. 检查安全配置
./security-check.sh
```

### 传统部署
```bash
# 1. 运行部署脚本
sudo ./deploy.sh

# 2. 配置SSL证书
sudo ./setup-letsencrypt.sh your-domain.com

# 3. 检查安全配置
./security-check.sh
```

## 📊 安全等级评估

### A+ 等级要求
- [ ] 使用TLS 1.3
- [ ] 配置HSTS
- [ ] 设置安全头
- [ ] 使用强加密套件
- [ ] 证书有效期合理
- [ ] 自动续期配置

### 额外安全措施
- [ ] 配置fail2ban
- [ ] 限制管理后台访问IP
- [ ] 启用日志监控
- [ ] 定期安全更新
- [ ] 数据加密存储

## 🔧 故障排除

### 1. 证书问题
```bash
# 检查证书状态
openssl x509 -in ssl/cert.pem -text -noout

# 检查证书有效期
openssl x509 -in ssl/cert.pem -noout -dates

# 重新生成证书
./generate-ssl.sh
```

### 2. Nginx配置问题
```bash
# 测试配置
nginx -t

# 重新加载配置
nginx -s reload

# 查看错误日志
tail -f /var/log/nginx/error.log
```

### 3. 安全头问题
```bash
# 检查安全头
curl -I https://your-domain.com

# 使用在线工具检测
# https://securityheaders.com/
```

## 📚 参考资源

### 官方文档
- [Nginx SSL配置](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Let's Encrypt文档](https://letsencrypt.org/docs/)
- [Mozilla SSL配置生成器](https://ssl-config.mozilla.org/)

### 安全标准
- [OWASP安全头](https://owasp.org/www-project-secure-headers/)
- [SSL/TLS部署最佳实践](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)

### 工具推荐
- [Certbot](https://certbot.eff.org/) - 自动SSL证书管理
- [SSL Labs](https://www.ssllabs.com/) - SSL配置检测
- [Security Headers](https://securityheaders.com/) - 安全头检测

---

**注意**：生产环境部署前，请务必：
1. 使用有效的SSL证书
2. 配置所有安全头
3. 定期更新证书
4. 监控安全状态
5. 备份证书文件 