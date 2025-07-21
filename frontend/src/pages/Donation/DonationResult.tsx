import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, Typography, Button, Result, List, Avatar, Spin, message } from 'antd';
import { getPublicDonationRecords } from '../../api/donation';

const { Title, Paragraph, Text } = Typography;

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const DonationResult: React.FC = () => {
  const query = useQuery();
  const navigate = useNavigate();
  const status = query.get('status') || 'success';
  const amount = query.get('amount');
  const orderNo = query.get('order_no');
  const paymentMethod = query.get('payment_method');
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (status === 'success') {
      setLoading(true);
      getPublicDonationRecords(10)
        .then(res => setRecords(res.data))
        .catch(() => message.error('加载捐赠榜单失败'))
        .finally(() => setLoading(false));
    }
  }, [status]);

  return (
    <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
      <Card style={{ maxWidth: 480, width: '100%' }}>
        <Result
          status={status === 'success' ? 'success' : 'error'}
          title={status === 'success' ? '感谢您的捐赠！' : '支付未完成'}
          subTitle={
            <div>
              {status === 'success' ? (
                <>
                  <Paragraph>您的捐赠已成功，我们非常感谢您的支持！</Paragraph>
                  {amount && (
                    <Paragraph>
                      <Text strong>捐赠金额：</Text>
                      <Text type="danger">{amount} 元</Text>
                    </Paragraph>
                  )}
                  {paymentMethod && (
                    <Paragraph>
                      <Text strong>支付方式：</Text>
                      <Text>{paymentMethod}</Text>
                    </Paragraph>
                  )}
                  {orderNo && (
                    <Paragraph>
                      <Text strong>订单号：</Text>
                      <Text>{orderNo}</Text>
                    </Paragraph>
                  )}
                </>
              ) : (
                <Paragraph>
                  支付未完成或失败。请检查网络或支付状态，如有疑问请联系客服。
                </Paragraph>
              )}
            </div>
          }
          extra={[
            status === 'success' ? (
              <Button type="primary" key="donation" onClick={() => navigate('/donation')}>继续支持</Button>
            ) : (
              <Button type="primary" key="retry" onClick={() => navigate('/donation')}>重试捐赠</Button>
            ),
            <Button key="home" onClick={() => navigate('/')}>返回首页</Button>,
          ]}
        />
      </Card>
      {status === 'success' && (
        <Card style={{ maxWidth: 480, width: '100%', marginTop: 24 }} title="近期捐赠榜单">
          {loading ? <Spin /> : (
            <List
              itemLayout="horizontal"
              dataSource={records}
              renderItem={(item, idx) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar>{item.donor_name ? item.donor_name[0] : '?'}</Avatar>}
                    title={<span>{item.is_anonymous ? '匿名' : item.donor_name}</span>}
                    description={<span>￥{item.amount} | {item.payment_method}</span>}
                  />
                  <span style={{ color: '#aaa' }}>#{idx + 1}</span>
                </List.Item>
              )}
            />
          )}
        </Card>
      )}
    </div>
  );
};

export default DonationResult; 