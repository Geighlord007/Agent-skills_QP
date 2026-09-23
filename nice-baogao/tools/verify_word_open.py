#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Open every delivered .docx in real Microsoft Word and report what fails.

WHY THIS EXISTS
---------------
Two delivered documents could not be opened by Word at all (error 25272) and every
gate passed them, because `verify_docx.py` reads documents with **python-docx**,
which is far more permissive than Word. The defect was a duplicated note anchor:
the bilingual conversion pass duplicated paragraphs (Chinese original ->
"REFERENCE TRANSLATION" -> English) and copied `w:footnoteReference` /
`w:commentReference` elements with them, so each note was anchored three times.
Word validates anchor uniqueness on load and refuses the file; python-docx never
notices.

The lesson generalises: a verifier is only as strict as the program that consumes
the artefact. Nothing in this repository had ever asked Word whether it could open
its own output.

USAGE
-----
    python _tools/verify_word_open.py            # every delivered .docx
    python _tools/verify_word_open.py --sample 10
    python _tools/verify_word_open.py <folder> --recursive

Needs Word installed and pywin32. Word COM cannot open a non-ASCII path, so each
file is staged to an ASCII temp path first. Renders are serialised: one Word
instance at a time, always quit in a `finally`, so no orphaned WINWORD is left
wedging the COM ROT for anything else.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ("_tools", "_admin", "99_Archive", ".git", "98_Reference_Library")


def delivered_docs(root: str, recursive: bool) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        if any(s in dirpath for s in SKIP):
            continue
        for fn in filenames:
            if fn.lower().endswith(".docx") and not fn.startswith("~$"):
                out.append(os.path.join(dirpath, fn))
        if not recursive:
            dirnames[:] = []
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default=ROOT)
    ap.add_argument("--recursive", action="store_true", default=True)
    ap.add_argument("--sample", type=int, default=0, help="check only N evenly spaced files")
    args = ap.parse_args()

    try:
        import pythoncom  # type: ignore
        import win32com.client  # type: ignore
    except ImportError:
        print("pywin32 not available -- cannot ask Word. Skipping.")
        return 0

    docs = delivered_docs(args.folder, args.recursive)
    # A single FILE argument must check that file. `delivered_docs` walks it as a
    # directory, finds nothing, and the checker used to print "no documents found" and
    # return 0 -- a vacuous PASS, exactly the way gate 3c once passed a truncated
    # portal because it had zero links in which to find a broken one. A checker that
    # silently checks nothing is worse than no checker.
    if os.path.isfile(args.folder):
        docs = [args.folder]
    if args.sample and args.sample < len(docs):
        step = max(1, len(docs) // args.sample)
        docs = docs[::step][:args.sample]
    if not docs:
        print(f"no documents found under {args.folder!r} -- refusing to report a vacuous pass")
        return 2

    tmpdir = tempfile.mkdtemp(prefix="wordopen_")
    bad = []
    for i, path in enumerate(docs, 1):
        stage = os.path.join(tmpdir, f"d{i}.docx")
        try:
            shutil.copyfile(path, stage)
        except Exception as e:  # noqa: BLE001
            bad.append((path, f"could not stage: {e}"))
            continue
        pythoncom.CoInitialize()
        word = None
        try:
            word = win32com.client.DispatchEx("Word.Application")
            for attr, val in (("Visible", False), ("DisplayAlerts", 0)):
                try:
                    setattr(word, attr, val)
                except Exception:
                    pass
            doc = word.Documents.Open(stage, ReadOnly=True,
                                      AddToRecentFiles=False, Visible=False)
            doc.Close(False)
            print(f"  OK    {os.path.relpath(path, ROOT)}")
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            code = ""
            for token in msg.replace("(", " ").replace(")", " ").split():
                if token.isdigit() and len(token) >= 4:
                    code = token
            bad.append((path, f"{msg[:90]}{' [word error ' + code + ']' if code else ''}"))
            print(f"  FAIL  {os.path.relpath(path, ROOT)}")
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
    shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{len(docs)} documents, {len(bad)} that Word cannot open")
    for path, why in bad:
        print(f"   ! {os.path.relpath(path, ROOT)}\n       {why}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
