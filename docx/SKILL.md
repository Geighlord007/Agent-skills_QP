---
name: docx
description: "Create, edit, polish, and validate Word documents (.docx) via C# OpenXML SDK, pure-Python surgical/OOXML editing, Linux/WSL2 WIR engine, citation-aware Markdown-to-Word conversion, and post-build figure/structural verification (Route 4). Use for creating formatted .docx reports/specs from scratch, filling or editing existing .docx templates, adding comments/tracked changes, converting Markdown + citation.jsonl into Word, or polishing/verifying delivered reports (widen_extent, count invariants, serialized Word open). Do not use for full-document translation pipelines (use baoyu-document-translator-v4) or authoring standalone charts (use consulting-chart)."
---

# Part 1: Routing

Plain text extraction (`cat` / `read_file`) strips all Word formatting. Whenever layout, styles, or structure matter, route by what inputs you have:

## Route 1 — Existing `.docx` whose format/style matters (Edit / Fill / Review)

If a `.doc` (legacy binary) is supplied, convert first: `libreoffice --headless --convert-to docx <file.doc>`.
If the `.docx` is only a raw text/data source whose formatting is irrelevant, extract text and use Route 3 instead.

Choose the editing backend by **task type and platform**:

| Task | Native Windows 11 / macOS | Linux / WSL2 (Python 3.12) |
|------|---------------------------|----------------------------|
| **Format-preserving text replacement / template fill** (keeps runs, fields, headers/footers, text boxes, footnotes) | **`scripts/engine_surgical/`** (`extract_elements()` + `apply_keyed_parts()` / `SurgicalSession`). Pure Python; shared write-back core for `baoyu-document-translator-v4` (do not duplicate). | `scripts/engine_surgical/` or WIR (`scripts/engine/`). |
| **Comments, tracked changes (`w:ins`/`w:del`), or structural edits** (insert/delete paragraphs, tables, sections) | **Preferred: run WIR `.so` under WSL2 (Python 3.12)**. On pure native Windows/macOS, use **C# OpenXML SDK** or **`zipfile + lxml` direct OOXML editing** followed by `Validator.dll` validation (do **not** use `python-docx` high-level API for tracked changes or complex comments; `engine_surgical` only modifies `<w:t>` text). | **WIR engine** (`scripts/engine/_core...linux-gnu.so`, retained intentionally for Linux/WSL2 machines; see `references/wir-reference.md`). |

## Route 2 — Markdown + `citation.jsonl` (`md2docx`)

Trigger when you have an existing Markdown document **paired with a `citation.jsonl` database** requiring Word footnotes, endnotes, or hyperlink cross-references (`references/md2docx-reference.md`):

```bash
python scripts/md2docx/md2docx_convert.py <file.md> --citation <citation.jsonl> --style footnote --output-dir <dir>
```

Intermediate files are isolated in a temporary directory and cleaned up automatically. Do **not** author Markdown from scratch just to run `pandoc` — use Route 3 for native Word quality.

## Route 3 — Create from Scratch (C# + OpenXML SDK)

No target `.docx`, no upstream Markdown + `citation.jsonl`. Build via the cross-platform Python CLI (`references/openxml-sdk-reference.md`):

```bash
python scripts/docx_cli.py env                      # Check dotnet, Python, optional tools
python scripts/docx_cli.py init                     # Create workspace in <temp>/docx-work/
# Edit <temp>/docx-work/Program.cs
python scripts/docx_cli.py build <output/Topic.docx> # Compile -> run -> auto-fix -> validate
```

`build` auto-aligns `Docx.csproj` with the installed .NET SDK (8/9/10+), checks CJK `\uXXXX` escape abuse, runs `validate_all.py` (with pure-Python fallback on Windows/macOS), and runs `dotnet validator/Validator.dll` (with `rollForward: Major`).

## Route 4 — Polish & Verify Delivered `.docx` (成品文档精修与验尸)

Use after a `.docx` report is built (or received for final QA) to widen undersized embedded figures without redrawing, guard structural count invariants, and run a serialized host-app open test (`references/polish-and-verify.md`):

```bash
python scripts/polish/verify_counts.py capture <report.docx> --out baseline.json
python scripts/polish/widen_extent.py <report.docx> --list
python scripts/polish/widen_extent.py <report.docx> --target rId12=445pt --dry-run
python scripts/polish/verify_counts.py check <report.docx> --baseline baseline.json
python scripts/polish/verify_word_open.py <report.docx>
```

Before redrawing any embedded figure for small text, check `consulting-chart/scripts/scale_law.py` on its source SVG first, then prefer byte-exact `widen_extent.py` (Lever 1) over redrawing (Lever 2). Never run `verify_word_open.py` concurrently across parallel agents.

---

# Part 2: Reference Map (Progressive Disclosure)

Read the **Common Traps** section of your chosen reference first, then load only the modules your document needs:

```
docx/
├── SKILL.md                           ← Routing, platform matrix, rules
├── references/
│   ├── openxml-sdk-reference.md       → C# creation patterns, XSD order, traps
│   ├── wir-reference.md               → WIR editing API (Linux/WSL2 only)
│   ├── md2docx-reference.md           → Citation-aware MD -> Word pipeline
│   ├── cover-background-guide.md      → Bespoke Playwright + SVG cover/body/back backgrounds
│   ├── polish-and-verify.md           → Route 4: 3-lever figure polish & 8 verification rules
│   ├── chart-reference.md             → Native Word charts (pie, bar, line)
│   ├── omml-reference.md              → OMML math equations
│   └── matplotlib-guide.md            → Complex charts Word cannot render natively
├── scripts/
│   ├── docx_cli.py                    → Cross-platform CLI (env / init / build / validate)
│   ├── validate_all.py                → Element-order auto-fix + business rules (native + pure-Python fallback)
│   ├── engine/                        → WIR native core (Linux/WSL2 + Python 3.12 only)
│   ├── engine_surgical/               → Pure-Python format-preserving extract + write-back (all platforms)
│   ├── polish/                        → Route 4 tools (widen_extent.py, verify_counts.py, verify_word_open.py)
│   └── md2docx/                       → Citation -> Word post-processors
├── validator/                         → Cross-platform OpenXML XSD Validator.dll (.NET rollForward: Major)
└── assets/templates/
    ├── Docx.csproj                    → C# project template (.NET 10 + OpenXml 3.3.0)
    ├── Program.cs                     → Starter entry point
    ├── Example.cs                     → English full-featured demo (consult when building EN docs)
    └── CJKExample.cs                  → Chinese/CJK demo (consult when building CJK docs)
```

---

# Part 3: Hard Rules & Quality Standards

1. **Never rewrite an existing template from scratch** — edit in place via Route 1.
2. **Never hand-write Markdown and pipe through Pandoc** for general document creation — use Route 3.
3. **Always validate before delivery** — run `python scripts/docx_cli.py validate <file.docx>` after any edit or creation.
4. **Clean delivery & topic naming** — name files by topic in the user's language (e.g., `储能电站分析报告.docx`, `Energy_Storage_Report.docx`), never `output.docx`; leave no `v1`/`v2`/`final` or temp clutter in the output folder.
5. **Language consistency** — keep body, headings, headers/footers, TOC, chart labels, and filenames in the user's language.
6. **Low-saturation 3-tier palette** — pick ONE hue family with Primary (headings) / Dark (body) / Light (captions); never pure `#FF0000`/`#0000FF`.
7. **Bespoke cover backgrounds** — when a cover is needed, follow `references/cover-background-guide.md` to render original Playwright + SVG PNGs matching your palette; keep center text zones clean with strong contrast.
8. **Word count tolerance** — targets like "X字左右" allow ±20%.

## Delivery Checklist

1. File opens cleanly in Word / WPS without repair prompts.
2. `python scripts/docx_cli.py validate <file.docx>` passes (business rules + OpenXML XSD).
3. Headers, footers, and page numbers are present and correctly positioned.
4. Zero placeholder text remains (`[Company Name]`, `TODO`, etc.).
5. All intended images/charts are embedded (verify image count in `build` output).
6. Cover/back-cover typography contrasts cleanly against its background.
