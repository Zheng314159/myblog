import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { App, Spin, Result } from "antd";
import { useDispatch } from "react-redux";
import { loginSuccess } from "../../features/user/userSlice";
import { getMe } from "../../api/auth";
import { TokenManager } from "../../utils/tokenManager";

const OAuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { message } = App.useApp();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // 从URL参数中获取token
        const access_token = searchParams.get('access_token');
        const refresh_token = searchParams.get('refresh_token');
        const token_type = searchParams.get('token_type') || 'bearer';
        const error = searchParams.get('error');

        if (error) {
          setErrorMessage(`OAuth登录失败: ${error}`);
          setStatus('error');
          return;
        }

        if (!access_token || !refresh_token) {
          setErrorMessage('未获取到有效的访问令牌');
          setStatus('error');
          return;
        }

        // 存储token
        TokenManager.storeTokens({
          access_token,
          refresh_token,
          token_type
        });

        // 获取用户信息
        const userInfoResp = await getMe();
        const userInfo = userInfoResp.data;

        // 更新Redux状态
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

        message.success('OAuth登录成功！');
        navigate('/');

      } catch (error: any) {
        console.error("OAuth回调处理失败:", error);
        const msg = error?.response?.data?.message || error.message || "OAuth登录失败";
        setErrorMessage(msg);
        setStatus('error');
      }
    };

    handleOAuthCallback();
  }, [searchParams, navigate, dispatch, message]);

  if (status === 'loading') {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column'
      }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>正在处理OAuth登录...</div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Result
          status="error"
          title="OAuth登录失败"
          subTitle={errorMessage}
          extra={[
            <button 
              key="retry" 
              onClick={() => navigate('/login')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#1890ff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              返回登录页
            </button>
          ]}
        />
      </div>
    );
  }

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh' 
    }}>
      <Result
        status="success"
        title="OAuth登录成功"
        subTitle="正在跳转到首页..."
      />
    </div>
  );
};

export default OAuthCallback; 