#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUDIT STEP 4 -- measure the ink.

For every placement located in step 3, crop the figure's rectangle out of the 600-dpi
render of the ACTUAL printed page and measure the ink in it with `ink.analyse`.
1 px = 0.12 pt.

Runs incrementally and is resumable: whatever has been measured is written to
`measured.json` after every document, so a stop leaves usable output.

    python measure.py [--only SUB] [--force] [--crops-for LIST]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import pymupdf  # noqa: E402

from ink import analyse, smallest_text, PT_PER_PX  # noqa: E402

DPI = 600
CROPDIR = os.path.join(HERE, "crops")
MAX_CROP_PX = 20000               # refuse absurd rects


def crop_gray(page, rect):
    z = DPI / 72.0
    clip = pymupdf.Rect(rect)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip,
                          colorspace=pymupdf.csGRAY, alpha=False)
    if pix.width > MAX_CROP_PX or pix.height > MAX_CROP_PX or pix.width < 2 or pix.height < 2:
        return None
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return np.ascontiguousarray(arr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    pl = json.load(open(os.path.join(HERE, "placements.json"), encoding="utf-8"))
    out_path = os.path.join(HERE, "measured.json")
    done = {}
    if os.path.exists(out_path) and not a.force:
        done = json.load(open(out_path, encoding="utf-8")).get("documents", {})

    docs = pl["documents"]
    if a.only:
        docs = [d for d in docs if a.only.lower() in d["document"].lower()]

    os.makedirs(CROPDIR, exist_ok=True)
    for i, d in enumerate(docs, 1):
        rel = d["document"]
        if rel in done and not a.force:
            print(f"[{i:>2}/{len(docs)}] cached {rel}", flush=True)
            continue
        if not d.get("pdf"):
            done[rel] = {"items": [], "note": "no PDF"}
            continue
        pdf = os.path.join(ROOT, d["pdf"])
        if not os.path.exists(pdf):
            done[rel] = {"items": [], "note": "PDF missing"}
            continue
        doc = pymupdf.open(pdf)
        items = []
        for it in d["items"]:
            rec = dict(it)
            rec.pop("rect_pt", None)
            if not it.get("rect_pt"):
                rec.update({"smallest_text_pt": None, "confidence": "unmeasurable",
                            "verdict": "UNMEASURABLE",
                            "note": "placement not located on any page"})
                items.append(rec)
                continue
            page = doc[it["page_no"] - 1]
            gray = crop_gray(page, it["rect_pt"])
            if gray is None:
                rec.update({"smallest_text_pt": None, "confidence": "unmeasurable",
                            "verdict": "UNMEASURABLE", "note": "crop failed or too large"})
                items.append(rec)
                continue
            res = analyse(gray)
            st = smallest_text(res)
            rec.update({
                "crop_px": res["size_px"], "ink": res["ink"],
                "photographic": res["photographic"],
                "stamp_families": res["stamp_families"],
                "pattern_components": res["pattern_components"],
                "n_runs": len(res["runs"]),
                "n_text_runs": sum(1 for r in res["runs"] if r["kind"] == "TEXT"),
                "n_mark_runs": sum(1 for r in res["runs"] if r["kind"] == "MARK"),
                "n_unsure_runs": sum(1 for r in res["runs"] if r["kind"] == "UNSURE"),
                "n_lines": len(res["lines"]),
                "lines": [{k: v for k, v in ln.items() if k != "runs"} |
                          {"runs": [{kk: vv for kk, vv in r.items() if kk != "why"}
                                    for r in ln["runs"]]}
                          for ln in res["lines"]],
                "runs": res["runs"],
                "smallest_text_pt": st["pt"], "confidence": st["confidence"],
                "note": st.get("note", ""), "range_pt": st.get("range_pt"),
                "nominal_pt": st.get("nominal_pt"), "glyph_class": st.get("glyph_class"),
                "line_extent_pt": st.get("line_extent_pt"),
                "smallest_unsure_pt": st.get("smallest_unsure_pt"),
                "smallest_run_pt": st.get("smallest_run_pt"),
                "nominal_if_x_pt": st.get("nominal_if_x_pt"),
                "candidates": st.get("candidates", []),
                "line_runs": st.get("line_runs", []),
            })
            if st["pt"] is None:
                rec["verdict"] = "NO-TEXT"
            else:
                rec["verdict"] = "FAIL" if st["nominal_pt"] < 6.0 else "PASS"
            # a 1-px-wide or near-empty rect is not a figure at all
            if it.get("px_w") and it["px_h"] and (it["px_w"] <= 8 or it["px_h"] <= 8):
                rec["verdict"] = "NO-TEXT"
                rec["note"] = ("media part is a %sx%s placeholder -- Word's own bullet "
                               "glyph image, not a figure" % (it["px_w"], it["px_h"]))
                rec["smallest_text_pt"] = None
                rec["confidence"] = "no-text"
            items.append(rec)
        doc.close()
        done[rel] = {"items": items}
        # atomic: this is tens of MB rewritten per document, so a bare truncate-then-write
        # loses the whole run if it crashes and hands a concurrent reader a parse error.
        tmp = out_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"documents": done, "dpi": DPI, "pt_per_px": PT_PER_PX}, fh,
                      ensure_ascii=False, indent=1)
        for attempt in range(8):
            try:
                os.replace(tmp, out_path)
                break
            except PermissionError:
                import time
                time.sleep(0.4 * (attempt + 1))
        n_ok = sum(1 for x in items if x["verdict"] == "PASS")
        n_bad = sum(1 for x in items if x["verdict"] == "FAIL")
        n_nt = sum(1 for x in items if x["verdict"] == "NO-TEXT")
        n_un = sum(1 for x in items if x["verdict"] == "UNMEASURABLE")
        print(f"[{i:>2}/{len(docs)}] {rel}  ->  {len(items)} figs  "
              f"PASS {n_ok}  FAIL {n_bad}  NO-TEXT {n_nt}  UNMEAS {n_un}", flush=True)
    print("-> measured.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
