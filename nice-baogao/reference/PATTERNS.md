# Patterns

## Extracting a design system instead of inventing one

Read tokens off the **shipped artefacts**; a brand PDF is aspirational, the compiled CSS is
what readers actually see.

| token | where to read it |
|---|---|
| colours | the site's compiled CSS — grep custom-property declarations and hex literals |
| typefaces | the CSS `font-family` declarations, then confirm the files are actually bundled |
| what a document really uses | a delivered file's `word/styles.xml` and `word/fontTable.xml` |
| which assets exist | the package's `[Content_Types].xml` and `word/media/` |

Then derive a chart theme from the same module, so documents and figures cannot drift.

Two details that matter more than they look:

* **Weight.** A brand built on a single weight (400 only, no bold) forces you to express
  importance another way — size, space, one accent colour, italic. Decide the **emphasis
  ladder** explicitly and write it into the standard, or every document will invent its own.
* **An accent face against a neutral body face**, used sparingly, is a cheap and highly
  repeatable signature. One signature phrase style (e.g. a serif italic set ~1.24× larger
  than the surrounding sans) carries more identity than a whole palette.

## Writing the standard

Write a number for every decision. A standard with adjectives produces arguments; a standard
with numbers produces comparisons. Cover: per-level type size and line-height, spacing on
one grid unit, alignment, indent, letter-spacing, the emphasis ladder, page furniture,
table rules, figure width cap and type floor, caption and source format, and the hygiene
list (conversion residue and invisible characters).

Put the **targets**, not just the floors, in the standard — and say why the target exceeds
the floor (instrument tolerance).

## Finding documents that need figures

A document that is all text and no figure is a finding, not a defect. Triage by reading the
body: a claim that is a *process*, a *comparison*, a *timeline* or a *hierarchy* can carry a
diagram; a claim that is a single number cannot. Produce a proposal with one placement per
figure, and mark anything that needs research before it can be drawn rather than drawing a
plausible-looking invention.

## Making the set navigable

Readers need a way in that does not require opening 70 files:

* a prospectus (`README.md`) and machine index (`RESEARCH_INDEX.csv`);
* a single self-contained portal `index.html` — inline the fonts, ship no external
  references, so it works offline;
* a mind map and an architecture diagram as SVG.

**Verify the portal is complete, not just well-formed.** A gate that finds `href`s and
reports "0 broken of 0 checked" passes a truncated file. Assert the closing tags exist, that
the anchor count is non-zero, and that the file's length is in the expected range — a
truncated portal is the failure mode, and it fails *silently*.

## Order of work

1. Reversibility (Phase 0) — before touching anything.
2. Tokens and the standard (Phases 1–2).
3. Classification and moves (Phase 3).
4. Figures: scale law, canvas contract, then measurement (Phases 4–5).
5. Fixes by lever order (Phase 6).
6. Verification against a baseline captured *before* the fixes (Phase 7).

## Pitfalls that recur across document sets

* **Style-level first-line indent** (e.g. `Normal` carrying `firstLine="480"`) pushes
  full-width figures into the margin. Clear it at the style level, not per paragraph.
* **Row-level table border overrides** defeat cell borders and draw vertical rules you
  thought you had removed.
* **Bad field anchors**: duplicated footnote/comment anchors make a document fail to open.
  A sweep that finds unopenable files should be followed by a byte-level anchor census.
* **Broken `NOTEREF` fields** print as `错误！未定义书签。`. Collapse each field to its
  cached result; do not try to repoint bookmarks.
* **Footnotes, endnotes, headers, footers and text boxes are separate story parts.** A
  language or hygiene gate that scans only `document.xml` will miss real on-page text.
* **Portal truncation** — see above.
