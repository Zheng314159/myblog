# 微信支付V3集成说明

## 概述

本项目已集成微信支付V3功能，支持扫码支付方式。用户可以通过微信扫描二维码完成捐赠支付。

## 功能特性

- ✅ 微信扫码支付（Native支付）
- ✅ 微信JSAPI支付（小程序支付）
- ✅ 支付回调处理
- ✅ 订单状态管理
- ✅ 支付结果通知
- ✅ 错误处理机制
- ✅ 订单查询功能
- ✅ 订单关闭功能
- ✅ 退款功能

## 配置步骤

### 1. 微信支付商户配置

1. 注册微信支付商户号
2. 获取以下信息：
   - 微信App ID
   - 微信商户号
   - API V3密钥
   - 支付证书

### 2. 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# 微信支付V3配置
WECHAT_APP_ID=你的微信App ID
WECHAT_MCH_ID=你的微信商户号
WECHAT_KEY=你的微信API V3密钥
WECHAT_CERT_PATH=keys/wechat_cert.pem
WECHAT_KEY_PATH=keys/wechat_key.pem
WECHAT_NOTIFY_URL=http://你的域名/api/v1/donation/callback/wechat
WECHAT_GATEWAY=https://api.mch.weixin.qq.com
WECHAT_QR_BASE=http://你的域名/qr/wechat
```

### 3. 证书文件配置

将微信支付证书文件放置在 `keys/` 目录下：

```
keys/
├── wechat_cert.pem    # 微信支付证书
└── wechat_key.pem     # 微信支付私钥
```

### 4. 安装依赖

```bash
pip install wechatpayv3==1.3.11
```

## API 接口

### 创建捐赠订单

**POST** `/api/v1/donation/create`

请求参数：
```json
{
  "donor_name": "张三",
  "donor_email": "zhangsan@example.com",
  "donor_message": "支持你们！",
  "is_anonymous": false,
  "amount": 10.00,
  "currency": "CNY",
  "donation_type": "ONE_TIME",
  "payment_method": "WECHAT"
}
```

响应示例：
```json
{
  "id": 123,
  "donor_name": "张三",
  "amount": 10.00,
  "payment_method": "WECHAT",
  "payment_status": "PENDING",
  "wechat_qr": "weixin://wxpay/bizpayurl?pr=xxx",
  "wechat_prepay_id": "wx123456789",
  "wechat_trade_type": "NATIVE"
}
```

### 微信支付回调

**POST** `/api/v1/donation/callback/wechat`

微信支付完成后的回调接口，自动处理支付结果。

## 前端集成

### 支付流程

1. 用户选择微信支付方式
2. 系统使用V3 API创建微信支付订单
3. 生成支付二维码
4. 用户扫码支付
5. 微信回调通知支付结果
6. 系统使用V3 API验证回调并更新订单状态

### 二维码显示

前端会自动显示微信支付二维码，用户可以使用微信扫码支付。

## 测试

### 运行测试脚本

```bash
python test_wechat_pay.py
```

### 测试内容

- 配置验证
- 实例创建
- V3新功能测试
- 订单创建

## V3版本优势

### 1. 更安全的协议

- 使用API V3协议，安全性更高
- 支持RSA签名验证
- 自动加密解密回调数据

### 2. 更多支付场景

- Native支付（扫码支付）
- JSAPI支付（小程序支付）
- H5支付（网页支付）
- 小程序支付

### 3. 更完善的功能

- 订单查询
- 订单关闭
- 退款处理
- 更好的错误处理

### 4. 官方推荐

- 微信官方推荐的SDK
- 持续维护和更新
- 更好的文档支持

## 注意事项

### 1. 证书安全

- 证书文件应妥善保管，不要提交到版本控制
- 定期更新证书
- 使用HTTPS传输

### 2. 回调URL

- 回调URL必须使用HTTPS
- 确保回调URL可以被微信访问
- 建议使用域名而非IP地址

### 3. 金额处理

- 微信支付金额单位为分
- 系统会自动转换金额单位
- 注意金额精度处理

### 4. 错误处理

- 网络异常处理
- 签名验证失败处理
- 订单状态异常处理

## 常见问题

### Q: 微信支付配置不完整怎么办？

A: 检查 `.env` 文件中的微信支付配置项是否都已填写。

### Q: 证书文件找不到怎么办？

A: 确保证书文件已放置在 `keys/` 目录下，文件名与配置一致。

### Q: 回调处理失败怎么办？

A: 检查回调URL是否正确，网络是否通畅，证书是否有效。

### Q: 二维码无法显示怎么办？

A: 检查微信支付订单是否创建成功，网络连接是否正常。

### Q: V3版本与V2版本有什么区别？

A: V3版本使用更安全的API协议，支持更多支付场景，功能更完善。

## 开发说明

### 核心文件

- `app/core/wechat_pay.py` - 微信支付V3工具类
- `app/api/v1/donation.py` - 捐赠API（包含微信支付V3处理）
- `app/core/config.py` - 配置文件（包含微信支付V3配置）

### 主要类

- `WeChatPayV3` - 微信支付V3工具类
- `DonationRecord` - 捐赠记录模型
- `DonationConfig` - 捐赠配置模型

### 扩展功能

如需添加更多微信支付功能（如H5支付、小程序支付等），可以扩展 `WeChatPayV3` 类。 