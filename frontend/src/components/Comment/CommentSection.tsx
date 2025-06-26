import React, { useEffect, useState } from "react";
import { List, Form, Input, Button, message } from "antd";
import { getComments, addComment } from "../../api/comment";
import { useSelector } from "react-redux";
import { RootState } from "../../app/store";

const CommentSection: React.FC<{ articleId: string | number }> = ({ articleId }) => {
  const [comments, setComments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState("");
  const { isAuthenticated } = useSelector((state: RootState) => state.user);

  const fetchComments = () => {
    setLoading(true);
    getComments(articleId).then((res: any) => {
      setComments(res.items || res.data || []);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchComments();
    // eslint-disable-next-line
  }, [articleId]);

  const handleSubmit = async () => {
    if (!content) return;
    setLoading(true);
    try {
      await addComment(articleId, { content });
      setContent("");
      fetchComments();
      message.success("评论成功");
    } catch (e: any) {
      message.error(e.message || "评论失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>评论</h3>
      {isAuthenticated && (
        <Form.Item>
          <Input.TextArea
            rows={3}
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="写下你的评论..."
          />
          <Button type="primary" onClick={handleSubmit} loading={loading} style={{ marginTop: 8 }}>
            发表评论
          </Button>
        </Form.Item>
      )}
      <List
        dataSource={comments}
        renderItem={item => (
          <div style={{ borderBottom: '1px solid #eee', marginBottom: 8, paddingBottom: 8 }}>
            <div style={{ fontWeight: 'bold' }}>{item.author?.username || "匿名"}</div>
            <div>{item.content}</div>
            <div style={{ color: '#888', fontSize: 12 }}>{item.created_at?.slice(0, 16)}</div>
          </div>
        )}
      />
    </div>
  );
};

export default CommentSection;