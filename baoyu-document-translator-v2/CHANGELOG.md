# CHANGELOG — baoyu-document-translator-v2

## 2.2.1 (2026-09-22) — Safe Docx evaluation + tracked-output notes (docs only)

### Added
- references/safe-docx-evaluation.md: measured coverage vs our extraction (table cells 99.4%,
  body 87.4%, textboxes 100%, headers/footers 100%, footnotes via get-footnotes), full-document
  A/B (473 paragraphs applied, 40 rejected for crossing field results, tracked output = 471 w:ins
  + 473 w:del, Word opens fine), hard limits (field-intersection unsupported; whole-document
  compare fails on WPS-heavy files), and the recommended hybrid write-back architecture.
- GUIDE.md: "留痕/审阅版" section — optional tracked delivery via Safe Docx.

### Notes
- No functional change: write-back engines unchanged (WIR on Linux/WSL2, surgical elsewhere).

## 2.2.0 (2026-09-22) — documentation只留三步 + WIR 定位修正

### Changed (docs only; no functional change, scripts frozen)
- SKILL.md: added a TL;DR (3 commands), an environment table (Linux/WSL2 → WIR first choice;
  native Windows/macOS → surgical), and an "optional QA pack" section listing gate/render-QA/
  localize/paginate/toc/reconcile/selftest as NOT run by default.
- WIR positioning corrected: it is a third-party compiled engine whose Linux-only .so
  cannot load on native Windows — it is NOT experimental/broken. Linux/WSL2 = first choice.
- New GUIDE.md: one-page Chinese guide (3 steps, engine choice, file inventory, limits).
- Version 2.1.4 → 2.2.0.

## 2.1.6 (2026-09-22) — field-result discipline finalized; gate concat field-aware

### Fixed
- Field RESULT runs: exclude ONLY purely-numeric generated results (SEQ/PAGEREF/PAGE).
  Static content inside field results (TOC entry titles, cached dates, alphanumeric codes
  like CCTCC M20241460) is translatable: extracted, written, and counted by the gate.
- verify_structure: fa_text() field-aware concat used for body presence AND story
  coverage (header/footer/footnote), so cached field digits no longer break adjacency.
- Production: SDT/TOC-field cached entries + cover-date cell surfaced by extraction and
  translated via auto-mapped fixups (full-width digit normalization for TOC numbering).
- reconcile: exit 1 only above 20% mismatch tolerance (sidebar/legend false positives).
- render_qa: --cjk-allow / --ignore-substr / --toc-min-entries policy flags.
- surgical: textbox write-back via write_para (W1 text-swallow fixed); field state machine
  shared across direct/ins/hyperlink children.

### Acceptance (all re-run)
- production gate exit 0 | D gate exit 0 (--cjk-allow) | truncation exit 1 | selftest 23/23.

## 2.1.5 (2026-09-22) — v5 blockers closed (textbox alignment, render-gate policy, claim precision)

### Fixed
- surgical textbox write-back (body + header/footer): use write_para (parts-aligned over
  ALL runs incl. tab runs) — fixes [Alpha][tab][Beta] text-swallow (W1).
- para_runs/para_run_elems: field state machine now shared across direct runs, w:ins and
  w:hyperlink children — body-level field RESULT runs truly excluded (claim now true).
- verify_structure: presence check covers story textbox/sdt (silent loss now reds).
- render_qa: --cjk-allow PATH, --ignore-substr "a|b" (documented export artifacts),
  --toc-min-entries N (heuristic window skip) — policy-green renders under documented rules.
- reconcile: exit 1 only when mismatches > 20% of TOC entries (sidebar/legend false positives).
- SKILL Step 5: removed phantom --precheck command; README: absolute-path note for Word COM.

### Selftest
- Fixture: tab-run textbox paragraph + body SEQ-field caption; checks: tab alignment
  extract+write, SEQ result exclusion, gate catches textbox wrong-text (23 checks).

## 2.1.4 (2026-09-22) — gate honesty restored + field-result discipline + selftest coverage

### Fixed (v4 evaluation blockers)
- verify_structure: removed self-referential tolerance (present_src); merged-cell exemption
  now requires ANOTHER key of the same physical cell to be present; full-text presence is
  punctuation-insensitive; added direction-aware truncation heuristic (CJK->EN lo=0.5,
  EN->CJK lo=0.2/hi=4) — truncated artifacts now exit 1 (acceptance-tested).
- localize fields: TOC \\c unwrap REMOVED (node-count neutral now); SEQ cached results
  blanked (caption numbers come from translated static text); step is gate-neutral.
- render_pdf: updates TOC fields only (SEQ results intentionally static).
- extract/surgical: field RESULT runs (cached SEQ/PAGEREF numbers) excluded from parts and
  write targets; WPS fused runs still translated; hyperlink runs included everywhere.
- extract: multi-paragraph cell text joins paragraphs with \\n (translator sees structure).
- MARKER_RE tolerates optional trailing pipe (third occurrence of this authoring bug).
- surgical: --consolidate-max N (cover-style consolidation threshold configurable).
- verify_structure: --cjk-allow PATH whitelist so deliberate bilingual retention coexists
  with the CJK gate (D final gate exit 0 with 15-entry allowlist).

### Selftest
- Fixture + checks extended: body textbox, SDT paragraph, hyperlink runs, multi-w:t runs,
  para_splits cells, cover consolidation, TR-prefixed write-back proof (18 checks, all PASS).

### Acceptance evidence
- truncation 90% artifact -> gate exit 1; production clean chain -> gate exit 0;
- D (2754 elements) -> gate exit 0 with allowlist, 83 pages, 0 blank pages.

## 2.1.3 (2026-09-22) — last structural blind spots closed (hyperlink runs, multi-w:t runs, textbox tables)

### Fixed
- para_runs / para_run_elems now include runs inside w:hyperlink (TOC entries, SDT headings),
  skipping field control/result runs so PAGEREF page numbers survive.
- set_run_text blanks EXTRA w:t nodes in WPS runs carrying multiple w:t (source-language
  residue previously survived in the same run).
- extract + surgical cover tables nested inside text boxes (pict/shape > textbox >
  txbxContent > tbl) as t_txbx_* keys.

### Verified (doc D final)
- 84 pages, 0 blank pages; structure gate PASS on structure items; rendered CJK = 44 lines,
  ALL deliberate first-occurrence bilingual company headers (by design, documented).
- SDT TOC entries (30), SDT heading, textbox-table cells (53) all translated.

## 2.1.2 (2026-09-22) — coverage blind-spots closed + environment-adaptive WIR

### Added
- extract: text boxes inside header/footer parts (txbx_h/f/hfirst/ffirst), paragraphs inside
  SDT content controls (p_sdt_*), multi-paragraph cell para_splits.
- surgical: write-back for body text boxes, header/footer text boxes, SDT paragraphs;
  run-consolidation for short high-variance (cover/title) paragraphs.
- engine_select.py + write_docx_wir.py: environment-adaptive engine (Linux+WIR / else surgical);
  wir-integration.md de-hardcoded; SKILL.md Step 6 documents selection.
- render_pdf.ps1: update SEQ and TOC fields before export.

### Verified on 5th production-grade doc (Wanlian Securities new-energy report, 2600 elements,
23 tables, 83 textbox elements, SDT chart captions): gate PASS on structure; rendered CJK
residuals classified: TOC field cached entries (WPS cache), footer page-frame static runs,
SDT-nested table cells — recorded as known blind spots (P1).

### Known limitations (carried)
- SDT-nested tables not extracted/written (P1).
- WPS TOC field cached Chinese entries survive Word PDF export unless field update succeeds (P2).
- Footer page-frame static CJK runs inside nested text boxes need per-doc patch (P2).

## 2.1.1 (2026-09-22) — governance + render-loop closure (post 3rd evaluation, 7.1/10)

### Changed
- SKILL.md: version 2.1.0→2.1.1 content refresh — WIR downgraded to *experimental /
  unavailable on Windows* everywhere (Step 0, both WIR sections, integration,
  troubleshooting); supported route = surgical path; directory tree completed
  (json_to_markdown_v2, build_fixture, selftest, paginate_plan, toc_pages);
  Troubleshooting gained rows: field switches, `--expect-cjk`, mixed-language filter,
  selftest, figure-plate semantics.
- README.md: quick start rewritten to the supported pipeline (was the worst path).
- `verify_structure.py`: full-text containment checks (was first-25-chars, let 90%-truncated
  text pass); uncovered non-body check now exact.
- `extract_docx_v2.py`: footnote `runs` = count of w:t-bearing runs (was all runs, causing
  parts/runs mismatch downstream).
- `write_docx_surgical.py`: warn (not silent drop) when footnote parts exceed text runs.
- `localize_cjk_en.py fields`: sanitize CJK date switches, WPS `Time`→`TIME`, rename CJK
  SEQ/TOC sequence identifiers (表/图→Table/Figure), renumber cached SEQ results,
  unwrap WPS list-of-tables/figures `TOC \c` fields (fused-run aware).
- `render_pdf.ps1`: update SEQ fields before PDF export (stale WPS cached results).
- `render_qa.py`: pages with images but no text = figure plates, not blank pages.
- `paginate_plan.py`: `--h1-always` (user policy: every Heading-1 on a new page),
  zero-height empty section-break marks + trailing empties, front-matter candidates
  (short paragraphs before first Heading-1 + toc/title styles), frequency-based chrome
  exclusion for source page-top mapping, translated-parts (not source text) matching.
- `toc_pages.py` (new): rewrite TOC entry page numbers from the rendered PDF.

### Known limitations (carried)
- Word PDF export re-evaluates some WPS-origin fields; a residual render-time
  "Error! Unrecognized switch argument" may appear in exported PDFs only (docx w:t is
  CJK-clean; interactive Word shows cached results). Workaround: select-all + F9 in Word
  before export.
- Artistic covers (high run-style variance) → patchwork formatting (P1: run-consolidation
  mode planned). Watermark translation not configurable (P2). SDT content still blind.
  Multi-line cell line breaks merged by proportional split (P1).

## 2.1.0 (2026-09-22) — localization & fidelity hardening (production-driven)

### Added
- `scripts/write_docx_surgical.py` — w:t-level write-back (Step 6 default): preserves
  page breaks, `w:ptab`, fields (fldChar/instrText), anchored drawings, `w:pict`;
  covers body, footnotes/endnotes, header/footer default+first+even variants, textboxes;
  field-run injection guard; footnote reference-run alignment fix.
- `scripts/verify_structure.py` — blocking gate (Step 7a): structure-node diff vs source,
  translated-text presence, all-part CJK residue, non-body story coverage, merged-cell
  duplicate warning; non-zero exit on failure.
- `scripts/merge_keyed_structure_aware.py` — Step 4 default merge: source `parts` as
  template (empty runs stay empty, `\t`/`\n` delimiter runs preserved, boundary-aware
  split across real text runs only).
- `scripts/localize_cjk_en.py` — CJK→EN layout pass: fonts / numbering / tracking / justify.
- `scripts/render_pdf.ps1`, `scripts/render_qa.py` — rendered QA (Step 7b): blank pages
  (auto chrome detection), `--cjk-scan`, `--toc-check`, `--montage`; non-zero exit.
- `scripts/chunk_keyed.py`, `scripts/reconcile_consistency.py`,
  `references/subagent-prompt-template.md` — Step 3 tooling.
- `scripts/build_fixture.py`, `scripts/selftest.py` — structural fixture + one-command
  selftest (fields/ptab/merges/tracked-ins/first-page header/gate).
- `references/cjk-en-localization-pitfalls.md` — CJK→EN checklist (run-structure audit,
  font localization, numbering/tracking traps incl. the bullet-lvlText TRAP, pagination
  rebuild, TOC page rewrite, coverage blind spots, merge guidance, rendered-QA mandate).

### Changed
- `extract_docx_v2.py`: physical-cell dedup (gridSpan/vMerge; one key per `w:tc`);
  tracked-insertion (`w:ins`) runs extracted; first/even-page header & footer variants;
  body textbox (`w:txbxContent`) extraction; `text` = join(parts) so ins content is
  translatable; linked sections no longer multiply-extracted.
- SKILL.md: Step 4/6/7 rewired to the new defaults; Troubleshooting table extended;
  dependencies updated (PyMuPDF, Pillow); phantom `qa_check_v2/qa_images_v2/qa_images_ocr_v2`
  references removed.

### Known limitations (tracked)
- WIR high-fidelity path not loadable on Windows (docx skill ships Linux `.so` only) —
  treat as unavailable; simple+surgical path is the supported route.
- Artistic covers (high run-style variance) get patchwork formatting under proportional
  run distribution — run-consolidation mode planned (P1).
- Watermark/header-brand translation not configurable (P2).

## 2.0.0 — keyed markdown round-trip, all-story extraction, PPTX table write-back.
