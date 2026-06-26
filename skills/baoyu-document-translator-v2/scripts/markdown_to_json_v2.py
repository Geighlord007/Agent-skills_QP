#!/usr/bin/env python3
"""
Merge keyed translated markdown back into extracted JSON.

Usage: python markdown_to_json_v2.py extracted.json translation.md output.json

Expects HTML comment markers:
  <!--key:p_body_0|runs:3|type:paragraph-->

Maps by key, so the translator may reorder, split, or merge paragraphs
without breaking the document — as long as markers are preserved.
"""
import sys
import json
import re
from pathlib import Path


MARKER_RE = re.compile(r"<!--\s*key:([^|]+)\|runs:(\d+)(?:\|type:([^\s>]+))?\s*-->")


def parse_markdown(md_text):
    """Parse keyed markdown into a dict of key -> (runs, text)."""
    result = {}
    current_key = None
    current_runs = 1
    current_lines = []

    def flush():
        nonlocal current_key, current_runs, current_lines
        if current_key is not None:
            text = "\n".join(current_lines).strip()
            result[current_key] = (current_runs, text)
        current_key = None
        current_runs = 1
        current_lines = []

    for line in md_text.splitlines():
        m = MARKER_RE.match(line.strip())
        if m:
            flush()
            current_key = m.group(1).strip()
            current_runs = int(m.group(2))
            # type is optional, currently unused
        else:
            current_lines.append(line)

    flush()
    return result


def split_into_parts(text, num_runs, source_parts=None):
    """Split translated text into N parts matching original run count."""
    if num_runs <= 1:
        return [text]

    text = text.strip()
    if not text:
        return [""] * num_runs

    # Strategy 1: if source parts exist, try to match lengths proportionally
    if source_parts:
        total_len = sum(len(p) for p in source_parts if p)
        if total_len == 0:
            return proportional_split(text, num_runs)
        ratios = [max(len(p), 1) / total_len for p in source_parts]
        parts = []
        start = 0
        for i in range(num_runs - 1):
            end = int(start + ratios[i] * len(text))
            # Move end to a good boundary
            end = find_boundary(text, end, forward=True)
            parts.append(text[start:end].strip())
            start = end
        parts.append(text[start:].strip())
        return parts

    return proportional_split(text, num_runs)


def proportional_split(text, num_runs):
    """Fallback: split near punctuation, otherwise proportional."""
    parts = []
    avg = len(text) // num_runs
    for i in range(num_runs - 1):
        split_point = find_boundary(text, avg, forward=True)
        parts.append(text[:split_point].strip())
        text = text[split_point:].strip()
        avg = len(text) // (num_runs - i - 1)
    parts.append(text.strip())
    return parts


def find_boundary(text, pos, forward=True):
    """Find a good text boundary near pos. Prefer punctuation."""
    if not text:
        return 0
    pos = max(0, min(pos, len(text)))

    # Search forward/backward for punctuation
    punctuation = "。，；！？.,;!? \t\n"
    radius = 30

    # Forward search
    for j in range(pos, min(pos + radius, len(text))):
        if text[j] in punctuation:
            return j + 1

    # Backward search
    for j in range(pos, max(pos - radius, 0), -1):
        if j < len(text) and text[j] in punctuation:
            return j + 1

    return pos


def merge_translation(extracted_path, md_path, output_path):
    extracted = json.loads(Path(extracted_path).read_text(encoding="utf-8"))
    md_text = Path(md_path).read_text(encoding="utf-8")

    translations = parse_markdown(md_text)
    elements = extracted.get("elements", [])

    warnings = []
    missing = []

    for elem in elements:
        key = elem.get("key")
        if key not in translations:
            missing.append(key)
            continue

        expected_runs = elem.get("runs", 1)
        runs, translated_text = translations[key]

        if runs != expected_runs:
            warnings.append(
                f"{key}: marker says runs={runs}, expected {expected_runs}; using expected"
            )

        source_parts = elem.get("parts", [])
        elem["parts"] = split_into_parts(translated_text, expected_runs, source_parts)

    if missing:
        print(f"WARNING: {len(missing)} elements missing translation")
        for k in missing[:10]:
            print(f"  - {k}")

    if warnings:
        print("WARNINGS:")
        for w in warnings[:10]:
            print(f"  - {w}")

    Path(output_path).write_text(
        json.dumps(extracted, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Written to {output_path}")
    return extracted


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage: python {sys.argv[0]} extracted.json translation.md output.json")
        sys.exit(1)

    merge_translation(sys.argv[1], sys.argv[2], sys.argv[3])
