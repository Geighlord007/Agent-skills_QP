# Bio-Research Methodology

Generic research methodology for life-sciences topics. Domain-specific
supplements live in `references/submodes/`. Run all script commands from the
`{project_name}/` workspace directory, substituting `<skill_dir>` with the
installed path of `bio-research`.

## Mode map

| Mode | Goal | Search rounds | Threads | Report length target |
|------|------|---------------|---------|----------------------|
| quick | Orientation or pre-read | 3–5 | 3–4 | 800–1,500 words |
| standard | Decision-ready report | 8–12 | 5–8 | 3,000–6,000 words |
| deep | Comprehensive review / external-facing | 15+ | 8–12 | 6,000–12,000+ words |

## Phase A — Research

### Step 0 — Scoping

Before launching threads:

1. Parse the user's question. Extract:
   - Target molecule, organism, process, or technology.
   - Stated purpose (R&D, regulatory, investment, competitive intelligence).
   - Constraints (time, geography, expression host, regulatory pathway).
2. Do a quick web search to confirm identities and discover hidden dimensions
   (e.g., a key patent, a recent FDA GRAS notice, a safety signal).
3. Select threads from `references/thread-library.md`.
4. Save `drafts/scoping.md` with the selected threads and rationale.

### Step 1 — Thread research

Launch one parallel subagent per thread using the parallel subagent tool
available in your current runtime. Each agent writes ONLY to its own thread
files (`drafts/T{NN}_{thread_name}.md` and `datas/sources_T{NN}.jsonl`) so
parallel threads never collide on shared files or source IDs.

Thread prompt template:

```
You are a life-sciences research assistant.

Project: {project_name}
Thread ID: T{NN}
Thread: {thread_name}
Objective: {one-sentence goal for this thread}
Depth mode: {quick|standard|deep}

Tasks:
1. Search authoritative sources for the questions below.
2. Record every source in datas/sources_T{NN}.jsonl using the schema in
   references/source-persistence.md, with thread-scoped IDs "T{NN}-1", "T{NN}-2", ...
3. Write findings to drafts/T{NN}_{thread_name}.md.
4. Flag contradictions and low-confidence claims.

Questions:
- {Q1}
- {Q2}
- ...

Output requirements:
- Structured bullets/tables.
- Every fact annotated with its thread-scoped source ID [T{NN}-1], [T{NN}-2], ...
- Confidence label per claim: High / Medium / Low.
- No report prose; collect and organize data only.
```

### Step 2 — Conflict resolution

After all threads return:

1. Read every `drafts/T*.md`.
2. Identify contradictions in facts, numbers, timelines, or ownership.
3. For each contradiction, spawn a focused verification subagent with an explicit
   authoritative source order:
   - Peer-reviewed papers > official regulatory databases > patents > company press releases.
   - Any new verification sources are written to `datas/sources_conflicts.jsonl`
     with IDs `C-1`, `C-2`, ...
4. Write the resolution to `drafts/conflicts.md`.
5. Mark unresolved items with `⚠️ UNRESOLVED` and include them in the Phase A summary.

### Step 2.5 — Source merge, ID freeze, and Phase A wrap-up

Merge and deduplicate all per-thread source files into the canonical
`datas/sources.jsonl` **before** Phase B writing begins, and automatically
rewrite thread-scoped citations (`[T01-1]`, `[C-1]`, etc.) in `drafts/` to final
canonical integer IDs (`[1]`, `[2]`, ...):

```bash
python <skill_dir>/scripts/merge_sources.py datas/ --output datas/sources.jsonl --rewrite-drafts drafts/
```

Then update `progress.md` and summarize:
- Selected threads and why.
- 3–5 key findings.
- Unresolved conflicts.
- Data-sparse dimensions.
- Recommended report structure.

In manual mode, wait for user approval before Phase B. In auto mode, continue
after a brief summary.

## Phase B — Report assembly

### Step 3 — Outline

Use `references/report-template.md` as a skeleton. Adapt sections to the threads
that actually produced data. Save `drafts/outline.md`.

### Step 4 — Section writing

Rules:

1. Read only the threads mapped to the current section (`drafts/T*.md` already
   contain the final canonical `[N]` IDs from Step 2.5).
2. Read `datas/sources.jsonl` for canonical source details.
3. Write the section in English.
4. Cite every key claim with `[N]`.
5. Save `report.md` after each section.
6. Never leave a leaf heading without content.

### Step 5 — Citation verification

```bash
python <skill_dir>/scripts/verify_citations.py report.md datas/sources.jsonl
```

### Step 6 — Validation gate

```bash
python <skill_dir>/scripts/validate_report.py report.md --mode <quick|standard|deep>
```

If it fails, return to Step 4 and fix the specific flagged issues.

### Step 7 — Quality evaluation

Apply `references/rubric.md`. Save results to `eval/quality_evaluation.md`.

### Step 8 — Fix and deliver

1. Fix only rubric-identified issues.
2. Re-run `verify_citations.py` and `validate_report.py`.
3. Convert to DOCX:
   ```bash
   python <skill_dir>/scripts/md_to_docx.py report.md output/{project}_report.docx
   ```
4. Deliver both `report.md` and `output/{project}_report.docx`.
