import React, { useEffect, useState } from "react";
import { List, Tag, Input, Typography, Spin, Empty } from "antd";
import { useNavigate, useSearchParams } from "react-router-dom";
import { searchArticles } from "../../api/search.ts";
import { getPopularTags } from "../../api/tag.ts";
import { PopularTag } from "../../api/tag.ts";
import HotTags from "@/components/HotTags/hotTags.tsx";
const { Title } = Typography;

const Search: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [articles, setArticles] = useState<any[]>([]);
  const [tags, setTags] = useState<PopularTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  const query = searchParams.get('q') || '';
  const tag = searchParams.get('tag') || '';

useEffect(() => {
  setLoading(true);
  searchArticles({ q: query, tag, skip: 0, limit: 20, status: "published" })
    .then((res) => {
      setArticles(res.data || []);
      setLoading(false);
    })
    .catch(() => setLoading(false));

  getPopularTags().then((res) => {
    setTags(res.data.tags || []);
  });
}, [query, tag]);


  return (
    <div>
      <Title level={2}>全部文章</Title>

      <HotTags tags={tags} />
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