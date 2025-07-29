import axios from "axios";
import { TokenManager } from "../utils/tokenManager";

// ✅ 默认使用 "/api/v1"，可通过环境变量覆盖（用于未来脱离代理部署）
const baseURL = "/api/v1";
const request = axios.create({
  baseURL, // 所有请求将以此为前缀
  timeout: 10000,
});

let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

async function getValidToken(): Promise<string> {
  if (!refreshPromise) {
    isRefreshing = true;
    refreshPromise = TokenManager.refreshTokens().finally(() => {
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
// 响应拦截器：token 自动刷新 & 重试
request.interceptors.response.use((res) => res, async (error) => {
  const originalRequest = error.config;
  const isTokenError = error.response?.status === 401 || (
    error.response?.status === 500 &&
    typeof error.response?.data?.detail === 'string' &&
    /token|expired/i.test(error.response.data.detail)
  );

  if (isTokenError && TokenManager.getRefreshToken() && !originalRequest._retry) {
    originalRequest._retry = true;
    try {
      const newToken = await getValidToken();
      originalRequest.headers = originalRequest.headers || {};
      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return request(originalRequest);
    } catch {
      return Promise.reject(error);
    }
  }

  return Promise.reject(error);
});

// 你可以在这里添加拦截器等
// request.interceptors.request.use(...)
// request.interceptors.response.use(...)

export default request; 