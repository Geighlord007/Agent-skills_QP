#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUDIT STEP 3 -- find where Word actually put each displayed image.

Reads the PDF Word produced and pairs every `w:drawing` / `v:imagedata` placement from
`document.xml` with the rectangle the image really occupies on the page. The pairing is
scored on three independent signals:

  * the asked-for display size (`wp:extent` / VML style) against the placed rect size
  * the media part's own pixel aspect against the placed rect aspect
  * the media part's own pixel size against the pixel size of the image Word embedded

and resolved by a greedy minimum-cost assignment, so no rect is used twice. Tiny images
(<= 8 px) are Word's own 2x2 glyph placeholders, not figures, and are excluded from the
candidate set -- they are counted and reported instead.

    python locate.py     ->  placements.json
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import pymupdf  # noqa: E402

MIN_FIGURE_PX = 8


def aspect(rec):
    pw, ph = rec.get("px_w"), rec.get("px_h")
    if pw and ph:
        return pw / ph
    return None


def rects_on_page(page):
    out = []
    for info in page.get_image_info(xrefs=True):
        xref = info.get("xref", 0)
        w, h = info.get("width") or 0, info.get("height") or 0
        bbox = info.get("bbox")
        if not bbox:
            continue
        r = pymupdf.Rect(bbox)
        if r.width <= 0.5 or r.height <= 0.5:
            continue
        out.append({"xref": xref, "px_w": w, "px_h": h, "rect": r,
                    "tiny": (w <= MIN_FIGURE_PX or h <= MIN_FIGURE_PX)})
    return out


def cost(pl, r):
    """Size + aspect agreement.

    The width the XML asks for is the reliable key: in this corpus Word prints the figure
    at the asked WIDTH and rescales the height to fit its container, so height and aspect
    must be weighted down or every squeezed figure misses. The embedded pixel size is not
    used at all: Word resamples every image on export (a 7528 px figure comes out 1220 px),
    so pixel dimensions say nothing about identity."""
    c = 0.0
    aw, ah = (pl.get("extent_pt") or [None, None])[:2]
    if aw:
        c += abs(math.log(max(1e-6, r["rect"].width) / aw))
    if ah:
        c += 0.5 * abs(math.log(max(1e-6, r["rect"].height) / ah))
    ar = aspect(pl)
    if ar:
        c += 0.5 * abs(math.log((r["rect"].width / r["rect"].height) / ar))
    return c


def aspect_cost(pl, r):
    ar = aspect(pl)
    if not ar:
        return 99.0
    return abs(math.log((r["rect"].width / r["rect"].height) / ar))


MAX_COST = 0.50          # width err 65 % / height+aspect err ~40 % each
MAX_ASPECT_COST = 0.12


def main() -> int:
    inv = json.load(open(os.path.join(HERE, "inventory_raw.json"), encoding="utf-8"))
    status_path = os.path.join(HERE, "render_status.json")
    status = json.load(open(status_path, encoding="utf-8")) if os.path.exists(status_path) else {}

    all_docs = []
    diag = {"docs_rendered": 0, "docs_missing_pdf": 0, "placements": 0,
            "matched": 0, "unmatched_placement": 0, "unmatched_rect": 0,
            "tiny_rects_ignored": 0, "big_rects_unused": 0}
    for d in inv["documents"]:
        if not d["placements"]:
            continue
        rel = d["document"]
        st = status.get(rel) or {}
        slug = st.get("slug")
        pdf = os.path.join(HERE, "pdf", (slug + ".pdf")) if slug else None
        if not pdf or not os.path.exists(pdf):
            diag["docs_missing_pdf"] += 1
            all_docs.append({"document": rel, "pdf": None, "items": [],
                             "note": "not rendered"})
            continue
        diag["docs_rendered"] += 1
        doc = pymupdf.open(pdf)
        rects = []                       # (page_no, info)
        tiny = 0
        for pno in range(doc.page_count):
            for r in rects_on_page(doc[pno]):
                if r["tiny"]:
                    tiny += 1
                    continue
                rects.append((pno + 1, r))
        doc.close()
        diag["tiny_rects_ignored"] += tiny

        placements = d["placements"]
        pairs = []
        for pi, pl in enumerate(placements):
            for ri, (pno, r) in enumerate(rects):
                c = cost(pl, r)
                if c <= MAX_COST:
                    pairs.append((c, pi, ri))
        pairs.sort(key=lambda t: t[0])
        taken_p, taken_r = set(), set()
        assign = {}
        for c, pi, ri in pairs:
            if pi in taken_p or ri in taken_r:
                continue
            taken_p.add(pi)
            taken_r.add(ri)
            assign[pi] = (ri, c, "size+aspect")
        # pass 2 -- floating pictures inside a VML group carry an extent that does not
        # describe their printed size, so fall back to the media part's own aspect, and
        # only when that leaves exactly one candidate.
        left_p = [pi for pi in range(len(placements)) if pi not in taken_p]
        left_r = [ri for ri in range(len(rects)) if ri not in taken_r]
        for pi in left_p:
            cands = []
            for ri in left_r:
                if ri in taken_r:
                    continue
                c = aspect_cost(placements[pi], rects[ri][1])
                if c <= MAX_ASPECT_COST:
                    cands.append((c, ri))
            cands.sort()
            if len(cands) == 1:
                c, ri = cands[0]
                taken_p.add(pi)
                taken_r.add(ri)
                assign[pi] = (ri, c, "aspect-only")
        # pass 3 -- leftovers pair up one for one in document order. Floating pictures
        # inside a VML group carry an extent that does not describe their printed size
        # (Biomining's decorative arrow icons), so order is the only signal left.
        lp = [pi for pi in range(len(placements)) if pi not in taken_p]
        lr = [ri for ri in range(len(rects)) if ri not in taken_r]
        if lp and len(lp) == len(lr):
            for pi, ri in zip(sorted(lp), sorted(lr)):
                taken_p.add(pi)
                taken_r.add(ri)
                assign[pi] = (ri, None, "order")

        items = []
        for pi, pl in enumerate(placements):
            if pi in assign:
                ri, c, how = assign[pi]
                pno, r = rects[ri]
                items.append({
                    "seq": pl["seq"], "media_part": pl.get("shown_target"),
                    "kind": pl.get("kind"), "producer": pl.get("producer"),
                    "px_w": pl.get("px_w"), "px_h": pl.get("px_h"),
                    "extent_pt": pl.get("extent_pt"), "extent_src": pl.get("extent_src"),
                    "page_no": pno,
                    "rect_pt": [round(r["rect"].x0, 3), round(r["rect"].y0, 3),
                                round(r["rect"].x1, 3), round(r["rect"].y1, 3)],
                    "placed_pt": [round(r["rect"].width, 3), round(r["rect"].height, 3)],
                    "pdf_img_px": [r["px_w"], r["px_h"]],
                    "match_cost": (round(c, 4) if c is not None else None),
                    "match_kind": how,
                })
                diag["matched"] += 1
                diag["match_kind_" + how] = diag.get("match_kind_" + how, 0) + 1
            else:
                items.append({
                    "seq": pl["seq"], "media_part": pl.get("shown_target"),
                    "kind": pl.get("kind"), "producer": pl.get("producer"),
                    "px_w": pl.get("px_w"), "px_h": pl.get("px_h"),
                    "extent_pt": pl.get("extent_pt"), "extent_src": pl.get("extent_src"),
                    "page_no": None, "rect_pt": None, "placed_pt": None,
                    "pdf_img_px": None, "match_cost": None,
                })
                diag["unmatched_placement"] += 1
        unused = [i for i in range(len(rects)) if i not in taken_r]
        diag["big_rects_unused"] += len(unused)
        diag["placements"] += len(placements)
        all_docs.append({
            "document": rel, "pdf": os.path.relpath(pdf, ROOT), "items": items,
            "rects_found": len(rects), "tiny_skipped": tiny,
            "unused_rects": [{"page": rects[i][0],
                              "placed_pt": [round(rects[i][1]["rect"].width, 2),
                                            round(rects[i][1]["rect"].height, 2)],
                              "pdf_img_px": [rects[i][1]["px_w"], rects[i][1]["px_h"]]}
                             for i in unused],
        })

    with open(os.path.join(HERE, "placements.json"), "w", encoding="utf-8") as fh:
        json.dump({"documents": all_docs, "diagnostics": diag}, fh,
                  ensure_ascii=False, indent=1)
    print(json.dumps(diag, indent=1))
    for d in all_docs:
        if d.get("unused_rects"):
            print(f"  unused rects in {d['document']}: {d['unused_rects'][:4]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
