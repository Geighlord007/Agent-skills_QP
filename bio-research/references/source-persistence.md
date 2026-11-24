# Source Persistence

All final sources are stored in `datas/sources.jsonl` as newline-delimited JSON.
During Phase A, each parallel thread writes to its own `datas/sources_T{NN}.jsonl`
to prevent concurrent write collisions; at Step 2.5 (before Phase B writing),
`merge_sources.py` merges, deduplicates, and freezes final sequential IDs `1..N`.

## Schema

Each line is a JSON object with these fields:

```json
{
  "id": 1,
  "type": "paper",
  "title": "Human and bovine milk osteopontin influence the transcriptome of Caco-2 cells",
  "authors": "West et al.",
  "year": 2023,
  "venue": "Journal of Nutrition",
  "identifier": "PMID: 36904165",
  "url": "https://pubmed.ncbi.nlm.nih.gov/36904165/",
  "accessed": "2026-06-26",
  "confidence": "high",
  "notes": "Independent peer-reviewed study; supports Caco-2 transcriptome comparison claim"
}
```

### Field definitions

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Thread-scoped string (`"T01-1"`) during Phase A; unique integer (`1..N`) in merged `datas/sources.jsonl` matching in-text `[N]` |
| `type` | yes | `paper`, `patent`, `official`, `news`, `preprint`, `database`, `company` |
| `title` | yes | Short descriptive title |
| `authors` | no | Authors, assignee, or issuing agency |
| `year` | no | Publication, filing, or issue year |
| `venue` | no | Journal, patent office, or database |
| `identifier` | no | PMID, DOI, patent number, GRN number, etc. |
| `url` | yes* | Stable URL. Required unless the source is offline-only. |
| `accessed` | yes | Date fetched, ISO-8601 |
| `confidence` | yes | `high`, `medium`, `low` |
| `notes` | no | Context for how the source was used |

*If `url` is truly unavailable, set it to `""` and explain in `notes`.

## Thread agent responsibilities (Phase A)

When thread `T{NN}` finds a source, it must:

1. Append a complete source record to `datas/sources_T{NN}.jsonl` immediately
   (do NOT write directly to shared `datas/sources.jsonl`).
2. Assign a thread-scoped ID (`"T{NN}-1"`, `"T{NN}-2"`, ...).
3. Annotate findings in `drafts/T{NN}_{topic}.md` with `[T{NN}-1]`, `[T{NN}-2]`.
4. Prefer high-confidence sources; mark company/press sources appropriately.

## Merge and ID freeze (Step 2.5 — BEFORE Phase B writing)

Run from the `{project_name}/` workspace directory:

```bash
python <skill_dir>/scripts/merge_sources.py datas/ --output datas/sources.jsonl --rewrite-drafts drafts/
```

This script:
- Reads all `datas/sources_*.jsonl` files (or a single `datas/sources.jsonl` if
  passed a single file path).
- Deduplicates by normalized `identifier` (PMID/DOI/patent), `url`, or `title`.
- Assigns final sequential integer IDs `1..N`.
- Writes `datas/sources.jsonl` (backing up any existing `datas/sources.jsonl` to
  `datas/sources.jsonl.bak`) and saves the old-to-new mapping to
  `datas/source_id_map.json`.
- When `--rewrite-drafts drafts/` is passed, rewrites all `[T{NN}-k]` / `[C-k]`
  markers in `drafts/*.md` to final `[N]` IDs so Phase B writers use exact IDs.

## Citation verification (Step 5)

```bash
python <skill_dir>/scripts/verify_citations.py report.md datas/sources.jsonl
```

It checks:
- No duplicate source `id` entries exist in `datas/sources.jsonl`.
- Every `[N]` in `report.md` resolves to a source ID.
- Every source ID is cited at least once.
- Every source has a non-empty `url` or `identifier`.

## Handling missing sources

If a key claim lacks a source:

1. Search again for a supporting source (during Phase A or before finalizing).
2. If none is found, downgrade the claim to a hypothesis and mark `⚠️ unverified`.
3. Do not delete the claim unless it is no longer relevant.
