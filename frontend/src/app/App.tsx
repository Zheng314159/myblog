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
          // 启动token检查
          TokenManager.startTokenCheck();
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

    // 清理函数
    return () => {
      TokenManager.stopTokenCheck();
    };
  }, [dispatch]);

  return (
    <ConfigProvider locale={zhCN} theme={{ algorithm: theme.defaultAlgorithm }}>
      <AntdApp>
        <Helmet>
          <title>基于极坐标系的理论物理框架</title>
        </Helmet>
        <AppRouter />
        <Notification />
      </AntdApp>
    </ConfigProvider>
  );
};

export default App; 