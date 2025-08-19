import re
from pathlib import Path

def latex_to_markdown(latex_text: str) -> str:
    # 去掉文档头尾
    latex_text = re.sub(r"\\documentclass.*?\n", "", latex_text, flags=re.DOTALL)
    latex_text = re.sub(r"\\begin{document}", "", latex_text)
    latex_text = re.sub(r"\\end{document}", "", latex_text)

    # 章节替换
    latex_text = re.sub(r"\\part\{(.+?)\}", r"# \1", latex_text)
    latex_text = re.sub(r"\\chapter\{(.+?)\}", r"# \1", latex_text)
    latex_text = re.sub(r"\\section\{(.+?)\}", r"## \1", latex_text)
    latex_text = re.sub(r"\\subsection\{(.+?)\}", r"### \1", latex_text)
    latex_text = re.sub(r"\\paragraph\{.*?\}", r"", latex_text)

    # 图片替换
    latex_text = re.sub(
        r"\\begin{figure}.*?\\includegraphics.*?\{(.+?)\}.*?\\caption\{(.+?)\}.*?\\end{figure}",
        r"![\2](\1)",
        latex_text,
        flags=re.DOTALL,
    )

    # equation / align 环境 -> $$ ... $$
    latex_text = re.sub(
        r"\\begin{equation\*?}(.+?)\\end{equation\*?}",
        lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n",
        latex_text,
        flags=re.DOTALL,
    )
    latex_text = re.sub(
        r"\\begin{align\*?}(.+?)\\end{align\*?}",
        lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n",
        latex_text,
        flags=re.DOTALL,
    )

    # 行内公式 \( ... \) -> $...$
    latex_text = re.sub(r"\\\((.+?)\\\)", r"$\1$", latex_text)

    # 去掉 label / ref 但保留文字
    latex_text = re.sub(r"\\label\{.*?\}", "", latex_text)
    latex_text = re.sub(r"\\ref\{.*?\}", "", latex_text)

    # 删除多余的 LaTeX 控制符
    latex_text = re.sub(r"\\[a-zA-Z]+\*", "", latex_text)

    # 清理多余空行
    latex_text = re.sub(r"\n{3,}", "\n\n", latex_text)

    return latex_text.strip()


if __name__ == "__main__":
    # 输入 LaTeX 文件路径
    # input_file = Path("metaphysics.tex")
    # output_file = Path("metaphysics.md")

    # text = input_file.read_text(encoding="utf-8")
    # md = latex_to_markdown(text)
    # output_file.write_text(md, encoding="utf-8")
    # print(f"✅ 转换完成！输出文件: {output_file}")
    ...