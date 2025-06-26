import React, { useEffect } from "react";
import { Layout, ConfigProvider, theme } from "antd";
import zhCN from "antd/locale/zh_CN";
import { Helmet } from "react-helmet";
import AppRouter from "./router";
import Notification from "../components/Notification/Notification";
import { useDispatch } from "react-redux";
import { loginSuccess, logout } from "../features/user/userSlice";
import { getMe } from "../api/auth";

const { Header, Content, Footer } = Layout;

const App: React.FC = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const access_token = localStorage.getItem("access_token");
    const refresh_token = localStorage.getItem("refresh_token");
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
          dispatch(logout());
        });
    }
  }, [dispatch]);

  return (
    <ConfigProvider locale={zhCN} theme={{ algorithm: theme.defaultAlgorithm }}>
      <Helmet>
        <title>FastAPI 博客系统</title>
      </Helmet>
      <Layout style={{ minHeight: "100vh" }}>
        <Header style={{ background: "#fff", padding: 0 }}>
          <div style={{ fontWeight: 700, fontSize: 22 }}>FastAPI 博客系统</div>
        </Header>
        <Content style={{ margin: "24px 16px 0" }}>
          <AppRouter />
        </Content>
        <Footer style={{ textAlign: "center" }}>
          FastAPI Blog ©2025 Created by OpenAI GPT-4
        </Footer>
        <Notification />
      </Layout>
    </ConfigProvider>
  );
};

export default App; 