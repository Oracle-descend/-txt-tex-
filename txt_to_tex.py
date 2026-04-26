# 这个脚本将纯文本小说转换为 LaTeX 格式，适合使用 XeLaTeX 编译。它会自动识别章节标题并进行适当的转义处理，以确保特殊字符在 LaTeX 中正确显示。请根据需要调整输入输出路径和编码设置。
import re
from pathlib import Path

# 输入输出路径，请根据实际情况修改
src = Path(r"c:\Users\06210\txt-tex\神级龙卫-神级龙卫.txt")
dst = Path(r"c:\Users\06210\txt-tex\神级龙卫-神级龙卫.tex")


def escape_tex(text: str) -> str:
    text = text.replace("\\", r"\textbackslash{}")
    text = text.replace("{", r"\{").replace("}", r"\}")
    text = text.replace("$", r"\$")
    text = text.replace("&", r"\&")
    text = text.replace("#", r"\#")
    text = text.replace("_", r"\_")
    text = text.replace("%", r"\%")
    text = text.replace("~", r"\textasciitilde{}")
    text = text.replace("^", r"\textasciicircum{}")
    return text


chapter_re = re.compile(
    r"^第\s*[0-9零一二三四五六七八九十百千万两〇]+\s*章.*$"
)


def parse_chapter_title(line: str) -> str | None:
    s = line.strip()
    if not s:
        return None

    # 兼容“章节目录 第X章...”和“第X章...”两种形式
    if s.startswith("章节目录"):
        s = s[len("章节目录") :].strip()

    if chapter_re.match(s):
        return s

    return None


def read_text(path: Path) -> str:
    # 优先 UTF-8（含容错），避免因个别坏字节整体退回到 gb18030 导致全书乱码
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue

    # 兜底：UTF-8 忽略错误（通常只会丢失极少数字符）
    text_utf8_lossy = path.read_text(encoding="utf-8", errors="ignore")
    if text_utf8_lossy:
        return text_utf8_lossy

    # 最后再尝试其他编码
    for enc in ("gb18030", "utf-16"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue

    return path.read_text(encoding="latin1", errors="ignore")


raw = read_text(src)
lines = raw.splitlines()

# 生成 LaTeX 文档结构（标题可根据需要修改），并处理章节标题和普通文本
out = []
out.append(r"\documentclass[UTF8,12pt,openany]{ctexbook}")
out.append(r"\usepackage[a4paper,margin=2.5cm]{geometry}")
out.append(r"\usepackage{hyperref}")
out.append(r"\usepackage{setspace}")
out.append(r"\setstretch{1.35}")
out.append("")
out.append(r"\title{神级龙卫}")
out.append(r"\author{}")
out.append(r"\date{}")
out.append("")
out.append(r"\begin{document}")
out.append(r"\maketitle")
out.append("")

started = False

for line in lines:
    s = line.strip()

    if not s:
        out.append("")
        continue

    if s in {"------------", "正文"}:
        continue

    chap_title = parse_chapter_title(s)
    if chap_title:
        chap = escape_tex(chap_title)
        out.append("")
        out.append(rf"\chapter*{{{chap}}}")
        out.append("")
        started = True
        continue

    # 未出现章节标题前的内容，作为普通文本保留
    txt = escape_tex(s)
    if txt:
        out.append(txt)
        out.append("")

if not started:
    # 没识别到章节时，至少保证内容保留
    pass

out.append(r"\end{document}")
out.append("")

content = "\n".join(out)
dst.write_text(content, encoding="utf-8")
print(f"Generated: {dst}")
print(f"Total source lines: {len(lines)}")
print(f"Total tex lines: {len(out)}")
