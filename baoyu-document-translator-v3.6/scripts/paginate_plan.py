# -*- coding: utf-8 -*-
"""Pagination pre-pass + bounded repair (v2.1, Step 4.5).

Blank pages in CJK->EN jobs come from CJK authoring artifacts (empty spacer paragraphs,
natural-flow page starts) interacting with longer English text. This script makes the
fix DETERMINISTIC (one pass, no render loop):

  1. Source page-top mapping: render/obtain source.pdf; a heading whose SOURCE text is
     the first content line of a source page gets pageBreakBefore in the output.
  2. Empty spacer paragraphs immediately preceding those page-break headings are deleted.
  3. --repair mode (bounded auto-repair, use AT MOST ONCE after a render gate reports
     blank pages): zero-height every empty paragraph (no text/drawing/sectPr) so stranded
     marks cannot occupy a page.

Usage:
  python paginate_plan.py source.pdf extracted.json translated.json output.docx
  python paginate_plan.py --repair output.docx
"""
import sys, re, json, zipfile, shutil
import pymupdf
from pathlib import Path

CHROME = re.compile(r"^(Page\s|\d+\s*$)")

def page_tops(pdf):
    doc = pymupdf.open(pdf)
    raw_tops, freq = [], {}
    for i in range(len(doc)):
        lines = [l.strip() for l in doc[i].get_text().split("\n") if l.strip()]
        for l in set(lines):
            freq[l] = freq.get(l, 0) + 1
        raw_tops.append(lines)
    n = len(doc)
    tops = []
    for lines in raw_tops:
        body = [l for l in lines if not CHROME.match(l) and freq.get(l, 0) < max(2, int(0.6 * n))]
        tops.append(body[0] if body else "")
    return tops

def flat(s):
    return re.sub(r"\s+", "", s)

def para_text(p):
    return "".join(t.text or "" for t in p.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
def qn(t): return "{%s}%s" % (W, t)

def main():
    if sys.argv[1] == "--repair":
        docx = Path(sys.argv[2])
        tmp = str(docx) + ".tmp"
        n = 0
        with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    from lxml import etree
                    root = etree.fromstring(data)
                    for p in root.findall(".//" + qn("p")):
                        txt = para_text(p)
                        if txt.strip() or p.find(".//" + qn("drawing")) is not None \
                           or p.find(".//" + qn("pict")) is not None \
                           or p.find(".//" + qn("sectPr")) is not None:
                            continue
                        ppr = p.find(qn("pPr"))
                        if ppr is None:
                            ppr = etree.SubElement(p, qn("pPr"))
                            p.insert(0, ppr)
                        for sp in ppr.findall(qn("spacing")):
                            ppr.remove(sp)
                        sp = etree.Element(qn("spacing"))
                        sp.set(qn("before"), "0"); sp.set(qn("after"), "0")
                        sp.set(qn("line"), "0"); sp.set(qn("lineRule"), "exact")
                        ppr.insert(0, sp)
                        n += 1
                    data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                zout.writestr(item, data)
        shutil.move(tmp, str(docx))
        print("repair: zeroed %d empty paragraphs" % n)
        return

    pdf, extj, trj, docx = sys.argv[1:5]
    tops = page_tops(pdf)
    tops_flat = {flat(t) for t in tops if t}
    ext = {e["key"]: e for e in json.load(open(extj, encoding="utf-8"))["elements"]}
    tr = {e["key"]: e for e in json.load(open(trj, encoding="utf-8"))["elements"]}
    targets = {}
    all_heads = "--all-headings" in sys.argv
    h1_always = "--h1-always" in sys.argv
    keys = list(ext.keys())
    first_h1 = next((i for i, k in enumerate(keys)
                     if (ext[k].get("style") or "").lower().startswith("heading 1")), len(keys))
    for pos, k in enumerate(keys):
        e = ext[k]
        st = (e.get("style") or "").lower()
        if h1_always and (st.startswith("heading 1") or st.startswith("heading1")):
            tr_parts = "".join(tr[k].get("parts", [])) if k in tr else e.get("text", "")
            targets[flat(tr_parts)] = k
            continue
        if all_heads:
            heading_like = st.startswith("heading") or "title" in st or (
                len(e.get("text", "")) < 60 and e.get("runs", 9) <= 3)
        else:
            front_matter = pos < first_h1 and len(e.get("text", "")) < 60 and e.get("runs", 9) <= 3
            heading_like = (st.startswith("heading 1") or st.startswith("heading1")
                            or st in ("title",) or st.startswith("toc") or front_matter)
        if not heading_like:
            continue
        src = flat(e.get("text", ""))
        if src and src in tops_flat:
            tr_parts = "".join(tr[k].get("parts", [])) if k in tr else e.get("text", "")
            targets[flat(tr_parts)] = k
    print("headings with source page-top start:", len(targets))

    from lxml import etree
    tmp = str(docx) + ".tmp"
    injected = deleted = 0
    with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                root = etree.fromstring(data)
                body = root.find(qn("body"))
                kids = list(body)
                for idx, child in enumerate(kids):
                    if child.tag != qn("p"):
                        continue
                    if flat(para_text(child)) not in targets:
                        continue
                    ppr = child.find(qn("pPr"))
                    if ppr is None:
                        ppr = etree.Element(qn("pPr"))
                        child.insert(0, ppr)
                    if ppr.find(qn("pageBreakBefore")) is None:
                        pbb = etree.Element(qn("pageBreakBefore"))
                        ps = ppr.find(qn("pStyle"))
                        ppr.insert(list(ppr).index(ps) + 1 if ps is not None else 0, pbb)
                        injected += 1
                    # delete empty spacers immediately before this heading
                    j = idx - 1
                    while j >= 0:
                        prev = kids[j]
                        if prev.tag != qn("p"):
                            break
                        ptxt = para_text(prev)
                        if ptxt.strip() or prev.find(".//" + qn("drawing")) is not None \
                           or prev.find(".//" + qn("sectPr")) is not None:
                            break
                        body.remove(prev)
                        deleted += 1
                        j -= 1
                # zero-height every empty section-break mark paragraph (stranded marks
                # otherwise occupy their own page) and trailing empty paragraphs
                zeroed = 0
                def zero(p):
                    ppr = p.find(qn("pPr"))
                    if ppr is None:
                        ppr = etree.SubElement(p, qn("pPr"))
                        p.insert(0, ppr)
                    for sp in ppr.findall(qn("spacing")):
                        ppr.remove(sp)
                    sp = etree.Element(qn("spacing"))
                    sp.set(qn("before"), "0"); sp.set(qn("after"), "0")
                    sp.set(qn("line"), "0"); sp.set(qn("lineRule"), "exact")
                    ppr.insert(0, sp)
                for p in body.findall(qn("p")):
                    if para_text(p).strip() or p.find(".//" + qn("drawing")) is not None:
                        continue
                    if p.find(".//" + qn("sectPr")) is not None:
                        zero(p); zeroed += 1
                for p in reversed(body.findall(qn("p"))):
                    if para_text(p).strip() or p.find(".//" + qn("drawing")) is not None \
                       or p.find(".//" + qn("sectPr")) is not None:
                        break
                    zero(p); zeroed += 1
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(item, data)
    shutil.move(tmp, str(docx))
    print("paginate_plan: pbb injected=%d, spacers deleted=%d, empty marks zeroed=%d"
          % (injected, deleted, zeroed))

if __name__ == "__main__":
    main()
