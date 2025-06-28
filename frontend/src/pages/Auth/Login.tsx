import React, { useState } from "react";
import { Form, Input, Button, Typography, App } from "antd";
import { login, getMe } from "../../api/auth";
import { useDispatch } from "react-redux";
import { loginSuccess } from "../../features/user/userSlice";
import { useNavigate } from "react-router-dom";
import { TokenManager } from "../../utils/tokenManager";

const { Title } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { message } = App.useApp();

  const onFinish = async (values: any) => {
    console.log("表单提交内容：", values);
    setLoading(true);
    try {
      const res = await login(values);
      const { access_token, refresh_token } = res.data;
      console.log('[DEBUG] 登录接口返回:', res.data);
      if (!access_token || !refresh_token) {
        message.error('登录失败：未获取到有效的 access_token 或 refresh_token');
        setLoading(false);
        return;
      }
      // 使用 TokenManager 存储 token
      TokenManager.storeTokens({
        access_token,
        refresh_token,
        token_type: "bearer"
      });
      
      // 登录后获取用户信息
      const userInfoResp = await getMe();
      console.log("getMe 响应：", userInfoResp);
      console.log("userInfoResp.data:", userInfoResp.data);
      const userInfo = userInfoResp.data;
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
      message.success("登录成功");
      navigate("/");
    } catch (e: any) {
      const msg = e?.response?.data?.message || e.message || "登录失败";
      message.error(msg);
      console.error("登录错误:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
      <Title level={3}>登录</Title>
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="username" label="用户名" rules={[{ required: true, message: "请输入用户名" }]}>
          <Input autoComplete="username" />
        </Form.Item>
        <Form.Item name="password" label="密码" rules={[{ required: true, message: "请输入密码" }]}>
          <Input.Password autoComplete="current-password" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>登录</Button>
        </Form.Item>
      </Form>
      <div style={{ margin: "16px 0" }}>
        没有账号？<a href="/register">注册</a>
      </div>
      <div>
        <Button type="default" block href="/api/v1/oauth/github/login" style={{ marginBottom: 8 }}>GitHub 登录</Button>
        <Button type="default" block href="/api/v1/oauth/google/login">Google 登录</Button>
      </div>
    </div>
  );
};

export default Login; 