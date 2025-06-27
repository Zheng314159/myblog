import React from "react";
import MDEditor from "@uiw/react-md-editor";
import MarkdownRenderer from "../../utils/markdownRenderer";

interface Props {
  value: string;
  onChange: (v: string) => void;
  height?: number;
  placeholder?: string;
  preview?: "live" | "edit" | "preview";
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

  return (
    <div data-color-mode="light">
      <MDEditor 
        value={value} 
        onChange={handleChange} 
        height={height}
        preview={preview}
        previewOptions={previewOptions}
        // 启用数学公式支持
        textareaProps={{
          placeholder: placeholder,
        }}
      />
    </div>
  );
};

export default MarkdownEditor;