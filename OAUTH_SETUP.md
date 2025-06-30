# OAuth设置指南

本指南将帮助你设置Google和GitHub OAuth认证。

## 目录
- [GitHub OAuth设置](#github-oauth设置)
- [Google OAuth设置](#google-oauth设置)
- [环境变量配置](#环境变量配置)
- [测试OAuth功能](#测试oauth功能)
- [常见问题](#常见问题)

## GitHub OAuth设置

### 1. 创建GitHub OAuth应用

1. 访问 [GitHub Developer Settings](https://github.com/settings/developers)
2. 点击 "New OAuth App"
3. 填写应用信息：
   - **Application name**: 你的应用名称（如：My Blog App）
   - **Homepage URL**: `http://localhost:3000`
   - **Application description**: 应用描述（可选）
   - **Authorization callback URL**: `http://localhost:8000/api/v1/oauth/github/callback`

4. 点击 "Register application"
5. 记录下 **Client ID** 和 **Client Secret**

### 2. 配置环境变量

在 `.env` 文件中添加：

```env
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## Google OAuth设置

### 1. 创建Google OAuth应用

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google+ API：
   - 进入 "APIs & Services" > "Library"
   - 搜索 "Google+ API" 并启用

4. 创建OAuth 2.0凭据：
   - 进入 "APIs & Services" > "Credentials"
   - 点击 "Create Credentials" > "OAuth 2.0 Client IDs"
   - 选择 "Web application"

5. 配置OAuth同意屏幕：
   - 应用名称：你的应用名称
   - 用户支持电子邮件：你的邮箱
   - 开发者联系信息：你的邮箱

6. 配置重定向URI：
   - 添加 `http://localhost:8000/api/v1/oauth/google/callback`

7. 记录下 **Client ID** 和 **Client Secret**

### 2. 配置环境变量

在 `.env` 文件中添加：

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 环境变量配置

完整的OAuth相关环境变量配置：

```env
# OAuth Settings
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OAUTH_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## 测试OAuth功能

### 1. 运行测试脚本

```bash
python test_oauth.py
```

这个脚本会测试：
- OAuth配置是否正确
- OAuth端点是否可访问
- 登录URL是否正确生成
- 数据库模型是否正常
- OAuth服务方法是否存在

### 2. 手动测试OAuth流程

#### GitHub OAuth测试：

1. 访问：`http://localhost:8000/api/v1/oauth/github/login`
2. 应该重定向到GitHub授权页面
3. 授权后应该重定向回你的应用

#### Google OAuth测试：

1. 访问：`http://localhost:8000/api/v1/oauth/google/login`
2. 应该重定向到Google授权页面
3. 授权后应该重定向回你的应用

### 3. 检查OAuth提供商端点

访问：`http://localhost:8000/api/v1/oauth/providers`

应该返回可用的OAuth提供商列表。

## 前端集成

### 1. 添加OAuth登录按钮

在你的前端应用中添加OAuth登录按钮：

```tsx
// GitHub登录
const handleGitHubLogin = () => {
  window.location.href = 'http://localhost:8000/api/v1/oauth/github/login';
};

// Google登录
const handleGoogleLogin = () => {
  window.location.href = 'http://localhost:8000/api/v1/oauth/google/login';
};
```

### 2. 处理OAuth回调

创建OAuth回调页面来处理授权后的重定向：

```tsx
// OAuthCallback.tsx
import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    
    if (accessToken) {
      // 保存token到localStorage
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken || '');
      
      // 重定向到主页或仪表板
      navigate('/');
    } else {
      // 处理错误
      navigate('/login?error=oauth_failed');
    }
  }, [searchParams, navigate]);

  return <div>处理OAuth登录...</div>;
};
```

## 常见问题

### 1. "OAuth not configured" 错误

**原因**: 环境变量未正确设置
**解决方案**: 
- 检查 `.env` 文件中的OAuth配置
- 确保Client ID和Client Secret正确
- 重启服务器

### 2. "Invalid redirect URI" 错误

**原因**: 重定向URI不匹配
**解决方案**:
- 检查OAuth应用配置中的重定向URI
- 确保与代码中的回调URL完全匹配

### 3. "Access denied" 错误

**原因**: 用户取消了授权
**解决方案**: 
- 这是正常行为，用户可以选择不授权
- 在前端处理这种情况

### 4. 数据库连接错误

**原因**: 数据库未正确配置
**解决方案**:
- 确保数据库文件存在
- 运行数据库迁移
- 检查数据库连接配置

### 5. 前端重定向失败

**原因**: 前端URL配置错误
**解决方案**:
- 检查 `FRONTEND_URL` 环境变量
- 确保前端服务器正在运行
- 检查CORS配置

## 安全注意事项

1. **保护Client Secret**: 永远不要在前端代码中暴露Client Secret
2. **使用HTTPS**: 在生产环境中使用HTTPS
3. **验证状态参数**: 在OAuth流程中使用state参数防止CSRF攻击
4. **限制重定向URI**: 只允许必要的重定向URI
5. **定期轮换密钥**: 定期更新OAuth应用的密钥

## 生产环境配置

在生产环境中，需要：

1. 更新重定向URI为生产域名
2. 使用HTTPS
3. 配置正确的CORS设置
4. 使用环境变量管理敏感信息
5. 配置日志记录

## 调试技巧

1. **检查网络请求**: 使用浏览器开发者工具查看网络请求
2. **查看服务器日志**: 检查FastAPI服务器日志
3. **测试端点**: 使用Postman或curl测试OAuth端点
4. **验证配置**: 运行测试脚本验证配置

## 支持

如果遇到问题：

1. 检查本指南的常见问题部分
2. 运行 `python test_oauth.py` 进行诊断
3. 查看服务器日志获取详细错误信息
4. 确保所有依赖都已正确安装 