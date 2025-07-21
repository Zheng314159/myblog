import React, { useState, useEffect, useRef } from 'react';
import {
  Form,
  Input,
  Button,
  Radio,
  Checkbox,
  InputNumber,
  message,
  Card,
  Space,
  Divider,
  Typography,
  Row,
  Col,
  App,
  Select,
} from 'antd';
import { HeartOutlined, UserOutlined, MessageOutlined } from '@ant-design/icons';
import { createDonation, getDonationConfig, DonationConfig, getDonationGoals, getPaymentMethods, DonationGoal } from '../../api/donation';
import { useSelector } from 'react-redux';
import { RootState } from '../../app/store';
import PaymentDetailModal from './PaymentDetailModal';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface DonationFormProps {
  onSuccess?: (donation: any) => void;
  onCancel?: () => void;
}

const DonationForm: React.FC<DonationFormProps> = ({ onSuccess, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState<DonationConfig | null>(null);
  const [customAmount, setCustomAmount] = useState<number | null>(null);
  const [paymentModalVisible, setPaymentModalVisible] = useState(false);
  const [paymentInfo, setPaymentInfo] = useState<any>(null);
  const [donationInfo, setDonationInfo] = useState<any>(null);
  const [alipayFormHtml, setAlipayFormHtml] = useState<string | null>(null);
  const [goals, setGoals] = useState<DonationGoal[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<number | null>(null);
  const [methods, setMethods] = useState<{type: string, name: string}[]>([]);
  const [paymentMethod, setPaymentMethod] = useState<string | undefined>(undefined);
  
  const user = useSelector((state: RootState) => state.user.userInfo);
  const { message } = App.useApp();

  const alipayFormContainerRef = useRef<HTMLDivElement>(null);

  const paymentTypeMap: Record<string, string> = {
    alipay: 'ALIPAY',
    wechatpayv3: 'WECHAT',
    paypal: 'PAYPAL',
  };

  useEffect(() => {
    loadConfig();
    getDonationGoals(true).then(res => {
      setGoals(res.data);
      if (res.data.length > 0) setSelectedGoal(res.data[0].id);
    });
    getPaymentMethods().then(res => {
      const methods = res.data?.methods || [];
      setMethods(methods);
      if (methods.length > 0) {
        setPaymentMethod(methods[0].type);
      }
    });
  }, []);

  useEffect(() => {
    if (alipayFormHtml && alipayFormContainerRef.current) {
      // 提交表单
      const form = alipayFormContainerRef.current.querySelector('form#alipaysubmit') as HTMLFormElement;
      if (form) {
        form.submit();
      }
    }
  }, [alipayFormHtml]);

  const loadConfig = async () => {
    try {
      const response = await getDonationConfig();
      setConfig(response.data);
      
      // 如果有用户信息，自动填充姓名
      if (user) {
        form.setFieldsValue({
          donor_name: user.username,
          donor_email: user.email,
        });
      }
    } catch (error) {
      message.error('加载捐赠配置失败');
    }
  };

  const handleSubmit = async (values: any) => {
    if (!config?.is_enabled) {
      message.error('捐赠功能未启用');
      return;
    }
    if (!values.payment_method && config.alipay_enabled) {
      values.payment_method = 'ALIPAY';
    }
    setLoading(true);
    try {
      const response = await createDonation({
        ...values,
        amount: values.amount || customAmount || 0,
        currency: 'CNY',
      });
      // 如果是支付宝网页支付，直接渲染 form 跳转，关闭外层 Modal
      if (response.data.alipay_form_html) {
        setAlipayFormHtml(response.data.alipay_form_html);
        onSuccess?.(response.data); // 关闭外层 Modal
        setPaymentInfo(null);
        setDonationInfo(null);
        setPaymentModalVisible(false);
        message.success('正在跳转支付宝支付...');
        form.resetFields();
        setCustomAmount(null);
        return;
      }
      // 其它方式弹出支付详情弹窗
      setPaymentInfo(response.data);
      setDonationInfo({
        amount: values.amount || customAmount || 0,
        order_no: response.data.id,
        payment_method: values.payment_method,
      });
      setPaymentModalVisible(true);
      message.success('捐赠记录创建成功，请完成支付！');
      form.resetFields();
      setCustomAmount(null);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建捐赠记录失败');
    } finally {
      setLoading(false);
    }
  };

  const presetAmounts = config?.preset_amounts 
    ? JSON.parse(config.preset_amounts) 
    : [5, 10, 20, 50, 100];

  const getPaymentMethodLabel = (method: string) => {
    const labels = {
      ALIPAY: '支付宝',
      WECHAT: '微信支付',
      PAYPAL: 'PayPal',
    };
    return labels[method as keyof typeof labels] || method;
  };

  const getDonationTypeLabel = (type: string) => {
    const labels = {
      ONE_TIME: '一次性捐赠',
      MONTHLY: '月度捐赠',
      YEARLY: '年度捐赠',
    };
    return labels[type as keyof typeof labels] || type;
  };

  if (!config) {
    return <div>加载中...</div>;
  }

  if (!config.is_enabled) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '10px 0 40px 0' }}>
          <Title level={3} style={{ marginBottom: 32 }}>感谢您对我们的支持与理解</Title>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 64, alignItems: 'center' }}>
            <img src="pay1.png" alt="二维码1" style={{ width: 180, height: 180 }} />
            <img src="pay2.png" alt="二维码2" style={{ width: 180, height: 180 }} />
          </div>
        </div>
      </Card>
    );
  }

  if (alipayFormHtml) {
    // 去除 <script>，只渲染 form
    const htmlWithoutScript = alipayFormHtml.replace(/<script[\s\S]*?<\/script>/gi, '');
    return (
      <div ref={alipayFormContainerRef} dangerouslySetInnerHTML={{ __html: htmlWithoutScript }} />
    );
  }

  return (
    <Card>
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <HeartOutlined style={{ fontSize: '48px', color: '#ff4d4f' }} />
        <Title level={2}>{config.title}</Title>
        <Text type="secondary">{config.description}</Text>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          payment_method: config.alipay_enabled ? 'ALIPAY' : undefined,
        }}
      >
        {/* 捐赠者信息 */}
        <Form.Item
          label="捐赠者姓名"
          name="donor_name"
          rules={[{ required: true, message: '请输入捐赠者姓名' }]}
        >
          <Input 
            prefix={<UserOutlined />} 
            placeholder="请输入您的姓名"
            maxLength={50}
          />
        </Form.Item>

        <Form.Item
          label="邮箱地址"
          name="donor_email"
          rules={[
            { type: 'email', message: '请输入有效的邮箱地址' }
          ]}
        >
          <Input placeholder="可选，用于接收感谢邮件" />
        </Form.Item>

        <Form.Item
          label="留言"
          name="donor_message"
        >
          <TextArea
            prefix={<MessageOutlined />}
            placeholder="可选，留下您想说的话..."
            rows={3}
            maxLength={200}
            showCount
          />
        </Form.Item>

        <Form.Item name="is_anonymous" valuePropName="checked">
          <Checkbox>匿名捐赠</Checkbox>
        </Form.Item>

        <Divider />

        {/* 捐赠金额 */}
        <Form.Item label="捐赠金额">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Row gutter={[8, 8]}>
              {presetAmounts.map((amount: number) => (
                <Col key={amount}>
                  <Button
                    type={customAmount === amount ? 'primary' : 'default'}
                    onClick={() => {
                      setCustomAmount(amount);
                      form.setFieldsValue({ amount: amount });
                    }}
                  >
                    ¥{amount}
                  </Button>
                </Col>
              ))}
            </Row>
            {/* 目标选择下拉框 */}
            {goals.length > 0 && (
              <Form.Item label="捐赠目标" name="goal_id" rules={[{ required: true, message: '请选择捐赠目标' }]} initialValue={goals[0]?.id?.toString()}>
                <Select style={{ width: '100%' }}>
                  {goals.map(goal => (
                    <Select.Option value={goal.id.toString()} key={goal.id.toString()}>{goal.title}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            )}
            <Form.Item name="amount" noStyle>
              <InputNumber
                placeholder="或输入自定义金额"
                min={0.01}
                max={99999}
                precision={2}
                style={{ width: '100%' }}
                onChange={(value) => setCustomAmount(value)}
                addonBefore="¥"
              />
            </Form.Item>
          </Space>
        </Form.Item>

        <Divider />

        {/* 支付方式 */}
        <Form.Item
          label="支付方式"
          name="payment_method"
          rules={[{ required: true, message: '请选择支付方式' }]}
        >
          <Radio.Group
            value={paymentMethod}
            onChange={e => setPaymentMethod(e.target.value)}
          >
            {methods.map(m => (
              <Radio key={m.type} value={paymentTypeMap[m.type] || m.type}>{m.name}</Radio>
            ))}
          </Radio.Group>
        </Form.Item>

        <Divider />

        {/* 提交按钮 */}
        <Form.Item>
          <Space style={{ width: '100%', justifyContent: 'center' }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              size="large"
              icon={<HeartOutlined />}
            >
              确认捐赠
            </Button>
            {onCancel && (
              <Button size="large" onClick={onCancel}>
                取消
              </Button>
            )}
          </Space>
        </Form.Item>
      </Form>

      <PaymentDetailModal
        open={paymentModalVisible}
        onClose={() => {
          setPaymentModalVisible(false);
          if (paymentInfo) {
            onSuccess?.(paymentInfo);
          }
        }}
        paymentInfo={paymentInfo || {}}
        donationInfo={donationInfo || {}}
      />
    </Card>
  );
};

export default DonationForm; 