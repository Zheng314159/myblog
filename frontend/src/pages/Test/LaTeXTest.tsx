import React, { useState } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import MarkdownRenderer from '../../utils/markdownRenderer';

const LaTeXTest: React.FC = () => {
  const [latexInput, setLatexInput] = useState('\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}');
  const [renderedLatex, setRenderedLatex] = useState('');

  const renderLatex = () => {
    try {
      const html = katex.renderToString(latexInput, {
        throwOnError: false,
        errorColor: '#cc0000',
        displayMode: true
      });
      setRenderedLatex(html);
    } catch (error) {
      setRenderedLatex(`<span style="color: red;">错误: ${error}</span>`);
    }
  };

  const renderInlineLatex = () => {
    try {
      const html = katex.renderToString(latexInput, {
        throwOnError: false,
        errorColor: '#cc0000',
        displayMode: false
      });
      setRenderedLatex(html);
    } catch (error) {
      setRenderedLatex(`<span style="color: red;">错误: ${error}</span>`);
    }
  };

  // 预定义的测试公式
  const testFormulas = [
    { name: '二次方程', formula: '\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}' },
    { name: '求和', formula: '\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}' },
    { name: '积分', formula: '\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}' },
    { name: '分数', formula: '\\frac{a}{b}' },
    { name: '根号', formula: '\\sqrt{x}' },
    { name: '上标', formula: 'x^2' },
    { name: '下标', formula: 'x_i' },
    { name: '希腊字母', formula: '\\alpha, \\beta, \\gamma' },
    { name: '等于号', formula: 'a = b' },
    { name: '矩阵', formula: '\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}' },
  ];

  // Markdown + LaTeX 测试内容
  const markdownLatexContent = `# Markdown + LaTeX 测试

这是一个测试页面，用于验证 Markdown 和 LaTeX 的组合渲染效果。

## 行内公式

当 $a \\neq 0$ 时，方程 $ax^2 + bx + c = 0$ 的解为：

## 块级公式

二次方程的求根公式：

$$\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

## 更多数学公式

### 积分公式

$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

### 求和公式

$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$

## 列表

- 数学公式：$E = mc^2$
- 物理常数：$\\hbar = \\frac{h}{2\\pi}$
- 欧拉公式：$e^{i\\pi} + 1 = 0$

## 代码示例

\`\`\`python
def quadratic_formula(a, b, c):
    """计算二次方程的解"""
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        return x1, x2
    else:
        return None
\`\`\`

## 表格

| 公式 | 描述 |
|------|------|
| $E = mc^2$ | 质能方程 |
| $F = ma$ | 牛顿第二定律 |
| $PV = nRT$ | 理想气体方程 |
`;

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>干净的 LaTeX 测试页面</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>直接 KaTeX 渲染测试</h2>
        <div style={{ marginBottom: '10px' }}>
          <input
            type="text"
            value={latexInput}
            onChange={(e) => setLatexInput(e.target.value)}
            style={{ 
              width: '500px', 
              padding: '8px', 
              marginRight: '10px',
              fontSize: '14px'
            }}
            placeholder="输入 LaTeX 公式"
          />
          <button onClick={renderLatex} style={{ marginRight: '10px', padding: '8px 16px' }}>
            块级渲染
          </button>
          <button onClick={renderInlineLatex} style={{ padding: '8px 16px' }}>
            行内渲染
          </button>
        </div>
        
        {renderedLatex && (
          <div style={{ 
            padding: '20px', 
            border: '2px solid #ddd', 
            borderRadius: '8px',
            backgroundColor: '#f9f9f9',
            marginTop: '10px',
            minHeight: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <div dangerouslySetInnerHTML={{ __html: renderedLatex }} />
          </div>
        )}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>预定义公式测试</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
          {testFormulas.map((test, index) => (
            <div key={index} style={{ 
              border: '1px solid #ddd', 
              borderRadius: '6px', 
              padding: '15px',
              backgroundColor: '#fff'
            }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#666' }}>{test.name}</h4>
              <div style={{ 
                marginBottom: '8px', 
                fontFamily: 'monospace', 
                fontSize: '12px',
                backgroundColor: '#f5f5f5',
                padding: '4px',
                borderRadius: '3px'
              }}>
                {test.formula}
              </div>
              <div style={{ 
                padding: '10px',
                backgroundColor: '#f9f9f9',
                borderRadius: '4px',
                textAlign: 'center'
              }}>
                <div dangerouslySetInnerHTML={{ 
                  __html: katex.renderToString(test.formula, {
                    throwOnError: false,
                    errorColor: '#cc0000',
                    displayMode: true
                  })
                }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>行内公式测试</h2>
        <div style={{ 
          padding: '20px', 
          border: '1px solid #ddd', 
          borderRadius: '6px',
          backgroundColor: '#fff',
          fontSize: '16px',
          lineHeight: '1.8'
        }}>
          <p>这是一个行内公式测试：当 <span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('a \\neq 0', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} /> 时，方程 <span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('ax^2 + bx + c = 0', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} /> 的解为 <span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} />。</p>
          
          <p>另一个例子：<span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('E = mc^2', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} /> 是爱因斯坦的质能方程，其中 <span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('c', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} /> 是光速。</p>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>对齐测试</h2>
        <div style={{ 
          padding: '20px', 
          border: '1px solid #ddd', 
          borderRadius: '6px',
          backgroundColor: '#fff',
          fontSize: '16px'
        }}>
          <p>测试上标对齐：<span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('x^2 + y^2 = z^2', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} /></p>
          
          <p>测试分数对齐：<span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('\\frac{1}{2} = 0.5', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} /></p>
          
          <p>测试根号对齐：<span dangerouslySetInnerHTML={{ 
            __html: katex.renderToString('\\sqrt{16} = 4', {
              throwOnError: false,
              errorColor: '#cc0000',
              displayMode: false
            })
          }} /></p>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>Markdown + LaTeX 组合测试</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <h3>输入内容</h3>
            <textarea
              value={markdownLatexContent}
              readOnly
              style={{
                width: '100%',
                height: '400px',
                padding: '10px',
                fontFamily: 'monospace',
                fontSize: '12px',
                backgroundColor: '#f5f5f5'
              }}
            />
          </div>
          
          <div>
            <h3>渲染结果</h3>
            <div 
              className="markdown-content"
              dangerouslySetInnerHTML={{ __html: MarkdownRenderer.render(markdownLatexContent) }}
              style={{
                border: '1px solid #ddd',
                padding: '16px',
                backgroundColor: '#fff',
                minHeight: '400px',
                fontSize: '14px',
                lineHeight: '1.6',
                overflow: 'auto'
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default LaTeXTest; 