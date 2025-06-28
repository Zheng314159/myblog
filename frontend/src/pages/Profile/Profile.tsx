import React, { useEffect, useState } from "react";
import { Card, Typography, List, Button, message, Divider } from "antd";
import { getMe } from "../../api/auth";
import { getArticles, deleteArticle } from "../../api/article";
import { useNavigate } from "react-router-dom";

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [articles, setArticles] = useState<any[]>([]);
  const navigate = useNavigate();

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

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      <Card>
        <Title level={3}>个人信息</Title>
        <Text>用户名：{user.username}</Text>
        <br />
        <Text>邮箱：{user.email}</Text>
        <br />
        <Text>角色：{user.role}</Text>
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
    </div>
  );
};

export default Profile;