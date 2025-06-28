import React, { useEffect, useState } from "react";
import { List, Tag, Input, Typography, Spin } from "antd";
import { getArticles } from "../../api/article";
import { getPopularTags } from "../../api/tag";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;

const Home: React.FC = () => {
  const [articles, setArticles] = useState<any[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    getArticles({ status: 'published' }).then((res) => {
      const allArticles = res.items || res.data || [];
      const adminArticles = allArticles.filter((item: any) => item.author?.role === 'admin');
      setArticles(adminArticles);
      setLoading(false);
    });
    getPopularTags().then((res) => {
      setTags(res.tags || res.data || []);
    });
  }, []);

  return (
    <div>
      <Title level={2}>最新文章</Title>
      <Input.Search
        placeholder="搜索文章..."
        enterButton
        onSearch={(v) => navigate(`/search?q=${encodeURIComponent(v)}`)}
        style={{ maxWidth: 400, marginBottom: 24 }}
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      <div style={{ marginBottom: 16 }}>
        热门标签：
        {tags.map((tag) => (
          <Tag key={typeof tag === 'string' ? tag : tag.name} color="blue" style={{ cursor: "pointer" }} onClick={() => navigate(`/search?q=${typeof tag === 'string' ? tag : tag.name}`)}>
            {typeof tag === 'string' ? tag : tag.name}
          </Tag>
        ))}
      </div>
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