# -*- coding: utf-8 -*-
"""Marker-safe chunk splitter for keyed markdown (v2.1, Step 3 tooling).

Splits source.md into chunks at <!--key:...--> boundaries with a character budget.
Blocks are never split; TOC/tab/page-number structure stays inside one chunk.

Usage: python chunk_keyed.py source.md out_dir [max_chars=4200]
"""
import sys, re
from pathlib import Path

MARK = re.compile(r"^\s*<!--\s*key:")

def main():
    src = Path(sys.argv[1]); outdir = Path(sys.argv[2])
    max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 4200
    outdir.mkdir(parents=True, exist_ok=True)
    blocks, cur = [], []
    for ln in src.read_text(encoding="utf-8").splitlines():
        if MARK.match(ln):
            if cur: blocks.append(cur)
            cur = [ln]
        else:
            cur.append(ln)
    if cur: blocks.append(cur)
    chunks, cc, cl = [], [], 0
    for b in blocks:
        bl = sum(len(x) for x in b)
        if cc and cl + bl > max_chars:
            chunks.append(cc); cc, cl = [], 0
        cc.append(b); cl += bl
    if cc: chunks.append(cc)
    for i, ch in enumerate(chunks, 1):
        (outdir / ("chunk-%02d-source.md" % i)).write_text(
            "\n".join("\n".join(b) for b in ch).rstrip() + "\n", encoding="utf-8")
        print("chunk-%02d-source.md: %d blocks, %d chars" % (i, len(ch), sum(len(x) for b in ch for x in b)))
    print("TOTAL %d chunks, %d blocks" % (len(chunks), len(blocks)))

if __name__ == "__main__":
    main()
