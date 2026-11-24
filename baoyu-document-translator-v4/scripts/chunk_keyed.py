# -*- coding: utf-8 -*-
"""Marker-safe chunk splitter for keyed markdown (v4.3, Mode A / DOCX Step 3 tooling).

Splits source.md into chunks at <!--key:...--> boundaries with a character budget.
Blocks are never split; TOC/tab/page-number structure stays inside one chunk.
When `--extracted extracted.json` is passed, also emits `chunk-NN-runs.json` containing
multi-run metadata (parts, run_styles, para_splits) for each chunk's review pass.

Usage:
  python chunk_keyed.py source.md out_dir [max_chars=4200] [--extracted extracted.json]
"""
import argparse
import json
import re
from pathlib import Path

MARK = re.compile(r"^\s*<!--\s*key:([^|>]+)")


def extract_key(line: str) -> str:
    m = MARK.match(line)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser(description="Marker-safe chunk splitter for keyed markdown.")
    ap.add_argument("source", help="Keyed source.md")
    ap.add_argument("outdir", help="Output directory for chunk-NN-source.md")
    ap.add_argument("max_chars", nargs="?", type=int, default=4200, help="Char budget per chunk (default: 4200)")
    ap.add_argument("--extracted", default=None, help="Optional extracted.json to also emit chunk-NN-runs.json")
    args = ap.parse_args()

    src = Path(args.source)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    extracted_by_key = {}
    if args.extracted:
        ex_data = json.loads(Path(args.extracted).read_text(encoding="utf-8"))
        for elem in ex_data.get("elements", []):
            if elem.get("runs", 1) > 1:
                extracted_by_key[elem["key"]] = {
                    "runs": elem["runs"],
                    "parts": elem.get("parts", []),
                    **({"run_styles": elem["run_styles"]} if "run_styles" in elem else {}),
                    **({"para_splits": elem["para_splits"]} if "para_splits" in elem else {}),
                }

    blocks, cur = [], []
    for ln in src.read_text(encoding="utf-8").splitlines():
        if MARK.match(ln):
            if cur:
                blocks.append(cur)
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        blocks.append(cur)

    chunks, cc, cl = [], [], 0
    for b in blocks:
        bl = sum(len(x) for x in b)
        if cc and cl + bl > args.max_chars:
            chunks.append(cc)
            cc, cl = [], 0
        cc.append(b)
        cl += bl
    if cc:
        chunks.append(cc)

    for i, ch in enumerate(chunks, 1):
        (outdir / f"chunk-{i:02d}-source.md").write_text(
            "\n".join("\n".join(b) for b in ch).rstrip() + "\n", encoding="utf-8"
        )
        run_note = ""
        if extracted_by_key:
            chunk_runs = {}
            for b in ch:
                k = extract_key(b[0])
                if k in extracted_by_key:
                    chunk_runs[k] = extracted_by_key[k]
            (outdir / f"chunk-{i:02d}-runs.json").write_text(
                json.dumps(chunk_runs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            run_note = f", {len(chunk_runs)} multi-run keys"
        chars = sum(len(x) for b in ch for x in b)
        print(f"chunk-{i:02d}-source.md: {len(ch)} blocks, {chars} chars{run_note}")
    print(f"TOTAL {len(chunks)} chunks, {len(blocks)} blocks")


if __name__ == "__main__":
    main()
