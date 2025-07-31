import React, { useEffect, useState } from "react";
import { Button, Form, Input, List, App, Popconfirm } from "antd";
import DOMPurify from "dompurify";
import { useSelector } from "react-redux";
import type { RootState } from "@/app/store.ts";
import { getComments, addComment, deleteComment } from "@/api/comment.ts";
import MarkdownRenderer from "@/utils/markdownRenderer.ts";

interface User {
  id: number;
  username: string;
  full_name: string;
  role: "ADMIN" | "USER";
}

interface Comment {
  id: number;
  content: string;
  author: User;
  article_id: number;
  parent_id: number | null;
  replies: Comment[];
  created_at: string;
  updated_at: string;
}

const CommentSection: React.FC<{ articleId: string | number }> = ({ articleId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState("");
  const [replyTo, setReplyTo] = useState<number | null>(null);

  const { isAuthenticated, userInfo } = useSelector((state: RootState) => state.user);
  const { message } = App.useApp();

  const fetchComments = () => {
    setLoading(true);
    getComments(articleId)
      .then((res: any) => {
        setComments(res.items || res.data || []);
      })
      .catch((error) => {
        console.error("Error fetching comments:", error);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchComments();
    // eslint-disable-next-line
  }, [articleId]);

  const handleSubmit = async () => {
    if (!content.trim()) return;
    setLoading(true);
    try {
      await addComment(articleId, { content, parent_id: replyTo });
      setContent("");
      setReplyTo(null);
      fetchComments();
      message.success("评论成功");
    } catch (e: any) {
      message.error(e.message || "评论失败");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (commentId: number) => {
    try {
      await deleteComment(articleId, commentId);
      message.success("删除成功");
      fetchComments();
    } catch (e: any) {
      message.error(e.message || "删除失败");
    }
  };

  const renderComment = (comment: Comment) => (
    <div
      key={comment.id}
      style={{
        borderBottom: "1px solid #eee",
        marginBottom: 8,
        paddingBottom: 8,
        paddingLeft: comment.parent_id ? 24 : 0,
      }}
    >
      <div style={{ fontWeight: "bold" }}>{comment.author?.username || "匿名"}</div>

      <div
        className="markdown-content"
        dangerouslySetInnerHTML={{
          __html: DOMPurify.sanitize(
            MarkdownRenderer.postprocessContent(MarkdownRenderer.render(comment.content || ""))
          ),
        }}
        style={{ fontSize: "14px", lineHeight: "1.6", marginTop: "4px" }}
      />

      <div style={{ color: "#888", fontSize: 12, marginTop: "8px" }}>
        {comment.created_at?.slice(0, 16)}
      </div>

      <div style={{ marginTop: 6 }}>
        {isAuthenticated && (
          <Button
            size="small"
            type="link"
            onClick={() => {
              setReplyTo(comment.id);
              setContent(`@${comment.author.username} `);
            }}
          >
            回复
          </Button>
        )}

        {userInfo?.id === comment.author?.id && (
          <Popconfirm
            title="确认删除这条评论？"
            onConfirm={() => handleDelete(comment.id)}
            okText="删除"
            cancelText="取消"
          >
            <Button size="small" type="link" danger>
              删除
            </Button>
          </Popconfirm>
        )}
      </div>

      {/* 嵌套回复 */}
      {comment.replies?.length > 0 &&
        comment.replies.map((reply) => renderComment(reply))}
    </div>
  );

  return (
    <div>
      <h3>评论</h3>

      {isAuthenticated ? (
        <Form.Item>
          <Input.TextArea
            rows={3}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={
              replyTo
                ? "回复中..."
                : "写下你的评论... (支持 Markdown 和 LaTeX 公式)"
            }
          />
          <Button
            type="primary"
            onClick={handleSubmit}
            loading={loading}
            style={{ marginTop: 8 }}
            disabled={!content.trim()}
          >
            {replyTo ? "提交回复" : "发表评论"}
          </Button>
          {replyTo && (
            <Button
              style={{ marginLeft: 8 }}
              onClick={() => {
                setReplyTo(null);
                setContent("");
              }}
            >
              取消回复
            </Button>
          )}
        </Form.Item>
      ) : (
        <div
          style={{
            padding: "10px",
            backgroundColor: "#fff7e6",
            border: "1px solid #ffd591",
            borderRadius: "4px",
            marginBottom: "10px",
          }}
        >
          请先登录后再发表评论
        </div>
      )}

      <List
        dataSource={comments.filter((c) => c.parent_id === null)}
        loading={loading}
        locale={{ emptyText: "暂无评论" }}
        renderItem={(item) => renderComment(item)}
      />
    </div>
  );
};

export default CommentSection;
