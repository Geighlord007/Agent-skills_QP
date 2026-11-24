#!/usr/bin/env python3
"""Merge, deduplicate, and freeze canonical IDs for sources.jsonl.

Supports either:
  1. Merging a datas/ directory containing per-thread files (sources_*.jsonl)
     into canonical datas/sources.jsonl BEFORE Phase B writing, optionally
     rewriting thread-scoped citations [T01-1] in drafts/*.md to final [N].
  2. Deduplicating a single existing sources.jsonl in place (backward compatible).
"""

import argparse
import json
import os
import re
import shutil
import sys
from collections import OrderedDict
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def _norm_key(source: dict) -> str:
    """Compute a normalized deduplication key from identifier, url, or title."""
    ident = str(source.get("identifier") or "").strip().lower()
    if ident:
        return f"id:{ident}"
    url = str(source.get("url") or "").strip().rstrip("/").lower()
    if url:
        return f"url:{url}"
    title = str(source.get("title") or "").strip().lower()
    if title:
        return f"title:{title}"
    return ""


def load_sources_file(path: Path) -> list[dict]:
    sources: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                sources.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in {path}:{lineno}: {line[:80]}..."
                ) from e
    return sources


def collect_input_files(source_path: Path) -> list[Path]:
    if source_path.is_file():
        return [source_path]
    if source_path.is_dir():
        files = sorted(
            p for p in source_path.glob("sources_*.jsonl") if p.is_file()
        )
        canonical = source_path / "sources.jsonl"
        if not files and canonical.is_file():
            files = [canonical]
        return files
    return []


def merge_and_dedupe(
    input_files: list[Path],
) -> tuple[list[dict], dict[str, int]]:
    """Deduplicate sources across input_files and return (merged, id_map).

    id_map maps each original stringified source id (e.g. "T01-1", "C-2")
    to its final canonical integer ID (1..N).
    """
    seen: OrderedDict[str, dict] = OrderedDict()
    key_to_new_id: dict[str, int] = {}
    id_map: dict[str, int] = {}

    for path in input_files:
        for s in load_sources_file(path):
            old_id = s.get("id")
            key = _norm_key(s) or f"__unnamed_{len(seen)}"
            if key not in seen:
                new_id = len(seen) + 1
                record = dict(s)
                record["id"] = new_id
                seen[key] = record
                key_to_new_id[key] = new_id
            final_id = key_to_new_id[key]
            if old_id is not None and str(old_id).strip():
                id_map[str(old_id).strip()] = final_id

    return list(seen.values()), id_map


def rewrite_drafts(drafts_dir: Path, id_map: dict[str, int]) -> int:
    """Rewrite thread-scoped citations like [T01-1] or [C-2] in drafts/*.md."""
    if not drafts_dir.is_dir():
        return 0
    # Only rewrite non-numeric / scoped tokens (e.g. T01-1, C-1) so we never
    # accidentally collide with already-numeric [1] or markdown array syntax.
    scoped_map = {k: v for k, v in id_map.items() if not k.isdigit()}
    if not scoped_map:
        return 0

    token_re = re.compile(r"\[([A-Za-z][A-Za-z0-9_-]*-\d+)\]")
    updated_files = 0
    for md_file in sorted(drafts_dir.glob("*.md")):
        original = md_file.read_text(encoding="utf-8")

        def _replace(match: re.Match) -> str:
            tok = match.group(1)
            if tok in scoped_map:
                return f"[{scoped_map[tok]}]"
            return match.group(0)

        rewritten = token_re.sub(_replace, original)
        if rewritten != original:
            md_file.write_text(rewritten, encoding="utf-8")
            updated_files += 1
    return updated_files


def save_sources(path: Path, sources: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for s in sources:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(
        description="Merge, deduplicate, and freeze IDs for sources.jsonl"
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Path to datas/ directory (containing sources_*.jsonl) or a single sources.jsonl file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output canonical sources.jsonl path (defaults to <dir>/sources.jsonl or in-place)",
    )
    parser.add_argument(
        "--rewrite-drafts",
        type=Path,
        default=None,
        help="Optional drafts/ directory whose [T{NN}-k] citations will be rewritten to final [N]",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Write a .jsonl.bak backup before overwriting an existing output file",
    )
    args = parser.parse_args()

    if not args.source.exists():
        print(f"ERROR: {args.source} not found")
        raise SystemExit(1)

    input_files = collect_input_files(args.source)
    if not input_files:
        print(f"ERROR: No sources*.jsonl files found in {args.source}")
        raise SystemExit(1)

    output_path = (
        args.output
        if args.output is not None
        else (args.source / "sources.jsonl" if args.source.is_dir() else args.source)
    )

    backup_path = None
    if args.backup and output_path.exists():
        backup_path = output_path.with_suffix(".jsonl.bak")
        shutil.copy2(output_path, backup_path)

    sources, id_map = merge_and_dedupe(input_files)
    save_sources(output_path, sources)

    map_path = output_path.parent / "source_id_map.json"
    map_path.write_text(
        json.dumps(id_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    rewritten_count = 0
    if args.rewrite_drafts is not None:
        rewritten_count = rewrite_drafts(args.rewrite_drafts, id_map)

    msg = (
        f"Merged {len(sources)} unique sources from {len(input_files)} file(s) "
        f"-> {output_path} (id map: {map_path})"
    )
    if backup_path:
        msg += f" | backup: {backup_path}"
    if args.rewrite_drafts is not None:
        msg += f" | drafts rewritten: {rewritten_count}"
    print(msg)


if __name__ == "__main__":
    main()
