import axios from "axios";

const request = axios.create({
  baseURL: "/api/v1", // 可根据需要调整
  timeout: 10000,
  withCredentials: true,
});

// 请求拦截器：自动加 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 你可以在这里添加拦截器等
// request.interceptors.request.use(...)
// request.interceptors.response.use(...)

export default request; 