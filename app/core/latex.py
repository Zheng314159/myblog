"""
LaTeX渲染服务
支持数学公式渲染和LaTeX内容处理
"""

import re
import base64
import hashlib
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LatexRenderer:
    """LaTeX渲染器 - 简化版本"""
    
    def __init__(self, output_dir: str = "uploads/latex"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查是否有LaTeX支持
        self.has_latex_support = self._check_latex_support()
        
    def _check_latex_support(self) -> bool:
        """检查系统是否有LaTeX支持"""
        try:
            import subprocess
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            logger.warning("系统未安装LaTeX，将使用简化模式")
            return False
    
    def extract_latex_blocks(self, content: str) -> List[Dict[str, str]]:
        """从内容中提取LaTeX块"""
        latex_blocks = []
        
        # 匹配行内数学公式 $...$ 或 \(...\)
        inline_patterns = [
            r'\$([^$]+)\$',
            r'\\\(([^)]+)\\\)'
        ]
        
        # 匹配块级数学公式 $$...$$ 或 \[...\]
        block_patterns = [
            r'\$\$([^$]+)\$\$',
            r'\\\[([^\]]+)\\\]'
        ]
        
        # 匹配LaTeX环境
        environment_patterns = [
            r'\\begin\{([^}]+)\}(.*?)\\end\{\1\}',
            r'\\begin\{([^}]+)\}(.*?)\\end\{([^}]+)\}'
        ]
        
        # 处理行内公式
        for pattern in inline_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                latex_blocks.append({
                    'type': 'inline',
                    'content': match.group(1),
                    'start': match.start(),
                    'end': match.end(),
                    'original': match.group(0)
                })
        
        # 处理块级公式
        for pattern in block_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                latex_blocks.append({
                    'type': 'block',
                    'content': match.group(1),
                    'start': match.start(),
                    'end': match.end(),
                    'original': match.group(0)
                })
        
        # 处理LaTeX环境
        for pattern in environment_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                latex_blocks.append({
                    'type': 'environment',
                    'content': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'original': match.group(0)
                })
        
        return sorted(latex_blocks, key=lambda x: x['start'])
    
    def render_latex_to_image(self, latex_content: str, block_type: str = 'block') -> Optional[str]:
        """将LaTeX内容渲染为图片 - 简化版本"""
        try:
            # 生成唯一文件名
            content_hash = hashlib.md5(latex_content.encode()).hexdigest()[:8]
            filename = f"latex_{content_hash}.png"
            filepath = self.output_dir / filename
            
            # 如果文件已存在，直接返回
            if filepath.exists():
                return f"/api/v1/articles/latex/{filename}"
            
            if self.has_latex_support:
                return self._render_with_latex(latex_content, block_type, filepath)
            else:
                return self._render_with_placeholder(latex_content, block_type, filepath)
                
        except Exception as e:
            logger.error(f"LaTeX渲染失败: {e}")
            return None
    
    def _render_with_latex(self, latex_content: str, block_type: str, filepath: Path) -> Optional[str]:
        """使用系统LaTeX渲染"""
        try:
            import subprocess
            import tempfile
            
            # LaTeX模板
            latex_template = r"""
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{geometry}
\usepackage{color}
\usepackage{graphicx}
\usepackage{mathtools}
\usepackage{physics}
\usepackage{siunitx}
\usepackage{chemfig}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

\geometry{margin=1in}
\pagestyle{empty}

\begin{document}
\thispagestyle{empty}

%s

\end{document}
"""
            
            # 准备LaTeX内容
            if block_type == 'inline':
                latex_doc = latex_template % f"${latex_content}$"
            else:
                latex_doc = latex_template % latex_content
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
                f.write(latex_doc)
                tex_file = f.name
            
            try:
                # 编译LaTeX文档
                result = subprocess.run([
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory=' + str(self.output_dir),
                    tex_file
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    logger.error(f"LaTeX compilation failed: {result.stderr}")
                    return None
                
                # 获取PDF文件路径
                pdf_file = Path(tex_file).with_suffix('.pdf')
                pdf_path = self.output_dir / pdf_file.name
                
                if not pdf_path.exists():
                    logger.error("PDF file not generated")
                    return None
                
                # 转换为PNG
                result = subprocess.run([
                    'convert',
                    '-density', '300',
                    '-quality', '90',
                    str(pdf_path),
                    str(filepath)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    logger.error(f"PDF to PNG conversion failed: {result.stderr}")
                    return None
                
                # 清理临时文件
                os.unlink(tex_file)
                for ext in ['.aux', '.log', '.out', '.pdf']:
                    temp_file = self.output_dir / Path(tex_file).with_suffix(ext).name
                    if temp_file.exists():
                        temp_file.unlink()
                
                return f"/api/v1/articles/latex/{filename}"
                
            except subprocess.TimeoutExpired:
                logger.error("LaTeX rendering timeout")
                return None
            except Exception as e:
                logger.error(f"LaTeX rendering error: {e}")
                return None
                
        except Exception as e:
            logger.error(f"LaTeX rendering failed: {e}")
            return None
    
    def _render_with_placeholder(self, latex_content: str, block_type: str, filepath: Path) -> Optional[str]:
        """使用占位符渲染（当没有LaTeX支持时）"""
        try:
            # 创建一个简单的SVG占位符
            svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="100" fill="#f0f0f0" stroke="#ccc" stroke-width="1"/>
  <text x="200" y="50" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">
    LaTeX: {latex_content[:50]}{'...' if len(latex_content) > 50 else ''}
  </text>
  <text x="200" y="70" text-anchor="middle" font-family="Arial" font-size="10" fill="#999">
    (需要安装LaTeX以显示数学公式)
  </text>
</svg>"""
            
            # 保存SVG文件
            svg_file = filepath.with_suffix('.svg')
            svg_file.write_text(svg_content, encoding='utf-8')
            
            # 返回SVG URL
            return f"/api/v1/articles/latex/{svg_file.name}"
            
        except Exception as e:
            logger.error(f"占位符渲染失败: {e}")
            return None
    
    def process_content(self, content: str) -> Tuple[str, List[Dict[str, str]]]:
        """处理内容中的LaTeX，返回处理后的内容和LaTeX块信息"""
        latex_blocks = self.extract_latex_blocks(content)
        processed_content = content
        rendered_blocks = []
        
        # 从后往前替换，避免位置偏移
        for block in reversed(latex_blocks):
            image_url = self.render_latex_to_image(block['content'], block['type'])
            if image_url:
                rendered_blocks.append({
                    **block,
                    'image_url': image_url
                })
                # 替换原内容为图片标记
                placeholder = f"![LaTeX]({image_url})"
                processed_content = (
                    processed_content[:block['start']] + 
                    placeholder + 
                    processed_content[block['end']:]
                )
        
        return processed_content, rendered_blocks
    
    def validate_latex(self, latex_content: str) -> Tuple[bool, str]:
        """验证LaTeX语法"""
        try:
            # 基本语法检查
            if not latex_content.strip():
                return False, "LaTeX内容不能为空"
            
            # 检查未闭合的括号
            if latex_content.count('{') != latex_content.count('}'):
                return False, "括号不匹配"
            
            if latex_content.count('[') != latex_content.count(']'):
                return False, "方括号不匹配"
            
            # 检查基本的LaTeX命令
            basic_commands = [
                r'\\[a-zA-Z]+',  # 基本命令
                r'\\[a-zA-Z]+\{[^}]*\}',  # 带参数的命令
                r'\\[a-zA-Z]+\[[^\]]*\]',  # 带可选参数的命令
            ]
            
            # 这里可以添加更多的验证规则
            return True, "LaTeX语法正确"
            
        except Exception as e:
            return False, f"LaTeX验证失败: {str(e)}"


# 全局LaTeX渲染器实例
latex_renderer = LatexRenderer() 