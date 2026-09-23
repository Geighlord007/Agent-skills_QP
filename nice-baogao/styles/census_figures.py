"""Census every DISPLAYED figure, not every script.

The mistake this corrects: CATALOG.md was built from the ~91 names in
`_tools/redraw/*.py`. That is a list of scripts the author wrote. What a reader sees is
275 displayed figures, and the two sets are not the same thing -- 224 figures have an
editable source, 52 have none at all, and 5 are orphans referenced by nothing.

A style document whose catalogue does not account for the whole population cannot answer
"is this figure covered by the style?" -- which is the only question it exists to answer.
"""
import collections
import csv
import os

ROOT = r"C:\Users\Windows11\Desktop\废话\Desk Research"
A = os.path.join(ROOT, "_admin")
OUT = os.path.join(A, "FIGURE_CENSUS.md")

meas = list(csv.DictReader(open(os.path.join(A, "FIGURE_MEASUREMENT.csv"),
                                encoding="utf-8-sig")))
prov = list(csv.DictReader(open(os.path.join(A, "FIGURE_PROVENANCE.csv"),
                                encoding="utf-8-sig")))
ix = {(p["document"], os.path.basename(p["media_part"])): p for p in prov}

rows = []
for m in meas:
    key = (m["document"], os.path.basename(m["media_part"]))
    p = ix.get(key, {})
    state = p.get("state", "?")
    producer = m["producer"]
    if state == "ORPHAN":
        cls = "orphan"
    elif producer == "matplotlib" and state == "KNOWN_CURRENT":
        cls = "chart"
    elif producer == "matplotlib":
        cls = "chart-no-source"
    elif state == "KNOWN_CURRENT":
        cls = "diagram"
    else:
        cls = "external-bitmap"
    rows.append({"class": cls, "document": m["document"],
                 "part": os.path.basename(m["media_part"]), "page": m["page_no"],
                 "verdict": m["verdict"], "state": state, "producer": producer,
                 "pt": m["nominal_pt"]})

counts = collections.Counter(r["class"] for r in rows)
print("displayed figures: %d" % len(rows))
for k, v in counts.most_common():
    print("  %-18s %d" % (k, v))

by_cls_doc = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    by_cls_doc[r["class"]][r["document"]].append(r)

LBL = {
    "diagram": "Drawn diagrams (editable source exists)",
    "chart": "matplotlib charts (editable source exists)",
    "external-bitmap": "External / extracted bitmaps (NO editable source)",
    "chart-no-source": "Charts with NO editable source",
    "orphan": "Orphans (referenced by no document element)",
}
COVER = {
    "diagram": "STYLE.md §8 (six families). Find the nearest precedent in the taxonomy.",
    "chart": "STYLE.md §5 (rules) + §9c (forms).",
    "external-bitmap": "STYLE.md §9d -- a CITATION, not an illustration. Do not redraw.",
    "chart-no-source": "STYLE.md §9d -- report; do not substitute a drawing.",
    "orphan": "Not displayed. Measured and reported only.",
}

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("# Figure census -- every displayed figure, by class\n\n")
    fh.write("Generated from the page-render measurement and the provenance ledger, so it\n"
             "accounts for **every figure a reader sees**, not for every script an author\n"
             "wrote. Regenerate with `_tools/work/census_displayed.py`.\n\n")
    fh.write("| class | count | covered by |\n|---|---|---|\n")
    for k, v in counts.most_common():
        fh.write("| %s | **%d** | %s |\n" % (k, v, COVER[k]))
    fh.write("\nTotal **%d** displayed figures.\n\n" % len(rows))
    fh.write("> A catalogue built from script names misses the largest class here. Of the\n"
             "> four, only two come from a script at all.\n\n")
    for k in ("diagram", "chart", "external-bitmap", "chart-no-source", "orphan"):
        if k not in by_cls_doc:
            continue
        fh.write("## %s -- %d\n\n" % (LBL[k], counts[k]))
        fh.write("%s\n\n" % COVER[k])
        for doc in sorted(by_cls_doc[k]):
            items = by_cls_doc[k][doc]
            fh.write("* **%s** (%d)\n" % (doc, len(items)))
            for r in sorted(items, key=lambda x: int(x["page"] or 0)):
                fh.write("  * p%s `%s` -- %s\n" % (r["page"], r["part"], r["verdict"]))
        fh.write("\n")
print("\nwrote %s" % OUT)
