import React, { useEffect, useState } from "react";
import { Card, Typography, List, Button, message as antdMessage, Modal as AntdModal, Divider, Modal, Form, Input, Alert, Tabs, Image, App } from "antd";
import { getMe, changePassword, sendChangePasswordCode } from "../../api/auth";
import { getArticles, deleteArticle } from "../../api/article";
import { useNavigate } from "react-router-dom";
import { getUserMediaList, deleteMedia } from "../../api/upload";

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [articles, setArticles] = useState<any[]>([]);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [changePasswordVisible, setChangePasswordVisible] = useState(false);
  const [changePasswordLoading, setChangePasswordLoading] = useState(false);
  const [verificationCodeSent, setVerificationCodeSent] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [mediaFiles, setMediaFiles] = useState<any[]>([]);
  const [mediaLoading, setMediaLoading] = useState(false);
  const { message, modal } = App.useApp();

  // 获取邮箱配置状态
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('/api/v1/auth/config');
        const config = await response.json();
        setEmailEnabled(config.email_enabled);
      } catch (error) {
        console.error('获取配置失败:', error);
        setEmailEnabled(false);
      }
    };
    fetchConfig();
  }, []);

  useEffect(() => {
    getMe().then((res) => {
      const me = res.data || res;
      setUser(me);
      if (me?.username) {
        getArticles({ author: me.username }).then((res) => {
          setArticles(res.data || []);
        });
      }
    });
  }, []);

  useEffect(() => {
    if (user?.id) {
      setMediaLoading(true);
      getUserMediaList(user.id).then((res) => {
        setMediaFiles(res.data || res);
      }).finally(() => setMediaLoading(false));
    }
  }, [user]);

  if (!user) return <div>加载中...</div>;

  // 分组：已发布和草稿
  const publishedArticles = articles.filter(a => a.status === 'published');
  const draftArticles = articles.filter(a => a.status === 'draft');

  // 删除文章
  const handleDelete = (id: number | string) => {
    if (window.confirm('确定要删除这篇文章吗？删除后不可恢复！')) {
      deleteArticle(id).then(() => {
        message.success('删除成功');
        // 重新加载文章列表
        if (user?.username) {
          getArticles({ author: user.username }).then((res) => {
            setArticles(res.data || []);
          });
        }
      });
    }
  };

  // 发送验证码
  const handleSendVerificationCode = async () => {
    setSendingCode(true);
    try {
      const response = await sendChangePasswordCode();
      const data = response.data;
      
      if (data.email_enabled === false) {
        message.warning('邮箱验证已关闭，无需发送验证码');
        setVerificationCodeSent(true);
      } else {
        message.success('验证码已发送到您的邮箱');
        setVerificationCodeSent(true);
      }
    } catch (error: any) {
      if (error?.response?.status === 401) {
        message.error('登录状态已失效，请重新登录后再操作！');
      } else {
        const msg = error?.response?.data?.message || '发送验证码失败';
        message.error(msg);
      }
    } finally {
      setSendingCode(false);
    }
  };

  // 修改密码
  const handleChangePassword = async (values: any) => {
    setChangePasswordLoading(true);
    try {
      const changeData: any = {
        current_password: values.currentPassword,
        new_password: values.newPassword
      };

      // 如果邮箱验证开启，需要验证码
      if (emailEnabled) {
        if (!values.verificationCode) {
          message.error('请输入验证码');
          setChangePasswordLoading(false);
          return;
        }
        changeData.verification_code = values.verificationCode;
      }
      // 如果邮箱验证关闭，不需要验证码，但可以传递空字符串

      await changePassword(changeData);
      message.success('密码修改成功');
      setChangePasswordVisible(false);
      form.resetFields();
      setVerificationCodeSent(false);
    } catch (error: any) {
      const msg = error?.response?.data?.message || '密码修改失败';
      message.error(msg);
    } finally {
      setChangePasswordLoading(false);
    }
  };

  // 打开修改密码弹窗
  const handleOpenChangePassword = () => {
    setChangePasswordVisible(true);
    setVerificationCodeSent(false);
    form.resetFields();
  };

  // 关闭修改密码弹窗
  const handleCloseChangePassword = () => {
    setChangePasswordVisible(false);
    setVerificationCodeSent(false);
    form.resetFields();
  };

  // 新增：多媒体文件删除
  const handleDeleteMedia = (id: number | string) => {
    modal.confirm({
      title: '确定要删除该多媒体文件吗？',
      content: '删除后不可恢复',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteMedia(id);
          message.success('删除成功');
          setMediaFiles(files => files.filter(f => f.id !== id));
        } catch (e) {
          message.error('删除失败');
        }
      }
    });
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      <Card>
        <Title level={3}>个人信息</Title>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong style={{ minWidth: 80 }}>用户名：</Text>
            <Text>{user.username}</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong style={{ minWidth: 80 }}>邮箱：</Text>
            <Text>{user.email}</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong style={{ minWidth: 80 }}>角色：</Text>
            <Text style={{ 
              color: user.role === 'ADMIN' ? '#ff4d4f' : '#1890ff',
              fontWeight: 'bold'
            }}>
              {user.role === 'ADMIN' ? '管理员' : '普通用户'}
            </Text>
          </div>
          {user.full_name && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Text strong style={{ minWidth: 80 }}>姓名：</Text>
              <Text>{user.full_name}</Text>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong style={{ minWidth: 80 }}>注册时间：</Text>
            <Text>{user.created_at ? new Date(user.created_at).toLocaleString('zh-CN') : '未知'}</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong style={{ minWidth: 80 }}>状态：</Text>
            <Text style={{ 
              color: user.is_active ? '#52c41a' : '#ff4d4f',
              fontWeight: 'bold'
            }}>
              {user.is_active ? '正常' : '已禁用'}
            </Text>
          </div>
        </div>
        <Button 
          type="primary" 
          style={{ marginTop: 16 }}
          onClick={handleOpenChangePassword}
        >
          修改密码
        </Button>
      </Card>
      
      <Card style={{ marginTop: 24 }}>
        <Title level={4}>我的已发布</Title>
        <List
          dataSource={publishedArticles}
          renderItem={item => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => navigate(`/edit/${item.id}`)}>编辑</Button>,
                <Button type="link" onClick={() => navigate(`/article/${item.id}`)}>查看</Button>,
                <Button type="link" danger onClick={() => handleDelete(item.id)}>删除</Button>
              ]}
            >
              <List.Item.Meta title={item.title} description={item.created_at?.slice(0, 16)} />
            </List.Item>
          )}
        />
        <Divider />
        <Title level={4}>我的草稿</Title>
        <List
          dataSource={draftArticles}
          renderItem={item => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => navigate(`/edit/${item.id}`)}>编辑</Button>,
                <Button type="link" onClick={() => navigate(`/article/${item.id}`)}>查看</Button>,
                <Button type="link" danger onClick={() => handleDelete(item.id)}>删除</Button>
              ]}
            >
              <List.Item.Meta title={item.title} description={item.created_at?.slice(0, 16)} />
            </List.Item>
          )}
        />
      </Card>

      {/* 我的多媒体文件分组管理区 */}
      <Card style={{ marginTop: 24 }}>
        <Title level={4}>我的多媒体文件</Title>
        <Tabs
          defaultActiveKey="image"
          items={[
            {
              key: "image",
              label: "图片",
              children: (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
                  {mediaFiles.filter(f => f.type === 'image').length === 0 && <span>暂无图片</span>}
                  {mediaFiles.filter(f => f.type === 'image').map(f => (
                    <div key={f.id} style={{ width: 120, textAlign: 'center' }}>
                      <Image 
                        src={f.url} 
                        width={100} 
                        height={100} 
                        style={{ objectFit: 'cover' }} 
                        fallback="https://via.placeholder.com/100x100?text=加载失败"
                        alt={f.filename}
                      />
                      <div style={{ fontSize: 12, wordBreak: 'break-all', textAlign: 'center' }} title={f.filename}>
                        <span style={{
                          display: 'inline-block',
                          maxWidth: '100%',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          verticalAlign: 'bottom'
                        }}>{f.filename}</span>
                      </div>
                      <Button danger size="small" style={{ marginTop: 4 }} onClick={() => handleDeleteMedia(f.id)}>删除</Button>
                    </div>
                  ))}
                </div>
              )
            },
            {
              key: "video",
              label: "视频",
              children: (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
                  {mediaFiles.filter(f => f.type === 'video').length === 0 && <span>暂无视频</span>}
                  {mediaFiles.filter(f => f.type === 'video').map(f => (
                    <div key={f.id} style={{ width: 180, textAlign: 'center' }}>
                      <video src={f.url} width={160} height={100} controls style={{ background: '#000' }} />
                      <div style={{ fontSize: 12, wordBreak: 'break-all', textAlign: 'center' }} title={f.filename}>
                        <span style={{
                          display: 'inline-block',
                          maxWidth: '100%',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          verticalAlign: 'bottom'
                        }}>{f.filename}</span>
                      </div>
                      <Button danger size="small" style={{ marginTop: 4 }} onClick={() => handleDeleteMedia(f.id)}>删除</Button>
                    </div>
                  ))}
                </div>
              )
            },
            {
              key: "pdf",
              label: "PDF",
              children: (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
                  {mediaFiles.filter(f => f.type === 'pdf').length === 0 && <span>暂无PDF</span>}
                  {mediaFiles.filter(f => f.type === 'pdf').map(f => (
                    <div key={f.id} style={{ width: 180, textAlign: 'center' }}>
                      <div style={{height:60,display:'flex',alignItems:'center',justifyContent:'center',background:'#fafafa',marginBottom:8}}>
                        <img src="/pdf_icon.svg" alt="pdf" style={{height:40}} />
                      </div>
                      <div style={{ fontSize: 12, wordBreak: 'break-all', textAlign: 'center' }} title={f.filename}>
                        <span style={{
                          display: 'inline-block',
                          maxWidth: '100%',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          verticalAlign: 'bottom'
                        }}>{f.filename}</span>
                      </div>
                      <div style={{ marginTop: 4 }}>
                        <Button danger size="small" onClick={() => handleDeleteMedia(f.id)}>删除</Button>
                        <a href={f.url} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 8 }}>预览</a>
                      </div>
                    </div>
                  ))}
                </div>
              )
            }
          ]}
        />
      </Card>

      {/* 修改密码弹窗 */}
      <Modal
        title="修改密码"
        open={changePasswordVisible}
        onCancel={handleCloseChangePassword}
        footer={null}
      >
        {emailEnabled ? (
          <Alert
            message="邮箱验证已开启"
            description="修改密码需要验证邮箱，我们将向您的邮箱发送验证码"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
        ) : (
          <Alert
            message="邮箱验证已关闭"
            description="修改密码无需邮箱验证，可直接修改"
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Form form={form} onFinish={handleChangePassword} layout="vertical">
          <Form.Item 
            name="currentPassword" 
            label="当前密码" 
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password />
          </Form.Item>
          
          <Form.Item 
            name="newPassword" 
            label="新密码" 
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度至少6位' }
            ]}
          >
            <Input.Password />
          </Form.Item>
          
          <Form.Item 
            name="confirmPassword" 
            label="确认新密码" 
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('newPassword') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password />
          </Form.Item>
          
          <Form.Item 
            name="verificationCode" 
            label="验证码" 
            rules={emailEnabled ? [{ required: true, message: '请输入验证码' }] : []}
          >
            <Input 
              placeholder={emailEnabled ? "请输入验证码" : "邮箱验证已关闭，无需验证码"}
              disabled={!emailEnabled}
              suffix={
                <Button 
                  type="link" 
                  size="small" 
                  loading={sendingCode}
                  onClick={handleSendVerificationCode}
                  disabled={verificationCodeSent || !emailEnabled}
                >
                  {!emailEnabled ? '已关闭' : (verificationCodeSent ? '已发送' : '发送验证码')}
                </Button>
              }
            />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={changePasswordLoading} block>
              确认修改
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Profile;