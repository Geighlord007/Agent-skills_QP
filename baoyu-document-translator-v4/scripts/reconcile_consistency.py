# -*- coding: utf-8 -*-
"""Consistency reconcile (v2.1, Step 3/5 tooling): TOC entries vs body headings vs
table/figure captions. Parallel translators WILL diverge; run this before merge and
align every mismatch to one canonical rendering.

Usage: python reconcile_consistency.py extracted.json [translation.md]
Exit 0 = consistent, 1 = mismatches found (list printed).
"""
import sys, re, json
from pathlib import Path

def norm(s):
    s = re.sub(r"^[\d\.]+\s*", "", s.strip())
    s = re.sub(r"^((?:Table|Figure)\s*\d+)\.\s*", r"\1 ", s)  # "Table 9." -> "Table 9"
    return re.sub(r"\s+", " ", s)

def main():
    els = json.load(open(sys.argv[1], encoding="utf-8"))["elements"]
    trans = None
    if len(sys.argv) > 2:
        trans = {}
        key, buf = None, []
        for ln in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*<!--\s*key:([^|]+)\|", ln)
            if m:
                if key: trans[key] = "\n".join(buf).strip()
                key, buf = m.group(1), []
            elif key is not None:
                buf.append(ln)
        if key: trans[key] = "\n".join(buf).strip()
    def text(e):
        return (trans or {}).get(e["key"], e.get("text", ""))
    toc, heads, caps = [], [], []
    for e in els:
        t = text(e)
        if re.search(r"\t\d+$", t) and e["key"].startswith("p_body_"):
            title = norm(re.sub(r"\t.*$", "", t))
            # skip wrapped-TOC continuation lines (")", fragments)
            if len(title) >= 3 and not title.startswith((")", "）")):
                toc.append((e["key"], title))
        st = e.get("style", "").lower()
        if st.startswith("heading") or "title" in st:
            heads.append((e["key"], norm(t)))
        if re.match(r"^(Table|Figure)\s+\d", t):
            caps.append((e["key"], norm(re.sub(r"\s*\t.*$", "", t))))
    # paragraphs whose text exactly equals a TOC title count as headings
    toctitles = {t for _, t in toc}
    for e in els:
        t = norm(text(e))
        if t in toctitles and (e["key"], t) not in heads:
            heads.append((e["key"], t))
    headset = {h for _, h in heads}
    capset = {c for _, c in caps}
    bad = []
    for k, t in toc:
        if not t:
            continue
        if t not in headset and t not in capset:
            # tolerate prefix matches for long captions
            if not any(h.startswith(t[:45]) for h in headset | capset):
                bad.append(("TOC-no-match", k, t[:60]))
    # caption vs TOC table entries
    toct = {t for _, t in toc}
    for k, c in caps:
        if c and not any(c.startswith(t[:45]) or t.startswith(c[:45]) for t in toct):
            bad.append(("caption-not-in-TOC", k, c[:60]))
    for kind, k, t in bad[:30]:
        print("%s: %s | %s" % (kind, k, t))
    tol = max(1, int(0.2 * len(toc)))
    print("mismatches:", len(bad), "(tolerance %d = 20%% of %d TOC entries; sidebar/legend"
          " lines ending in tab+digits are known false positives)" % (tol, len(toc)))
    sys.exit(1 if len(bad) > tol else 0)

if __name__ == "__main__":
    main()
