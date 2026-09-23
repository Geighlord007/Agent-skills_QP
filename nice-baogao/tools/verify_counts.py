#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The closing check for the figure-legibility work.

The standing objective ends with a verification clause: `verify_all` at 17/17, Word able to
open every delivered document, and **no document's word, table, image or paragraph count
changed**. This script makes that one command instead of an improvised sequence, and it is
deliberately explicit about which changes are expected and which are not.

WHY A DEDICATED SCRIPT
----------------------
Across this work, five separate measurement instruments each reported "clean" while the
artefact was wrong -- `check_scale()` blind to canvas overflow, `fig.findobj(Text)` missing
`ax.title` on matplotlib 3.10, an overflow audit whose 1 px tolerance hid a 17 px clip, a
screen that scored 36 identical tick marks as a text label, and one that scored a photograph
with no text as a "0.0 pt defect". In every case the fault was in what the instrument LOOKED
at, not in how it measured. So this script states its own scope out loud and prints what it
did not check.

WHAT IT COMPARES
----------------
Against `_admin/FIGURE_WORK_BASELINE.csv`, captured before the remaining fixes began:
  * words / tables / inline images / paragraphs -- a CHANGE IS A FAILURE, because a figure fix
    has no business altering a count;
  * the media-set hash -- a change is EXPECTED for a document whose figure was re-rendered,
    and reported rather than failed, with the parts that changed named.

Deliberately NOT checked here: whether figures are legible. That is the measurement worker's
ground-truth page-render pass, and it cannot be inferred from counts. Saying so is the point.

Run:  python _tools/verify_figure_work.py
"""
from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(ROOT, "_admin", "FIGURE_WORK_BASELINE.csv")
SKIP = ("_tools", "_admin", "99_Archive", ".git", "98_Reference_Library")


def counts(path: str):
    from docx import Document
    d = Document(path)
    words = sum(len(p.text.split()) for p in d.paragraphs)
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                words += len(c.text.split())
    z = zipfile.ZipFile(path)
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    h = hashlib.sha256()
    for n in sorted(media):
        h.update(hashlib.sha256(z.read(n)).digest())
    return {"words": words, "tables": len(d.tables),
            "inline_images": len(d.inline_shapes), "paragraphs": len(d.paragraphs),
            "media_parts": len(media), "media_sha16": h.hexdigest()[:16]}


def main() -> int:
    if not os.path.exists(BASELINE):
        print("no baseline: run the capture that produced _admin/FIGURE_WORK_BASELINE.csv first")
        return 2
    base = {r["document"]: r for r in
            csv.DictReader(open(BASELINE, encoding="utf-8-sig"))}
    docs = []
    for dp, _dn, fs in os.walk(ROOT):
        if any(s in dp for s in SKIP):
            continue
        for f in fs:
            if f.lower().endswith(".docx") and not f.startswith("~$"):
                docs.append(os.path.relpath(os.path.join(dp, f), ROOT).replace("\\", "/"))

    FAIL_FIELDS = ("words", "tables", "inline_images", "paragraphs")
    count_drift, fig_rewrites, missing, new = [], [], [], []
    for rel in sorted(docs):
        if rel not in base:
            new.append(rel)
            continue
        try:
            now = counts(os.path.join(ROOT, rel))
        except Exception as e:  # noqa: BLE001
            missing.append((rel, str(e)[:60]))
            continue
        was = base[rel]
        drift = {k: (was[k], now[k]) for k in FAIL_FIELDS if str(was[k]) != str(now[k])}
        if drift:
            count_drift.append((rel, drift))
        if was["media_sha16"] != now["media_sha16"]:
            fig_rewrites.append((rel, was["media_parts"], now["media_parts"]))
    gone = [r for r in base if r not in set(docs)]

    print("=" * 74)
    print("FIGURE WORK -- CLOSING CHECK")
    print("=" * 74)
    print(f"baseline documents : {len(base)}")
    print(f"documents on disk  : {len(docs)}")
    print(f"count drift        : {len(count_drift)}   <- must be 0")
    print(f"figures re-rendered: {len(fig_rewrites)}   <- expected, media hash changed")
    print(f"unreadable         : {len(missing)}")
    print(f"new since baseline : {len(new)}")
    print(f"missing since base : {len(gone)}")
    for rel, drift in count_drift[:10]:
        print(f"   DRIFT {rel}")
        for k, (a, b) in drift.items():
            print(f"        {k}: {a} -> {b}")
    for rel, a, b in fig_rewrites[:14]:
        print(f"   rewritten {rel}  (media {a} -> {b})")
    for rel, why in missing:
        print(f"   UNREADABLE {rel}: {why}")
    print("\n--- gates ---")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "_tools", "verify_all.py")],
                       capture_output=True, text=True)
    tail = [l for l in (r.stdout or "").splitlines() if "checks," in l]
    print("   " + (tail[-1] if tail else "verify_all produced no summary line"))
    print("\nNOT CHECKED HERE: whether any figure is legible. That needs the ground-truth")
    print("page-render measurement, and cannot be inferred from document counts.")
    return 1 if (count_drift or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
