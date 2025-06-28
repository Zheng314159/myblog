import MarkdownIt from 'markdown-it';
import katex from 'katex';
import 'katex/dist/katex.min.css';

// 创建 markdown-it 实例
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
});

export interface MarkdownRenderOptions {
  sanitize?: boolean;
  highlight?: (code: string, lang: string) => string;
}

export class MarkdownRenderer {
  /**
   * 渲染 Markdown 内容
   */
  static render(content: string, options: MarkdownRenderOptions = {}): string {
    try {
      // 1. 先用 markdown-it 渲染 markdown
      let rendered = md.render(content || "");

      // 2. 再用 KaTeX 渲染 HTML 里的公式
      // 块级公式 $$...$$
      rendered = rendered.replace(/\$\$([\s\S]*?)\$\$/g, (match, formula) => {
        try {
          return katex.renderToString(formula.trim(), {
            throwOnError: false,
            errorColor: '#cc0000',
            displayMode: true
          });
        } catch (error) {
          return `<span style=\"color: #cc0000;\">LaTeX 错误: ${error}</span>`;
        }
      });
      // 行内公式 $...$
      rendered = rendered.replace(/\$([^$\n]+?)\$/g, (match, formula) => {
        try {
          return katex.renderToString(formula.trim(), {
            throwOnError: false,
            errorColor: '#cc0000',
            displayMode: false
          });
        } catch (error) {
          return `<span style=\"color: #cc0000;\">LaTeX 错误: ${error}</span>`;
        }
      });
      return rendered;
    } catch (error) {
      console.error('Markdown rendering error:', error);
      return `<div class=\"markdown-error\">渲染错误: ${error}</div>`;
    }
  }

  /**
   * 预处理内容 - 直接使用 KaTeX 处理 LaTeX 公式
   */
  private static preprocessContent(content: string): string {
    // 处理块级公式 $$...$$
    content = content.replace(/\$\$([\s\S]*?)\$\$/g, (match, formula) => {
      try {
        return katex.renderToString(formula.trim(), {
          throwOnError: false,
          errorColor: '#cc0000',
          displayMode: true
        });
      } catch (error) {
        return `<span style="color: #cc0000;">LaTeX 错误: ${error}</span>`;
      }
    });

    // 处理行内公式 $...$
    content = content.replace(/\$([^$\n]+?)\$/g, (match, formula) => {
      try {
        return katex.renderToString(formula.trim(), {
          throwOnError: false,
          errorColor: '#cc0000',
          displayMode: false
        });
      } catch (error) {
        return `<span style="color: #cc0000;">LaTeX 错误: ${error}</span>`;
      }
    });

    return content;
  }

  /**
   * 后处理渲染结果
   */
  private static postprocessContent(rendered: string): string {
    // 添加额外的样式类
    rendered = rendered
      // 为表格添加样式
      .replace(/<table>/g, '<table class="markdown-table">')
      // 为代码块添加样式
      .replace(/<pre>/g, '<pre class="markdown-code-block">')
      // 为行内代码添加样式
      .replace(/<code>/g, '<code class="markdown-inline-code">')
      // 为链接添加样式
      .replace(/<a /g, '<a class="markdown-link" target="_blank" rel="noopener noreferrer" ');

    return rendered;
  }

  /**
   * 提取纯文本（用于搜索等）
   */
  static extractText(content: string): string {
    // 移除 LaTeX 公式
    const withoutLatex = content
      .replace(/\$[^$]+\$/g, '') // 行内公式
      .replace(/\$\$[^$]+\$\$/g, '') // 块级公式
      .replace(/\\\([^)]+\\\)/g, '') // 行内公式
      .replace(/\\\[[^\]]+\\\]/g, ''); // 块级公式

    // 移除 Markdown 标记
    const withoutMarkdown = withoutLatex
      .replace(/#{1,6}\s+/g, '') // 标题
      .replace(/\*\*([^*]+)\*\*/g, '$1') // 粗体
      .replace(/\*([^*]+)\*/g, '$1') // 斜体
      .replace(/`([^`]+)`/g, '$1') // 行内代码
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 链接
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1') // 图片
      .replace(/^\s*[-*+]\s+/gm, '') // 列表项
      .replace(/^\s*\d+\.\s+/gm, '') // 有序列表
      .replace(/^\s*>\s+/gm, '') // 引用
      .replace(/^\s*`{3,}.*$/gm, '') // 代码块开始
      .replace(/^\s*`{3,}$/gm, ''); // 代码块结束

    return withoutMarkdown.trim();
  }

  /**
   * 验证 LaTeX 语法
   */
  static validateLatex(latex: string): { isValid: boolean; error?: string } {
    try {
      // 使用 KaTeX 尝试渲染来验证语法
      katex.renderToString(latex, { throwOnError: true });
      return { isValid: true };
    } catch (error) {
      return { 
        isValid: false, 
        error: error instanceof Error ? error.message : '未知错误' 
      };
    }
  }

  /**
   * 预览 LaTeX 公式
   */
  static previewLatex(latex: string): string {
    try {
      return katex.renderToString(latex, { 
        throwOnError: false,
        errorColor: '#cc0000',
        strict: false
      });
    } catch (error) {
      return `<span style="color: #cc0000;">LaTeX 渲染错误: ${error}</span>`;
    }
  }
}

// 导出默认实例
export default MarkdownRenderer; 