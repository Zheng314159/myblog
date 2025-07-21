import React from "react";
import MDEditor from "@uiw/react-md-editor";
import MarkdownRenderer from "../../utils/markdownRenderer";
import DOMPurify from "dompurify";

interface Props {
  value: string;
  onChange: (v: string) => void;
  height?: number;
  placeholder?: string;
  preview?: "live" | "edit" | "preview" | "split";
}

const MarkdownEditor: React.FC<Props> = ({ 
  value, 
  onChange, 
  height = 400,
  placeholder = "请输入Markdown内容...",
  preview = "live"
}) => {
  // 自定义预览渲染器
  const previewOptions = {
    components: {
      // 自定义代码高亮
      code: ({ inline, children, className, ...props }: any) => {
        const match = /language-(\w+)/.exec(className || '');
        return !inline && match ? (
          <pre className="markdown-code-block">
            <code className={className} {...props}>
              {children}
            </code>
          </pre>
        ) : (
          <code className="markdown-inline-code" {...props}>
            {children}
          </code>
        );
      },
    },
  };

  // 处理onChange事件
  const handleChange = (val?: string) => {
    if (val !== undefined) {
      onChange(val);
    }
  };

  // 自定义分屏模式
  if (preview === 'split') {
    return (
      <div style={{ display: 'flex', height }}>
        <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: '6px 0 0 6px', overflow: 'hidden' }}>
          <MDEditor
            value={value}
            onChange={handleChange}
            height={height}
            preview="edit"
            textareaProps={{ placeholder }}
          />
        </div>
        <div style={{ flex: 1, border: '1px solid #d9d9d9', borderLeft: 'none', borderRadius: '0 6px 6px 0', background: '#fff', overflow: 'auto', padding: 16 }}>
          <div className="markdown-content" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(MarkdownRenderer.postprocessContent(MarkdownRenderer.render(value))) }} />
        </div>
      </div>
    );
  }

  // 其它模式（纯编辑、纯预览）
  if (preview === 'edit') {
    return (
      <div data-color-mode="light">
        <MDEditor
          value={value}
          onChange={handleChange}
          height={height}
          preview="edit"
          textareaProps={{
            placeholder: placeholder,
          }}
        />
      </div>
    );
  }
  // 纯预览模式
  if (preview === 'preview') {
    return (
      <div style={{ border: '1px solid #d9d9d9', borderRadius: '6px', background: '#fff', padding: 16, minHeight: height, overflow: 'auto' }}>
        <div className="markdown-content" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(MarkdownRenderer.postprocessContent(MarkdownRenderer.render(value))) }} />
      </div>
    );
  }
  // 其它情况默认返回 null
  return null;
};

export default MarkdownEditor;