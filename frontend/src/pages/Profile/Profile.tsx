import React, { useEffect, useState } from "react";
import { Card, Typography, List, Button, message } from "antd";
import { getMe } from "../../api/auth";
import { getArticles } from "../../api/article";
import { useNavigate } from "react-router-dom";

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [articles, setArticles] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    getMe().then(setUser);
    getArticles({ author: user?.username }).then((res) => {
      setArticles(res.items || res.data || []);
    });
  }, [user?.username]);

  if (!user) return <div>加载中...</div>;

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
        <Title level={4}>我的文章</Title>
        <List
          dataSource={articles}
          renderItem={item => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => navigate(`/edit/${item.id}`)}>编辑</Button>,
                <Button type="link" onClick={() => navigate(`/article/${item.id}`)}>查看</Button>
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