# 邮箱配置指南

本文档将帮助您配置邮箱功能，以便在用户注册和密码重置时发送邮件。

## 1. 创建环境配置文件

首先，复制 `env.example` 文件为 `.env`：

```bash
cp env.example .env
```

## 2. 配置邮箱设置

编辑 `.env` 文件，设置以下邮箱相关配置：

```env
# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_ENABLED=true
```

## 3. 不同邮箱服务商的配置

### Gmail 配置

1. 启用两步验证
2. 生成应用专用密码：
   - 访问 [Google 账户设置](https://myaccount.google.com/)
   - 进入"安全性" → "应用专用密码"
   - 生成新的应用专用密码

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-digit-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_ENABLED=true
```

### QQ邮箱配置

1. 开启SMTP服务：
   - 登录QQ邮箱
   - 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
   - 开启"POP3/SMTP服务"

2. 获取授权码：
   - 开启服务后会获得授权码
   - 使用授权码作为密码

```env
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
EMAIL_USER=your-qq@qq.com
EMAIL_PASSWORD=your-authorization-code
EMAIL_FROM=your-qq@qq.com
EMAIL_ENABLED=true
```

### 163邮箱配置

1. 开启SMTP服务：
   - 登录163邮箱
   - 设置 → POP3/SMTP/IMAP
   - 开启"SMTP服务"

2. 获取授权码：
   - 开启服务后会获得授权码
   - 使用授权码作为密码

```env
SMTP_SERVER=smtp.163.com
SMTP_PORT=587
EMAIL_USER=your-email@163.com
EMAIL_PASSWORD=your-authorization-code
EMAIL_FROM=your-email@163.com
EMAIL_ENABLED=true
```

### 126邮箱配置

```env
SMTP_SERVER=smtp.126.com
SMTP_PORT=587
EMAIL_USER=your-email@126.com
EMAIL_PASSWORD=your-authorization-code
EMAIL_FROM=your-email@126.com
EMAIL_ENABLED=true
```

## 4. 测试邮箱功能

配置完成后，运行测试脚本：

```bash
python test_email_simple.py
```

或者使用原有的测试脚本：

```bash
python test_email.py
```

## 5. 常见问题

### 认证失败
- 确保使用了正确的密码（应用专用密码或授权码）
- 检查邮箱地址是否正确
- 确保已开启SMTP服务

### 连接失败
- 检查SMTP服务器地址和端口
- 确保网络连接正常
- 检查防火墙设置

### Gmail 特定问题
- 必须启用两步验证
- 必须使用应用专用密码，不能使用账户密码
- 确保"不够安全的应用"设置已关闭

## 6. 邮箱功能使用

配置成功后，系统将在以下情况自动发送邮件：

1. **用户注册**：发送欢迎邮件
2. **密码重置**：发送密码重置链接
3. **评论通知**：当文章收到新评论时通知作者

## 7. 安全注意事项

- 不要在代码中硬编码邮箱密码
- 定期更换应用专用密码或授权码
- 使用环境变量存储敏感信息
- 在生产环境中使用更安全的邮件服务 