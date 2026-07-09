#!/usr/bin/env python3
"""
Validate a BG-info JSON file against the expected schema.
Usage: python validate_bg_json.py --input data.json
"""

import argparse
import json
import sys

REQUIRED_TOP_KEYS = [
    "company_name",
    "overview",
    "strategic_context",
    "sources",
]

OPTIONAL_TOP_KEYS = [
    "strategic_image",
    "strategic_image_caption",
    "divisions",
    "brands",
    "financials",
    "alternative_proteins",
    "ma_transactions",
    "innovation",
]


def validate(data):
    errors = []
    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            errors.append(f"Missing required key: {key}")
    for key in data:
        if key not in REQUIRED_TOP_KEYS + OPTIONAL_TOP_KEYS:
            errors.append(f"Unknown key: {key}")

    if not isinstance(data.get("sources", []), list):
        errors.append("'sources' must be a list")
    else:
        for i, src in enumerate(data.get("sources", [])):
            if "url" not in src:
                errors.append(f"Source {i} missing 'url'")

    if data.get("divisions") and not isinstance(data["divisions"], list):
        errors.append("'divisions' must be a list")

    if data.get("ma_transactions") and not isinstance(data["ma_transactions"], list):
        errors.append("'ma_transactions' must be a list")

    if data.get("financials") and not isinstance(data["financials"], list):
        errors.append("'financials' must be a list")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate BG-info JSON")
    parser.add_argument("--input", "-i", required=True, help="Path to JSON file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = validate(data)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
