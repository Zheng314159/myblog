import React, { useEffect, useState } from "react";
import { List, Tag, Input, Typography, Spin, Empty } from "antd";
import { useNavigate, useSearchParams } from "react-router-dom";
import { searchArticles } from "../../api/search";
import { getPopularTags } from "../../api/tag";

const { Title } = Typography;

const Search: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [articles, setArticles] = useState<any[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  const query = searchParams.get('q') || '';

  useEffect(() => {
    setLoading(true);
    searchArticles(query, { skip: 0, limit: 20, status: 'published' })
      .then((res) => {
        setArticles(res.data || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('搜索失败:', error);
        setLoading(false);
      });
    getPopularTags().then((res) => {
      setTags(res.tags || res.data || []);
    });
  }, [query]);

  return (
    <div>
      <Title level={2}>全部文章</Title>
      <Input.Search
        placeholder="搜索文章..."
        enterButton
        onSearch={v => navigate(`/search?q=${encodeURIComponent(v)}`)}
        style={{ maxWidth: 400, marginBottom: 24 }}
        value={search}
        onChange={e => setSearch(e.target.value)}
        defaultValue={query}
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
        {articles.length > 0 ? (
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
        ) : (
          <Empty description={query ? `没有找到包含 "${query}" 的文章` : "暂无文章"} style={{ marginTop: 50 }} />
        )}
      </Spin>
    </div>
  );
};

export default Search; 