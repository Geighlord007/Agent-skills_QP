#!/usr/bin/env python3
"""
Validate keyed translated JSON.

Usage: python validate_v2.py translated.json extracted.json
"""
import sys
import json
from pathlib import Path


def validate(trans_path, extracted_path=None):
    errors = []

    try:
        trans_data = json.loads(Path(trans_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"JSON parse error in {trans_path}: {e}"]

    if "elements" not in trans_data:
        return False, ["Missing 'elements' key in translation JSON"]

    trans_elements = trans_data["elements"]
    extracted_keys = set()

    if extracted_path and Path(extracted_path).exists():
        try:
            ext_data = json.loads(Path(extracted_path).read_text(encoding="utf-8"))
            extracted_keys = {e["key"] for e in ext_data.get("elements", [])}
        except Exception as e:
            errors.append(f"Could not load extracted JSON: {e}")

    seen_keys = set()
    for i, elem in enumerate(trans_elements):
        key = elem.get("key")
        if not key:
            errors.append(f"Element {i}: missing 'key'")
            continue

        if key in seen_keys:
            errors.append(f"Element {i}: duplicate key '{key}'")
        seen_keys.add(key)

        runs = elem.get("runs")
        parts = elem.get("parts", [])

        if runs is None:
            errors.append(f"Element '{key}': missing 'runs'")
            continue

        if not isinstance(parts, list):
            errors.append(f"Element '{key}': 'parts' is not a list")
            continue

        if len(parts) != runs:
            errors.append(
                f"Element '{key}': parts length ({len(parts)}) != runs ({runs})"
            )

        if elem.get("hyperlink") and "url" not in elem["hyperlink"]:
            errors.append(f"Element '{key}': hyperlink missing url")

    if extracted_keys:
        trans_keys = {e["key"] for e in trans_elements}
        missing = extracted_keys - trans_keys
        extra = trans_keys - extracted_keys

        if missing:
            errors.append(f"Missing {len(missing)} elements: {list(missing)[:5]}...")
        if extra:
            errors.append(f"Extra {len(extra)} elements not in original: {list(extra)[:5]}...")

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_v2.py <translations.json> [extracted.json]")
        sys.exit(1)

    trans_path = sys.argv[1]
    extracted_path = sys.argv[2] if len(sys.argv) > 2 else None

    is_valid, errors = validate(trans_path, extracted_path)

    if is_valid:
        print("✓ Validation passed")
        data = json.loads(Path(trans_path).read_text(encoding="utf-8"))
        print(f"  Elements: {len(data['elements'])}")
        sys.exit(0)
    else:
        print("✗ Validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
