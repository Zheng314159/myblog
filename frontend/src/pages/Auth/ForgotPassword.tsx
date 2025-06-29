import React, { useState } from "react";
import { Form, Input, Button, Typography, App, Card, Alert } from "antd";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;

const ForgotPassword: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const navigate = useNavigate();
  const { message } = App.useApp();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // 这里应该调用发送密码重置邮件的API
      const response = await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: values.email }),
      });

      if (response.ok) {
        setEmailSent(true);
        message.success('密码重置邮件已发送到您的邮箱');
      } else {
        const error = await response.json();
        message.error(error.message || '发送失败');
      }
    } catch (error) {
      message.error('发送失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
        <Card>
          <Title level={3}>邮件已发送</Title>
          <Alert
            message="密码重置邮件已发送"
            description="请检查您的邮箱，点击邮件中的链接重置密码。如果未收到邮件，请检查垃圾邮件文件夹。"
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Button type="primary" onClick={() => navigate("/login")} block>
            返回登录
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
      <Title level={3}>找回密码</Title>
      <Card>
        <Alert
          message="密码重置"
          description="请输入您的邮箱地址，我们将向您发送密码重置链接。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item 
            name="email" 
            label="邮箱地址" 
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入您的邮箱地址" />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              发送重置邮件
            </Button>
          </Form.Item>
        </Form>
        
        <div style={{ margin: "16px 0", textAlign: "center" }}>
          <Button type="link" onClick={() => navigate("/login")}>
            返回登录
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default ForgotPassword; 