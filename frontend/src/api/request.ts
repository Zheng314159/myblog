import axios from "axios";
import { TokenManager } from "../utils/tokenManager";

const request = axios.create({
  baseURL: "/api/v1", // 可根据需要调整
  timeout: 10000,
});

// 请求拦截器：自动加 token
request.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
    console.log("[DEBUG] TokenManager.getAccessToken() =", token);
    if (token) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${token}`;
      console.log("Request with token:", token.substring(0, 20) + "...");
    } else {
      console.log("No token found for request");
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
    if (error.response?.status === 401) {
      console.log("Authentication error detected");
      TokenManager.debugTokens();
      TokenManager.clearTokens();
      if (isSendCodeApi) {
        // 只弹窗提示
        window.alert('登录状态已失效，请重新登录后再操作！');
      } else {
        // 其他接口自动跳转
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