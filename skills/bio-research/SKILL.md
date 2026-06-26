---
name: bio-research
description: Use when the user asks to research a topic in life sciences, biotechnology, synthetic biology, protein engineering, strain development, fermentation, cell assays, regulatory pathways, or adjacent areas. Supports optional sub-modes for cosmetics and synthetic-biology-specific inquiries. Triggers include "research", "调研", "文献调研", "competitive landscape", "patent analysis", "cell assay", "regulatory", "GRAS", "fermentation", "protein engineering", "strain" in a scientific or R&D context.
---

# Life Sciences Research Skill

Generate evidence-backed, English-language research reports for biotechnology and life-sciences topics. The skill is domain-adaptive: it selects research threads from a library rather than forcing every question into a fixed cosmetic-ingredient template.

## Core principles

- **English by default.** All report bodies, tables, figure captions, and references are written in English. User-facing status updates may be in Chinese if the user writes in Chinese.
- **Evidence first.** Every key claim cites a source. No claim without a citation leaves the assembly phase.
- **Source persistence.** All sources are recorded in `datas/sources.jsonl` with stable IDs; the final report references these IDs so links are not lost during assembly.
- **Domain-adaptive threads.** Threads are chosen per project from `references/thread-library.md`, not hard-coded.
- **No truncation.** Each section must pass a minimum-length gate and a citation-coverage gate before delivery.
- **Optional visuals.** Standard/Deep modes may generate base64 SVG charts for comparisons, timelines, or mechanism schematics.

---

## 1. Router — decide whether to trigger this skill

Trigger if the user asks for:
- Research, survey, literature review, or competitive analysis of a biological/biotech topic.
- Patent, regulatory, safety, or FTO analysis for a bio-product, ingredient, or process.
- Cell-assay, strain, fermentation, protein-engineering, or synthetic-biology design support.

Do **not** trigger for:
- Simple factual lookups answerable in 1-2 web searches.
- Code debugging or non-scientific tasks.

---

## 2. Intent clarification

Before starting, determine:

1. **Language.** Default is English unless the user explicitly requests another language.
2. **Depth mode.** Choose based on user signal and decision stakes.

| Mode | User signal | Duration | Threads | Output |
|------|-------------|----------|---------|--------|
| **quick** | "quick look", "one-pager", " briefing", or a simple orientation question | 2-5 min | 3-4 focused threads | 1-2 page markdown |
| **standard** | Default for most research requests | 10-20 min | 5-8 threads | Full report, DOCX |
| **deep** | "comprehensive", "deep dive", investment or regulatory decision | 20-40 min | 8-12 threads + conflict resolution | Full report, DOCX, optional charts |

If unclear, present the three options and ask the user to choose. In auto mode, default to **standard**.

3. **Sub-mode (optional).** If the topic clearly matches cosmetics or synthetic biology, load the corresponding sub-mode file:
   - Cosmetics: `references/submodes/cosmetic.md`
   - Synthetic biology: `references/submodes/synbio.md`

Sub-modes add domain-specific data sources and thread suggestions; they do not replace the generic workflow.

---

## 3. Project directory

Each research project gets its own directory. All work stays inside it.

```
{project_name}/
├── report.md                  # current report draft
├── progress.md                # phase, completed steps, blockers
├── cmts.md                    # user comments history
├── preferences.md             # distilled user preferences
├── datas/
│   ├── sources.jsonl          # stable source registry (REQUIRED)
│   ├── evidence.jsonl         # atomic evidence snippets
│   └── *.md / *.json          # raw extracts from databases
├── drafts/
│   ├── T{NN}_{topic}.md       # per-thread findings
│   └── conflicts.md           # conflict resolution log
├── eval/
│   └── quality_evaluation.md  # rubric-based score
├── output/
│   ├── {project}_report.docx  # final DOCX
│   └── charts/                # SVG charts (if any)
└── references/                # copied-in rubric/checklist for this run
```

---

## 4. Workflow

The workflow separates **research** from **writing** and gates each transition.

### Phase A — Research

1. **Scoping (Step 0).** Read `references/thread-library.md` and select threads appropriate to the topic and mode. Confirm scope with the user in manual mode; proceed in auto mode.
2. **Thread research (Step 1).** Launch one subagent per thread using `AgentSwarm`. Each thread writes to `drafts/T{NN}_{topic}.md` and appends sources to `datas/sources.jsonl`.
3. **Conflict resolution (Step 2).** Read all thread drafts, identify factual conflicts, and spawn focused verification subagents. Mark unresolved conflicts with `⚠️`.
4. **Phase A wrap-up (Step 2.5).** Update `progress.md`, summarize 3-5 key findings and unresolved conflicts, and **wait for user approval before Phase B** (manual mode only).

### Phase B — Report assembly

5. **Outline (Step 3).** Load `references/report-template.md`, map threads to sections, and produce a section outline saved to `drafts/outline.md`.
6. **Section writing (Step 4).** Write one section at a time, reading only the relevant thread files and `datas/sources.jsonl`. Save `report.md` after every section.
7. **Source merge (Step 4.5).** Run `scripts/merge_sources.py` to normalize and deduplicate `datas/sources.jsonl`.
8. **Citation verification (Step 5).** Run `scripts/verify_citations.py` to ensure every `[N]` in `report.md` resolves to a source and every source has a URL/PMID/patent number.
9. **Validation gate (Step 6).** Run `scripts/validate_report.py`. If it fails, return to Step 4.
10. **Quality evaluation (Step 7).** Apply `references/rubric.md` and save `eval/quality_evaluation.md`.
11. **Fix & deliver (Step 8).** Fix only rubric-identified issues, re-run affected checks, convert to DOCX with `scripts/md_to_docx.py`, and deliver.

---

## 5. Hard rules

- **No writing in Phase A; no new research in Phase B.**
- **Every key claim has a citation** in the report body (`[N]` format).
- **Every source has a link** (PMID, DOI, patent number, or stable URL).
- **No empty sections.** If no data exists, write "No publicly available information was found for this dimension."
- **No truncation.** Each section must meet the minimum length gate from `references/format-rules.md`.
- **No markdown format drift.** Use only `#`/`##`/`###` for headings and `-` for bullets; do not mix `*` for bullets.
- **Charts are optional.** Generate them only when real data supports them and the mode is standard/deep.

---

## 6. Reference files

Read these on demand:

| File | When |
|------|------|
| `references/methodology.md` | Before Phase A |
| `references/thread-library.md` | During scoping |
| `references/report-template.md` | Before Phase B |
| `references/format-rules.md` | During writing |
| `references/source-persistence.md` | When creating thread prompts and citations |
| `references/image-handling.md` | When generating charts |
| `references/databases.md` | When choosing search targets |
| `references/rubric.md` | During quality evaluation |
| `references/submodes/cosmetic.md` | Cosmetics topic |
| `references/submodes/synbio.md` | Synthetic-biology topic |

---

## 7. Stop conditions

Stop and report instead of forcing a pass if:
- External search tools are unavailable after three retries.
- `validate_report.py` fails three consecutive times and the cause is unresolvable (e.g., zero accessible sources).
- The user explicitly interrupts or changes scope mid-run.
