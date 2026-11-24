"""
PaddleOCR Document Parsing Library

Lightweight HTTP wrapper for PaddleOCR layout-parsing endpoints.
"""

import base64
import logging
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

DEFAULT_TIMEOUT = 600  # seconds (10 minutes) for read/write/pool
DEFAULT_CONNECT_TIMEOUT = 30.0  # seconds for TCP/TLS connect
MAX_LOCAL_FILE_MB = 50.0  # pre-flight guard before base64 encoding
MAX_RETRIES = 2  # retries on transient network errors or 502/503/504
RETRY_BACKOFF_SECONDS = 1.0
RETRYABLE_STATUS_CODES = frozenset({502, 503, 504})
LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

API_GUIDE_URL = "https://www.paddleocr.com"
FILE_TYPE_PDF = 0
FILE_TYPE_IMAGE = 1
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")


# =============================================================================
# Console / Environment Utilities
# =============================================================================


def configure_stdio_utf8() -> None:
    """Configure stdout/stderr to UTF-8 with replacement on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def _get_env(key: str) -> str:
    """Get environment variable, defaulting to empty string with whitespace stripped."""
    return os.getenv(key, "").strip()


def _http_timeout_from_env(env_key: str, default_seconds: float) -> float:
    """Read a positive finite HTTP timeout in seconds from the environment."""
    raw = os.getenv(env_key)
    if raw is None:
        return float(default_seconds)
    stripped = raw.strip()
    if not stripped:
        return float(default_seconds)
    try:
        timeout = float(stripped)
    except (ValueError, TypeError):
        logger.warning(
            "Invalid %s value %r; using default %ss",
            env_key,
            raw,
            default_seconds,
        )
        return float(default_seconds)
    if not math.isfinite(timeout) or timeout <= 0:
        logger.warning(
            "%s must be a finite number > 0 (got %r); using default %ss",
            env_key,
            raw,
            default_seconds,
        )
        return float(default_seconds)
    return timeout


def _resolve_api_url(api_url: str, env_var: str) -> str:
    """Validate URL scheme: allow https://, or http:// for loopback hosts only."""
    lower = api_url.lower()
    if lower.startswith("http://"):
        host = (urlparse(api_url).hostname or "").lower()
        if host not in LOOPBACK_HOSTS:
            raise ValueError(
                f"{env_var} must use https:// (http:// is only allowed for localhost/127.0.0.1/::1)."
            )
        return api_url
    if not lower.startswith("https://"):
        return f"https://{api_url}"
    return api_url


def get_config() -> tuple[str, str]:
    """
    Get API URL and token from environment.

    Returns:
        tuple of (api_url, token)

    Raises:
        ValueError: If required env vars are missing, API URL uses non-loopback http://,
            or URL path doesn't end with /layout-parsing.
    """
    api_url = _get_env("PADDLEOCR_DOC_PARSING_API_URL")
    token = _get_env("PADDLEOCR_ACCESS_TOKEN")

    if not api_url:
        raise ValueError(
            f"PADDLEOCR_DOC_PARSING_API_URL not configured. Get your API at: {API_GUIDE_URL}"
        )
    if not token:
        raise ValueError(
            f"PADDLEOCR_ACCESS_TOKEN not configured. Get your API at: {API_GUIDE_URL}"
        )

    api_url = _resolve_api_url(api_url, "PADDLEOCR_DOC_PARSING_API_URL")
    api_path = urlparse(api_url).path.rstrip("/")
    if not api_path.endswith("/layout-parsing"):
        raise ValueError(
            "PADDLEOCR_DOC_PARSING_API_URL must be a full endpoint ending with "
            "/layout-parsing. "
            "Example: https://your-service.paddleocr.com/layout-parsing"
        )

    return api_url, token


# =============================================================================
# File Utilities
# =============================================================================


def _detect_file_type(path_or_url: str) -> int:
    """Detect file type: 0=PDF, 1=Image."""
    path = path_or_url.lower()
    if path.startswith(("http://", "https://")):
        path = unquote(urlparse(path).path)

    if path.endswith(".pdf"):
        return FILE_TYPE_PDF
    if path.endswith(IMAGE_EXTENSIONS):
        return FILE_TYPE_IMAGE
    raise ValueError(f"Unsupported file format: {path_or_url}")


def _load_file_as_base64(file_path: str) -> str:
    """Load local file after pre-flight size validation and encode as base64."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise ValueError(f"File is empty (0 bytes): {file_path}")

    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_LOCAL_FILE_MB:
        raise ValueError(
            f"Local file is too large ({size_mb:.1f} MB > {MAX_LOCAL_FILE_MB:.0f} MB limit) "
            f"for base64 upload: {file_path}. Compress images with optimize_file.py, "
            "split PDFs with split_pdf.py, or pass --file-url instead."
        )

    return base64.b64encode(path.read_bytes()).decode("ascii")


# =============================================================================
# API Request
# =============================================================================


def _make_api_request(
    api_url: str, token: str, params: dict[str, Any]
) -> dict[str, Any]:
    """
    Make PaddleOCR document parsing API request with separated connect timeout
    and lightweight exponential backoff for transient 502/503/504 or network errors.
    """
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
        "Client-Platform": "official-skill",
    }

    read_timeout = _http_timeout_from_env(
        "PADDLEOCR_DOC_PARSING_TIMEOUT", float(DEFAULT_TIMEOUT)
    )
    timeout = httpx.Timeout(
        read_timeout,
        connect=min(DEFAULT_CONNECT_TIMEOUT, read_timeout),
    )

    resp: Optional[httpx.Response] = None
    last_exc: Optional[Exception] = None

    with httpx.Client(timeout=timeout) as client:
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = client.post(api_url, json=params, headers=headers)
            except TypeError as e:
                raise RuntimeError(
                    "Request parameters cannot be JSON-encoded; use only JSON-serializable "
                    f"option values ({e})"
                ) from e
            except httpx.TimeoutException as e:
                raise RuntimeError(f"API request timed out after {read_timeout}s") from e
            except httpx.RequestError as e:
                last_exc = e
                if attempt < MAX_RETRIES:
                    delay = RETRY_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Transient request error (%s); retrying in %.1fs...",
                        e,
                        delay,
                    )
                    time.sleep(delay)
                    continue
                raise RuntimeError(f"API request failed: {e}") from e

            if resp.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                delay = RETRY_BACKOFF_SECONDS * (2**attempt)
                logger.warning(
                    "Transient HTTP %s; retrying in %.1fs...",
                    resp.status_code,
                    delay,
                )
                time.sleep(delay)
                continue
            break

    if resp is None:
        raise RuntimeError(f"API request failed: {last_exc}")

    if resp.status_code != 200:
        error_detail = ""
        try:
            error_body = resp.json()
            if isinstance(error_body, dict):
                error_detail = str(error_body.get("errorMsg", "")).strip()
        except ValueError:
            pass

        if not error_detail:
            error_detail = (resp.text[:200] or "No response body").strip()

        if resp.status_code == 403:
            raise RuntimeError(f"Authentication failed (403): {error_detail}")
        if resp.status_code == 429:
            raise RuntimeError(f"API rate limit exceeded (429): {error_detail}")
        if resp.status_code >= 500:
            raise RuntimeError(
                f"API service error ({resp.status_code}): {error_detail}"
            )
        raise RuntimeError(f"API error ({resp.status_code}): {error_detail}")

    try:
        result = resp.json()
    except ValueError as e:
        raise RuntimeError(f"Invalid JSON response: {resp.text[:200]}") from e

    if not isinstance(result, dict):
        raise RuntimeError(
            f"Unexpected JSON shape (expected object): {resp.text[:200]}"
        )

    if result.get("errorCode", 0) != 0:
        msg = result.get("errorMsg", "Unknown error")
        raise RuntimeError(f"API error: {msg}")

    return result


# =============================================================================
# Main API
# =============================================================================


def parse_document(
    file_path: Optional[str] = None,
    file_url: Optional[str] = None,
    file_type: Optional[int] = None,
    **options: Any,
) -> dict[str, Any]:
    """
    Parse document with PaddleOCR.

    Args:
        file_path: Local file path (mutually exclusive with file_url)
        file_url: URL to file (mutually exclusive with file_path)
        file_type: Optional file type override (0=PDF, 1=Image)
        **options: Additional API options (e.g. useDocOrientationClassify=True)

    Returns:
        Envelope dict: {"ok": bool, "text": str, "result": dict | None, "error": dict | None}
    """
    fp = file_path.strip() if file_path else ""
    fu = file_url.strip() if file_url else ""
    if fp and fu:
        return _error(
            "INPUT_ERROR",
            "Provide only one of file_path or file_url, not both",
        )
    if not fp and not fu:
        return _error("INPUT_ERROR", "file_path or file_url required")
    if file_type is not None and file_type not in (FILE_TYPE_PDF, FILE_TYPE_IMAGE):
        return _error("INPUT_ERROR", "file_type must be 0 (PDF) or 1 (Image)")

    try:
        api_url, token = get_config()
    except ValueError as e:
        return _error("CONFIG_ERROR", str(e))

    try:
        resolved_file_type: Optional[int] = None
        if fu:
            params: dict[str, Any] = {"file": fu}
            if file_type is not None:
                resolved_file_type = file_type
            else:
                try:
                    resolved_file_type = _detect_file_type(fu)
                except ValueError:
                    resolved_file_type = None
        else:
            resolved_file_type = (
                file_type if file_type is not None else _detect_file_type(fp)
            )
            params = {"file": _load_file_as_base64(fp)}

        params["visualize"] = False
        params.update(options)
        if resolved_file_type is not None:
            params["fileType"] = resolved_file_type
        else:
            params.pop("fileType", None)
    except (ValueError, OSError) as e:
        return _error("INPUT_ERROR", str(e))

    try:
        result = _make_api_request(api_url, token, params)
    except RuntimeError as e:
        return _error("API_ERROR", str(e))

    try:
        text = _extract_text(result)
    except ValueError as e:
        return _error("API_ERROR", str(e))

    return {
        "ok": True,
        "text": text,
        "result": result,
        "error": None,
    }


def _extract_text(result: dict[str, Any]) -> str:
    """Extract concatenated page markdown from document parsing result."""
    if not isinstance(result, dict):
        raise ValueError("Invalid API response: top-level response must be an object")

    raw_result = result.get("result")
    if not isinstance(raw_result, dict):
        raise ValueError("Invalid API response: missing 'result' object")

    pages = raw_result.get("layoutParsingResults")
    if not isinstance(pages, list):
        raise ValueError(
            "Invalid API response: result.layoutParsingResults must be an array"
        )

    texts = []
    for i, page in enumerate(pages):
        if not isinstance(page, dict):
            raise ValueError(
                f"Invalid API response: result.layoutParsingResults[{i}] must be an object"
            )

        markdown = page.get("markdown")
        if not isinstance(markdown, dict):
            raise ValueError(
                f"Invalid API response: result.layoutParsingResults[{i}].markdown must be an object"
            )

        text = markdown.get("text")
        if not isinstance(text, str):
            raise ValueError(
                f"Invalid API response: result.layoutParsingResults[{i}].markdown.text must be a string"
            )
        texts.append(text)

    return "\n\n".join(texts)


def _error(code: str, message: str) -> dict[str, Any]:
    """Create error response envelope."""
    return {
        "ok": False,
        "text": "",
        "result": None,
        "error": {"code": code, "message": message},
    }
