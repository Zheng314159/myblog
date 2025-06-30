import React, { useEffect, useState } from "react";
import { List, Tag, Typography, Spin } from "antd";
import { getArticles } from "../../api/article";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;

const Home: React.FC = () => {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    getArticles({ status: 'published' }).then((res) => {
      const allArticles = res.items || res.data || [];
      const adminArticles = allArticles.filter((item: any) => item.author?.role === 'ADMIN');
      setArticles(adminArticles);
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <Title level={2}>最新文章</Title>
      <Spin spinning={loading}>
        <List
          itemLayout="vertical"
          dataSource={articles}
          renderItem={item => (
            <List.Item
              key={item.id}
              onClick={() => navigate(`/article/${item.id}`)}
              style={{ cursor: "pointer" }}
              extra={item.tags && item.tags.map((tag: any) => <Tag key={typeof tag === 'string' ? tag : tag.name}>{typeof tag === 'string' ? tag : tag.name}</Tag>)}
            >
              <List.Item.Meta
                title={item.title}
                description={`作者: ${item.author?.username || "匿名"} | 发布时间: ${item.created_at?.slice(0, 10)}`}
              />
              <div>{item.summary || item.content?.slice(0, 120) + "..."}</div>
            </List.Item>
          )}
        />
      </Spin>
    </div>
  );
};

export default Home; 