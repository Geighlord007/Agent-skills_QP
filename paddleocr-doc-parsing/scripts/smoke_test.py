"""
Smoke Test for PaddleOCR Document Parsing Skill

Verifies dependencies, configuration, and API connectivity.

Usage:
    python smoke_test.py
    python smoke_test.py --skip-api-test
    python smoke_test.py --test-url "https://example.com/test.pdf"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib import DEFAULT_TIMEOUT, configure_stdio_utf8

configure_stdio_utf8()


def print_config_guide() -> None:
    """Print cross-platform configuration guide (PowerShell and Bash)."""
    print(
        f"""
============================================================
HOW TO CONFIGURE API CREDENTIALS
============================================================

1. Visit https://www.paddleocr.com -> click API -> choose a model
   (e.g. PaddleOCR-VL-1.6, PaddleOCR-VL-1.5, or PP-StructureV3)
2. Copy the API URL (ending with /layout-parsing) and Access Token

PowerShell (current session):
  $env:PADDLEOCR_DOC_PARSING_API_URL = "https://your-service.paddleocr.com/layout-parsing"
  $env:PADDLEOCR_ACCESS_TOKEN = "your_token_here"
  $env:PADDLEOCR_DOC_PARSING_TIMEOUT = "{DEFAULT_TIMEOUT}"  # optional

PowerShell (persist for user):
  setx PADDLEOCR_DOC_PARSING_API_URL "https://your-service.paddleocr.com/layout-parsing"
  setx PADDLEOCR_ACCESS_TOKEN "your_token_here"

Bash / zsh:
  export PADDLEOCR_DOC_PARSING_API_URL="https://your-service.paddleocr.com/layout-parsing"
  export PADDLEOCR_ACCESS_TOKEN="your_token_here"
  export PADDLEOCR_DOC_PARSING_TIMEOUT="{DEFAULT_TIMEOUT}"  # optional

Self-hosted local service:
  http://127.0.0.1:<port>/layout-parsing is also allowed.
============================================================
""",
        file=sys.stderr,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PaddleOCR Document Parsing smoke test"
    )
    parser.add_argument("--test-url", help="Optional: Custom document URL for testing")
    parser.add_argument(
        "--skip-api-test",
        action="store_true",
        help="Skip API connectivity test, only check configuration",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("PaddleOCR Document Parsing - Smoke Test")
    print("=" * 60)

    print("\n[1/3] Checking dependencies...")
    try:
        import httpx

        print(f"  + httpx: {httpx.__version__}")
    except ImportError:
        print("  X httpx not installed", file=sys.stderr)
        print("  Install with: pip install httpx", file=sys.stderr)
        return 1

    print("\n[2/3] Checking configuration...")
    from lib import get_config

    try:
        api_url, token = get_config()
        print(f"  + PADDLEOCR_DOC_PARSING_API_URL: {api_url}")
        masked_token = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
        print(f"  + PADDLEOCR_ACCESS_TOKEN: {masked_token}")
    except ValueError as e:
        print(f"  X {e}", file=sys.stderr)
        print_config_guide()
        return 1

    if args.skip_api_test:
        print("\n[3/3] Skipping API connectivity test (--skip-api-test)")
        print("\n" + "=" * 60)
        print("Configuration Check Complete!")
        print("=" * 60)
        return 0

    print("\n[3/3] Testing API connectivity...")
    test_url = (
        args.test_url
        or "https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/pp_structure_v3_demo.png"
    )
    print(f"  Test document: {test_url}")

    from lib import parse_document

    result = parse_document(file_url=test_url)
    if not result.get("ok"):
        error = result.get("error", {})
        print(
            f"\n  X API call failed ({error.get('code')}): {error.get('message')}",
            file=sys.stderr,
        )
        if "Authentication" in error.get("message", ""):
            print(
                "  Hint: Verify PADDLEOCR_ACCESS_TOKEN is valid and not expired.",
                file=sys.stderr,
            )
        return 1

    print("  + API call successful!")
    text = result.get("text", "")
    if text:
        preview = text[:200].replace("\n", " ")
        if len(text) > 200:
            preview += "..."
        print(f"\n  Preview: {preview}")

    print("\n" + "=" * 60)
    print("Smoke Test PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
