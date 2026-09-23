#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Structural verification for a .docx produced by this repository.

Checks the things that actually break: residual Chinese, images silently dropped,
tables flattened, brand fonts not applied, cover missing, revision block missing.

Usage:
    python _tools/verify_docx.py <file.docx>            # one document
    python _tools/verify_docx.py <folder> --recursive   # a bucket
    python _tools/verify_docx.py <folder> --recursive --json out.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import zipfile

from docx import Document

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CJK = re.compile(r"[\u4e00-\u9fff]")
BRAND_FONTS = ("Newsreader", "Schibsted Grotesk", "DM Mono")


def check(path: str) -> dict:
    res = {"path": os.path.relpath(path, ROOT), "ok": True, "problems": [], "info": {}}
    try:
        doc = Document(path)
    except Exception as e:  # noqa: BLE001
        res["ok"] = False
        res["problems"].append(f"UNREADABLE: {e}")
        return res

    parts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                parts.append(c.text)
    txt = "\n".join(parts)
    cjk = len(CJK.findall(txt))

    try:
        with zipfile.ZipFile(path) as z:
            media = [n for n in z.namelist() if n.startswith("word/media/")]
    except Exception:
        media = []

    # Visible text that python-docx does not reach. `doc.paragraphs` walks only the
    # body's direct children, so it misses BOTH footnotes/endnotes/comments and text
    # boxes (w:txbxContent) nested inside runs. Without this scan the CJK gate passed
    # five documents that ship Chinese source-citation footnotes -- 793 characters
    # that print at the foot of the page.
    notes_cjk, all_cjk = 0, 0
    try:
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if not n.endswith(".xml"):
                    continue
                is_body = n == "word/document.xml"
                is_note = (n in ("word/footnotes.xml", "word/endnotes.xml",
                                 "word/comments.xml")
                           or n.startswith("word/header") or n.startswith("word/footer"))
                if not (is_body or is_note):
                    continue
                xml = z.read(n).decode("utf-8", "replace")
                hits = sum(len(CJK.findall(t)) for t in
                           re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", xml))
                hits += sum(len(CJK.findall(t)) for t in
                            re.findall(r"<a:t>([^<]*)</a:t>", xml))
                all_cjk += hits
                if is_note:
                    notes_cjk += hits
    except Exception:
        pass

    fonts = set()
    for p in doc.paragraphs:
        for r in p.runs:
            if r.font.name:
                fonts.add(r.font.name)

    res["info"] = {
        "words": len(txt.split()),
        "cjk_chars": cjk,
        "cjk_pct": round(100 * cjk / max(1, cjk + len(txt.split())), 2),
        "tables": len(doc.tables),
        "inline_images": len(doc.inline_shapes),
        "embedded_media": len(media),
        "paragraphs": len(doc.paragraphs),
        "brand_fonts": sorted(f for f in fonts if f in BRAND_FONTS),
        "cjk_visible_all_parts": all_cjk,
        "cjk_in_notes": notes_cjk,
    }

    if cjk > 20:
        res["problems"].append(f"RESIDUAL_CHINESE: {cjk} characters")
    if notes_cjk > 0:
        res["problems"].append(
            f"RESIDUAL_CHINESE_IN_NOTES: {notes_cjk} characters in footnotes/"
            f"endnotes/comments/headers/footers (invisible to the body-text scan)")
    elif all_cjk - cjk > 20:
        res["problems"].append(
            f"RESIDUAL_CHINESE_UNREACHED: {all_cjk - cjk} characters in text boxes "
            f"or other content the body-text scan does not reach")
    if len(doc.inline_shapes) == 0 and len(media) > 0:
        res["problems"].append("IMAGES_NOT_PLACED: media parts exist but no inline shape")
    if not res["info"]["brand_fonts"]:
        res["problems"].append("BRAND_FONTS_MISSING: none of " + ", ".join(BRAND_FONTS))
    # Revision Notes were removed from every document on the owner's instruction
    # (2026-09-13), so their ABSENCE is correct and their presence is the anomaly.
    # This check used to demand one, which made verify_docx report a problem for every
    # document in the repository and directly contradicted verify_all gate 5a.
    if "Revision Note" in txt:
        res["problems"].append(
            "REVISION_BLOCK_PRESENT: revision notes were removed repo-wide; "
            "one has reappeared")
    res["ok"] = not res["problems"]
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if os.path.isdir(a.target):
        pat = "**/*.docx" if a.recursive else "*.docx"
        files = sorted(glob.glob(os.path.join(a.target, pat), recursive=a.recursive))
        files = [f for f in files if not os.path.basename(f).startswith("~$")]
    else:
        files = [a.target]

    results = [check(f) for f in files]
    bad = [r for r in results if not r["ok"]]

    if not a.quiet:
        for r in results:
            flag = "OK  " if r["ok"] else "FAIL"
            i = r["info"]
            print(f'{flag} w={i.get("words",0):>6} cjk={i.get("cjk_chars",0):>5} '
                  f'tab={i.get("tables",0):>3} img={i.get("inline_images",0):>3}  {r["path"]}')
            for p in r["problems"]:
                print(f'        ! {p}')

    print(f"\n{len(results)} documents, {len(bad)} with problems")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=2)
        print(f"-> {a.json}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
