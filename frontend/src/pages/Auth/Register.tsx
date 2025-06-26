import React, { useState } from "react";
import { Form, Input, Button, message, Typography } from "antd";
import { register } from "../../api/auth";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await register(values);
      message.success("注册成功，请登录").then(() => {
        navigate("/login");
      });
    } catch (e: any) {
      const msg = e?.response?.data?.message || e.message || "注册失败";
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: 32 }}>
      <Title level={3}>注册</Title>
      <Form onFinish={onFinish} layout="vertical">
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
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            注册
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