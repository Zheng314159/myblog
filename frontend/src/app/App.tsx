import React, { useEffect } from "react";
import { App as AntdApp, ConfigProvider, theme } from "antd";
import zhCN from "antd/locale/zh_CN";
import { Helmet } from "react-helmet";
import AppRouter from "./router";
import Notification from "../components/Notification/Notification";
import { useDispatch } from "react-redux";
import { loginSuccess, logout, setLoading } from "../features/user/userSlice";
import { getMe } from "../api/auth";
import { TokenManager } from "../utils/tokenManager";

const App: React.FC = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const access_token = TokenManager.getAccessToken();
    const refresh_token = TokenManager.getRefreshToken();
    
    if (access_token) {
      getMe()
        .then(res => {
          const userInfo = res.data;
          dispatch(loginSuccess({
            accessToken: access_token,
            refreshToken: refresh_token,
            userInfo: {
              id: userInfo.id,
              username: userInfo.username,
              email: userInfo.email,
              role: userInfo.role,
            },
          }));
        })
        .catch(() => {
          // 如果获取用户信息失败，清除无效的token
          TokenManager.clearTokens();
          dispatch(logout());
        });
    } else {
      // 如果没有token，直接设置loading为false
      dispatch(setLoading(false));
    }
  }, [dispatch]);

  return (
    <ConfigProvider locale={zhCN} theme={{ algorithm: theme.defaultAlgorithm }}>
      <AntdApp>
        <Helmet>
          <title>FastAPI 博客系统</title>
        </Helmet>
        <AppRouter />
        <Notification />
      </AntdApp>
    </ConfigProvider>
  );
};

export default App; 