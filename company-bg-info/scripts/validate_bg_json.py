#!/usr/bin/env python3
"""Validate BG-info JSON data before rendering DOCX."""

import argparse
import json
from pathlib import Path
import sys

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_TOP = ("company_name", "overview", "strategic_context", "sources")
ALLOWED_TOP = set(REQUIRED_TOP) | {
    "logo_path", "strategic_image", "strategic_image_caption",
    "divisions", "brands", "financials", "alternative_proteins",
    "ma_transactions", "innovation",
}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Root JSON value must be an object"]

    for k in REQUIRED_TOP:
        v = data.get(k)
        if k == "sources":
            if not isinstance(v, list):
                errors.append("Missing or invalid 'sources' (must be a list)")
        elif not isinstance(v, str) or not v.strip():
            errors.append(f"Missing or empty required string '{k}'")

    unknown = sorted(set(data.keys()) - ALLOWED_TOP)
    if unknown:
        errors.append(f"Unexpected top-level key(s): {', '.join(unknown)}")

    for i, item in enumerate(data.get("divisions") or []):
        if not isinstance(item, dict):
            errors.append(f"divisions[{i}] must be an object")
            continue
        for f in ("name", "description", "brands", "revenue"):
            if f not in item or not isinstance(item[f], str):
                errors.append(f"divisions[{i}].{f} must be a string")

    for i, item in enumerate(data.get("financials") or []):
        if not isinstance(item, dict) or not isinstance(item.get("year"), str) or not isinstance(item.get("metrics"), dict):
            errors.append(f"financials[{i}] must have string 'year' and object 'metrics'")

    for i, item in enumerate(data.get("ma_transactions") or []):
        if not isinstance(item, dict):
            errors.append(f"ma_transactions[{i}] must be an object")
            continue
        for f in ("year", "target", "amount", "description"):
            if f not in item or not isinstance(item[f], str):
                errors.append(f"ma_transactions[{i}].{f} must be a string")

    for i, src in enumerate(data.get("sources") or []):
        url = src.get("url") if isinstance(src, dict) else None
        if not isinstance(url, str) or not url.strip().startswith(("http://", "https://")):
            errors.append(f"sources[{i}].url must be an http(s) URL")

    return errors


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate BG-info JSON")
    ap.add_argument("--input", "-i", required=True, help="Path to data.json")
    args = ap.parse_args()

    p = Path(args.input)
    if not p.is_file():
        print(f"ERROR: File not found: {p}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate(data)
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {p} passed validation ({len(data.get('sources') or [])} source(s)).")


if __name__ == "__main__":
    main()
