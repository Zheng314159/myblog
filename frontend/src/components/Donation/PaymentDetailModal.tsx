import React, { useEffect, useRef } from 'react';
import { Modal, Button, Typography, Space, Divider } from 'antd';

const { Text, Title } = Typography;

export interface PaymentDetailModalProps {
  open: boolean;
  onClose: () => void;
  paymentInfo: any; // 后端返回的所有支付字段
  donationInfo?: {
    amount?: number;
    order_no?: string;
    payment_method?: string;
  };
}

const getPaymentMethodLabel = (method: string) => {
  const labels: Record<string, string> = {
    ALIPAY: '支付宝',
    WECHAT: '微信支付',
    PAYPAL: 'PayPal',
  };
  return labels[method] || method;
};

const PaymentDetailModal: React.FC<PaymentDetailModalProps> = ({
  open,
  onClose,
  paymentInfo,
  donationInfo = {},
}) => {
  const { amount, order_no, payment_method } = donationInfo;
  const hasJumpedRef = useRef(false);

  // 自动跳转逻辑
  useEffect(() => {
    if (!open) {
      hasJumpedRef.current = false;
      return;
    }
    // 只在首次弹窗时自动跳转
    if (hasJumpedRef.current) return;
    if (payment_method === 'ALIPAY' && paymentInfo.alipay_form_html) {
      // form 已自动提交，无需 window.open
      hasJumpedRef.current = true;
      return;
    }
    if (payment_method === 'PAYPAL' && paymentInfo.paypal_url) {
      window.open(paymentInfo.paypal_url, '_blank');
      hasJumpedRef.current = true;
      return;
    }
    if (payment_method === 'WECHAT' && paymentInfo.wechat_url) {
      window.open(paymentInfo.wechat_url, '_blank');
      hasJumpedRef.current = true;
      return;
    }
  }, [open, payment_method, paymentInfo]);

  // 动态渲染支付内容
  const renderPaymentContent = () => {
    if (payment_method === 'ALIPAY') {
      if (paymentInfo.alipay_form_html) {
        // 网页支付自动提交表单
        return (
          <div dangerouslySetInnerHTML={{ __html: paymentInfo.alipay_form_html }} />
        );
      }
      return (
        <>
          {paymentInfo.alipay_qr && (
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <img src={paymentInfo.alipay_qr} alt="支付宝二维码" style={{ width: 180, height: 180 }} />
              <div>请使用支付宝扫码支付</div>
            </div>
          )}
          {paymentInfo.alipay_url && (
            <div style={{ textAlign: 'center', marginBottom: 8 }}>
              <Button type="primary" href={paymentInfo.alipay_url} target="_blank" rel="noopener noreferrer" block>
                跳转支付宝支付
              </Button>
            </div>
          )}
        </>
      );
    }
    if (payment_method === 'WECHAT') {
      return (
        <>
          {paymentInfo.wechat_qr && (
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <img src={paymentInfo.wechat_qr} alt="微信支付二维码" style={{ width: 180, height: 180 }} />
              <div>请使用微信扫码支付</div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
                订单号: {donationInfo.order_no}
              </div>
            </div>
          )}
          {paymentInfo.wechat_error && (
            <div style={{ textAlign: 'center', color: '#ff4d4f' }}>
              微信支付生成失败: {paymentInfo.wechat_error}
            </div>
          )}
        </>
      );
    }
    if (payment_method === 'PAYPAL') {
      return (
        <>
          {paymentInfo.paypal_qr && (
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <img src={paymentInfo.paypal_qr} alt="PayPal二维码" style={{ width: 180, height: 180 }} />
              <div>请使用 PayPal 扫码支付</div>
            </div>
          )}
          {paymentInfo.paypal_url && (
            <div style={{ textAlign: 'center', marginBottom: 8 }}>
              <Button type="primary" href={paymentInfo.paypal_url} target="_blank" rel="noopener noreferrer" block>
                跳转 PayPal 支付
              </Button>
            </div>
          )}
        </>
      );
    }
    return <Text type="secondary">请根据页面提示完成支付</Text>;
  };

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={null}
      centered
      title={<Title level={4} style={{ margin: 0 }}>支付详情</Title>}
      destroyOnHidden
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div style={{ textAlign: 'center' }}>
          <Text strong>支付方式：</Text>
          <Text>{getPaymentMethodLabel(payment_method || '')}</Text>
        </div>
        <div style={{ textAlign: 'center' }}>
          <Text strong>捐赠金额：</Text>
          <Text type="danger" style={{ fontSize: 18 }}>{amount} 元</Text>
        </div>
        {order_no && (
          <div style={{ textAlign: 'center' }}>
            <Text strong>订单号：</Text>
            <Text>{order_no}</Text>
          </div>
        )}
        <Divider style={{ margin: '8px 0' }} />
        {renderPaymentContent()}
        <Divider style={{ margin: '8px 0' }} />
        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">支付完成后请点击下方按钮</Text>
        </div>
        <Button type="primary" block onClick={onClose}>
          我已完成支付
        </Button>
      </Space>
    </Modal>
  );
};

export default PaymentDetailModal; 