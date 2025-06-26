import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getArticle } from "../../api/article";
import { Card, Typography, Tag, Spin, Divider } from "antd";
import MarkdownViewer from "../../components/MarkdownViewer/MarkdownViewer";
import CommentSection from "../../components/Comment/CommentSection";

const { Title, Text } = Typography;

const ArticleDetail: React.FC = () => {
  const { id } = useParams();
  const [article, setArticle] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getArticle(id!).then((res) => {
      setArticle(res.data || res);
      setLoading(false);
    });
  }, [id]);

  if (loading || !article) return <Spin spinning={true}>加载中...</Spin>;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      <Card>
        <Title>{article.title}</Title>
        <div>
          <Text type="secondary">
            作者：{article.author?.username || "匿名"} | 发布时间：{article.created_at?.slice(0, 16)}
          </Text>
        </div>
        <div style={{ margin: "8px 0" }}>
          {article.tags?.map((tag: any) => (
            <Tag key={tag.id || tag.name || tag}>
              {typeof tag === 'string' ? tag : tag.name}
            </Tag>
          ))}
        </div>
        <Divider />
        <MarkdownViewer content={article.content || ""} />
      </Card>
      <Divider />
      <CommentSection articleId={id!} />
    </div>
  );
};

export default ArticleDetail;