import request from './request';

// 获取支持的 OAuth 平台及绑定状态
export const getOAuthProviders = () => request.get('/api/v1/oauth/providers');

// 跳转第三方登录
export const oauthLogin = (provider: string) =>
  window.location.href = `/api/v1/oauth/login/${provider}`;

// 绑定第三方账号
export const bindOAuth = (provider: string, code: string) =>
  request.post(`/api/v1/oauth/bind/${provider}`, { code });

// 解绑第三方账号
export const unbindOAuth = (provider: string) =>
  request.post(`/api/v1/oauth/unbind/${provider}`);




// 3. OAuth 绑定/解绑
// 后端接口建议（FastAPI）
// /api/v1/oauth/login/{provider}：第三方登录（GitHub、Gitee、QQ、微信等）
// /api/v1/oauth/bind/{provider}：绑定第三方账号（需登录）
// /api/v1/oauth/unbind/{provider}：解绑第三方账号（需登录）
// /api/v1/oauth/providers：获取支持的 OAuth 平台及绑定状态

// 前端页面建议
// 个人中心（/profile）：展示已绑定的第三方账号，支持绑定/解绑
// 登录页：支持第三方登录按钮，跳转 OAuth 授权
// 4. 页面结构建议
// /tags：标签云/标签列表
// /tags/:id：标签详情（含文章列表）
// /search：搜索页
// /profile：个人中心（含 OAuth 绑定/解绑）
// /login：登录页（含第三方登录入口）
// 5. 其他建议
// 所有接口建议支持分页、搜索、排序
// 前端接口统一用 request 封装，便于全局处理 token、错误等
// OAuth 绑定/解绑建议前后端联调，注意安全性（如二次确认、token 校验）