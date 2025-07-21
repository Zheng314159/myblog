import React, { useState, useEffect } from "react";
import { Form, Input, Button, Typography, App, Steps, Card, Alert, Divider } from "antd";
import { GithubOutlined, GoogleOutlined } from "@ant-design/icons";
import { register, getMe } from "../../api/auth";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { loginSuccess } from "../../features/user/userSlice";
import { TokenManager } from "../../utils/tokenManager";

const { Title } = Typography;

interface OAuthProvider {
  name: string;
  display_name: string;
  login_url: string;
  status: 'available' | 'unavailable';
  message: string;
}

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [verificationCode, setVerificationCode] = useState("");
  const [oauthProviders, setOauthProviders] = useState<OAuthProvider[]>([]);
  const [oauthLoading, setOauthLoading] = useState(true);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const dispatch = useDispatch();
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
    setLoading(true);
    try {
      // 如果邮箱验证开启，需要验证码
      if (emailEnabled && currentStep === 0) {
        // 发送验证码到邮箱
        const response = await fetch('/api/v1/auth/send-verification-code', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: values.email }),
        });

        if (response.ok) {
          message.success("验证码已发送到您的邮箱，请查收");
          setCurrentStep(1);
        } else {
          const error = await response.json();
          message.error(error.detail || '发送验证码失败');
        }
        setLoading(false);
        return;
      }

      // 如果邮箱验证关闭，或者已经验证完成，直接注册
      const registerData = emailEnabled ? { ...values, verification_code: verificationCode } : values;
      const registerResponse = await register(registerData);
      
      // 注册成功后，获取用户信息并直接登录
      if (registerResponse.data) {
        const userResponse = await getMe();
        const userInfo = userResponse.data;
        
        // 更新Redux状态
        dispatch(loginSuccess({
          accessToken: registerResponse.data.access_token,
          refreshToken: registerResponse.data.refresh_token,
          userInfo: {
            id: userInfo.id,
            username: userInfo.username,
            email: userInfo.email,
            role: userInfo.role,
          },
        }));
        
        // 启动token检查
        TokenManager.startTokenCheck();
        
        message.success("注册成功，已自动登录");
        navigate("/"); // 跳转到首页
      }
    } catch (e: any) {
      const msg = e?.response?.data?.message || e.message || "注册失败";
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSendVerificationCode = async () => {
    try {
      const email = form.getFieldValue('email');
      if (!email) {
        message.error('请先输入邮箱地址');
        return;
      }
      
      // 调用发送验证码的API
      const response = await fetch('/api/v1/auth/send-verification-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        message.success('验证码已发送到您的邮箱');
      } else {
        const error = await response.json();
        message.error(error.detail || '发送验证码失败');
      }
    } catch (error) {
      message.error('发送验证码失败');
    }
  };

  const handleOAuthLogin = (provider: 'github' | 'google') => {
    window.location.href = `/api/v1/oauth/${provider}/login`;
  };

  const getOAuthProvider = (name: string) => {
    return oauthProviders.find(p => p.name === name);
  };

  const githubProvider = getOAuthProvider('github');
  const googleProvider = getOAuthProvider('google');

  const steps = [
    {
      title: '填写信息',
      description: '填写注册信息',
    },
    {
      title: '邮箱验证',
      description: '验证邮箱',
    },
  ];

  return (
    <div style={{ maxWidth: 500, margin: "0 auto", padding: 32 }}>
      <Title level={3}>注册</Title>
      
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

      {/* 只在有OAuth提供商或邮箱注册可用时显示分割线 */}
      {((!oauthLoading && oauthProviders.length > 0) || emailEnabled) && (
        <Divider>或</Divider>
      )}
      
      {emailEnabled && (
        <Card style={{ marginBottom: 24 }}>
          <Alert
            message="邮箱验证已开启"
            description="注册需要验证邮箱，我们将向您的邮箱发送验证码"
            type="info"
            showIcon
          />
        </Card>
      )}

      {emailEnabled && (
        <Steps current={currentStep} items={steps} style={{ marginBottom: 24 }} />
      )}

      <Form form={form} onFinish={onFinish} layout="vertical">
        <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="email" label="邮箱" rules={[{ required: true, type: "email" }]}>
          <Input />
        </Form.Item>
        <Form.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}>
          <Input.Password />
        </Form.Item>
        <Form.Item name="full_name" label="昵称">
          <Input />
        </Form.Item>

        {emailEnabled && currentStep === 1 && (
          <Form.Item label="验证码" required>
            <div style={{ display: 'flex', gap: 8 }}>
              <Input
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="请输入验证码"
                style={{ flex: 1 }}
              />
              <Button onClick={handleSendVerificationCode}>
                重新发送
              </Button>
            </div>
          </Form.Item>
        )}

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            {emailEnabled && currentStep === 0 ? '下一步' : '注册'}
          </Button>
        </Form.Item>
      </Form>
      
      <div style={{ margin: "16px 0" }}>
        已有账号？<a href="/login">登录</a>
      </div>
    </div>
  );
};

export default Register;