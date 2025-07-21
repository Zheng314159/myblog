import React, { useState, useEffect } from "react";
import { Form, Input, Button, Typography, App, Card, Alert } from "antd";
import { useNavigate, useSearchParams } from "react-router-dom";

const { Title } = Typography;

const ResetPassword: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { message } = App.useApp();

  // 从URL参数获取token
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setError('无效的重置链接，缺少token参数');
    }
  }, [token]);

  const onFinish = async (values: any) => {
    if (!token) {
      message.error('无效的重置链接');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          new_password: values.new_password,
        }),
      });

      if (response.ok) {
        setSuccess(true);
        message.success('密码重置成功！');
      } else {
        const errorData = await response.json();
        setError(errorData.message || '密码重置失败');
        message.error(errorData.message || '密码重置失败');
      }
    } catch (error) {
      setError('网络错误，请稍后重试');
      message.error('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
        <Card>
          <Title level={3}>密码重置成功</Title>
          <Alert
            message="密码重置成功"
            description="您的密码已经成功重置，请使用新密码登录。"
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Button type="primary" onClick={() => navigate("/login")} block>
            前往登录
          </Button>
        </Card>
      </div>
    );
  }

  if (error && !token) {
    return (
      <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
        <Card>
          <Title level={3}>重置链接无效</Title>
          <Alert
            message="重置链接无效"
            description="您访问的重置链接无效或已过期，请重新申请密码重置。"
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Button type="primary" onClick={() => navigate("/forgot-password")} block>
            重新申请重置
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
      <Title level={3}>重置密码</Title>
      <Card>
        <Alert
          message="重置密码"
          description="请输入您的新密码，密码长度至少为6位。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        {error && (
          <Alert
            message="重置失败"
            description={error}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item 
            name="new_password" 
            label="新密码" 
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度至少为6位' }
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>
          
          <Form.Item 
            name="confirm_password" 
            label="确认新密码" 
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              重置密码
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

export default ResetPassword; 