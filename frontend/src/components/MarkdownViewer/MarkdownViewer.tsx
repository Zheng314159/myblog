import React, { useMemo } from "react";
// @ts-expect-error: no types
import MarkdownIt from "markdown-it";
// @ts-expect-error: no types
import mk from "markdown-it-katex";
import "katex/dist/katex.min.css";

const md = MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
}).use(mk);

const MarkdownViewer: React.FC<{ content: string }> = ({ content }) => {
  const html = useMemo(() => md.render(content || ""), [content]);
  return (
    <div
      style={{ padding: 12, background: '#fafafa', borderRadius: 4 }}
      className="markdown-body"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};

export default MarkdownViewer;
