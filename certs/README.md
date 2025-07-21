# 微信支付证书目录

## 文件说明

请将以下微信支付证书文件放置在此目录：

### 必需文件

1. **apiclient_key.pem** - 微信支付商户私钥
   - 从微信商户平台下载
   - 用于API调用签名

2. **wechat_platform_cert.pem** - 微信支付平台证书
   - 从微信商户平台下载
   - 用于验证回调签名

### 文件格式

证书文件应为PEM格式，内容类似：

```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----
```

### 安全注意事项

- 证书文件包含敏感信息，请妥善保管
- 不要将证书文件提交到版本控制系统
- 定期更新证书文件
- 使用HTTPS传输

### 获取证书

1. 登录微信商户平台
2. 进入"账户中心" -> "API安全"
3. 下载API证书和平台证书
4. 将证书文件重命名并放置在此目录 