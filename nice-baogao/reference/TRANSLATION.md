# Translation and language normalisation

The largest workstream by volume in the source engagement: **every filename and every word
of content** into the target language, with **formatting preserved exactly**.

## Decide the policy before translating anything

**Which documents may stay bilingual?** Exception: **legal and commercial instruments
only** — contracts, licensing terms, agreements — where the counterparty's language has
legal force. Each such document carries a note saying **the original language prevails**.
Everything else becomes monolingual. In the source engagement this was 8 documents out of
61; the other 53 were fully converted, and 13 were once mis-counted as defects because the
filter tested a column that did not exist (`language`) instead of the real ones.

**Fix the glossary first.** Dozens of files must render the same term the same way. A
glossary written after translation produces a library that reads as if written by different
people. Include: product and molecule names, company names, regulatory terms, units, and the
confidence tags. Then audit compliance at the end — a term that drifts across 40 files is
not fixable by proofreading one.

## Preserve formatting exactly

Translate **run-by-run inside the existing document**, not by round-tripping through
markdown and rebuilding. A rebuild loses merged cells, list numbering, character styles,
inline emphasis boundaries and field codes. The source engagement's contract called this out
explicitly and the fidelity it bought was worth the extra machinery.

Then check the things that a text-only pass will miss:

* **Footnotes, endnotes, headers, footers, and text boxes are separate story parts.** A gate
  that reads only `document.xml` reports a clean document while source-language text prints
  on the page. This shipped once: **793 CJK characters across five documents' footnotes.**
* **Document metadata** — core properties, titles, author fields — carries language too.
* **Filenames and folder names** are user-visible. Rename them, and keep the old paths in the
  move manifest so the change is traceable.
* **Field results and cached values** can hold original-language text even when the field
  code has been translated.

## Residue: the marks that make a document read as machine-written

A conversion or translation pass leaves traces. Sweep for all of them, in every story part:

| residue | why it matters |
|---|---|
| `**bold**`, `## heading`, `--- rule`, `*em*` | markdown that survived a round-trip; readers see the syntax characters |
| non-breaking, zero-width and thin spaces | invisible, but change line breaking and make text unsearchable |
| doubled spaces, space before punctuation | conversion artefacts |
| letter-spacing / tracking left set | a styling pass that set `w:spacing` on runs makes body text look cramped and inconsistent with the standard |
| straight vs curly quotation marks | mixed usage across files is the clearest tell |
| leftover template text, placeholder markers, `TODO` | |
| **bilingual leftovers** — one paragraph left in the source language inside an otherwise translated document | the most visible defect of all |

**Set letter spacing to zero everywhere** if the standard says standard tracking; a run-level
`w:spacing` element is easy to introduce and hard to notice, and it must be removed from
every run, not just the first.

## Verification

Two checks, both required:

1. **Structural** — parse every story part and assert no source-language characters remain
   outside the exempt set; assert no residue patterns; assert filename normalisation.
2. **Render and look at it.** Word → PDF → PNG, then **actually view the pages** and confirm
   the cover renders, text is not overflowing its box, tables are intact, figures are present
   and in the target language. Every layout defect found in the source engagement was caught
   by eye and by nothing else.

   *Caveat that matters:* the render check verifies layout, not glyph metrics. Rasterisers
   disagree by up to 19% on variable fonts, so any claim about **measured text width or size**
   must be made from rasterised pixels, not from a font metric.

## Report format

Per bucket, with these sections — the last two are the ones that produce value:

```
### Documents processed
### Figures
### Blocked / needs a human
### Facts that look wrong or unsourced      <- goes straight into the provenance ledger
### Defects found in the documents while working
```

**"Blocked / needs a human" is a required section.** An agent that cannot resolve a term or
a legal phrasing should stop and say so rather than inventing a rendering that later
propagates into 40 files.
