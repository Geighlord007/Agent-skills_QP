# Project: Yeast-Expressed Human Osteopontin (OPN) — Recommended Cell Assays

**Mode:** standard  
**Language:** English  
**Objective:** Recommend a prioritized set of cell assays for yeast-expressed human OPN to support safety and functional claims, with full source traceability.

## Selected threads

| Thread | File | Focus |
|--------|------|-------|
| T1 | `drafts/T01_fundamentals.md` | OPN identity, structure, native sources, key properties |
| T2 | `drafts/T02_mechanism.md` | Biological mechanisms: barrier, immune modulation, bone mineralization |
| T5 | `drafts/T05_safety.md` | Safety/toxicology precedent, allergenicity, genotoxicity requirements |
| T6 | `drafts/T06_clinical.md` | Human and animal evidence for OPN functions |
| T7 | `drafts/T07_regulatory.md` | GRAS, Novel Food, EFSA, FSANZ precedents |
| T11 | `drafts/T11_assays.md` | Recommended cell assays, models, readouts, prioritization |

## Phase

Completed: Phase B — Report assembly, validation, and delivery.

## Deliverables

- `report.md` — validated research report (4,888 words, 32 citations)
- `output/yeast_opn_cell_assay_report.docx` — DOCX conversion
- `output/charts/assay_priority_tiers.svg` — optional priority-tier chart
- `datas/sources.jsonl` — 32 unique sources with URLs/PMIDs/patents
- `eval/quality_evaluation.md` — rubric-based score (32/35)

## Validation

- `verify_citations.py`: passed (32/32 citations resolve)
- `validate_report.py`: passed (standard mode)
- `md_to_docx.py`: DOCX generated successfully

## Notes

- Output is in English as required.
- `cosmetic-research` skill was not modified.
- Report highlights key data gap: no published yeast-expressed hOPN cell-assay benchmarks.
