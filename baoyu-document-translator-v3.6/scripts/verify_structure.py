# -*- coding: utf-8 -*-
"""Structure-preservation gate (v2.1, P0): fail if write-back destroyed run structure.

Compares counts of structure-bearing nodes between source and output docx:
  w:instrText, w:fldChar, w:drawing, w:pict, w:ptab, w:br type="page", w:hyperlink
Also verifies every translated key's concatenated text appears in the output story text.

Usage: python verify_structure.py source.docx output.docx translated.json
Exit 0 = preserved, 1 = loss detected.
"""
import sys, re, json, zipfile, html

NODES = [r"<w:instrText", r"<w:fldChar", r"<w:drawing>", r"<w:pict>", r"<w:ptab",
         r'<w:br w:type="page"/>', r"<w:hyperlink"]

def counts(z):
    c = {}
    for n in z.namelist():
        if not n.endswith(".xml"):
            continue
        x = z.read(n).decode("utf-8", "ignore")
        for pat in NODES:
            c[pat] = c.get(pat, 0) + len(re.findall(pat, x))
    return c

def fa_text(x):
    """Field-aware text concat: skip field RESULT runs (cached SEQ/PAGEREF numbers sit
    between translated runs and would break adjacency); keep fused-run cached text and
    static source-language text inside field results (TOC entry titles, cached dates)."""
    toks = list(re.finditer(r'<w:fldChar w:fldCharType="(\w+)"|<w:t[^>]*>([^<]*)</w:t>', x))
    pieces = []
    mode = None
    i = 0
    while i < len(toks):
        m = toks[i]
        if m.group(1):
            ftype = m.group(1)
            if ftype == "begin":
                mode = "inside"
                if i + 1 < len(toks) and toks[i + 1].group(2) is not None:
                    pieces.append(html.unescape(toks[i + 1].group(2)))
                    i += 1
            elif ftype == "separate":
                mode = "result"
            elif ftype == "end":
                mode = None
        else:
            if mode is None:
                pieces.append(html.unescape(m.group(2)))
            elif mode == "result":
                t = m.group(2)
                # exclude only purely-numeric generated results (SEQ/PAGEREF/PAGE);
                # static content inside field results (TOC titles, cached dates,
                # alphanumeric codes) is translatable and must stay in the concat
                if not re.fullmatch(r"[\d\.\,\;\:\s\/\-\%]*", t):
                    pieces.append(html.unescape(t))
        i += 1
    return "".join(pieces)


def main():
    src, out, js = sys.argv[1], sys.argv[2], sys.argv[3]
    cs, co = counts(zipfile.ZipFile(src)), counts(zipfile.ZipFile(out))
    bad = [(p, cs[p], co[p]) for p in NODES if co[p] < cs[p]]
    for p, a, b in bad:
        print("LOSS %s: source=%d output=%d" % (p, a, b))
    # text presence check (body story); unescape entities; whitespace-insensitive;
    # tolerate merged-cell duplicate keys (same source text, last-write-wins per tc)
    import html
    z = zipfile.ZipFile(out)
    x = z.read("word/document.xml").decode("utf-8")
    raw = fa_text(x)
    alltext = re.sub(r"\s+", "", raw)
    els = json.load(open(js, encoding="utf-8"))["elements"]
    expect_cjk = "--expect-cjk" in sys.argv
    def flat(s):
        return re.sub(r"\s+", "", s)
    def pn(s):
        # punctuation-insensitive presence: period/colon variants between TOC lists,
        # captions and their translations must not read as missing text
        return re.sub(r"[.,;:!?]", "", flat(s))
    cellpos = {}
    for e in els:
        if e.get("type") == "table_cell":
            cellpos.setdefault((e.get("table"), e.get("row"), e.get("col")), []).append(e)
    def cell_won(e):
        """Merged-cell duplicate exemption: another key for the SAME physical cell has
        its translated text present in the output (last-write-wins). Never exempts the
        element by its own source text (that made the full-text check vacuous)."""
        for e2 in cellpos.get((e.get("table"), e.get("row"), e.get("col")), []):
            if e2 is not e:
                t2 = html.unescape("".join(e2.get("parts", [])).strip())
                if len(t2) > 25 and flat(t2) in alltext:
                    return True
        return False
    alltext_pn = pn(raw)
    miss = 0
    for e in els:
        if e.get("story") not in ("body", "textbox", "sdt", None):
            continue
        t = html.unescape("".join(e.get("parts", [])).strip())
        if len(t) > 25 and pn(t) not in alltext_pn:
            if e.get("type") == "table_cell" and cell_won(e):
                continue  # merged-cell duplicate: another variant won the cell
            miss += 1
            if miss <= 5:
                print("TEXT MISSING:", t[:60])
    print("missing-text elements:", miss)
    # translation completeness vs source (cross-lingual length-ratio heuristic):
    # catches translator/merge truncation that the presence check cannot see because
    # the output faithfully mirrors a truncated translated.json
    trunc = 0
    for e in els:
        if e.get("story") not in ("body", None):
            continue
        s = flat(e.get("text", ""))
        t = flat(html.unescape("".join(e.get("parts", []))))
        if len(s) > 40 and t:
            ratio = len(t) / len(s)
            # direction-aware completeness bounds: CJK->EN normally expands (ratio
            # ~1.5-4), EN->CJK contracts (~0.4-0.8); truncation falls far below either
            src_cjk = bool(re.search(r"[\u4e00-\u9fff]", e.get("text", "")))
            lo = 0.5 if src_cjk else 0.2
            hi = 4.0 if expect_cjk else 8.0
            if ratio < lo or ratio > hi:
                trunc += 1
                if trunc <= 5:
                    print("SUSPECT TRUNCATION (ratio %.2f):" % ratio, e["key"], t[:50])
    print("suspect-truncation elements:", trunc)
    problems = bool(bad) or miss > 0 or trunc > 0

    # CJK residue across ALL word parts (catches untranslated headers/footers/footnotes/
    # textboxes that body-only checks miss; rFonts attrs are not w:t so fonts don't trip).
    # For EN->CJK jobs pass --expect-cjk to invert semantics (skip this check).
    expect_cjk = "--expect-cjk" in sys.argv
    allow = []
    if "--cjk-allow" in sys.argv:
        ap = sys.argv[sys.argv.index("--cjk-allow") + 1]
        allow = [l.strip() for l in open(ap, encoding="utf-8") if l.strip()]
    cjk = re.compile(r"[\u4e00-\u9fff]")
    zo = zipfile.ZipFile(out)
    cjk_hits = []
    if not expect_cjk:
        for n in zo.namelist():
            if n.startswith("word/") and n.endswith(".xml"):
                for t in re.findall(r"<w:t[^>]*>([^<]*)</w:t>", zo.read(n).decode("utf-8", "ignore")):
                    if cjk.search(t) and not any(a in t for a in allow):
                        cjk_hits.append((n, t[:40]))
        if cjk_hits:
            problems = True
            print("CJK RESIDUE in output parts:", len(cjk_hits))
            for h in cjk_hits[:8]:
                print("   ", h)

    # story coverage: every translated header/footer/footnote key's text must appear
    # in the corresponding output parts (surgical writer skips headers/footers by
    # design — this check forces the source-restore step to actually happen)
    els = json.load(open(js, encoding="utf-8"))["elements"]
    part_text = {}
    for n in zo.namelist():
        if n.startswith("word/") and n.endswith(".xml"):
            part_text[n] = fa_text(zo.read(n).decode("utf-8", "ignore"))
    def flat(s):
        return re.sub(r"\s+", "", s)
    all_hdr = "".join(flat(v) for n, v in part_text.items()
                      if re.search(r"(header|footer)\d+\.xml", n))
    all_fn = "".join(flat(v) for n, v in part_text.items() if "footnotes.xml" in n or "endnotes.xml" in n)
    uncov = 0
    for e in els:
        st = e.get("story", "body")
        t = flat("".join(e.get("parts", [])))
        if len(t) < 8:
            continue
        if st.startswith(("header", "footer")) and t not in all_hdr:
            uncov += 1
            if uncov <= 5:
                print("UNCOVERED %s: %s" % (st, t[:40]))
        if st.startswith(("footnote", "endnote")) and t not in all_fn:
            uncov += 1
            if uncov <= 5:
                print("UNCOVERED %s: %s" % (st, t[:40]))
    print("uncovered non-body elements:", uncov)
    problems = problems or uncov > 0

    # merged-cell duplicate keys (same table+text, multiple keys -> one physical cell)
    seen = {}
    dup = 0
    for e in els:
        k = e.get("key", "")
        if k.startswith("t_"):
            sig = (k.split("_r")[0], flat(e.get("text", ""))[:50])
            if sig in seen:
                dup += 1
            seen[sig] = k
    if dup:
        print("WARNING merged-cell duplicate keys:", dup, "(last-write-wins; reconcile variants)")

    if problems:
        sys.exit(1)
    print("structure gate: PASS")

if __name__ == "__main__":
    main()
