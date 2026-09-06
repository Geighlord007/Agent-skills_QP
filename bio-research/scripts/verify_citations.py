#!/usr/bin/env python3
"""Verify that report citations resolve to sources.jsonl entries."""

import argparse
import json
import re
import sys
from pathlib import Path


def load_sources(path: Path) -> dict[int, dict]:
    sources = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            s = json.loads(line)
            sources[s["id"]] = s
    return sources


def extract_citations(report_text: str) -> set[int]:
    return set(int(m) for m in re.findall(r"\[(\d+)\]", report_text))


def main():
    parser = argparse.ArgumentParser(description="Verify citations in report")
    parser.add_argument("report", type=Path)
    parser.add_argument("sources", type=Path)
    args = parser.parse_args()

    report_text = args.report.read_text(encoding="utf-8")
    sources = load_sources(args.sources)
    citations = extract_citations(report_text)
    source_ids = set(sources.keys())

    errors = []

    # Orphan citations
    for cid in sorted(citations):
        if cid not in source_ids:
            errors.append(f"Citation [{cid}] not found in sources.jsonl")

    # Unused sources
    for sid in sorted(source_ids):
        if sid not in citations:
            errors.append(f"Source [{sid}] is not cited in report")

    # Sources missing URL or identifier
    for sid, s in sorted(sources.items()):
        if not (s.get("url") or s.get("identifier")):
            errors.append(f"Source [{sid}] missing both url and identifier")

    if errors:
        print("CITATION VERIFICATION FAILED")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"Citation verification passed: {len(citations)} citations, {len(sources)} sources.")


if __name__ == "__main__":
    main()
