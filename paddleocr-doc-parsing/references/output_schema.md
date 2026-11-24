# PaddleOCR Document Parsing Output Schema & CLI Reference

This document defines the output formats and CLI flags of `scripts/layout_caller.py`.

## Compact `stdout` Summary (Default & `--md-out` Modes)

When `--stdout` is **not** set and parsing succeeds, `layout_caller.py` prints a single compact JSON summary to `stdout` so agents can inspect metadata without loading megabytes of raw layout coordinates into context:

```json
{
  "ok": true,
  "pages": 3,
  "chars": 4520,
  "markdown_path": "C:\\work\\report.md",
  "json_path": null
}
```

- When `--md-out <FILE>` is passed without `--output`, only the Markdown file is written (`json_path` is `null`).
- When neither `--md-out` nor `--output` is passed, the full JSON envelope is auto-saved (compact, no `--pretty`) under `<system-temp>/paddleocr/doc-parsing/results/result_<timestamp>_<id>.json` and its path is printed to both `stderr` (`Result saved to: ...`) and `json_path`.
- When both `--md-out` and `--output` are passed, both files are written.

## Full JSON Envelope (`--output`, default temp file, or `--stdout`)

On success:

```json
{
  "ok": true,
  "text": "Extracted markdown text joined across all pages with \\n\\n",
  "result": { ... },
  "error": null
}
```

On error (`ok: false`, exit code `1`):

- No temp JSON or Markdown file is written.
- The error envelope is printed directly to `stderr` (or `stdout` if `--stdout` was passed):

```json
{
  "ok": false,
  "text": "",
  "result": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

## Error Codes

| Code           | Description                                                              |
| -------------- | ------------------------------------------------------------------------ |
| `INPUT_ERROR`  | Invalid arguments, missing/empty/>50 MB local file, or unsupported type. |
| `CONFIG_ERROR` | Missing or invalid `PADDLEOCR_DOC_PARSING_API_URL` or token.             |
| `API_ERROR`    | Network failure, timeout, HTTP error (403/429/5xx), or invalid JSON.     |

## Raw Provider Result (`result`)

Raw fields may vary slightly by model (`PaddleOCR-VL-1.6`, `PaddleOCR-VL-1.5`, `PP-StructureV3`). Typical structure:

```json
{
  "logId": "request-uuid",
  "errorCode": 0,
  "errorMsg": "Success",
  "result": {
    "layoutParsingResults": [
      {
        "prunedResult": { ... },
        "markdown": {
          "text": "Full page content in Markdown/HTML format",
          "images": {
            "imgs/filename.jpg": "https://..."
          }
        }
      }
    ]
  }
}
```

Key paths relative to the envelope root:

- `text` — Full document Markdown concatenated across all pages (`\n\n`-separated).
- `result.result.layoutParsingResults[n].markdown.text` — Page `n` Markdown.
- `result.result.layoutParsingResults[n].prunedResult` — Page `n` structured layout elements (regions, polygons, labels, confidence).

## CLI Command Examples (Single-Line, Cross-Platform)

```powershell
# Recommended: save clean Markdown directly
python "<skill-dir>/scripts/layout_caller.py" --file-path "./report.pdf" --md-out "./report.md"

# Save both Markdown and pretty-printed raw JSON
python "<skill-dir>/scripts/layout_caller.py" --file-path "./report.pdf" --md-out "./report.md" --output "./report.json" --pretty

# Phone-captured or skewed scan with orientation + unwarp enabled
python "<skill-dir>/scripts/layout_caller.py" --file-path "./photo.jpg" --use-orientation-classify --use-unwarping --md-out "./photo.md"

# Pass any extra model-specific API option
python "<skill-dir>/scripts/layout_caller.py" --file-url "https://example.com/doc.pdf" --option visualize=true --output "./out.json"

# Explicit file type override (0=PDF, 1=Image)
python "<skill-dir>/scripts/layout_caller.py" --file-url "https://example.com/download?id=42" --file-type 0 --md-out "./doc.md"

# Print full JSON envelope to stdout without saving files
python "<skill-dir>/scripts/layout_caller.py" --file-url "https://example.com/doc.pdf" --stdout
```
