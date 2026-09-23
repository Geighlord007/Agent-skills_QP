#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUDIT STEP 2 -- render every document that displays an image to PDF through Word.

This is the ground-truth renderer: whatever Word prints is what the reader gets. The
conversion goes through `_tools/docx_to_png.docx_to_pdf`, which stages the source to an
ASCII temp path -- Word COM cannot open the non-ASCII repository path at all
(RPC_S_CALL_FAILED) -- and which quits its Word instance in a `finally`.

Renders are strictly serialised. Status is appended to render_status.json after every
document so an interrupted run still leaves usable output.

    python render.py [--only SUBSTRING] [--force]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "_tools"))

from docx_to_png import docx_to_pdf  # noqa: E402

PDFDIR = os.path.join(HERE, "pdf")


def kill_hidden_word() -> int:
    """Orphaned automation instances wedge COM for everything else. Kill only the ones
    with no window title -- never a Word the human is using."""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process WINWORD -ErrorAction SilentlyContinue | "
             "Where-Object { $_.MainWindowTitle -eq '' } | "
             "Measure-Object).Count"],
            capture_output=True, text=True, timeout=60)
        n = int((out.stdout or "0").strip() or 0)
        if n:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-Process WINWORD -ErrorAction SilentlyContinue | "
                 "Where-Object { $_.MainWindowTitle -eq '' } | Stop-Process -Force"],
                capture_output=True, text=True, timeout=60)
        return n
    except Exception:  # noqa: BLE001
        return -1


def slug_for(rel: str) -> str:
    import re
    s = rel.replace("\\", "/")
    s = re.sub(r"\.docx$", "", s, flags=re.I)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s[:110]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    inv = json.load(open(os.path.join(HERE, "inventory_raw.json"), encoding="utf-8"))
    docs = [d for d in inv["documents"] if d["placements"]]
    if a.only:
        docs = [d for d in docs if a.only.lower() in d["document"].lower()]
    os.makedirs(PDFDIR, exist_ok=True)

    status_path = os.path.join(HERE, "render_status.json")
    status = {}
    if os.path.exists(status_path):
        status = json.load(open(status_path, encoding="utf-8"))

    print(f"{len(docs)} documents to render through Word", flush=True)
    t_all = time.time()
    fails = 0
    for i, d in enumerate(docs, 1):
        rel = d["document"]
        slug = slug_for(rel)
        pdf = os.path.join(PDFDIR, slug + ".pdf")
        if os.path.exists(pdf) and not a.force:
            st = status.get(rel, {})
            st.update({"slug": slug, "pdf": os.path.relpath(pdf, ROOT),
                       "cached": True})
            status[rel] = st
            print(f"[{i:>2}/{len(docs)}] cached  {rel}", flush=True)
            continue
        t0 = time.time()
        try:
            docx_to_pdf(os.path.join(ROOT, rel.replace("/", os.sep)), pdf)
            ok, err = True, ""
        except Exception as e:  # noqa: BLE001
            ok, err = False, f"{type(e).__name__}: {e}"
        dt = time.time() - t0
        if not ok:
            fails += 1
            killed = kill_hidden_word()
            print(f"[{i:>2}/{len(docs)}] FAIL {rel}  ({dt:.1f}s) {err}"
                  f"{'  [killed %d hidden WINWORD]' % killed if killed else ''}", flush=True)
        else:
            print(f"[{i:>2}/{len(docs)}] ok   {rel}  ({dt:.1f}s)", flush=True)
        status[rel] = {"slug": slug, "pdf": os.path.relpath(pdf, ROOT),
                       "ok": ok, "error": err, "seconds": round(dt, 1)}
        with open(status_path, "w", encoding="utf-8") as fh:
            json.dump(status, fh, ensure_ascii=False, indent=1)
    print(f"done in {time.time() - t_all:.0f}s; {fails} failures", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
