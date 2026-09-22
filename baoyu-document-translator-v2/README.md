# baoyu-document-translator v2.1

Optimized fork of `baoyu-document-translator` for format-preserving DOCX/PPTX
translation. v2.1 is a production-hardened revision: surgical w:t-level write-back,
structure-aware merge, all-story extraction, CJK→EN localization, blocking gates,
rendered QA, pagination pre-pass, and a regression selftest.

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

## Key improvements (v2.1 over v1)

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

## Files

- `SKILL.md` — full workflow, pitfalls cross-refs, troubleshooting
- `scripts/` — extraction / merge / write / localize / paginate / gate / QA / selftest
- `references/schema-v2.md` — keyed JSON schema
- `references/cjk-en-localization-pitfalls.md` — CJK→EN checklist (read for CJK jobs)
- `references/subagent-prompt-template.md` — parallel-chunk translation contract
- `references/optimization-notes.md` — v1 issues and v2 fixes
- `references/wir-integration.md` — experimental WIR engine notes (non-Windows only)
- `CHANGELOG.md` — version history
