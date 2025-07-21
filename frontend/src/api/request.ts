import axios from "axios";
import { TokenManager } from "../utils/tokenManager";

// ✅ 默认使用 "/api/v1"，可通过环境变量覆盖（用于未来脱离代理部署）
const baseURL = "/api/v1";
const request = axios.create({
  baseURL, // 所有请求将以此为前缀
  timeout: 10000,
});

let isRefreshing = false;
let refreshPromise: Promise<any> | null = null;

async function refreshToken() {
  if (!refreshPromise) {
    isRefreshing = true;
    const refresh_token = TokenManager.getRefreshToken();
    refreshPromise = axios
      .post(`${baseURL}/auth/refresh`, { refresh_token })
      .then((res) => {
        TokenManager.storeTokens(res.data);
        return res.data.access_token;
      })
      .catch((err) => {
        TokenManager.clearTokens();
        window.location.href = "/login";
        throw err;
      })
      .finally(() => {
        isRefreshing = false;
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

// 请求拦截器：自动加 token
request.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
    // console.log("[DEBUG] TokenManager.getAccessToken() =", token);
    if (token) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${token}`;
      // console.log("Request with token:", token.substring(0, 20) + "...");
    } else {
      // console.log("No token found for request");
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：处理认证错误
request.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const isSendCodeApi = error?.config?.url?.includes('/auth/send-change-password-code');
    const originalRequest = error.config;
    // 兼容后端 500 token 过期错误
    const isTokenError = error.response?.status === 401 ||
      (error.response?.status === 500 && (
        typeof error.response?.data?.detail === 'string' &&
        (error.response.data.detail.toLowerCase().includes('token') || error.response.data.detail.toLowerCase().includes('expired'))
      ));
    if (isTokenError && TokenManager.getRefreshToken() && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newToken = await refreshToken();
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
        return request(originalRequest);
      } catch (e) {
        // 已在 refreshToken 里处理跳转
        return Promise.reject(e);
      }
    }
    if (error.response?.status === 401) {
      // TokenManager.debugTokens();
      TokenManager.clearTokens();
      if (isSendCodeApi) {
        window.alert('登录状态已失效，请重新登录后再操作！');
      } else {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// 你可以在这里添加拦截器等
// request.interceptors.request.use(...)
// request.interceptors.response.use(...)

export default request; 