#!/usr/bin/env python3
"""Merge, deduplicate, and re-ID sources.jsonl."""

import argparse
import json
import shutil
from collections import OrderedDict
from pathlib import Path


def load_sources(path: Path) -> list[dict]:
    sources = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                sources.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON line: {line[:80]}...") from e
    return sources


def dedupe(sources: list[dict]) -> list[dict]:
    seen = OrderedDict()
    for s in sources:
        key = s.get("identifier") or s.get("url") or s.get("title", "").strip()
        if not key:
            key = f"__unnamed_{len(seen)}"
        if key not in seen:
            seen[key] = s
    return list(seen.values())


def reassign_ids(sources: list[dict]) -> list[dict]:
    for i, s in enumerate(sources, start=1):
        s["id"] = i
    return sources


def save_sources(path: Path, sources: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for s in sources:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Merge and deduplicate sources.jsonl")
    parser.add_argument("sources", type=Path, help="Path to sources.jsonl")
    args = parser.parse_args()

    if not args.sources.exists():
        print(f"ERROR: {args.sources} not found")
        raise SystemExit(1)

    backup = args.sources.with_suffix(".jsonl.bak")
    shutil.copy2(args.sources, backup)

    sources = load_sources(args.sources)
    sources = dedupe(sources)
    sources = reassign_ids(sources)
    save_sources(args.sources, sources)

    print(f"Merged {len(sources)} unique sources. Backup: {backup}")


if __name__ == "__main__":
    main()
