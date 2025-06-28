import React, { useMemo } from "react";
import MarkdownRenderer from "../../utils/markdownRenderer";

interface MarkdownViewerProps {
  content: string;
  className?: string;
  style?: React.CSSProperties;
}

const MarkdownViewer: React.FC<MarkdownViewerProps> = ({ 
  content, 
  className = "markdown-content",
  style = { 
    padding: 16, 
    background: '#ffffff', 
    borderRadius: 4,
    fontSize: '14px',
    lineHeight: '1.6'
  }
}) => {
  const html = useMemo(() => {
    try {
      const rendered = MarkdownRenderer.render(content || "");
      console.log('[MarkdownViewer] content:', content, '\n[MarkdownViewer] 渲染结果:', rendered);
      return rendered;
    } catch (error) {
      console.error('Markdown rendering error:', error);
      return `<div class="markdown-error">渲染错误: ${error}</div>`;
    }
  }, [content]);

  return (
    <div
      style={style}
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};

export default MarkdownViewer;
