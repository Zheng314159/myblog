import React, { useState } from "react";
import { useSelector } from "react-redux";
import { RootState } from "../../app/store";
import CommentSection from "../../components/Comment/CommentSection";
import { Button } from "antd";
import MarkdownRenderer from "../../utils/markdownRenderer";

const CommentTest: React.FC = () => {
  const { isAuthenticated, userInfo, isLoading } = useSelector((state: RootState) => state.user);
  const [showSampleComments, setShowSampleComments] = useState(false);

  // 示例评论数据
  const sampleComments = [
    {
      id: 1,
      author: { username: "数学爱好者" },
      content: "这篇文章的数学公式写得很好！比如这个二次方程：$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$",
      created_at: "2024-01-15 10:30:00"
    },
    {
      id: 2,
      author: { username: "物理学家" },
      content: "## 很好的文章\n\n特别是这个积分公式：\n\n$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$\n\n非常准确！",
      created_at: "2024-01-15 11:15:00"
    },
    {
      id: 3,
      author: { username: "学生" },
      content: "请问这个公式 $E = mc^2$ 是什么意思？\n\n还有这个求和公式：\n$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$\n\n谢谢！",
      created_at: "2024-01-15 12:00:00"
    }
  ];

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>评论组件测试</h1>
      
      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
        <h3>用户状态信息</h3>
        <p><strong>加载状态:</strong> {isLoading ? '加载中...' : '已加载'}</p>
        <p><strong>认证状态:</strong> {isAuthenticated ? '已登录' : '未登录'}</p>
        <p><strong>用户信息:</strong> {userInfo ? JSON.stringify(userInfo, null, 2) : '无'}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>评论组件测试</h3>
        <p>使用文章ID: 1 进行测试</p>
        <CommentSection articleId="1" />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>示例评论渲染测试</h3>
        <Button 
          type="primary" 
          onClick={() => setShowSampleComments(!showSampleComments)}
          style={{ marginBottom: '10px' }}
        >
          {showSampleComments ? '隐藏' : '显示'} 示例评论
        </Button>
        
        {showSampleComments && (
          <div style={{ 
            border: '1px solid #ddd', 
            borderRadius: '6px', 
            padding: '15px',
            backgroundColor: '#fff'
          }}>
            <h4>示例评论（展示 Markdown 和 LaTeX 渲染效果）</h4>
            {sampleComments.map(comment => (
              <div key={comment.id} style={{ 
                borderBottom: '1px solid #eee', 
                marginBottom: 12, 
                paddingBottom: 12 
              }}>
                <div style={{ fontWeight: 'bold' }}>{comment.author.username}</div>
                <div 
                  className="markdown-content"
                  dangerouslySetInnerHTML={{ 
                    __html: MarkdownRenderer.render(comment.content) 
                  }}
                  style={{
                    fontSize: '14px',
                    lineHeight: '1.6',
                    marginTop: '4px'
                  }}
                />
                <div style={{ color: '#888', fontSize: 12, marginTop: '8px' }}>
                  {comment.created_at}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>手动测试认证状态</h3>
        <div style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}>
          {isAuthenticated ? (
            <div>
              <p style={{ color: 'green' }}>✅ 用户已登录，应该能看到评论输入框</p>
              <p>用户名: {userInfo?.username}</p>
              <p>邮箱: {userInfo?.email}</p>
              <p>角色: {userInfo?.role}</p>
            </div>
          ) : (
            <div>
              <p style={{ color: 'red' }}>❌ 用户未登录，只能看到评论列表</p>
              <p>请先登录以测试评论功能</p>
            </div>
          )}
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>评论功能说明</h3>
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#f0f8ff', 
          border: '1px solid #b3d9ff', 
          borderRadius: '6px' 
        }}>
          <h4>支持的格式：</h4>
          <ul>
            <li><strong>Markdown 格式：</strong> 标题、粗体、斜体、列表、代码块等</li>
            <li><strong>LaTeX 公式：</strong> 行内公式 $...$ 和块级公式 $$...$$</li>
            <li><strong>代码高亮：</strong> 使用 ``` 包围的代码块</li>
            <li><strong>链接和图片：</strong> 标准的 Markdown 语法</li>
          </ul>
          
          <h4>示例：</h4>
          <pre style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '10px', 
            borderRadius: '4px',
            fontSize: '12px'
          }}>
{`## 标题
**粗体文本** 和 *斜体文本*

行内公式：$E = mc^2$

块级公式：
$$\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

\`\`\`python
def hello():
    print("Hello, World!")
\`\`\``}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default CommentTest; 