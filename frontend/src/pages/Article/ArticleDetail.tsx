import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getArticle } from "../../api/article";
import { Card, Typography, Tag, Spin, Divider, Button } from "antd";
import MarkdownViewer from "../../components/MarkdownViewer/MarkdownViewer";
import CommentSection from "../../components/Comment/CommentSection";
import { useSelector } from "react-redux";
import { RootState } from "../../app/store";

const { Title, Text } = Typography;

const ArticleDetail: React.FC = () => {
  const { id } = useParams();
  const [article, setArticle] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { userInfo } = useSelector((state: RootState) => state.user);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    getArticle(id!).then((res) => {
      setArticle(res.data || res);
      setLoading(false);
    });
  }, [id]);

  if (loading || !article) return <Spin spinning={true}>加载中...</Spin>;

  // 判断是否为作者
  const isAuthor = userInfo && article.author && userInfo.id === article.author.id;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      <Card
        extra={
          isAuthor && (
            <Button type="primary" onClick={() => navigate(`/edit/${article.id}`)}>
              编辑
            </Button>
          )
        }
      >
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