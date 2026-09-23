# -*- coding: utf-8 -*-
"""Surgical DOCX write-back (v2.1, P0-1): set ONLY <w:t> text nodes — never run.text=.

Preserves every non-text run child that python-docx `run.text =` destroys:
w:br page breaks, w:ptab, w:fldChar/w:instrText fields, w:drawing anchors, w:pict.

Location strategy mirrors extract_docx_v2.py exactly (python-docx enumeration), so
keys align even for merged cells (row.cells grid expansion); mutation is pure lxml
w:t surgery on the located elements.

Stories covered: body paragraphs, body tables, footnotes, endnotes.
Headers/footers: NOT covered (section.header misses first/even-page parts) — use the
source-restore technique, references/cjk-en-localization-pitfalls.md §6.

Usage: python write_docx_surgical.py input.docx output.docx translated.json
"""
import sys, json, re, zipfile, shutil
from docx import Document
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XMLSPACE = "{http://www.w3.org/XML/1998/namespace}space"

def qn(t):
    return "{%s}%s" % (W, t)

def set_run_text(r_el, text):
    # Field runs: pure control runs (fldChar/instrText without w:t) never receive text
    # (merge assigns them "" anyway). WPS-style FUSED field runs (fldChar+instrText+w:t
    # in one run) DO get their w:t replaced: field nodes preserved, cached result
    # translated. Pair with `localize_cjk_en.py fields` to sanitize CJK switches.
    has_field = (r_el.find(qn("fldChar")) is not None
                 or r_el.find(qn("instrText")) is not None)
    t = r_el.find(qn("t"))
    if has_field and t is None:
        return
    if text == "\t":
        # source run text came from a w:tab node: keep/create w:tab, blank any w:t
        if t is not None:
            t.text = ""
        if r_el.find(qn("tab")) is None:
            el = etree.Element(qn("tab"))
            r_el.append(el)
        return
    if text == "\n":
        if t is not None:
            t.text = ""
        if r_el.find(qn("br")) is None:
            r_el.append(etree.Element(qn("br")))
        return
    if t is None:
        if text == "":
            return
        t = etree.SubElement(r_el, qn("t"))
    t.text = text
    if text != text.strip():
        t.set(XMLSPACE, "preserve")
    elif t.get(XMLSPACE):
        del t.attrib[XMLSPACE]
    # WPS runs may carry MULTIPLE w:t nodes: blank the extras so no source-language
    # residue survives inside the same run
    for extra in r_el.findall(qn("t")):
        if extra is not t:
            extra.text = ""

def para_run_elems(p_el):
    """Mirror of extract_docx_v2.para_runs: direct w:r + w:ins runs + w:hyperlink runs.
    Field control runs and field RESULT runs (cached SEQ/PAGEREF numbers) are excluded
    so page/caption numbers survive; WPS FUSED runs (begin+instr+w:t in one run) ARE
    included so their cached text can be translated."""
    runs = []
    state = {"mode": None}  # shared across the whole paragraph (direct + ins + hyperlink)
    def consider(r):
        fc = r.find(qn("fldChar"))
        ftype = fc.get(qn("fldCharType")) if fc is not None else None
        has_t = r.find(qn("t")) is not None
        has_instr = r.find(qn("instrText")) is not None
        if ftype == "begin":
            if has_t:
                runs.append(r)      # fused WPS run: translate cached result
            state["mode"] = "inside"
            return
        if ftype == "separate":
            state["mode"] = "result"
            return
        if ftype == "end":
            state["mode"] = None
            return
        if has_instr:
            return
        if state["mode"] in ("inside", "result"):
            txt = "".join(t.text or "" for t in r.findall(qn("t")))
            if re.fullmatch(r"[\d\.\,\;\:\s\/\-\%]*", txt):
                return
        runs.append(r)
    def collect(container):
        for r in container:
            if r.tag == qn("r"):
                consider(r)
    for c in p_el:
        if c.tag == qn("r"):
            collect([c])
        elif c.tag == qn("ins"):
            collect(list(c))
        elif c.tag == qn("hyperlink"):
            collect(list(c))
    return runs


def write_para(p_el, parts):
    runs = para_run_elems(p_el)
    for i, r in enumerate(runs):
        set_run_text(r, parts[i] if i < len(parts) else "")

def write_notes(xml_bytes, els, tag, prefix):
    root = etree.fromstring(xml_bytes)
    for note in root.findall(".//" + qn(tag)):
        if note.get(qn("type")) in ("separator", "continuationSeparator"):
            continue
        nid = note.get(qn("id"))
        pi = 0
        for p in note.findall(qn("p")):
            runs = p.findall(".//" + qn("r"))
            # extraction built parts from runs THAT HAVE w:t (footnoteRef runs excluded);
            # align parts to those same runs so the reference mark never receives text.
            text_runs = [r for r in runs if r.find(qn("t")) is not None]
            txt = "".join((r.find(qn("t")).text or "") for r in text_runs)
            if not txt.strip():
                continue
            e = els.get("%s_%s_p%d" % (prefix, nid, pi))
            if e:
                if len(e["parts"]) > len(text_runs):
                    print("WARNING %s_%s_p%d: %d parts for %d text runs; extra dropped"
                          % (prefix, nid, pi, len(e["parts"]), len(text_runs)))
                for i, r in enumerate(text_runs):
                    set_run_text(r, e["parts"][i] if i < len(e["parts"]) else "")
            pi += 1
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

def main():
    src, dst, js = sys.argv[1], sys.argv[2], sys.argv[3]
    cons_max = 80
    if "--consolidate-max" in sys.argv:
        cons_max = int(sys.argv[sys.argv.index("--consolidate-max") + 1])
    els = {e["key"]: e for e in json.load(open(js, encoding="utf-8"))["elements"]}
    doc = Document(src)
    np = nt = 0
    for i, p in enumerate(doc.paragraphs):
        e = els.get("p_body_%d" % i)
        if e:
            runs = para_run_elems(p._p)
            trs = [r for r in runs if r.find(qn("t")) is not None]
            sigs = {etree.tostring(r.find(qn("rPr"))) if r.find(qn("rPr")) is not None else b""
                    for r in trs}
            if len(trs) >= 3 and len(sigs) >= 3 and sum(len(x) for x in e["parts"]) < cons_max:
                # cover/title-style paragraph: heterogeneous run formatting would
                # patchwork the translation; consolidate into the first text run
                joined = "".join(e["parts"])
                newparts = [""] * len(runs)
                first = True
                for idx, r in enumerate(runs):
                    if r.find(qn("t")) is None:
                        newparts[idx] = e["parts"][idx] if idx < len(e["parts"]) else ""
                    elif first:
                        newparts[idx] = joined
                        first = False
                write_para(p._p, newparts)
            else:
                write_para(p._p, e["parts"])
            np += 1
    for ti, t in enumerate(doc.tables):
        for ri, row in enumerate(t.rows):
            for ci, cell in enumerate(row.cells):
                e = els.get("t_body_%d_r%d_c%d" % (ti, ri, ci))
                if not e:
                    continue
                k = 0
                for p in cell._tc.findall(qn("p")):
                    for r in para_run_elems(p):
                        set_run_text(r, e["parts"][k] if k < len(e["parts"]) else "")
                        k += 1
                nt += 1
    # header/footer variants (default + first + even), mirroring extract_docx_v2 keys
    from docx.table import Table
    for si, section in enumerate(doc.sections):
        for attr, suffix, kind in (("header", "", "header"), ("first_page_header", "first", "header"),
                                   ("even_page_header", "even", "header"),
                                   ("footer", "", "footer"), ("first_page_footer", "first", "footer"),
                                   ("even_page_footer", "even", "footer")):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            pre, tpre = "p_%s%s_%s_" % (kind, suffix, si), "t_%s%s_%s_" % (kind, suffix, si)
            pi = ti = 0
            for child in part._element:
                tag = child.tag.split("}")[-1]
                if tag == "p":
                    e = els.get("%s%d" % (pre, pi))
                    if e:
                        write_para(child, e["parts"])
                    pi += 1
                elif tag == "tbl":
                    t = Table(child, part)
                    for ri, row in enumerate(t.rows):
                        for ci, cell in enumerate(row.cells):
                            e = els.get("%s%d_r%d_c%d" % (tpre, ti, ri, ci))
                            if not e:
                                continue
                            k = 0
                            for p in cell._tc.findall(qn("p")):
                                for r in para_run_elems(p):
                                    set_run_text(r, e["parts"][k] if k < len(e["parts"]) else "")
                                    k += 1
                    ti += 1
    # text boxes in body
    for n, tb in enumerate(doc.element.body.findall(".//" + qn("txbxContent"))):
        pi = 0
        for p in tb.findall(qn("p")):
            txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
            if not txt.strip():
                continue
            e = els.get("txbx_%d_p%d" % (n, pi))
            if e:
                write_para(p, e["parts"])
            pi += 1
    # text boxes in body (same enumeration order as extract_docx_v2)
    for n, tb in enumerate(doc.element.body.findall(".//" + qn("txbxContent"))):
        pi = 0
        for p in tb.findall(qn("p")):
            txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
            if not txt.strip():
                continue
            e = els.get("txbx_%d_p%d" % (n, pi))
            if e:
                write_para(p, e["parts"])
            pi += 1
        # tables nested inside text boxes (mirror extract enumeration)
        for ti, tbl in enumerate(tb.findall(qn("tbl"))):
            for ri, tr_el in enumerate(tbl.findall(qn("tr"))):
                seen_tc, ci = set(), 0
                for tc in tr_el.findall(qn("tc")):
                    if id(tc) in seen_tc:
                        continue
                    seen_tc.add(id(tc))
                    e = els.get("t_txbx_%d_%d_r%d_c%d" % (n, ti, ri, ci))
                    if e:
                        runs = [r for p in tc.findall(".//" + qn("p"))
                                for r in para_run_elems(p)]
                        for i, r in enumerate(runs):
                            set_run_text(r, e["parts"][i] if i < len(e["parts"]) else "")
                    ci += 1
    # text boxes inside header/footer parts (mirror extract enumeration)
    for si, section in enumerate(doc.sections):
        for attr, scope in (("header", "h"), ("footer", "f"),
                            ("first_page_header", "hfirst"), ("first_page_footer", "ffirst")):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            for n, tb in enumerate(part._element.findall(".//" + qn("txbxContent"))):
                pi = 0
                for p in tb.findall(qn("p")):
                    txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
                    if not txt.strip():
                        continue
                    e = els.get("txbx_%s%d_%d_p%d" % (scope, si, n, pi))
                    if e:
                        write_para(p, e["parts"])
                    pi += 1
    # paragraphs inside SDT content controls
    seen_sdt = set()
    for idx, sdt in enumerate(doc.element.body.findall(".//" + qn("sdt"))):
        if id(sdt) in seen_sdt:
            continue
        seen_sdt.add(id(sdt))
        pi = 0
        for p in sdt.findall(".//" + qn("p")):
            txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
            if not txt.strip():
                continue
            e = els.get("p_sdt_%d_p%d" % (idx, pi))
            if e:
                write_para(p, e["parts"])
            pi += 1
    tmp = dst + ".tmp"
    doc.save(tmp)
    # footnotes / endnotes via zip surgery
    zin = zipfile.ZipFile(tmp)
    names = zin.namelist()
    datas = {n: zin.read(n) for n in names}
    zin.close()
    if "word/footnotes.xml" in datas:
        datas["word/footnotes.xml"] = write_notes(datas["word/footnotes.xml"], els, "footnote", "fn")
    if "word/endnotes.xml" in datas:
        datas["word/endnotes.xml"] = write_notes(datas["word/endnotes.xml"], els, "endnote", "en")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, datas[n])
    import os
    os.remove(tmp)
    print("surgical write-back done: %d paragraphs, %d cells -> %s" % (np, nt, dst))

if __name__ == "__main__":
    main()
