# Format Rules

All reports produced by this skill must follow these formatting rules. The validation script enforces many of them.

## Language

- Report body, tables, captions, and references are in **English** unless the user explicitly requests another language.

## Headings

- Use `#` for title, `##` for sections, `###` for subsections, `####` for minor headings.
- Do not skip levels (e.g., `##` directly to `####`).
- Title case for section headings: "Executive Summary", "Competitive Landscape".

## Bullets and lists

- Use `-` for unordered lists.
- Do **not** use `*` for bullets anywhere in the report.
- Ordered lists use `1.`, `2.`, `3.`.
- Nested bullets use 2-space indentation.

## Emphasis

- Use `**bold**` for important terms, key numbers, and major conclusions.
- Use `*italic*` sparingly, only for genus/species names or foreign terms.
- Avoid redundant bolding of the same term within a short span.

## Citations

- In-text citations use `[N]` where N is the source ID from `datas/sources.jsonl`.
- Place citations immediately after the claim they support.
- Max two citations per sentence.
- Do not cite creative or obvious statements.

## Tables

- Every table has a header row.
- Every table has at least one row of data.
- Source citations may appear inside table cells as `[N]`.
- Keep table cells concise; move long explanations to prose.

## Section length gates

Minimum word counts per section (validation-enforced):

| Mode | Executive Summary | Major sections (##) | Subsections (###) |
|------|-------------------|---------------------|-------------------|
| quick | 80 | 150 | 80 |
| standard | 150 | 400 | 150 |
| deep | 250 | 600 | 250 |

A "major section" is any `##` heading. A "subsection" is any `###` heading.

## Charts

- Use base64 SVG embedded via standard HTML `<img>` only when data supports it.
- Every chart has an exhibit label and a source line.
- Charts must be referenced in the surrounding prose.

## References section

- Numbered list matching in-text `[N]` IDs.
- Each entry: ID. Type. Title/Description. URL/PMID/Patent. Accessed YYYY-MM-DD.
- No orphaned in-text citations; no unused source IDs.
