# baoyu-document-translator v2.2.2

Format-preserving **DOCX / PPTX / XLSX** translation — a production-hardened revision of
`baoyu-document-translator` (v1, **removed 2026-09-23** — see `../DEPRECATIONS.md`).
Includes surgical `w:t`-level write-back (or the WIR engine on Linux/WSL2), structure-aware
merge, all-story extraction, CJK→EN localization, blocking gates, rendered QA, pagination
pre-pass and a regression selftest.

## Scope & sibling dependencies

```
baoyu-translate   (upstream skill: the translation workflow itself — three modes, glossary)
        ▲
        │ called by both translators
        │
baoyu-document-translator-v2   ← THIS SKILL
   owns: extraction → chunking → merge → write-back → QA (optional pack)
        │
        │ borrows, only on Linux / WSL2 (native Windows cannot load the compiled engine)
        ▼
docx skill  →  WIR engine (`docx/scripts/engine`, Linux .so)      [optional dependency]
```

| Sibling skill | Role | Status |
|---|---|---|
| `baoyu-translate` | the actual translation workflow (quick / normal / refined, glossary) | **required** — v2 calls it |
| `docx` | supplies the WIR write-back engine | **optional** — Linux/WSL2 first choice; native Windows falls back to v2's surgical writer |
| `baoyu-document-translator` (v1) | old `python-docx` route (`run.text = ...` drops fields/page breaks) | **removed 2026-09-23**; recoverable from git history |
| `baoyu-document-translator-v2` | this skill | active |

Runtime engine choice: `python scripts/engine_select.py`.
XLSX needs no engine: `scripts/xlsx_translate.py` rewrites only shared strings + sheet names.

## Quick start (DOCX, supported path)

```bash
python scripts/extract_docx_v2.py input.docx extracted.json
python scripts/json_to_markdown_v2.py extracted.json source.md
# mixed CN/EN source? filter CJK-only blocks before chunking to save tokens:
#   (blocks without CJK keep their source text automatically at merge time)
python scripts/chunk_keyed.py source.md chunks/ 6000
# ... translate chunks (see references/subagent-prompt-template.md), concat drafts
#     into translation.md keeping every <!--key:...--> marker ...
python scripts/reconcile_consistency.py extracted.json translation.md   # exit 1 = align first
python scripts/merge_keyed_structure_aware.py extracted.json translation.md translated.json
python scripts/write_docx_surgical.py input.docx output.docx translated.json
python scripts/localize_cjk_en.py fonts     output.docx   # CJK→EN only
python scripts/localize_cjk_en.py numbering output.docx
python scripts/localize_cjk_en.py tracking  output.docx
python scripts/localize_cjk_en.py justify   output.docx
python scripts/localize_cjk_en.py fields    output.docx   # CJK field switches (WPS Time fields)
python scripts/paginate_plan.py source.pdf extracted.json translated.json output.docx --h1-always
python scripts/verify_structure.py input.docx output.docx translated.json   # add --expect-cjk for EN→ZH
pwsh -File scripts/render_pdf.ps1 -Docx output.docx -Pdf output.pdf
# NOTE: Word COM resolves relative paths against its own cwd — pass ABSOLUTE paths.
python scripts/render_qa.py output.pdf --cjk-scan --toc-check --montage sheets
python scripts/toc_pages.py output.pdf output.docx   # if TOC pages drifted
# regression check for skill developers:
python scripts/selftest.py ./selftest_run
```

Gate rule: `verify_structure.py` exit 1 = do NOT ship. `render_qa.py` exit 1 = inspect
(blank pages, rendered CJK, TOC mismatches); a page with images but no text is a figure
plate, not a blank.

## PPTX

```bash
python scripts/extract_pptx_v2.py input.pptx extracted.json
# ... translate ...
python scripts/write_pptx_v2.py input.pptx output.pptx translated.json
```

## Key improvements (v2.2 over v1)

1. **Keyed markdown markers** — mapping by stable key, not paragraph order.
2. **All stories extracted** — headers/footers (default+first+even), footnotes, endnotes,
   text boxes, tracked insertions; merged cells deduped to one key per physical cell.
3. **Surgical write-back** — only `<w:t>` nodes change; fields, images/anchors, page
   breaks, tabs, headers survive; fused WPS field runs handled; field-run guard.
4. **Structure-aware merge** — empty spacer runs stay empty; tab/page-number runs kept.
5. **CJK→EN localization + pagination pre-pass** — fonts, numbering, tracking, justify,
   field switches; deterministic page-break plan from source page tops; bounded repair.
6. **Blocking gates + rendered QA + selftest** — no silent shipping of broken docs.
7. **PPTX table cells** fully written back.
8. **EXTEND.md passthrough** for baoyu-translate preferences.
9. **XLSX translation** — `scripts/xlsx_translate.py` rewrites only `xl/sharedStrings.xml`
   text and sheet names, so styles, number formats, charts, images and formulas survive.
10. **Environment-adaptive write-back** — `engine_select.py` picks WIR (Linux/WSL2) or
    surgical (native Windows/macOS). A third-party option for tracked-changes delivery is
    evaluated in `references/safe-docx-evaluation.md`.

## Files

- `SKILL.md` — full workflow, pitfalls cross-refs, troubleshooting
- `GUIDE.md` — one-page guide (3 steps, engine choice, file inventory, known limits)
- `scripts/` — extraction / merge / write / localize / paginate / gate / QA / XLSX / selftest
- `references/schema-v2.md` — keyed JSON schema
- `references/cjk-en-localization-pitfalls.md` — CJK→EN checklist (read for CJK jobs)
- `references/subagent-prompt-template.md` — parallel-chunk translation contract
- `references/optimization-notes.md` — v1 issues and v2 fixes
- `references/wir-integration.md` — WIR engine integration (Linux/WSL2; see `scripts/engine_select.py`)
- `references/safe-docx-evaluation.md` — third-party tracked-changes A/B + hybrid write-back plan
- `CHANGELOG.md` — version history
