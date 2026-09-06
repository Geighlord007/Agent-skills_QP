#!/usr/bin/env python3
"""
Content QA for translated documents.

Usage:
    python qa_check.py original.json translated.docx [options]

Checks:
1. Untranslated text (source language characters remaining)
2. Element count mismatch (missing or extra elements)
3. Runs count mismatch per element
4. Empty text elements
5. Table structure integrity

Output: QA report to stdout and optional file.
"""
import sys
import json
import re
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def detect_language(text):
    """Detect if text contains CJK, Arabic, Cyrillic, etc."""
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return 'ja'
    if re.search(r'[\uac00-\ud7af]', text):
        return 'ko'
    if re.search(r'[\u0600-\u06ff]', text):
        return 'ar'
    if re.search(r'[\u0400-\u04ff]', text):
        return 'ru'
    return 'other'


def qa_docx(original_json, docx_path, out_path=None):
    """Run QA checks on a translated DOCX."""
    original = json.loads(Path(original_json).read_text(encoding='utf-8'))
    doc = Document(docx_path)

    issues = []
    warnings = []
    info = []

    # Build original element map
    orig_map = {e['key']: e for e in original.get('elements', [])}

    # Extract current elements from translated docx
    para_map = {id(p._p): p for p in doc.paragraphs}
    table_map = {id(t._tbl): t for t in doc.tables}

    current_elements = []
    para_idx = 0
    table_idx = 0

    for child in doc.element.body:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'p':
            para = para_map.get(id(child))
            if para is None:
                continue
            para_idx += 1
            text = para.text.strip()
            if text:
                current_elements.append({
                    'key': f'p{para_idx - 1}',
                    'type': 'paragraph',
                    'text': text,
                    'runs': len([r for r in para.runs if r.text.strip()])
                })

        elif tag == 'tbl':
            table = table_map.get(id(child))
            if table is None:
                continue
            table_idx += 1
            for ri, row in enumerate(table.rows):
                for ci, cell in enumerate(row.cells):
                    tcPr = cell._tc.find(qn('w:tcPr'))
                    is_merged = False
                    if tcPr is not None:
                        vMerge = tcPr.find(qn('w:vMerge'))
                        if vMerge is not None and vMerge.get(qn('w:val')) is None:
                            is_merged = True
                    if not is_merged and cell.text.strip():
                        current_elements.append({
                            'key': f't{table_idx - 1}_r{ri}_c{ci}',
                            'type': 'table_cell',
                            'text': cell.text.strip(),
                            'runs': len([r for p in cell.paragraphs for r in p.runs if r.text.strip()])
                        })

    # Check 1: Element count
    orig_count = len(orig_map)
    curr_count = len(current_elements)
    if curr_count != orig_count:
        issues.append(f"Element count mismatch: original={orig_count}, current={curr_count}")

    # Check 2: Missing / extra keys
    orig_keys = set(orig_map.keys())
    curr_keys = {e['key'] for e in current_elements}
    missing = orig_keys - curr_keys
    extra = curr_keys - orig_keys
    if missing:
        issues.append(f"Missing {len(missing)} elements: {list(missing)[:5]}")
    if extra:
        warnings.append(f"Extra {len(extra)} elements not in original: {list(extra)[:5]}")

    # Check 3: Per-element checks
    untranslated = []
    runs_mismatch = []

    for elem in current_elements:
        key = elem['key']
        text = elem['text']

        # Check for untranslated source language text
        lang = detect_language(text)
        if lang == 'zh':
            untranslated.append((key, text[:50]))

        # Check runs count
        if key in orig_map:
            orig_runs = orig_map[key].get('runs', 0)
            curr_runs = elem.get('runs', 0)
            if orig_runs != curr_runs:
                runs_mismatch.append(f"{key}: runs changed from {orig_runs} to {curr_runs}")

    if untranslated:
        issues.append(f"Found {len(untranslated)} elements with untranslated Chinese text")
        for key, text in untranslated[:10]:
            issues.append(f"  {key}: {text}")

    if runs_mismatch:
        warnings.append(f"Runs mismatch in {len(runs_mismatch)} elements")
        for msg in runs_mismatch[:10]:
            warnings.append(f"  {msg}")

    # Check 4: Empty elements
    empty_count = sum(1 for e in current_elements if not e['text'].strip())
    if empty_count > 0:
        warnings.append(f"{empty_count} elements have empty text")

    # Generate report
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("DOCUMENT TRANSLATION QA REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"File: {docx_path}")
    report_lines.append(f"Original elements: {orig_count}")
    report_lines.append(f"Current elements: {curr_count}")
    report_lines.append("")

    if issues:
        report_lines.append(f"❌ ISSUES ({len(issues)}):")
        for issue in issues:
            report_lines.append(f"  - {issue}")
        report_lines.append("")

    if warnings:
        report_lines.append(f"⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            report_lines.append(f"  - {warning}")
        report_lines.append("")

    if not issues and not warnings:
        report_lines.append("✅ All checks passed!")
        report_lines.append("")

    report_lines.append("=" * 60)

    report = "\n".join(report_lines)
    print(report)

    if out_path:
        Path(out_path).write_text(report, encoding='utf-8')
        print(f"\nReport saved to {out_path}")

    return len(issues) == 0


def main():
    if len(sys.argv) < 3:
        print("Usage: python qa_check.py <original.json> <translated.docx> [report.txt]")
        sys.exit(1)

    original_json = sys.argv[1]
    docx_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else None

    passed = qa_docx(original_json, docx_path, out_path)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
