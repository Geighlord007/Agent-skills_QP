# Quality Rubric

Score the report on 7 dimensions, 5 points each, for a maximum of 35. Red-line violations cap the total at 17.

## Red lines (any one caps score at 17)

1. Fabricated PMID, DOI, patent number, or database result.
2. Key claim supported only by a company/brand press release with no independent verification.
3. Internal contradiction left unresolved and unflagged.
4. Section heading with no substantive content.
5. Report body fails `scripts/validate_report.py` after three fix attempts.

## D1 — Source traceability (5)

- Every key claim has a citation `[N]`.
- Citations resolve to entries in `datas/sources.jsonl`.
- Sources have a reachable URL/PMID/patent number.
- Official/regulatory claims are backed by official sources, not media summaries.

## D2 — Evidence quality (5)

- Peer-reviewed data distinguished from press releases and unverified claims.
- Key numbers (NOAEL, yield, effect size, sample size) are reported with units and context.
- Contradictions are flagged and, where possible, resolved.

## D3 — Domain fit (5)

- Threads selected match the project type (protein, cell assay, strain, regulatory, etc.).
- Technical content is accurate for the sub-discipline.
- No irrelevant cosmetic-only sections are inserted unless the sub-mode is cosmetic.

## D4 — Structural completeness (5)

- All sections from the agreed outline are present and populated.
- Executive summary reflects the body.
- Recommendations and next steps are specific and actionable.

## D5 — Analytical depth (5)

- Beyond listing facts: explains why they matter and how they connect.
- Trade-offs and uncertainties are discussed.
- Bull/bear or pro/con perspectives are presented where relevant.

## D6 — Format & readability (5)

- Consistent Markdown: `#` headings, `-` bullets, no `*` bullet mixing.
- Tables are readable and have headers.
- No wall-of-text paragraphs over 300 words.
- English is clear and professional.

## D7 — Deliverable completeness (5)

- `report.md` and `output/{project}_report.docx` are produced.
- `datas/sources.jsonl` exists and is non-empty.
- `eval/quality_evaluation.md` is completed.

## Scoring scale

| Score | Meaning |
|-------|---------|
| 5 | Excellent, no significant issues |
| 4 | Good, minor issues |
| 3 | Acceptable, noticeable gaps |
| 2 | Poor, undermines credibility |
| 1 | Very poor |
| 0 | Missing |

## Output format

```
## Red-line check
- [ ] Fabricated citation
- [ ] Company-only key claim
- [ ] Unresolved internal contradiction
- [ ] Empty section
- [ ] Validation gate failed 3x
Triggered: (none / list)

## Total score
__/35

## Dimension scores
| Dimension | Score | Notes |
|-----------|-------|-------|
| D1 Source traceability | /5 | |
| D2 Evidence quality | /5 | |
| D3 Domain fit | /5 | |
| D4 Structural completeness | /5 | |
| D5 Analytical depth | /5 | |
| D6 Format & readability | /5 | |
| D7 Deliverable completeness | /5 | |

## Priority fixes
1. ...
```
