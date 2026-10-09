# -*- coding: utf-8 -*-
"""Rewrite TOC entry page numbers from the RENDERED pdf (v2.1, Step 7).

Detects body TOC entries (paragraphs whose text is 'Title<TAB>digits' or uses dot
leaders) and sets each entry's digits-run to the page where the title actually
renders (exact normalized match of a content line, searched after the TOC pages).

Usage: python toc_pages.py output.pdf output.docx
"""
import sys, re, zipfile, shutil
import pymupdf
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
def qn(t): return "{%s}%s" % (W, t)
def flat(s): return re.sub(r"\s+", "", s)

def main():
    pdf, docx = sys.argv[1], sys.argv[2]
    doc = pymupdf.open(pdf)
    pages = []
    for i in range(len(doc)):
        pages.append([flat(l) for l in doc[i].get_text().split("\n") if l.strip()])
    tmp = str(docx) + ".tmp"
    fixed = 0
    with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                root = etree.fromstring(data)
                for p in root.find(qn("body")).findall(qn("p")):
                    ts = p.findall(".//" + qn("t"))
                    txt = "".join(t.text or "" for t in ts)
                    m = re.match(r"^(.+?)[\t\.…·\s]*?(\d+)\s*$", txt)
                    if not m or "\t" not in txt and "..." not in txt and "…" not in txt:
                        continue
                    title = flat(m.group(1))
                    old = m.group(2)
                    if len(title) < 4:
                        continue
                    target = None
                    for i, lines in enumerate(pages):
                        if title in lines and not any(l == title + old for l in lines):
                            target = i + 1
                            break
                    if target is None or str(target) == old:
                        continue
                    for t in reversed(ts):
                        if (t.text or "").strip() == old:
                            t.text = str(target)
                            fixed += 1
                            break
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(item, data)
    shutil.move(tmp, str(docx))
    print("toc_pages: rewrote %d entry page numbers" % fixed)

if __name__ == "__main__":
    main()
