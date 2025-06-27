import React, { useEffect, useState } from "react";
import { List, Form, Input, Button, App } from "antd";
import { getComments, addComment } from "../../api/comment";
import { useSelector } from "react-redux";
import { RootState } from "../../app/store";
import MarkdownRenderer from "../../utils/markdownRenderer";

const CommentSection: React.FC<{ articleId: string | number }> = ({ articleId }) => {
  const [comments, setComments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState("");
  const { isAuthenticated } = useSelector((state: RootState) => state.user);
  const { message } = App.useApp();

  // 调试信息
  console.log('CommentSection render:', { articleId, isAuthenticated, content });

  const fetchComments = () => {
    setLoading(true);
    getComments(articleId).then((res: any) => {
      console.log('Comments fetched:', res);
      setComments(res.items || res.data || []);
      setLoading(false);
    }).catch((error) => {
      console.error('Error fetching comments:', error);
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
      
      {/* 调试信息 */}
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#f0f8ff', 
        border: '1px solid #ddd', 
        borderRadius: '4px',
        marginBottom: '10px',
        fontSize: '12px'
      }}>
        <strong>调试信息:</strong><br/>
        认证状态: {isAuthenticated ? '已登录' : '未登录'}<br/>
        文章ID: {articleId}<br/>
        评论数量: {comments.length}<br/>
        加载状态: {loading ? '加载中' : '已加载'}
      </div>

      {isAuthenticated && (
        <Form.Item>
          <Input.TextArea
            rows={3}
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="写下你的评论... (支持 Markdown 和 LaTeX 公式)"
          />
          <Button 
            type="primary" 
            onClick={handleSubmit} 
            loading={loading} 
            style={{ marginTop: 8 }}
            disabled={!content.trim()}
          >
            发表评论
          </Button>
        </Form.Item>
      )}

      {!isAuthenticated && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#fff7e6', 
          border: '1px solid #ffd591', 
          borderRadius: '4px',
          marginBottom: '10px'
        }}>
          请先登录后再发表评论
        </div>
      )}

      <List
        dataSource={comments}
        loading={loading}
        locale={{ emptyText: '暂无评论' }}
        renderItem={item => (
          <div style={{ borderBottom: '1px solid #eee', marginBottom: 8, paddingBottom: 8 }}>
            <div style={{ fontWeight: 'bold' }}>{item.author?.username || "匿名"}</div>
            <div 
              className="markdown-content"
              dangerouslySetInnerHTML={{ 
                __html: MarkdownRenderer.render(item.content || "") 
              }}
              style={{
                fontSize: '14px',
                lineHeight: '1.6',
                marginTop: '4px'
              }}
            />
            <div style={{ color: '#888', fontSize: 12, marginTop: '8px' }}>
              {item.created_at?.slice(0, 16)}
            </div>
          </div>
        )}
      />
    </div>
  );
};

export default CommentSection;