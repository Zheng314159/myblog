# PayPal支付集成设置指南

## 概述

本文档介绍如何在博客系统中集成PayPal支付功能。PayPal是全球领先的在线支付平台，支持多种货币和支付方式。

## 功能特性

- ✅ 支持PayPal Checkout API
- ✅ 支持沙盒和生产环境
- ✅ 支持多种货币（USD、EUR、CNY等）
- ✅ 支持Webhook回调
- ✅ 支持订单查询和退款
- ✅ 支持前端集成

## 配置参数

### 必需配置

在 `.env` 文件中配置以下参数：

```env
# PayPal配置
PAYPAL_CLIENT_ID=AYFxxx...yourClientID
PAYPAL_CLIENT_SECRET=EOdxxx...yourSecret
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
PAYPAL_RETURN_URL=https://yourdomain.com/paypal/return
PAYPAL_CANCEL_URL=https://yourdomain.com/paypal/cancel
PAYPAL_CURRENCY=USD
PAYPAL_QR_BASE=
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `PAYPAL_CLIENT_ID` | PayPal应用Client ID | `AYFxxx...yourClientID` |
| `PAYPAL_CLIENT_SECRET` | PayPal应用Secret | `EOdxxx...yourSecret` |
| `PAYPAL_API_BASE` | PayPal API基础URL | `https://api-m.sandbox.paypal.com` |
| `PAYPAL_RETURN_URL` | 支付成功返回URL | `https://yourdomain.com/paypal/return` |
| `PAYPAL_CANCEL_URL` | 支付取消返回URL | `https://yourdomain.com/paypal/cancel` |
| `PAYPAL_CURRENCY` | 支付货币 | `USD` |
| `PAYPAL_QR_BASE` | 二维码基础URL（可选） | `https://yourdomain.com/qr` |

## 获取PayPal应用凭证

### 1. 注册PayPal开发者账户

1. 访问 [PayPal开发者平台](https://developer.paypal.com/)
2. 使用PayPal账户登录
3. 完成开发者账户验证

### 2. 创建PayPal应用

1. 在开发者平台点击 "My Apps & Credentials"
2. 点击 "Create App"
3. 输入应用名称和描述
4. 选择应用类型（Web应用）
5. 创建应用

### 3. 获取Client ID和Secret

1. 在应用列表中找到刚创建的应用
2. 点击应用名称进入详情页
3. 复制 "Client ID" 和 "Secret"
4. 将这些值配置到 `.env` 文件中

### 4. 配置回调URL

1. 在应用详情页找到 "Web Experience" 设置
2. 配置 Return URL 和 Cancel URL
3. 确保URL与 `.env` 文件中的配置一致

## 环境配置

### 沙盒环境（测试）

```env
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
```

### 生产环境

```env
PAYPAL_API_BASE=https://api-m.paypal.com
```

## 代码结构

### 核心文件

- `app/core/paypal.py` - PayPal支付工具类
- `app/api/v1/donation.py` - 捐赠API（包含PayPal处理）
- `app/core/config.py` - 配置管理

### 主要功能

1. **订单创建** - 创建PayPal支付订单
2. **支付捕获** - 捕获已授权的支付
3. **订单查询** - 查询订单状态和详情
4. **退款处理** - 处理支付退款
5. **Webhook回调** - 处理PayPal回调通知

## API接口

### 创建捐赠订单

```http
POST /api/v1/donation/create
Content-Type: application/json

{
  "amount": 10.00,
  "title": "测试捐赠",
  "description": "这是一个测试捐赠",
  "payment_method": "PAYPAL"
}
```

### PayPal回调

```http
POST /api/v1/donation/callback/paypal
Content-Type: application/json

{
  "id": "PAY-123456789",
  "status": "COMPLETED",
  "amount": {
    "value": "10.00",
    "currency_code": "USD"
  }
}
```

## 前端集成

### 捐赠表单

在捐赠表单中添加PayPal选项：

```tsx
{config.paypal_enabled && (
  <Radio value="PAYPAL">PayPal</Radio>
)}
```

### 支付处理

当用户选择PayPal支付时：

1. 前端发送创建订单请求
2. 后端创建PayPal订单
3. 返回PayPal审批URL
4. 前端跳转到PayPal支付页面
5. 用户完成支付后返回
6. 后端处理回调并更新订单状态

## Webhook配置

### 1. 配置Webhook URL

在PayPal开发者平台配置Webhook URL：

```
https://yourdomain.com/api/v1/donation/callback/paypal
```

### 2. 选择事件类型

选择以下Webhook事件：

- `PAYMENT.CAPTURE.COMPLETED` - 支付完成
- `PAYMENT.CAPTURE.DENIED` - 支付被拒绝
- `PAYMENT.CAPTURE.PENDING` - 支付待处理
- `PAYMENT.CAPTURE.REFUNDED` - 支付已退款

### 3. 验证Webhook

PayPal会发送验证请求，确保Webhook URL有效。

## 测试流程

### 1. 沙盒测试

1. 使用沙盒环境配置
2. 使用PayPal沙盒账户测试支付
3. 验证订单创建和回调处理
4. 测试各种支付场景

### 2. 生产部署

1. 切换到生产环境配置
2. 使用真实的PayPal账户
3. 配置生产环境的Webhook
4. 进行完整的支付测试

## 错误处理

### 常见错误

1. **401 Unauthorized** - Client ID或Secret错误
2. **400 Bad Request** - 请求参数错误
3. **404 Not Found** - 订单不存在
4. **500 Internal Server Error** - 服务器内部错误

### 错误处理策略

1. 记录详细的错误日志
2. 实现重试机制
3. 提供用户友好的错误提示
4. 监控支付成功率

## 安全考虑

### 1. 数据安全

- 使用HTTPS传输所有数据
- 不要在代码中硬编码敏感信息
- 定期更新API密钥

### 2. 验证机制

- 验证PayPal回调签名
- 验证订单金额和状态
- 防止重复处理同一订单

### 3. 监控告警

- 监控支付成功率
- 监控API调用频率
- 设置异常告警机制

## 性能优化

### 1. 缓存策略

- 缓存PayPal访问令牌
- 缓存订单状态信息
- 使用Redis存储会话数据

### 2. 异步处理

- 异步处理Webhook回调
- 异步发送通知邮件
- 异步更新订单状态

## 维护和监控

### 1. 日志监控

- 记录所有PayPal API调用
- 记录支付成功和失败事件
- 监控API响应时间

### 2. 定期检查

- 检查PayPal应用状态
- 验证Webhook配置
- 更新API文档

## 故障排除

### 1. 访问令牌获取失败

- 检查Client ID和Secret是否正确
- 确认网络连接正常
- 检查API Base URL是否正确

### 2. 订单创建失败

- 检查请求参数格式
- 确认货币代码正确
- 验证回调URL配置

### 3. Webhook回调失败

- 检查Webhook URL是否可访问
- 验证回调签名
- 检查服务器日志

## 联系支持

如果遇到问题，可以：

1. 查看PayPal开发者文档
2. 联系PayPal技术支持
3. 查看系统日志和错误信息
4. 使用测试脚本验证配置

## 更新日志

- **v1.0.0** - 初始版本，支持基本的PayPal支付功能
- **v1.1.0** - 添加Webhook回调支持
- **v1.2.0** - 添加退款功能
- **v1.3.0** - 优化错误处理和日志记录 