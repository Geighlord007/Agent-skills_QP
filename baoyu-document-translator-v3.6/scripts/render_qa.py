# -*- coding: utf-8 -*-
"""Rendered-output QA for translated DOCX (v2.1 addendum, Step 7 mandatory).

Usage:
  python render_qa.py out.pdf [src.pdf] [--toc-check] [--cjk-scan] [--montage PREFIX]

Checks (rendered PDF only — text-level QA cannot see layout):
  1. blank-page scan with AUTO-DETECTED header/footer lines (lines whose normalized
     text appears on >=60% of pages) plus generic page-number patterns. No document-
     specific strings are hardcoded.
  2. --cjk-scan   : any CJK character rendered anywhere (catches live fields with CJK
     format switches, Chinese list numbering, leftover glyphs — invisible to w:t scans).
  3. --toc-check  : TOC entry page numbers vs actual heading/caption pages.
  4. --montage P  : 3x4 thumbnail sheets P_01.png ... for mandatory human visual review.
Exit code: 0 = clean, 1 = any blank page / TOC mismatch / CJK hit.
"""
import re, sys, math, io
import pymupdf

CJK = re.compile(r"[\u4e00-\u9fff]")
PAGENUM = re.compile(r"^Page\s*\d+|\b\d+\s*/\s*\d+$|^\d{1,4}$")


def page_lines(doc):
    return [[l.strip() for l in doc[i].get_text().split("\n") if l.strip()]
            for i in range(len(doc))]


def chrome_lines(lp):
    """Lines appearing on >=60% of pages = header/footer chrome."""
    from collections import Counter
    c = Counter()
    for lines in lp:
        for l in set(lines):
            c[l] += 1
    thr = max(2, int(0.6 * len(lp)))
    return {l for l, n in c.items() if n >= thr}


def main():
    args = sys.argv[1:]
    pdfs = [a for a in args if not a.startswith("--") and a.endswith(".pdf")]
    pdf_path = pdfs[0]
    src_path = pdfs[1] if len(pdfs) > 1 else None
    want_toc = "--toc-check" in args
    want_cjk = "--cjk-scan" in args
    montage = None
    if "--montage" in args:
        i = args.index("--montage")
        montage = args[i + 1] if i + 1 < len(args) else "sheet"
    doc = pymupdf.open(pdf_path)
    n = len(doc)
    lp = page_lines(doc)
    chrome = chrome_lines(lp)
    problems = 0

    print("pages:", n)
    if src_path:
        print("source pages:", len(pymupdf.open(src_path)))

    # 1 blank pages (a page with images but no text is a figure plate, not a blank)
    blanks = [i + 1 for i in range(n)
              if not [l for l in lp[i] if l not in chrome and not PAGENUM.search(l)]
              and not doc[i].get_images()]
    print("blank pages:", blanks if blanks else "none")
    problems += len(blanks)

    # 2 rendered CJK (policy-aware: --cjk-allow whitelist substrings for deliberate
    # bilingual retention; --ignore-substr for documented export artifacts)
    allow = []
    if "--cjk-allow" in sys.argv:
        ap = sys.argv[sys.argv.index("--cjk-allow") + 1]
        allow = [l.strip() for l in open(ap, encoding="utf-8") if l.strip()]
    ignore = []
    if "--ignore-substr" in sys.argv:
        ignore = sys.argv[sys.argv.index("--ignore-substr") + 1].split("|")
    if want_cjk:
        hits = [(i + 1, l[:60]) for i in range(n) for l in lp[i]
                if CJK.search(l) and not any(a in l for a in allow)
                and not any(g in l for g in ignore if g)]
        print("rendered CJK lines:", len(hits),
              ("(allowlist/ignore applied)" if allow or ignore else ""))
        for h in hits[:10]:
            print("   ", h)
        problems += len(hits)

    # 3 TOC page numbers (skip when too few entries detected: heuristic window)
    toc_min = 5
    if "--toc-min-entries" in sys.argv:
        toc_min = int(sys.argv[sys.argv.index("--toc-min-entries") + 1])
    if want_toc:
        norm = lambda s: re.sub(r"^[\d\.]+\s*", "", s)
        entries = {}
        for i in range(0, min(8, n)):
            for l in lp[i]:
                m = re.match(r"^(.+?)\.{3,}\s*(\d+)\s*$", l)
                if m:
                    entries[m.group(1).strip()] = int(m.group(2))

        def actual(t):
            t = t.replace("&amp;", "&")
            for i in range(4, n):
                for ln in lp[i]:
                    nl = norm(ln)
                    if nl == t or (len(t) > 25 and nl.startswith(t[:45])):
                        return i + 1
            return None
        bad = []
        for t, pg in entries.items():
            a = actual(norm(t).strip())
            if a and a != pg:
                bad.append((t[:50], pg, a))
        print("TOC entries:", len(entries), "| mismatches:", len(bad))
        if len(entries) < toc_min:
            print("TOC check skipped: fewer than %d entries detected (heuristic window)" % toc_min)
        else:
            for b in bad[:10]:
                print("   ", b)
            problems += len(bad)

    # 4 montage
    if montage:
        from PIL import Image
        per, cols, rows = 12, 3, 4
        for s in range(math.ceil(n / per)):
            pages = list(range(s * per, min(n, (s + 1) * per)))
            imgs = [Image.open(io.BytesIO(doc[i].get_pixmap(dpi=55).tobytes("png")))
                    for i in pages]
            W = max(im.width for im in imgs); H = max(im.height for im in imgs)
            sheet = Image.new("RGB", (W * cols, H * rows), "white")
            for k, im in enumerate(imgs):
                sheet.paste(im, ((k % cols) * W, (k // cols) * H))
            sheet.save("%s_%02d.png" % (montage, s + 1))
        print("montage sheets:", math.ceil(n / per), "(REVIEW EVERY SHEET VISUALLY)")

    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
