---
name: bio-research
description: >-
  Generate evidence-backed English-language research reports for life sciences,
  biotechnology, protein engineering, strain development, fermentation, cell
  assays, bio-product patent/FTO analysis, and biological regulatory pathways
  (GRAS, novel food, IND). Use when the user requests a structured biotech or
  life-sciences research report, competitive landscape, or technical survey
  (supports quick, standard, and deep modes). Do not use for general non-bio
  research (use deep-research), pure PubMed/literature lookups (use
  pubmed-database / literature-search), or recurring synbio weekly briefings
  (use synbio-weekly).
---

# Life Sciences Research Skill

Generate evidence-backed, English-language research reports for biotechnology and
life-sciences topics. The skill is domain-adaptive: it selects research threads
from `references/thread-library.md` rather than forcing every question into a
fixed template.

## Core principles

- **English by default.** Report bodies, tables, figure captions, and references
  are written in English. User-facing status updates may match the user's language.
- **Evidence first.** Every key claim cites a source (`[N]`). No uncited claim
  leaves the assembly phase.
- **Collision-free source persistence.** Each Phase A thread writes its own
  `datas/sources_T{NN}.jsonl`; all thread sources are merged, deduplicated, and
  assigned final IDs `1..N` in `datas/sources.jsonl` **before** Phase B writing.
- **Domain-adaptive threads.** Threads are chosen per project from
  `references/thread-library.md`.
- **No truncation.** Every section must pass minimum-length and citation gates.
- **Optional visuals.** Standard/Deep modes may generate charts for comparisons,
  timelines, or mechanism schematics when supported by real data.

---

## 1. Router — decide whether to trigger this skill

Trigger if the user asks for:
- Structured research report, technical survey, or competitive landscape on a
  life-sciences or biotechnology topic.
- Patent, FTO, regulatory (GRAS/novel food/IND), or safety analysis for a
  bio-product, ingredient, or bioprocess.
- Cell-assay, strain, fermentation, or protein-engineering technical evaluation.

Route elsewhere / do **not** trigger for:
- General non-biological deep research → use `deep-research`.
- Pure bibliographic/PubMed queries without a full report → use `pubmed-database` or `literature-search`.
- Standalone cosmetic-only market/formulation surveys → prefer `cosmetic-research` if installed.
- Weekly synthetic-biology industry briefings → use `synbio-weekly`.
- Simple factual lookups answerable in 1–2 searches.

---

## 2. Intent clarification

Before starting, determine:

1. **Language.** Default is English unless the user explicitly requests another.
2. **Depth mode.** Choose based on user signal and decision stakes:

| Mode | User signal | Duration | Threads | Output |
|------|-------------|----------|---------|--------|
| **quick** | "quick look", "one-pager", "briefing", orientation | 2–5 min | 3–4 focused threads | 1–2 page markdown |
| **standard** | Default for most research requests | 10–20 min | 5–8 threads | Full report, DOCX |
| **deep** | "comprehensive", "deep dive", investment/regulatory | 20–40 min | 8–12 threads + conflict resolution | Full report, DOCX, optional charts |

If unclear, present the three options and ask. In auto mode, default to **standard**.

3. **Sub-mode (optional).** Load if the topic clearly needs domain supplements:
   - Cosmetics R&D: `references/submodes/cosmetic.md`
   - Synthetic biology: `references/submodes/synbio.md`

---

## 3. Project directory & script paths

Each research project lives in its own `{project_name}/` workspace directory.
All helper scripts live in `<skill_dir>/scripts/` (run from `{project_name}/` as
`python <skill_dir>/scripts/<script>.py ...`).

```
{project_name}/
├── report.md                  # current report draft
├── progress.md                # phase, completed steps, pending items, blockers
├── cmts.md                    # user comments history
├── preferences.md             # distilled user preferences
├── datas/
│   ├── sources_T{NN}.jsonl    # per-thread raw source logs (Phase A)
│   ├── sources.jsonl          # merged canonical source registry (created end of Phase A)
│   ├── evidence.jsonl         # atomic evidence snippets
│   └── *.md / *.json          # raw extracts from databases
├── drafts/
│   ├── scoping.md             # selected threads & rationale
│   ├── T{NN}_{topic}.md       # per-thread findings
│   ├── conflicts.md           # conflict resolution log
│   └── outline.md             # section outline
├── eval/
│   └── quality_evaluation.md  # rubric-based score
└── output/
    ├── {project}_report.docx  # final DOCX
    └── charts/                # charts (PNG/SVG, if any)
```

---

## 4. Workflow

The workflow strictly separates **Phase A (research)** from **Phase B (writing)**.
Update `progress.md` at every step marked **(↻ progress)** with: current phase
and step, completed steps, pending user confirmations, and known blockers.

### Phase A — Research

1. **Scoping (Step 0).** Read `references/thread-library.md`, select threads for
   the topic and mode, and save `drafts/scoping.md`. Confirm scope in manual
   mode; proceed in auto mode. **(↻ progress)**
2. **Thread research (Step 1).** Launch one parallel subagent per thread using
   your runtime's subagent/parallel-agent tool. Each thread writes findings to
   `drafts/T{NN}_{topic}.md` using thread-scoped citations `[T{NN}-1]`, `[T{NN}-2]`
   and writes its sources exclusively to `datas/sources_T{NN}.jsonl` (never
   concurrently to `datas/sources.jsonl`). **(↻ progress)**
3. **Conflict resolution (Step 2).** Read all `drafts/T*.md`, identify factual
   contradictions, and run focused verification subagents (writing any new
   sources to `datas/sources_conflicts.jsonl`). Log outcomes in
   `drafts/conflicts.md` and mark unresolved conflicts `⚠️ UNRESOLVED`. **(↻ progress)**
4. **Source merge & ID freeze (Step 2.5).** Before any report prose is written,
   merge and deduplicate all `datas/sources_*.jsonl` into canonical
   `datas/sources.jsonl` and rewrite thread draft citations to final `[N]` IDs:
   ```bash
   python <skill_dir>/scripts/merge_sources.py datas/ --output datas/sources.jsonl --rewrite-drafts drafts/
   ```
   Summarize 3–5 key findings and unresolved conflicts; **wait for user approval
   before Phase B** (manual mode only). **(↻ progress)**

### Phase B — Report assembly

5. **Outline (Step 3).** Load `references/report-template.md`, map threads to
   sections, and save `drafts/outline.md`. **(↻ progress)**
6. **Section writing (Step 4).** Write one section at a time using the frozen
   canonical IDs in `datas/sources.jsonl` and the rewritten `drafts/T*.md`. Save
   `report.md` after every section. **(↻ progress after each section)**
7. **Citation verification (Step 5).** Verify every `[N]` resolves, no duplicate
   source IDs exist, and every source has a URL or identifier:
   ```bash
   python <skill_dir>/scripts/verify_citations.py report.md datas/sources.jsonl
   ```
   **(↻ progress)**
8. **Validation gate (Step 6).** Run structural and length checks:
   ```bash
   python <skill_dir>/scripts/validate_report.py report.md --mode <quick|standard|deep>
   ```
   If it fails, return to Step 4 to fix flagged sections. **(↻ progress)**
9. **Quality evaluation (Step 7).** Apply `references/rubric.md` and save
   `eval/quality_evaluation.md`. **(↻ progress)**
10. **Fix & deliver (Step 8).** Fix rubric-identified issues, re-run affected
    checks, convert to DOCX (or use the dedicated `docx` skill for bespoke
    corporate styling):
    ```bash
    python <skill_dir>/scripts/md_to_docx.py report.md output/{project}_report.docx
    ```
    Deliver `report.md` and `output/{project}_report.docx`. **(↻ progress)**

### Interruptions, rollbacks, and comments

- On user interruption, stop immediately and record the current step and resume
  hints in `progress.md`.
- On rollback, restore the relevant `drafts/` version and log why in `progress.md`.
- In modification mode, append user comments to `cmts.md` and update `progress.md`
  when scope, core claims, or blockers change.

---

## 5. Hard rules

- **No report writing in Phase A; no new research in Phase B.**
- **Freeze `datas/sources.jsonl` before writing `report.md`** (never re-ID sources
  after writing prose).
- **Every key claim has a citation** (`[N]`) and **every source has a link**
  (PMID, DOI, patent number, or stable URL).
- **No empty leaf sections.** If no data exists, state "No publicly available
  information was found for this dimension."
- **No truncation.** Sections must meet the length gates in `references/format-rules.md`.
- **Clean markdown.** Use `#`/`##`/`###` for headings and `-` for bullets (no `*` bullets).

---

## 6. Reference files (load on demand)

| File | When |
|------|------|
| `references/methodology.md` | Before Phase A |
| `references/thread-library.md` | During scoping |
| `references/report-template.md` | Before Phase B |
| `references/format-rules.md` | During writing |
| `references/source-persistence.md` | When creating thread prompts & citations |
| `references/image-handling.md` | When generating charts |
| `references/databases.md` | When choosing search targets |
| `references/rubric.md` | During quality evaluation |
| `references/submodes/cosmetic.md` | Cosmetics topic |
| `references/submodes/synbio.md` | Synthetic-biology topic |

---

## 7. Stop conditions

Stop and report instead of forcing a pass if:
- External search tools are unavailable after three retries.
- `validate_report.py` fails three consecutive times due to an unresolvable cause
  (e.g., zero accessible sources).
- The user interrupts or changes scope mid-run.
