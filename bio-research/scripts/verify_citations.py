#!/usr/bin/env python3
"""Verify that report citations resolve to unique sources.jsonl entries."""

import argparse
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
REFERENCES_HEADING_RE = re.compile(
    r"^##\s+(?:references|bibliography)\b.*$", re.IGNORECASE | re.MULTILINE
)


def load_sources(path: Path) -> tuple[dict[int, dict], list[str]]:
    sources: dict[int, dict] = {}
    errors: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON at {path}:{lineno}: {exc}")
                continue
            sid = s.get("id")
            if not isinstance(sid, int):
                errors.append(
                    f"Source at {path}:{lineno} has non-integer id {sid!r} "
                    f"(run merge_sources.py before Phase B writing)"
                )
                continue
            if sid in sources:
                errors.append(
                    f"Duplicate source ID [{sid}] at {path}:{lineno}"
                )
                continue
            sources[sid] = s
    return sources, errors


def extract_citations(report_text: str) -> set[int]:
    """Extract numeric [N] citations from report body (excluding code fences and References list)."""
    cleaned = FENCED_CODE_RE.sub("", report_text)
    m = REFERENCES_HEADING_RE.search(cleaned)
    body = cleaned[:m.start()] if m else cleaned
    return {int(n) for n in re.findall(r"\[(\d+)\]", body)}


def main():
    parser = argparse.ArgumentParser(description="Verify citations in report")
    parser.add_argument("report", type=Path)
    parser.add_argument("sources", type=Path)
    args = parser.parse_args()

    if not args.report.exists():
        print(f"ERROR: Report not found: {args.report}", file=sys.stderr)
        sys.exit(1)
    if not args.sources.exists():
        print(f"ERROR: Sources file not found: {args.sources}", file=sys.stderr)
        sys.exit(1)

    report_text = args.report.read_text(encoding="utf-8")
    sources, errors = load_sources(args.sources)
    citations = extract_citations(report_text)
    source_ids = set(sources.keys())

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

    print(
        f"Citation verification passed: {len(citations)} citations, "
        f"{len(sources)} unique sources."
    )


if __name__ == "__main__":
    main()
