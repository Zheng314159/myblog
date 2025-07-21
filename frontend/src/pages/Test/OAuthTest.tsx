import React from "react";
import { Button, Card, Typography, Space } from "antd";
import { GithubOutlined, GoogleOutlined } from "@ant-design/icons";

const { Title, Text } = Typography;

const OAuthTest: React.FC = () => {
  const handleOAuthLogin = (provider: 'github' | 'google') => {
    console.log(`点击了 ${provider} 登录按钮`);
    const url = `/api/v1/oauth/${provider}/login`;
    console.log(`跳转到: ${url}`);
    window.location.href = url;
  };

  const testDirectUrl = (provider: 'github' | 'google') => {
    const url = `http://localhost:8000/api/v1/oauth/${provider}/login`;
    console.log(`直接访问后端: ${url}`);
    window.open(url, '_blank');
  };

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Title level={2}>OAuth 登录测试</Title>
      
      <Card title="前端代理测试" style={{ marginBottom: 16 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong>测试前端代理到后端:</Text>
            <br />
            <Button 
              type="primary" 
              icon={<GithubOutlined />}
              onClick={() => handleOAuthLogin('github')}
              style={{ marginRight: 8 }}
            >
              GitHub 登录 (前端代理)
            </Button>
            <Button 
              type="primary" 
              icon={<GoogleOutlined />}
              onClick={() => handleOAuthLogin('google')}
            >
              Google 登录 (前端代理)
            </Button>
          </div>
        </Space>
      </Card>

      <Card title="直接后端测试" style={{ marginBottom: 16 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong>直接访问后端 (新窗口):</Text>
            <br />
            <Button 
              type="default" 
              icon={<GithubOutlined />}
              onClick={() => testDirectUrl('github')}
              style={{ marginRight: 8 }}
            >
              GitHub 登录 (直接后端)
            </Button>
            <Button 
              type="default" 
              icon={<GoogleOutlined />}
              onClick={() => testDirectUrl('google')}
            >
              Google 登录 (直接后端)
            </Button>
          </div>
        </Space>
      </Card>

      <Card title="调试信息">
        <div>
          <Text strong>当前页面URL:</Text> {window.location.href}
          <br />
          <Text strong>前端服务器:</Text> http://localhost:3000
          <br />
          <Text strong>后端服务器:</Text> http://localhost:8000
          <br />
          <Text strong>代理配置:</Text> /api → http://localhost:8000
        </div>
      </Card>
    </div>
  );
};

export default OAuthTest; 