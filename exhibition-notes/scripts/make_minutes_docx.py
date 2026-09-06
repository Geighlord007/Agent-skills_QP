#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 talk_dossier.json + talk_content.json 装配展会纪要 docx（总-分-总，嵌入压缩照片）。

talk_content.json 结构：
{
  "_title": "...", "_subtitle": "...", "_date": "2026 年 9 月 4 日（周五）",
  "_overview": ["总体概览段落", ...],
  "_closing":  ["横向观察段落", ...],
  "_scope_note": "记录范围说明（覆盖了什么、没录到什么）",
  "<talk_id>": {
      "highlights": ["核心亮点", ...],     # 加粗条目
      "body":       ["正文要点", ...],     # 普通陈述句，平实不浮夸
      "key_data":   ["数字/专利号/标准/产品代号", ...],
      "corrections":{"错词":"正词"},       # 仅留档，不直接入正文
      "speaker_note": "string|null"        # 若需修正讲者姓名
  }, ...
}

照片选择：若提供 --manifest（ocr/_manifest.json），按各场照片的 OCR 文字量取信息最丰富的
top N 张，再按拍摄时间排序展示；否则按时间取前 N 张。压缩图须已由 scan_media.py 用 PIL
转 RGB 存好（规避 python-docx 嵌入 iPhone JPEG 丢失关系的 bug）。
"""
import argparse
import io
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def hexrgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def set_run_font(run, latin, cjk, size=None, bold=None, color=None, italic=None):
    f = run.font
    if size is not None: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    if color is not None: f.color.rgb = color
    f.name = latin
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), cjk)
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)


def add_para(doc, text, latin, cjk, size=10.5, bold=False, italic=False, color=None,
             align=None, space_after=4, indent=None):
    p = doc.add_paragraph()
    if align is not None: p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after); pf.space_before = Pt(0)
    if indent is not None: pf.left_indent = Cm(indent)
    if text:
        r = p.add_run(text); set_run_font(r, latin, cjk, size=size, bold=bold, italic=italic, color=color)
    return p


def add_heading(doc, text, latin, cjk, accent, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(4)
    sizes = {0: 18, 1: 14, 2: 12.5}
    r = p.add_run(text); set_run_font(r, latin, cjk, size=sizes.get(level, 12), bold=True, color=accent)
    if level <= 1:
        pPr = p._p.get_or_add_pPr()
        pbdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "4"); bottom.set(qn("w:color"), "%06X" % int(accent))
        pbdr.append(bottom); pPr.append(pbdr)
    return p


def add_bullet(doc, text, latin, cjk):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("• " + text); set_run_font(r, latin, cjk, size=10.5)
    return p


def add_page_number(paragraph, latin, cjk, subtle):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar"); fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar"); fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin); run._r.append(instr); run._r.append(fld_end)
    set_run_font(run, latin, cjk, size=9, color=subtle)


def pick_photos(entry, manifest_by_file, max_n):
    photos = entry.get("photos", [])
    if not photos:
        return []
    scored = sorted(photos, key=lambda ph: -manifest_by_file.get(ph["file"], 0))
    top = scored[:max_n]
    top.sort(key=lambda x: x.get("exif") or "")
    return top


def main():
    ap = argparse.ArgumentParser(description="装配展会纪要 docx")
    ap.add_argument("--dossier", required=True)
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", default="", help="ocr/_manifest.json（用于按信息量选照片，可选）")
    ap.add_argument("--max-photos", type=int, default=6)
    ap.add_argument("--accent", default="2F5D62", help="标题色 hex（默认 2F5D62 低饱和青灰）")
    ap.add_argument("--cjk-font", default="微软雅黑")
    ap.add_argument("--latin-font", default="Calibri")
    args = ap.parse_args()

    dossier = json.loads(Path(args.dossier).read_text(encoding="utf-8"))
    content = json.loads(Path(args.content).read_text(encoding="utf-8"))
    manifest_by_file = {}
    if args.manifest and Path(args.manifest).exists():
        manifest_by_file = {m["file"]: m.get("chars", 0)
                            for m in json.loads(Path(args.manifest).read_text(encoding="utf-8"))}

    accent = hexrgb(args.accent)
    subtle = RGBColor(0x55, 0x55, 0x55)
    latin, cjk = args.latin_font, args.cjk_font

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = latin; normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), cjk)
    for s in doc.sections:
        s.top_margin = Cm(2.0); s.bottom_margin = Cm(2.0)
        s.left_margin = Cm(2.2); s.right_margin = Cm(2.2)

    sec = doc.sections[0]
    hp = sec.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run(content.get("_header", "展会纪要")); set_run_font(hr, latin, cjk, size=8.5, color=subtle)
    fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run("第 "); set_run_font(fr, latin, cjk, size=9, color=subtle)
    add_page_number(fp, latin, cjk, subtle)
    fr2 = fp.add_run(" 页"); set_run_font(fr2, latin, cjk, size=9, color=subtle)

    tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.space_before = Pt(6); tp.paragraph_format.space_after = Pt(2)
    tr = tp.add_run(content.get("_title", "展会纪要")); set_run_font(tr, latin, cjk, size=20, bold=True, color=accent)
    sp = doc.add_paragraph(); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sp.paragraph_format.space_after = Pt(2)
    sr = sp.add_run(content.get("_subtitle", "")); set_run_font(sr, latin, cjk, size=11, color=subtle)
    dp = doc.add_paragraph(); dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dp.paragraph_format.space_after = Pt(10)
    dr = dp.add_run(content.get("_date", "")); set_run_font(dr, latin, cjk, size=10.5, color=subtle)

    add_heading(doc, "总体概览", latin, cjk, accent, level=1)
    for para in content.get("_overview", []):
        add_para(doc, para, latin, cjk, size=10.5, space_after=5)

    add_heading(doc, "各场记录", latin, cjk, accent, level=1)
    embedded = 0
    for entry in dossier:
        tid = entry["id"]
        c = content.get(tid, {})
        add_heading(doc, f"{entry.get('agenda_time','')}   {entry.get('title','')}", latin, cjk, accent, level=2)
        spk = c.get("speaker_note") or entry.get("speaker", "")
        aff = entry.get("affiliation", "")
        meta = f"{spk}　·　{aff}" if aff and aff != "—" else spk
        if meta.strip():
            add_para(doc, meta, latin, cjk, size=10, italic=True, color=subtle, space_after=4)
        for h in c.get("highlights", []):
            add_bullet(doc, h, latin, cjk)
        for b in c.get("body", []):
            add_para(doc, b, latin, cjk, size=10.5, space_after=3)
        kd = [str(k) for k in c.get("key_data", []) if str(k).strip()]
        if kd:
            kp = doc.add_paragraph()
            kp.paragraph_format.space_before = Pt(2); kp.paragraph_format.space_after = Pt(4)
            kr0 = kp.add_run("关键数据 / 专利："); set_run_font(kr0, latin, cjk, size=9.5, bold=True, color=subtle)
            kr1 = kp.add_run("　".join(kd[:14])); set_run_font(kr1, latin, cjk, size=9, color=subtle)
        for ph in pick_photos(entry, manifest_by_file, args.max_photos):
            cp = Path(ph.get("compressed", ""))
            if not cp.exists():
                continue
            try:
                ip = doc.add_paragraph(); ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
                ip.paragraph_format.space_before = Pt(3); ip.paragraph_format.space_after = Pt(3)
                ip.add_run().add_picture(str(cp), width=Inches(4.6))
                embedded += 1
            except Exception as e:
                print(f"  [warn] 嵌入失败 {ph.get('file')}: {e}", flush=True)

    add_heading(doc, "横向观察", latin, cjk, accent, level=1)
    for para in content.get("_closing", []):
        add_para(doc, para, latin, cjk, size=10.5, space_after=5)
    note = content.get("_scope_note")
    if note:
        add_heading(doc, "记录范围说明", latin, cjk, accent, level=2)
        add_para(doc, note, latin, cjk, size=9.5, color=subtle, space_after=4)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.out)
    print(f"[make_minutes_docx] 保存 {args.out}  嵌入图片={embedded}", flush=True)


if __name__ == "__main__":
    main()
