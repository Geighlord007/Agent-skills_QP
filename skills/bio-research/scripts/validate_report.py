#!/usr/bin/env python3
"""Validate report structure, formatting, and minimum content gates."""

import argparse
import json
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
ASTERISK_BULLET_RE = re.compile(r"^\*\s", re.MULTILINE)
CITATION_RE = re.compile(r"\[(\d+)\]")

# Minimum words per section type by mode
MODE_LIMITS = {
    "quick": {"h2": 150, "h3": 80, "exec": 80},
    "standard": {"h2": 400, "h3": 150, "exec": 150},
    "deep": {"h2": 600, "h3": 250, "exec": 250},
}


def count_words(text: str) -> int:
    # Simple word count; handles English and CJK reasonably
    return len(re.findall(r"[\w\u4e00-\u9fff]+", text))


def parse_sections(text: str):
    """Return list of (level, title, body_text, subtree_text) for each heading.

    body_text is the content until the next heading of any level.
    subtree_text includes body_text plus all nested subsections until the next
    heading of the same or higher level (i.e., same or lower number).
    """
    matches = list(HEADING_RE.finditer(text))
    sections = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip()
        start = m.end()

        # Body ends at the very next heading
        next_any = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:next_any].strip()

        # Subtree ends at the next heading of same or higher level
        next_same_or_higher = len(text)
        for nxt in matches[i + 1:]:
            if len(nxt.group(1)) <= level:
                next_same_or_higher = nxt.start()
                break
        subtree = text[start:next_same_or_higher].strip()

        sections.append((level, title, body, subtree))
    return sections


def main():
    parser = argparse.ArgumentParser(description="Validate research report")
    parser.add_argument("report", type=Path)
    parser.add_argument("--mode", choices=["quick", "standard", "deep"], default="standard")
    parser.add_argument("--output-json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    text = args.report.read_text(encoding="utf-8")
    sections = parse_sections(text)
    limits = MODE_LIMITS[args.mode]
    errors = []
    warnings = []

    # 1. No asterisk bullets
    if ASTERISK_BULLET_RE.search(text):
        errors.append("Found asterisk bullets (* ); use hyphen bullets (- ) only.")

    # 2. No empty leaf sections (sections without subsections must have content)
    for i, (level, title, body, subtree) in enumerate(sections):
        has_subsection = any(
            lvl > level for lvl, _, _, _ in sections[i + 1:]
        )
        if not has_subsection and count_words(body) == 0:
            errors.append(f"Empty section: {'#' * level} {title}")

    # 3. Minimum lengths (use subtree content so parent sections with subsections count nested text)
    for level, title, body, subtree in sections:
        word_count = count_words(subtree)
        if level == 2 and word_count < limits["h2"]:
            errors.append(
                f"Section too short ({word_count} words, min {limits['h2']}): {title}"
            )
        if level == 3 and word_count < limits["h3"]:
            errors.append(
                f"Subsection too short ({word_count} words, min {limits['h3']}): {title}"
            )

    # 4. Executive summary check (first h2)
    h2_sections = [(t, subtree) for lvl, t, _, subtree in sections if lvl == 2]
    if h2_sections:
        exec_title, exec_subtree = h2_sections[0]
        if "summary" not in exec_title.lower():
            warnings.append("First section does not appear to be an Executive Summary.")
        if count_words(exec_subtree) < limits["exec"]:
            errors.append(
                f"Executive Summary too short ({count_words(exec_subtree)} words, min {limits['exec']})"
            )

    # 5. Citation presence
    total_words = count_words(text)
    citation_count = len(set(CITATION_RE.findall(text)))
    if citation_count == 0 and total_words > 200:
        errors.append("No citations found in report.")

    # 6. References section
    has_references = any("references" in t.lower() for _, t, _, _ in sections)
    if not has_references:
        errors.append("No References section found.")

    summary = {
        "mode": args.mode,
        "sections": len(sections),
        "words": total_words,
        "citations": citation_count,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }

    if args.output_json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Mode: {args.mode}")
        print(f"Sections: {len(sections)}")
        print(f"Words: {total_words}")
        print(f"Unique citations: {citation_count}")
        for w in warnings:
            print(f"WARNING: {w}")
        for e in errors:
            print(f"ERROR: {e}")
        if not errors:
            print("VALIDATION PASSED")
        else:
            print("VALIDATION FAILED")

    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
