---
name: paddleocr-doc-parsing
description: >-
  Extract structured Markdown and layout JSON from complex PDFs and document images—tables with
  cell-level precision, LaTeX formulas, figures, seals, charts, headers/footers, multi-column
  layouts, and accurate reading order via PaddleOCR cloud or self-hosted endpoints.
  Use for: 文档解析, 版面分析, 版面还原, 表格提取, 公式识别, 多栏排版, 扫描件结构化,
  发票, 财报, 复杂 PDF, PDF转Markdown, 图表, 阅读顺序; reading order, formula, LaTeX,
  layout parsing, structure extraction, PP-StructureV3, PaddleOCR-VL.
  Do not use for simple plain-text OCR, quick screenshots, or batch exhibition-photo workflows
  (use exhibition-notes for exhibition photos).
---

# PaddleOCR Document Parsing

Parse complex PDFs and document images into reading-order Markdown and structured layout JSON via PaddleOCR's `/layout-parsing` endpoint (`PaddleOCR-VL-1.6`, `PaddleOCR-VL-1.5`, `PP-StructureV3`, or self-hosted).

## Scope & Prerequisites

- **Use for**: Complex PDFs/scans with tables (invoices, financial reports), mathematical formulas (LaTeX), multi-column layouts, charts, seals, or mixed figures.
- **Do not use for**: Plain-text extraction, quick screenshot OCR, or batch exhibition photo processing (`exhibition-notes`).
- **Dependencies**: `pip install -r <skill-dir>/requirements.txt` (`httpx`). Optional for image optimization & PDF splitting: `pip install -r <skill-dir>/requirements-optimize.txt` (`Pillow`, `pypdfium2`).
- **Working directory**: Run scripts directly from the user's current working directory by referencing `<skill-dir>/scripts/...` (no need to `cd`, so relative input/output paths like `./report.pdf` stay valid).

## Core Workflow

1. **Parse to Markdown directly (recommended default)** — writes clean Markdown to `--md-out` and prints a compact metadata summary (`ok`, `pages`, `chars`, `markdown_path`, `json_path`) to `stdout` without dumping megabytes of raw JSON into context:
   ```powershell
   python "<skill-dir>/scripts/layout_caller.py" --file-path "./report.pdf" --md-out "./report.md"
   ```
   Or from a URL:
   ```powershell
   python "<skill-dir>/scripts/layout_caller.py" --file-url "https://example.com/paper.pdf" --md-out "./paper.md"
   ```
2. **Phone-captured, rotated, or curved scans** — enable orientation classification and/or unwarping (off by default for speed):
   ```powershell
   python "<skill-dir>/scripts/layout_caller.py" --file-path "./photo.jpg" --use-orientation-classify --use-unwarping --md-out "./photo.md"
   ```
3. **Need structured layout JSON (`prunedResult`, bounding boxes, confidence)** — omit `--md-out` (auto-saves compact JSON to system temp dir) or pass `--output "./result.json"`. Pass `--file-type 0` (PDF) or `--file-type 1` (image) only when the filename/URL lacks a standard extension.
4. **Output discipline**:
   - Return the complete extracted content the user asked for (all text, all tables, or body text without headers/footers) — do not silently truncate with `...` unless content exceeds ~10,000 chars, in which case save via `--md-out` and report the file path.
   - Only report metrics actually observed from the script output (`pages`, `chars`, saved paths); never fabricate confidence or block counts.

> Single-page images typically finish in 1–5s; 50+ page PDFs may take several minutes (default read timeout: 600s, connect timeout: 30s).

## First-Time Configuration

Required environment variables (get credentials from [paddleocr.com](https://www.paddleocr.com) → **API** → select an available model such as `PaddleOCR-VL-1.6`, `PaddleOCR-VL-1.5`, or `PP-StructureV3`):

- `PADDLEOCR_DOC_PARSING_API_URL` — full endpoint ending with `/layout-parsing` (`https://...`, or `http://127.0.0.1:<port>/layout-parsing` for local self-hosted deployments)
- `PADDLEOCR_ACCESS_TOKEN` — API access token
- `PADDLEOCR_DOC_PARSING_TIMEOUT` — optional read timeout in seconds (default `600`)

PowerShell (current session / persist):
```powershell
$env:PADDLEOCR_DOC_PARSING_API_URL = "https://your-service.paddleocr.com/layout-parsing"
$env:PADDLEOCR_ACCESS_TOKEN = "your_token"
```
Bash / zsh:
```bash
export PADDLEOCR_DOC_PARSING_API_URL="https://your-service.paddleocr.com/layout-parsing"
export PADDLEOCR_ACCESS_TOKEN="your_token"
```

Prefer configuring credentials via environment variables or the host app's settings rather than pasting tokens in chat. Verify setup anytime:
```powershell
python "<skill-dir>/scripts/smoke_test.py" --skip-api-test
python "<skill-dir>/scripts/smoke_test.py"
```

## Large Files & Preprocessing

- **Local file size limit**: Base64 local uploads are pre-checked at 50 MB; for larger files prefer `--file-url` or preprocess first.
- **Optimize large / phone-captured images** (auto-applies EXIF orientation, normalizes 16-bit TIFF / CMYK / alpha modes, creates parent dirs, safe for in-place overwrite):
  ```powershell
  python "<skill-dir>/scripts/optimize_file.py" "./scan.png" "./scan_opt.jpg" --quality 85 --target-size 10
  ```
- **Split large PDFs** (API max 100 pages per request; supports mixed ranges like `1-5,8,10-12`):
  ```powershell
  python "<skill-dir>/scripts/split_pdf.py" "./large.pdf" "./pages_1_5.pdf" --pages "1-5"
  ```

## Error Handling

When a request fails (`ok: false`), `layout_caller.py` writes the error JSON directly to `stderr` (exit code 1) and does **not** create a temp file.

- **Never silently fall back**: Always show the exact `error.code` and `error.message` to the user first, then let the user decide whether to fix credentials/retry or explicitly authorize an alternative approach.
- `CONFIG_ERROR`: Missing/invalid URL or token → guide user through First-Time Configuration.
- `API_ERROR` (403): Invalid or expired token → reconfigure `PADDLEOCR_ACCESS_TOKEN`.
- `API_ERROR` (429): Daily rate limit exceeded → inform user to wait or upgrade.
- `INPUT_ERROR`: Unsupported format, empty file, or >50 MB local file → convert to PDF/PNG/JPG, optimize, split, or use `--file-url`.
- Empty `text`: Document may be blank or contain no extractable text; retry with `--use-orientation-classify` if rotated.

## Reference

- [references/output_schema.md](references/output_schema.md) — Full JSON envelope schema, compact stdout summary, `layoutParsingResults` field paths, and complete CLI flag examples.
