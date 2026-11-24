#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把会议纪要 Markdown 装配成带截图的 docx。

纪要 md 由校对清洗流程产出（见 references/meeting-minutes.md），本脚本只负责排版：
标题、元信息行、轻量 md 渲染（#/##/### 标题、- 与数字列表、**加粗**、表格行兜底）、
按 select_key_frames 选图（清晰度 + 感知去重，缺 PIL 时退化为均匀抽样）、
PIL 压缩为 JPEG 临时文件后嵌入（自动清理，不残留缓存目录）、页眉页脚页码。

用法：
  python make_meeting_docx.py --config meetings.json --minutes-dir ./meetings --out-dir ./meetings

meetings.json 结构：
{
  "meetings": [
    {"name": "项目同步会",            # 纪要文件为 <name>_会议纪要.md
     "docx": "会议纪要_项目同步会_20250829.docx",
     "date": "2025 年 8 月 29 日", "duration": "约 75 分钟",
     "source": "项目同步会.mp4",
     "frames_dir": "./work/frames/项目同步会",   # 纯音频会议省略
     "images": 5}
  ]
}
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

if sys.platform == "win32":
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name, None)
        if _stream is not None and hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402  复用 select_key_frames / frame_hash


def hexrgb(h: str) -> RGBColor:
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def set_run_font(run, size=None, bold=None, italic=None, color=None, latin="Calibri", cjk="微软雅黑"):
    f = run.font
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = color
    f.name = latin
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), cjk)
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)


def add_runs_with_bold(p, text, size, color=None, bold_all=False, italic=False,
                       latin="Calibri", cjk="微软雅黑"):
    for i, part in enumerate(text.split("**")):
        if not part:
            continue
        r = p.add_run(part)
        set_run_font(r, size=size, bold=bold_all or (i % 2 == 1), italic=italic,
                     color=color, latin=latin, cjk=cjk)


def add_para(doc, text, size=10.5, bold=False, italic=False, color=None, align=None,
             space_after=4, indent=None, latin="Calibri", cjk="微软雅黑"):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(0)
    if indent is not None:
        pf.left_indent = Cm(indent)
    add_runs_with_bold(p, text, size, color=color, bold_all=bold, italic=italic,
                       latin=latin, cjk=cjk)
    return p


def add_heading(doc, text, accent, level=1, latin="Calibri", cjk="微软雅黑"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    set_run_font(r, size={1: 14, 2: 12.5, 3: 11.5}.get(level, 12), bold=True,
                 color=accent, latin=latin, cjk=cjk)
    if level == 1:
        pPr = p._p.get_or_add_pPr()
        pbdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), "%02X%02X%02X" % (accent[0], accent[1], accent[2]))
        pbdr.append(bottom)
        pPr.append(pbdr)
    return p


def add_bullet(doc, text, accent=None, numbered=False, num=None, latin="Calibri", cjk="微软雅黑"):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(2)
    prefix = f"{num}. " if numbered else "• "
    add_runs_with_bold(p, prefix + text, 10.5, latin=latin, cjk=cjk)


def add_page_number(paragraph, latin, cjk, subtle):
    run = paragraph.add_run()
    b = OxmlElement("w:fldChar")
    b.set(qn("w:fldCharType"), "begin")
    t = OxmlElement("w:instrText")
    t.set(qn("xml:space"), "preserve")
    t.text = " PAGE "
    e = OxmlElement("w:fldChar")
    e.set(qn("w:fldCharType"), "end")
    run._r.append(b)
    run._r.append(t)
    run._r.append(e)
    set_run_font(run, size=9, color=subtle, latin=latin, cjk=cjk)


def render_markdown_body(doc, md_text, accent, latin, cjk, subtle):
    lines = md_text.splitlines()
    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or line.startswith("# "):
            continue  # H1 由文档标题渲染
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if m:
            add_heading(doc, m.group(2).strip(), accent, level=len(m.group(1)) - 1,
                        latin=latin, cjk=cjk)
            continue
        m = re.match(r"^[-*]\s+(.*)$", line.strip())
        if m and not line.startswith("    "):
            add_bullet(doc, m.group(1).strip(), latin=latin, cjk=cjk)
            continue
        m = re.match(r"^(\d+)[.、]\s+(.*)$", line.strip())
        if m and len(m.group(2)) > 1 and not line.startswith("    "):
            add_bullet(doc, m.group(2).strip(), numbered=True, num=m.group(1),
                       latin=latin, cjk=cjk)
            continue
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            cells = [c for c in cells if not set(c) <= set("-: ")]
            if cells:
                add_para(doc, "　|　".join(cells), size=9.5, color=subtle, space_after=2,
                         latin=latin, cjk=cjk)
            continue
        add_para(doc, line.strip(), size=10.5, space_after=3, latin=latin, cjk=cjk)


def frame_caption(name: str) -> str:
    m = re.search(r"[_ ](\d+(?:\.\d+)?)s\.\w+$", name)
    if not m:
        return "会议画面截图"
    sec = float(m.group(1))
    return f"会议画面截图 · 约 {int(sec // 60):02d}:{int(sec % 60):02d}"


def compress_frame(src: Path, dst: Path, max_dim=1100, quality=62) -> Path:
    dst = dst.with_suffix(".jpg")
    with Image.open(src) as raw_img:
        img = raw_img.convert("RGB")
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)))
        img.save(dst, "JPEG", quality=quality)
    return dst


def build_one(doc, entry, minutes_md, accent, subtle, latin, cjk, tmp_dir: Path):
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.space_after = Pt(2)
    tr = tp.add_run(entry["name"] + " · 会议纪要")
    set_run_font(tr, size=20, bold=True, color=accent, latin=latin, cjk=cjk)
    meta_parts = [entry.get("date", ""), entry.get("duration", "")]
    if entry.get("source"):
        meta_parts.append("来源：" + Path(entry["source"]).name)
    meta_parts.append("转写引擎：百炼 Qwen ASR（说话人分离）")
    dp = doc.add_paragraph()
    dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dp.paragraph_format.space_after = Pt(8)
    dr = dp.add_run("　·　".join(x for x in meta_parts if x))
    set_run_font(dr, size=9.5, color=subtle, latin=latin, cjk=cjk)

    render_markdown_body(doc, minutes_md, accent, latin, cjk, subtle)

    frames_dir = entry.get("frames_dir")
    k = int(entry.get("images", 5))
    embedded = 0
    if frames_dir and Path(frames_dir).is_dir() and k > 0:
        add_heading(doc, "关键画面截图", accent, level=1, latin=latin, cjk=cjk)
        files = sorted(Path(frames_dir).glob("*.jpg")) + sorted(Path(frames_dir).glob("*.png"))
        picked = engine.select_key_frames(files, k=k)
        for idx, f in enumerate(picked, 1):
            dst = compress_frame(f, tmp_dir / f"frame_{idx:03d}_{f.stem}.jpg")
            ip = doc.add_paragraph()
            ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ip.paragraph_format.space_before = Pt(3)
            ip.paragraph_format.space_after = Pt(1)
            ip.add_run().add_picture(str(dst), width=Inches(4.7))
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.space_after = Pt(5)
            cr = cap.add_run(frame_caption(f.name))
            set_run_font(cr, size=9, color=subtle, latin=latin, cjk=cjk)
            embedded += 1
        if embedded:
            nr = doc.add_paragraph()
            nrun = nr.add_run(f"共嵌入 {embedded} 张画面截图（select_key_frames 清晰度+去重选图），完整帧见 {frames_dir}")
            set_run_font(nrun, size=8.5, italic=True, color=subtle, latin=latin, cjk=cjk)


def main():
    ap = argparse.ArgumentParser(description="会议纪要 md → 带截图 docx")
    ap.add_argument("--config", required=True, help="meetings.json（结构见文件头注释）")
    ap.add_argument("--minutes-dir", required=True, help="纪要 md 所在目录")
    ap.add_argument("--out-dir", required=True, help="docx 输出目录")
    ap.add_argument("--accent", default="2F5D62", help="标题色 hex（默认低饱和青灰）")
    ap.add_argument("--cjk-font", default="微软雅黑")
    ap.add_argument("--latin-font", default="Calibri")
    args = ap.parse_args()

    conf = json.loads(Path(args.config).read_text(encoding="utf-8"))
    accent = hexrgb(args.accent)
    subtle = RGBColor(0x55, 0x55, 0x55)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="vtranscribe_docx_") as tmp_root:
        tmp_dir = Path(tmp_root)
        for entry in conf["meetings"]:
            minutes_md = Path(args.minutes_dir) / f"{entry['name']}_会议纪要.md"
            if not minutes_md.exists():
                print(f"[skip] 缺纪要: {minutes_md}")
                continue
            doc = Document()
            normal = doc.styles["Normal"]
            normal.font.name = args.latin_font
            normal.font.size = Pt(10.5)
            normal.element.rPr.rFonts.set(qn("w:eastAsia"), args.cjk_font)
            for s in doc.sections:
                s.top_margin = Cm(2.0)
                s.bottom_margin = Cm(2.0)
                s.left_margin = Cm(2.2)
                s.right_margin = Cm(2.2)
            sec = doc.sections[0]
            hp = sec.header.paragraphs[0]
            hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            hr = hp.add_run("会议纪要 · " + entry["name"])
            set_run_font(hr, size=8.5, color=subtle, latin=args.latin_font, cjk=args.cjk_font)
            fp = sec.footer.paragraphs[0]
            fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fr = fp.add_run("第 ")
            set_run_font(fr, size=9, color=subtle, latin=args.latin_font, cjk=args.cjk_font)
            add_page_number(fp, args.latin_font, args.cjk_font, subtle)
            fr2 = fp.add_run(" 页")
            set_run_font(fr2, size=9, color=subtle, latin=args.latin_font, cjk=args.cjk_font)

            entry_tmp = tmp_dir / re.sub(r'[\\/:*?"<>|\r\n]+', "_", entry["name"])
            entry_tmp.mkdir(parents=True, exist_ok=True)
            build_one(doc, entry, minutes_md.read_text(encoding="utf-8"),
                      accent, subtle, args.latin_font, args.cjk_font, entry_tmp)

            out = out_dir / entry["docx"]
            doc.save(str(out))
            print(f"[ok] {out.name}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
