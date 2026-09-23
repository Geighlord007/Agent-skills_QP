#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Render a .docx to PNG pages for visual verification.

Pipeline: MS Word (COM) -> PDF -> PyMuPDF -> PNG. Word is used deliberately: it is
the ground-truth renderer, so if a document looks right here it will look right for
the reader. LibreOffice is not installed on this machine.

Usage:
    python _tools/docx_to_png.py <file.docx> [--pages 1,2,5] [--dpi 110]
    python _tools/docx_to_png.py <folder> --recursive --limit 20
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _ascii_stage_dir(path: str) -> tuple[str, str | None]:
    """Same idea for a destination path: Word will not WRITE to a non-ASCII path either."""
    try:
        path.encode("ascii")
        return path, None
    except UnicodeEncodeError:
        import tempfile
        import uuid
        d = os.path.join(tempfile.gettempdir(), "dsh_render_" + uuid.uuid4().hex[:8])
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "out.pdf"), d


def _ascii_stage(path: str) -> tuple[str, str | None]:
    """Stage a file to an ASCII temp path.

    Word COM on this machine CANNOT open a path containing non-ASCII characters: it fails
    with RPC_S_CALL_FAILED (-2147023170) regardless of retries. This repository lives under
    a Chinese-named folder, which is why rendering kept "failing intermittently" — the path
    was the cause, not contention. Returns (path_to_use, temp_to_clean_up).
    """
    try:
        path.encode("ascii")
        return path, None
    except UnicodeEncodeError:
        import shutil
        import tempfile
        import uuid
        d = os.path.join(tempfile.gettempdir(), "dsh_render_" + uuid.uuid4().hex[:8])
        os.makedirs(d, exist_ok=True)
        staged = os.path.join(d, "doc.docx")
        shutil.copy2(path, staged)
        return staged, d


def docx_to_pdf(docx: str, pdf: str, attempts: int = 4) -> None:
    """Render via Word, the ground-truth renderer.

    Word COM occasionally returns RPC_E_FAILED, usually because a previous instance was
    force-killed. It is transient, so retry with a growing pause and try both DispatchEx
    (a fresh instance) and Dispatch (attach to whatever exists).
    """
    import time

    import pythoncom  # type: ignore
    import win32com.client  # type: ignore

    src, cleanup_src = _ascii_stage(os.path.abspath(docx))
    dst, cleanup_dst = _ascii_stage_dir(os.path.abspath(pdf))
    last = None
    for attempt in range(attempts):
        for factory in ("DispatchEx", "Dispatch"):
            word = None
            try:
                pythoncom.CoInitialize()
                word = getattr(win32com.client, factory)("Word.Application")
                try:
                    word.Visible = False
                except Exception:
                    pass
                try:
                    word.DisplayAlerts = 0
                except Exception:
                    pass
                doc = word.Documents.Open(src, ReadOnly=True,
                                          AddToRecentFiles=False, Visible=False)
                doc.SaveAs(dst, FileFormat=17)   # wdFormatPDF
                doc.Close(False)
                if cleanup_dst:
                    import shutil as _sh
                    _sh.copy2(dst, os.path.abspath(pdf))
                return
            except Exception as e:  # noqa: BLE001
                last = e
            finally:
                try:
                    if word is not None:
                        word.Quit()
                except Exception:
                    pass
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
        time.sleep(2.5 * (attempt + 1))
    raise RuntimeError(f"Word could not render after {attempts} attempts: {last}")
    # (cleanup happens in the caller's finally below)


def pdf_to_png(pdf: str, out_dir: str, pages: list[int] | None, dpi: int = 110) -> list[str]:
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf  # type: ignore

    written = []
    base = os.path.splitext(os.path.basename(pdf))[0]
    with pymupdf.open(pdf) as doc:
        idxs = range(doc.page_count) if not pages else [p - 1 for p in pages if p <= doc.page_count]
        for i in idxs:
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            out = os.path.join(out_dir, f"{base}.page{i + 1}.png")
            pix.save(out)
            written.append(out)
    return written


def render_one(docx: str, pages: list[int] | None = None, dpi: int = 110) -> list[str]:
    out_dir = os.path.join(ROOT, "_reorg_work", "render")
    os.makedirs(out_dir, exist_ok=True)
    pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(docx))[0] + ".pdf")
    docx_to_pdf(docx, pdf)
    return pdf_to_png(pdf, out_dir, pages, dpi)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--pages", default="")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    pages = [int(x) for x in a.pages.split(",") if x.strip()] or None

    if os.path.isdir(a.target):
        pattern = "**/*.docx" if a.recursive else "*.docx"
        files = sorted(glob.glob(os.path.join(a.target, pattern), recursive=a.recursive))
        files = [f for f in files if not os.path.basename(f).startswith("~$")]
        if a.limit:
            files = files[: a.limit]
    else:
        files = [a.target]

    rc = 0
    for f in files:
        try:
            outs = render_one(f, pages if pages else [1], a.dpi)
            print(f"OK   {os.path.relpath(f, ROOT)} -> {len(outs)} page(s)")
            for o in outs:
                print(f"       {o}")
        except Exception as e:  # noqa: BLE001
            rc = 1
            print(f"FAIL {os.path.relpath(f, ROOT)}: {e}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
