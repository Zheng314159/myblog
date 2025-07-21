import React, { useState, useEffect } from 'react';
import {
  Layout,
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  List,
  Avatar,
  Typography,
  Space,
  Button,
  Modal,
  message,
  Divider,
  Tag,
} from 'antd';
import {
  HeartOutlined,
  TrophyOutlined,
  UserOutlined,
  DollarOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import DonationForm from '../../components/Donation/DonationForm';
import {
  getDonationGoals,
  getPublicDonationStats,
  getDonationConfig,
  DonationGoal,
  DonationConfig,
} from '../../api/donation';
import confetti from 'canvas-confetti';

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

const DonationPage: React.FC = () => {
  const [goals, setGoals] = useState<DonationGoal[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [config, setConfig] = useState<DonationConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDonationModal, setShowDonationModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    // 只要有目标完成就庆祝
    if (goals.some(g => g.is_completed && !g._celebrated)) {
      confetti();
      setGoals(goals.map(g => g.is_completed ? { ...g, _celebrated: true } : g));
    }
  }, [goals]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [goalsResponse, statsResponse, configResponse] = await Promise.all([
        getDonationGoals(true),
        getPublicDonationStats(),
        getDonationConfig(),
      ]);
      
      setGoals(goalsResponse.data);
      setStats(statsResponse.data);
      setConfig(configResponse.data);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDonationSuccess = (donation: any) => {
    setShowDonationModal(false);
    if (donation.payment_status === 'SUCCESS') {
      message.success('感谢您的捐赠！');
    }
    loadData();
  };

  const getPaymentMethodColor = (method: string) => {
    const colors = {
      ALIPAY: 'blue',
      WECHAT: 'green',
      PAYPAL: 'orange',
      BANK_TRANSFER: 'purple',
      CRYPTO: 'red',
    };
    return colors[method as keyof typeof colors] || 'default';
  };

  const getPaymentMethodLabel = (method: string) => {
    const labels = {
      ALIPAY: '支付宝',
      WECHAT: '微信支付',
      PAYPAL: 'PayPal',
      BANK_TRANSFER: '银行转账',
      CRYPTO: '加密货币',
    };
    return labels[method as keyof typeof labels] || method;
  };

  const getStatusColor = (status: string) => {
    const colors = {
      PENDING: 'orange',
      SUCCESS: 'green',
      FAILED: 'red',
      CANCELLED: 'gray',
    };
    return colors[status as keyof typeof colors] || 'default';
  };

  const getStatusLabel = (status: string) => {
    const labels = {
      PENDING: '待处理',
      SUCCESS: '成功',
      FAILED: '失败',
      CANCELLED: '已取消',
    };
    return labels[status as keyof typeof labels] || status;
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Content style={{ padding: '24px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          {/* 页面标题 */}
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <HeartOutlined style={{ fontSize: '64px', color: '#ff4d4f' }} />
            <Title level={1}>支持我们</Title>
            <Paragraph style={{ fontSize: '16px', color: '#666' }}>
              您的每一份支持都是我们继续前进的动力
            </Paragraph>
          </div>

          <Row gutter={[24, 24]}>
            {/* 立即捐赠表单 */}
            <Col xs={24}>
              <Card>
                <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                  <Title level={3}>立即捐赠</Title>
                  <Text type="secondary">选择金额和支付方式，支持我们继续创作</Text>
                </div>
                <Button
                  type="primary"
                  size="large"
                  icon={<HeartOutlined />}
                  onClick={() => setShowDonationModal(true)}
                  style={{ width: '100%', height: '60px', fontSize: '18px' }}
                >
                  开始捐赠
                </Button>
              </Card>
            </Col>
            {/* 捐赠目标 */}
            {goals.length > 0 && (
              <Col xs={24}>
                <Card title="捐赠目标" style={{ marginTop: '24px' }}>
                  <List
                    dataSource={goals}
                    renderItem={(goal) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={<TrophyOutlined style={{ fontSize: '24px', color: '#faad14' }} />}
                          title={goal.title}
                          description={goal.description}
                        />
                        <div style={{ textAlign: 'right', minWidth: '200px' }}>
                          <div>
                            <Text strong>¥{goal.current_amount}</Text>
                            <Text type="secondary"> / ¥{goal.target_amount}</Text>
                          </div>
                          <Progress
                            percent={goal.progress_percentage}
                            size="small"
                            status={goal.is_completed ? 'success' : 'active'}
                            strokeColor={goal.is_completed ? '#52c41a' : undefined}
                          />
                          <div style={{ marginTop: '8px' }}>
                            <Tag color={goal.is_completed ? 'green' : 'blue'}>
                              {goal.is_completed ? '已完成' : '进行中'}
                            </Tag>
                          </div>
                        </div>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
            )}
            {/* 捐赠统计 */}
            {config?.is_enabled && (
              <Col xs={24}>
                <Card title="捐赠统计">
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Statistic
                        title="总捐赠次数"
                        value={stats?.total_donations || 0}
                        prefix={<UserOutlined />}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="总捐赠金额"
                        value={stats?.total_amount || 0}
                        prefix={<DollarOutlined />}
                        suffix="元"
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="活跃目标"
                        value={stats?.active_goals || 0}
                        prefix={<TrophyOutlined />}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="货币单位"
                        value={stats?.currency || 'CNY'}
                        prefix={<DollarOutlined />}
                      />
                    </Col>
                  </Row>
                </Card>
              </Col>
            )}
            {/* 捐赠说明 */}
            <Col xs={24}>
              <Card title="捐赠说明">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>支持方式：</Text>
                    <br />
                    <Text type="secondary">
                      我们支持支付宝、微信支付、PayPal等多种支付方式，您可以选择最适合的方式进行捐赠。
                    </Text>
                  </div>
                  <Divider />
                  <div>
                    <Text strong>捐赠用途：</Text>
                    <br />
                    <Text type="secondary">
                      您的捐赠将用于服务器维护、功能开发、内容创作等方面，帮助我们提供更好的服务。
                    </Text>
                  </div>
                  <Divider />
                  <div>
                    <Text strong>隐私保护：</Text>
                    <br />
                    <Text type="secondary">
                      我们承诺保护您的隐私，捐赠信息仅用于内部统计，不会泄露给第三方。
                    </Text>
                  </div>
                </Space>
              </Card>
            </Col>
            {/* 联系我们 */}
            <Col xs={24}>
              <Card title="联系我们">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>邮箱：</Text>
                    <Text type="secondary">support@example.com</Text>
                  </div>
                  <div>
                    <Text strong>微信：</Text>
                    <Text type="secondary">donation_support</Text>
                  </div>
                  <div>
                    <Text strong>QQ群：</Text>
                    <Text type="secondary">123456789</Text>
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </div>

        {/* 捐赠表单模态框 */}
        <Modal
          title="捐赠"
          open={showDonationModal}
          onCancel={() => setShowDonationModal(false)}
          footer={null}
          width={600}
          destroyOnHidden
        >
          <DonationForm
            onSuccess={handleDonationSuccess}
            onCancel={() => setShowDonationModal(false)}
          />
        </Modal>
      </Content>
    </Layout>
  );
};

export default DonationPage; 