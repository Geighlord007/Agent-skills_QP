"""
PaddleOCR Document Parser CLI

Usage:
    python layout_caller.py --file-path "./report.pdf" --md-out "./report.md"
    python layout_caller.py --file-url "https://example.com/doc.pdf"
    python layout_caller.py --file-path "./scan.jpg" --use-orientation-classify --md-out "./scan.md"
"""

import argparse
import json
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from lib import configure_stdio_utf8, parse_document

configure_stdio_utf8()


def get_default_output_path() -> Path:
    """Build a unique result path under the OS temp directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    short_id = uuid.uuid4().hex[:8]
    return (
        Path(tempfile.gettempdir())
        / "paddleocr"
        / "doc-parsing"
        / "results"
        / f"result_{timestamp}_{short_id}.json"
    )


def resolve_path(path_arg: str) -> Path:
    return Path(path_arg).expanduser().resolve()


def parse_extra_options(option_pairs: Optional[list[str]]) -> dict[str, Any]:
    """Parse repeatable --option KEY=VALUE arguments into JSON-typed values."""
    options: dict[str, Any] = {}
    if not option_pairs:
        return options
    for raw in option_pairs:
        if "=" not in raw:
            raise ValueError(f"Invalid --option format (expected KEY=VALUE): {raw}")
        key, value_str = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Empty option key in: {raw}")
        value_str = value_str.strip()
        try:
            value = json.loads(value_str)
        except json.JSONDecodeError:
            value = value_str
        options[key] = value
    return options


def count_pages(result: dict[str, Any]) -> int:
    raw = result.get("result")
    if isinstance(raw, dict):
        inner = raw.get("result")
        if isinstance(inner, dict):
            pages = inner.get("layoutParsingResults")
            if isinstance(pages, list):
                return len(pages)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PaddleOCR Document Parsing - with layout analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save clean Markdown directly (recommended)
  python layout_caller.py --file-path "./report.pdf" --md-out "./report.md"

  # Phone-captured or rotated scan with orientation correction
  python layout_caller.py --file-path "./photo.jpg" --use-orientation-classify --md-out "./photo.md"

  # Save full compact JSON to system temp directory (default)
  python layout_caller.py --file-url "https://example.com/document.pdf"

  # Print full JSON envelope directly to stdout
  python layout_caller.py --file-url "https://example.com/document.pdf" --stdout

Configuration:
  Set environment variables: PADDLEOCR_DOC_PARSING_API_URL, PADDLEOCR_ACCESS_TOKEN
  Optional: PADDLEOCR_DOC_PARSING_TIMEOUT
        """,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file-url", help="URL to document (PDF, PNG, JPG, etc.)")
    input_group.add_argument("--file-path", help="Local file path")

    parser.add_argument(
        "--file-type",
        type=int,
        choices=[0, 1],
        help="Optional file type override (0=PDF, 1=Image)",
    )
    parser.add_argument(
        "--use-orientation-classify",
        action="store_true",
        help="Enable document orientation classification (recommended for rotated/phone-captured scans)",
    )
    parser.add_argument(
        "--use-unwarping",
        action="store_true",
        help="Enable document unwarping (recommended for curved/folded document photos)",
    )
    parser.add_argument(
        "--option",
        action="append",
        metavar="KEY=VALUE",
        help="Additional JSON API option (repeatable, e.g. --option visualize=true)",
    )

    parser.add_argument(
        "--md-out",
        metavar="FILE",
        help="Write extracted Markdown directly to FILE",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (off by default to keep JSON compact)",
    )

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Save full JSON envelope to FILE (default: auto-save to temp dir when --md-out is not used)",
    )
    output_group.add_argument(
        "--stdout",
        action="store_true",
        help="Print full JSON envelope to stdout instead of saving JSON to a file",
    )

    args = parser.parse_args()

    try:
        extra_options = parse_extra_options(args.option)
    except ValueError as e:
        err_envelope = {
            "ok": False,
            "text": "",
            "result": None,
            "error": {"code": "INPUT_ERROR", "message": str(e)},
        }
        print(json.dumps(err_envelope, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    options: dict[str, Any] = {
        "useDocUnwarping": args.use_unwarping,
        "useDocOrientationClassify": args.use_orientation_classify,
        "visualize": False,
    }
    options.update(extra_options)

    result = parse_document(
        file_path=args.file_path,
        file_url=args.file_url,
        file_type=args.file_type,
        **options,
    )

    indent = 2 if args.pretty else None

    if not result.get("ok"):
        err_json = json.dumps(result, indent=indent, ensure_ascii=False)
        target_stream = sys.stdout if args.stdout else sys.stderr
        print(err_json, file=target_stream)
        sys.exit(1)

    md_path: Optional[Path] = None
    if args.md_out:
        md_path = resolve_path(args.md_out)
        try:
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(result.get("text", ""), encoding="utf-8")
        except OSError as e:
            print(f"Error: Cannot write Markdown to {md_path}: {e}", file=sys.stderr)
            sys.exit(5)

    if args.stdout:
        print(json.dumps(result, indent=indent, ensure_ascii=False))
        sys.exit(0)

    json_path: Optional[Path] = None
    should_save_json = bool(args.output) or not bool(args.md_out)
    if should_save_json:
        json_path = (
            resolve_path(args.output)
            if args.output
            else get_default_output_path().resolve()
        )
        try:
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(
                json.dumps(result, indent=indent, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"Result saved to: {json_path}", file=sys.stderr)
        except OSError as e:
            print(f"Error: Cannot write JSON to {json_path}: {e}", file=sys.stderr)
            sys.exit(5)

    summary = {
        "ok": True,
        "pages": count_pages(result),
        "chars": len(result.get("text", "")),
        "markdown_path": str(md_path) if md_path else None,
        "json_path": str(json_path) if json_path else None,
    }
    print(json.dumps(summary, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
