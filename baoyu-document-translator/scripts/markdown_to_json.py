#!/usr/bin/env python3
"""
Merge translated markdown back into extracted JSON as parts.

Usage: python markdown_to_json.py extracted.json translation.md output.json

Strategy:
- Read original extracted.json (has structure: key, runs, parts)
- Read translated markdown text
- Match translated text elements to original elements by order
- Split translated text into parts matching original run count
- Write merged output.json

IMPORTANT: This is a simple line-by-line mapping. For complex documents
with multi-line paragraphs, use the agent-guided approach instead.
"""
import sys
import json
from pathlib import Path


def split_into_parts(text, num_runs):
    """Split translated text into N parts to match original run count.

    Simple strategy: if runs == 1, return whole text.
    If runs > 1, try to find natural split points.
    """
    if num_runs <= 1:
        return [text]

    text = text.strip()
    if not text:
        return [""] * num_runs

    # Try splitting by common punctuation that might separate runs
    # For now, simple equal split (agent should produce correct parts in refined mode)
    parts = []
    avg_len = len(text) // num_runs

    for i in range(num_runs):
        if i == num_runs - 1:
            parts.append(text)
        else:
            # Try to find a split point near avg_len
            split_point = avg_len
            # Look for a good break after avg_len
            for j in range(min(avg_len + 20, len(text) - 1), avg_len - 1, -1):
                if j < len(text) and text[j] in '。，；！？. ,;!?':
                    split_point = j + 1
                    break
            parts.append(text[:split_point])
            text = text[split_point:]

    return parts


def merge_translation(extracted_path, md_path, output_path):
    extracted = json.loads(Path(extracted_path).read_text(encoding='utf-8'))
    md_text = Path(md_path).read_text(encoding='utf-8')

    # Split markdown into non-empty lines/paragraphs
    md_lines = [line.strip() for line in md_text.split('\n\n') if line.strip()]

    elements = extracted.get("elements", [])

    if len(md_lines) < len(elements):
        print(f"WARNING: markdown has {len(md_lines)} lines but {len(elements)} elements")

    for i, elem in enumerate(elements):
        if i < len(md_lines):
            translated_text = md_lines[i]
            num_runs = elem.get("runs", 1)
            elem["parts"] = split_into_parts(translated_text, num_runs)
        # Keep original parts if no translation available

    # Write output
    Path(output_path).write_text(
        json.dumps(extracted, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f'Written to {output_path}')
    return extracted


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(f'Usage: python {sys.argv[0]} extracted.json translation.md output.json')
        sys.exit(1)

    merge_translation(sys.argv[1], sys.argv[2], sys.argv[3])
