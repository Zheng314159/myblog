# LaTeX 渲染解决方案

## 问题描述

在博客系统中，LaTeX数学公式渲染存在对齐问题，表现为：
- 上标（如 x²）位置偏移
- 分数线对齐不正确
- 等号与分数线不对齐
- 字符整体漂移

## 根本原因

问题出在 `markdown-it-katex` 插件上：
1. 该插件在markdown处理过程中处理LaTeX公式
2. 可能与markdown-it的其他处理步骤产生冲突
3. 导致KaTeX的精确数学布局被干扰

## 解决方案

### 1. 移除 markdown-it-katex 插件

```bash
pnpm remove markdown-it-katex
```

### 2. 直接使用 KaTeX 进行预处理

在 `MarkdownRenderer` 中，在markdown处理之前直接使用KaTeX渲染LaTeX公式：

```typescript
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
```

### 3. 简化CSS样式

移除所有自定义的KaTeX样式，让KaTeX使用其默认的精确数学布局：

```css
/* 移除所有自定义 KaTeX 样式 - 让 KaTeX 处理一切 */
```

## 优势

1. **完美对齐** - 直接使用KaTeX的精确数学布局
2. **更好的性能** - 减少了一层插件处理
3. **更少的依赖** - 移除了markdown-it-katex依赖
4. **更好的错误处理** - 可以精确控制LaTeX错误显示

## 测试验证

创建了专门的LaTeX测试页面 (`/test/latex`)，包含：
- 直接KaTeX渲染测试
- 预定义公式测试
- 行内公式测试
- 对齐测试
- Markdown + LaTeX组合测试

## 影响范围

此解决方案影响以下组件：
- `MarkdownRenderer` - 核心渲染逻辑
- `MarkdownViewer` - 文章显示
- `MarkdownEditor` - 文章编辑
- `ArticleDetail` - 文章详情页
- `ArticleEdit` - 文章编辑页

## 使用方法

### 行内公式
```markdown
当 $a \neq 0$ 时，方程 $ax^2 + bx + c = 0$ 的解为：
```

### 块级公式
```markdown
$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$
```

### 复杂公式
```markdown
$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$
```

## 注意事项

1. LaTeX公式中的反斜杠在Markdown中需要转义（双反斜杠）
2. 块级公式使用双美元符号 `$$`
3. 行内公式使用单美元符号 `$`
4. 错误处理会显示红色错误信息而不是崩溃

## 结论

通过直接使用KaTeX进行预处理，我们成功解决了LaTeX公式的对齐问题，实现了完美的数学公式渲染效果。 