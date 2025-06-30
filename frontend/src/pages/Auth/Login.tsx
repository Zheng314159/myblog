import React, { useState, useEffect } from "react";
import { Form, Input, Button, Typography, App, Divider, Alert } from "antd";
import { GithubOutlined, GoogleOutlined } from "@ant-design/icons";
import { login, getMe } from "../../api/auth";
import { useDispatch } from "react-redux";
import { loginSuccess } from "../../features/user/userSlice";
import { useNavigate } from "react-router-dom";
import { TokenManager } from "../../utils/tokenManager";

const { Title } = Typography;

interface OAuthProvider {
  name: string;
  display_name: string;
  login_url: string;
  status: 'available' | 'unavailable';
  message: string;
}

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [oauthProviders, setOauthProviders] = useState<OAuthProvider[]>([]);
  const [oauthLoading, setOauthLoading] = useState(true);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { message } = App.useApp();

  // 获取邮箱配置状态和OAuth提供商状态
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        // 获取邮箱配置
        const configResponse = await fetch('/api/v1/auth/config');
        const config = await configResponse.json();
        setEmailEnabled(config.email_enabled);
      } catch (error) {
        console.error('获取邮箱配置失败:', error);
        setEmailEnabled(false);
      }

      try {
        // 获取OAuth提供商状态
        const oauthResponse = await fetch('/api/v1/oauth/providers');
        const oauthData = await oauthResponse.json();
        setOauthProviders(oauthData.providers || []);
      } catch (error) {
        console.error('获取OAuth提供商失败:', error);
        setOauthProviders([]);
      } finally {
        setOauthLoading(false);
      }
    };
    fetchConfig();
  }, []);

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

  const handleForgotPassword = () => {
    navigate("/forgot-password");
  };

  const handleOAuthLogin = (provider: 'github' | 'google') => {
    window.location.href = `/api/v1/oauth/${provider}/login`;
  };

  const getOAuthProvider = (name: string) => {
    return oauthProviders.find(p => p.name === name);
  };

  const githubProvider = getOAuthProvider('github');
  const googleProvider = getOAuthProvider('google');

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
      <Title level={3} style={{ textAlign: 'center', marginBottom: 32 }}>登录</Title>
      
      {/* OAuth 登录按钮 */}
      {!oauthLoading && oauthProviders.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          {/* GitHub 登录按钮 */}
          {githubProvider && (
            <Button 
              type="default" 
              block 
              size="large"
              icon={<GithubOutlined />}
              onClick={() => handleOAuthLogin('github')}
              disabled={githubProvider.status === 'unavailable'}
              style={{ 
                marginBottom: 12,
                height: 44,
                fontSize: 16,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              使用 GitHub 登录
            </Button>
          )}

          {/* Google 登录按钮 - 只在网络可用时显示 */}
          {googleProvider && googleProvider.status === 'available' && (
            <Button 
              type="default" 
              block 
              size="large"
              icon={<GoogleOutlined />}
              onClick={() => handleOAuthLogin('google')}
              style={{ 
                height: 44,
                fontSize: 16,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              使用 Google 登录
            </Button>
          )}

          {/* Google 网络不可用时的提示 */}
          {googleProvider && googleProvider.status === 'unavailable' && (
            <Alert
              message="Google 登录暂时不可用"
              description="网络连接问题，Google 登录功能暂时不可用。请稍后再试或使用其他登录方式。"
              type="warning"
              showIcon
              style={{ marginBottom: 12 }}
            />
          )}
        </div>
      )}

      {/* 只在有OAuth提供商或邮箱登录可用时显示分割线 */}
      {((!oauthLoading && oauthProviders.length > 0) || emailEnabled) && (
        <Divider>或</Divider>
      )}
      
      {/* 传统登录表单 */}
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="username" label="用户名" rules={[{ required: true, message: "请输入用户名" }]}>
          <Input autoComplete="username" size="large" />
        </Form.Item>
        <Form.Item name="password" label="密码" rules={[{ required: true, message: "请输入密码" }]}>
          <Input.Password autoComplete="current-password" size="large" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block size="large">
            登录
          </Button>
        </Form.Item>
      </Form>
      
      {emailEnabled && (
        <div style={{ margin: "16px 0", textAlign: "center" }}>
          <Button type="link" onClick={handleForgotPassword}>
            忘记密码？
          </Button>
        </div>
      )}
      
      <div style={{ margin: "16px 0", textAlign: "center" }}>
        没有账号？<a href="/register">注册</a>
      </div>
    </div>
  );
};

export default Login; 