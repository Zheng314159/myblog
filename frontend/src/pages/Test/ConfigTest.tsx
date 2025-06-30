import React, { useState, useEffect } from "react";
import { Button, Card, Typography, Space, message, Divider } from "antd";
import { ReloadOutlined, SettingOutlined, CheckCircleOutlined } from "@ant-design/icons";

const { Title, Text } = Typography;

interface ConfigData {
  app_name?: string;
  email_enabled?: boolean;
  oauth_enabled?: boolean;
  github_oauth_enabled?: boolean;
  google_oauth_enabled?: boolean;
  frontend_url?: string;
  debug?: boolean;
}

const ConfigTest: React.FC = () => {
  const [config, setConfig] = useState<ConfigData>({});
  const [loading, setLoading] = useState(false);
  const [reloadLoading, setReloadLoading] = useState(false);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/config/');
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
        message.success('配置获取成功');
      } else {
        message.error('配置获取失败');
      }
    } catch (error) {
      message.error('配置获取失败: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const reloadConfig = async () => {
    setReloadLoading(true);
    try {
      const response = await fetch('/api/v1/config/reload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        message.success('配置重新加载成功: ' + data.message);
        // 重新获取配置
        await fetchConfig();
      } else {
        message.error('配置重新加载失败');
      }
    } catch (error) {
      message.error('配置重新加载失败: ' + error);
    } finally {
      setReloadLoading(false);
    }
  };

  const testAuthConfig = async () => {
    try {
      const response = await fetch('/api/v1/config/auth');
      if (response.ok) {
        const data = await response.json();
        message.success('认证配置: ' + JSON.stringify(data));
      } else {
        message.error('认证配置获取失败');
      }
    } catch (error) {
      message.error('认证配置获取失败: ' + error);
    }
  };

  const testOAuthConfig = async () => {
    try {
      const response = await fetch('/api/v1/config/oauth');
      if (response.ok) {
        const data = await response.json();
        message.success('OAuth配置: ' + JSON.stringify(data));
      } else {
        message.error('OAuth配置获取失败');
      }
    } catch (error) {
      message.error('OAuth配置获取失败: ' + error);
    }
  };

  const testConfigHealth = async () => {
    try {
      const response = await fetch('/api/v1/config/health');
      if (response.ok) {
        const data = await response.json();
        message.success('配置健康检查: ' + JSON.stringify(data));
      } else {
        message.error('配置健康检查失败');
      }
    } catch (error) {
      message.error('配置健康检查失败: ' + error);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Title level={2}>
        <SettingOutlined /> 配置管理测试
      </Title>
      
      <Card title="配置操作" style={{ marginBottom: 16 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Button 
              type="primary" 
              icon={<ReloadOutlined />}
              onClick={fetchConfig}
              loading={loading}
              style={{ marginRight: 8 }}
            >
              获取配置
            </Button>
            <Button 
              type="default" 
              icon={<ReloadOutlined />}
              onClick={reloadConfig}
              loading={reloadLoading}
            >
              重新加载配置
            </Button>
          </div>
          
          <Divider />
          
          <div>
            <Text strong>测试特定配置端点:</Text>
            <br />
            <Button 
              onClick={testAuthConfig}
              style={{ marginRight: 8, marginTop: 8 }}
            >
              测试认证配置
            </Button>
            <Button 
              onClick={testOAuthConfig}
              style={{ marginRight: 8, marginTop: 8 }}
            >
              测试OAuth配置
            </Button>
            <Button 
              onClick={testConfigHealth}
              style={{ marginTop: 8 }}
            >
              配置健康检查
            </Button>
          </div>
        </Space>
      </Card>

      <Card title="当前配置状态">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <Text strong>应用名称:</Text> {config.app_name || 'N/A'}
          </div>
          <div>
            <Text strong>调试模式:</Text> {config.debug ? '启用' : '禁用'}
          </div>
          <div>
            <Text strong>前端URL:</Text> {config.frontend_url || 'N/A'}
          </div>
          <div>
            <Text strong>邮箱功能:</Text> 
            {config.email_enabled ? (
              <span style={{ color: 'green' }}>
                <CheckCircleOutlined /> 启用
              </span>
            ) : (
              <span style={{ color: 'red' }}>禁用</span>
            )}
          </div>
          <div>
            <Text strong>OAuth功能:</Text> 
            {config.oauth_enabled ? (
              <span style={{ color: 'green' }}>
                <CheckCircleOutlined /> 启用
              </span>
            ) : (
              <span style={{ color: 'red' }}>禁用</span>
            )}
          </div>
          <div>
            <Text strong>GitHub OAuth:</Text> 
            {config.github_oauth_enabled ? (
              <span style={{ color: 'green' }}>
                <CheckCircleOutlined /> 启用
              </span>
            ) : (
              <span style={{ color: 'red' }}>禁用</span>
            )}
          </div>
          <div>
            <Text strong>Google OAuth:</Text> 
            {config.google_oauth_enabled ? (
              <span style={{ color: 'green' }}>
                <CheckCircleOutlined /> 启用
              </span>
            ) : (
              <span style={{ color: 'red' }}>禁用</span>
            )}
          </div>
        </Space>
      </Card>

      <Card title="使用说明" style={{ marginTop: 16 }}>
        <div>
          <Text strong>配置热加载说明:</Text>
          <ul>
            <li>修改 <code>.env</code> 文件中的配置</li>
            <li>点击"重新加载配置"按钮</li>
            <li>配置会立即生效，无需重启服务器</li>
            <li>支持所有配置字段的热加载，不仅仅是 EMAIL_ENABLED</li>
          </ul>
          
          <Text strong>API端点:</Text>
          <ul>
            <li><code>GET /api/v1/config/</code> - 获取所有配置</li>
            <li><code>GET /api/v1/config/auth</code> - 获取认证配置</li>
            <li><code>GET /api/v1/config/oauth</code> - 获取OAuth配置</li>
            <li><code>POST /api/v1/config/reload</code> - 重新加载配置</li>
            <li><code>GET /api/v1/config/health</code> - 配置健康检查</li>
          </ul>
        </div>
      </Card>
    </div>
  );
};

export default ConfigTest; 