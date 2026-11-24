#!/usr/bin/env python3
"""Validate report structure, formatting, and minimum content gates."""

import argparse
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
ASTERISK_BULLET_RE = re.compile(r"^\*\s", re.MULTILINE)
CITATION_RE = re.compile(r"\[(\d+)\]")

# Minimum words per section type by mode
MODE_LIMITS = {
    "quick": {"h2": 150, "h3": 80, "exec": 80},
    "standard": {"h2": 400, "h3": 150, "exec": 150},
    "deep": {"h2": 600, "h3": 250, "exec": 250},
}


def strip_fenced_code(text: str) -> str:
    """Replace fenced code blocks with empty lines so # comments aren't headings."""
    return FENCED_CODE_RE.sub("", text)


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


def _has_direct_subsection(sections, idx: int) -> bool:
    """Check whether sections[idx] has any nested subsection before the next sibling/parent."""
    level = sections[idx][0]
    for nxt_level, _, _, _ in sections[idx + 1:]:
        if nxt_level <= level:
            return False
        if nxt_level > level:
            return True
    return False


def _is_references_heading(title: str) -> bool:
    low = title.lower()
    return "references" in low or "bibliography" in low


def main():
    parser = argparse.ArgumentParser(description="Validate research report")
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--mode", choices=["quick", "standard", "deep"], default="standard"
    )
    parser.add_argument(
        "--output-json", action="store_true", help="Print JSON summary"
    )
    args = parser.parse_args()

    raw_text = args.report.read_text(encoding="utf-8")
    clean_text = strip_fenced_code(raw_text)
    sections = parse_sections(clean_text)
    limits = MODE_LIMITS[args.mode]
    errors = []
    warnings = []

    # 1. No asterisk bullets (outside fenced code blocks)
    if ASTERISK_BULLET_RE.search(clean_text):
        errors.append("Found asterisk bullets (* ); use hyphen bullets (- ) only.")

    # 2. No empty leaf sections (check only direct subtree, not rest of document)
    for i, (level, title, body, _subtree) in enumerate(sections):
        if not _has_direct_subsection(sections, i) and count_words(body) == 0:
            errors.append(f"Empty section: {'#' * level} {title}")

    # Identify first h2 (Executive Summary) index so it uses limits["exec"]
    first_h2_idx = next(
        (i for i, (lvl, _, _, _) in enumerate(sections) if lvl == 2), None
    )

    # 3. Minimum lengths (subtree word count; exclude Executive Summary & References from h2 floor)
    for i, (level, title, _body, subtree) in enumerate(sections):
        word_count = count_words(subtree)
        if level == 2:
            if i == first_h2_idx or _is_references_heading(title):
                continue
            if word_count < limits["h2"]:
                errors.append(
                    f"Section too short ({word_count} words, min {limits['h2']}): {title}"
                )
        elif level == 3:
            if word_count < limits["h3"]:
                errors.append(
                    f"Subsection too short ({word_count} words, min {limits['h3']}): {title}"
                )

    # 4. Executive summary check (first h2)
    if first_h2_idx is not None:
        _, exec_title, _, exec_subtree = sections[first_h2_idx]
        if "summary" not in exec_title.lower():
            warnings.append(
                "First section does not appear to be an Executive Summary."
            )
        exec_words = count_words(exec_subtree)
        if exec_words < limits["exec"]:
            errors.append(
                f"Executive Summary too short ({exec_words} words, min {limits['exec']})"
            )

    # 5. Citation presence
    total_words = count_words(raw_text)
    citation_count = len(set(CITATION_RE.findall(raw_text)))
    if citation_count == 0 and total_words > 200:
        errors.append("No citations found in report.")

    # 6. References section
    has_references = any(
        _is_references_heading(t) for _, t, _, _ in sections
    )
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
