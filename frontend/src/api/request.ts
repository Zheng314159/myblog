import axios from "axios";
import { TokenManager } from "../utils/tokenManager";

const request = axios.create({
  baseURL: "/api/v1", // 可根据需要调整
  timeout: 10000,
  withCredentials: true,
});

// 请求拦截器：自动加 token
request.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
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
    if (error.response?.status === 401) {
      console.log("Authentication error detected");
      
      // Debug token information
      TokenManager.debugTokens();
      
      // Clear invalid tokens
      TokenManager.clearTokens();
      
      // Redirect to login page
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// 你可以在这里添加拦截器等
// request.interceptors.request.use(...)
// request.interceptors.response.use(...)

export default request; 