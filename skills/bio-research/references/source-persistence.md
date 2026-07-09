# Source Persistence

All sources must be recorded in `datas/sources.jsonl` as newline-delimited JSON. This file is the single source of truth for citations.

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
| `id` | yes | Integer, unique within the project, matching in-text `[N]` |
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

## Thread agent responsibilities

When a thread agent finds a source, it must:

1. Append a complete source record to `datas/sources.jsonl` immediately.
2. Use the next available integer ID.
3. Annotate findings with `[N]` matching that ID.
4. Prefer high-confidence sources; mark company/press sources appropriately.

## Merge and deduplication

Before citation verification, run:

```bash
python scripts/merge_sources.py datas/sources.jsonl
```

This script:
- Removes duplicate URLs/PMIDs/patent numbers.
- Reassigns IDs sequentially.
- Outputs `datas/sources.jsonl` in place and writes `datas/sources_backup.jsonl`.

## Citation verification

Run:

```bash
python scripts/verify_citations.py report.md datas/sources.jsonl
```

It checks:
- Every `[N]` in `report.md` resolves to a source ID.
- Every source ID is cited at least once.
- Every source has a non-empty `url` or `identifier`.
- No duplicate IDs exist.

## Handling missing sources

If a key claim lacks a source:

1. Search again for a supporting source.
2. If none is found, downgrade the claim to a hypothesis and mark `⚠️ unverified`.
3. Do not delete the claim unless it is no longer relevant.
