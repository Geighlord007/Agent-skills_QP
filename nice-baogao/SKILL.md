---
name: nice-baogao
description: Harden a large document set (DOCX/PPTX + figures) into a consistent, presentable, legible state without touching a word or a number. Unifies layout and formatting to one written standard, applies a design system, adds missing figures, redraws ugly or illegible ones to a house style, and proves the result with measurements rather than assertions. Scoped to the presentation layer by default - the words and numbers stay the author's, and suspect data is reported separately rather than edited. Use for "整理文档规范", "统一文档风格", "文档排版美化", "图表看不清/字太小", "图太丑重画", "没图的地方补图", "figure legibility", "document set audit", "brand consistency across many docx", or any task where dozens of documents must be made consistent and presentable.
whenToUse: "用户要对一整套文档（几十份到几百份 DOCX/PPTX）做强整理时触发：全树翻译并保持格式、按统一设计系统重排、重画示意图、逐条核实事实并标注来源与置信度、测量并修复图中文字过小、最后做可验证的收尾。也适用于「文档很乱需要整理」「图表字太小」「风格不统一」「数字看着不对/没有出处」「要能回滚的重组」。核心特征：量大、要可回滚、结论必须可验证。"
---

# Hardening a document set

A repeatable method for taking a large, inconsistent document set to one standard —
**reversibly**, with every claim backed by a measurement rather than an assertion.

Built from a real engagement: 2,459 files / 3.68 GB, 73 delivered DOCX, 275 displayed
figures, **129 redraw scripts**, and **257 verified claims of which 48 were corrections to
the client's own documents**. Every rule here was paid for.

## Scope: the presentation layer, by default

**This method makes a document set consistent and presentable. It does not make it
factually correct, and it must not try to.**

The default scope is exactly: unify the layout, unify the formatting, beautify, **add a
figure where one is missing**, and **redraw a figure that is ugly or illegible into a better
one**. The words and the numbers are the author's, and they stay the author's.

**Never change a number, a figure's data, or a claim — not even a wrong one.** This is not
bureaucratic caution; it is the rule that keeps the deliverable trustworthy. Three reasons,
in order of how badly they bite:

1. **You will introduce a second unverified claim.** In the source engagement the audit
   "corrected" a company's revenue to ~CHF 3.6bn. Checked against the company's own
   published results, the real figure was **CHF 3.0bn** — the correction was itself wrong by
   20 %. A correction layer that is not itself verified is strictly worse than the original
   number, because it carries the authority of having been checked.
2. **You sever the link to the author's source.** The author may have had a basis you cannot
   see. Once you overwrite the value, the reader can neither see what was written nor learn
   what you relied on.
3. **Ownership becomes ambiguous.** The numbers are the author's responsibility. Change one
   and, when it later proves wrong, nobody can say who wrote it.

If you believe a number is wrong, **report it — separately, in writing, to the person who
commissioned the work.** Do not touch the document. That is what makes the finding useful
instead of damaging.

## If someone asks for fact-checking, it is not this skill

Fact-checking is a different job with a different deliverable, and **it is not part of
hardening a document set.** Do not do it under this skill, and do not let it creep in.

Why the boundary is absolute rather than a matter of taste:

* **A correction you apply is a second unverified claim.** In the source engagement this
  skill's own audit "corrected" a company's revenue to ~CHF 3.6bn; against the company's
  published results the real figure was **CHF 3.0bn** — the correction was itself wrong by
  20 %, while carrying the authority of having been checked. That is worse than the original
  number.
* **It severs the link to the author's source**, and it makes ownership of the number
  ambiguous.

If a client does want it, say plainly that it is a separate engagement, and keep it
completely out of the documents: findings go in a file beside them, never inside them, and
nothing is applied without the author's decision. The spec used for that work was kept out
of this skill for exactly this reason — see the note at the end of this file.

## Choose a figure style first

All figures come from a **style** in `styles/`. A style is a complete visual contract —
palette, typography, geometry, chart conventions, per-category rules — and styles are
swappable: the workflow below does not change, only the look.

**Ask once, at the start:**

```
Which figure style?
  a) synbio-editorial   the house style: engraved technical, restrained, one accent
                        hue assigned by meaning. Has a full catalogue (~100 figures),
                        a working toolkit and a proven corpus behind it.
  b) a new style        describe it; author it from styles/_template/
```

Record the answer in the set's `_admin/`. **If the user has no preference, use
`synbio-editorial`.** If they describe something else, **author a new style rather than
approximating inside an existing one** — an approximation produces a third,
undocumented look nobody can reproduce.

Each style folder holds `STYLE.md` (the spec), `CATALOG.md` (the figure taxonomy, with
precedents to copy from), `chart_kit.py` (matplotlib) and `diagram_kit.py` (drawn
figures). See `styles/README.md`.

**Two parts of a style are never optional**, in any style: a **type-size floor and
target measured in printed points**, and the **scale law** that governs them (Phase 7).
Legibility is not an aesthetic preference.

## Weight the work correctly

The visible work is beautification. Effort still drifts to whatever is easiest to
demonstrate, so rank deliberately:

| rank | workstream | scale in the source engagement |
|---|---|---|
| 1 | **layout, formatting and the design system** — one standard applied to every file | one contract, every file |
| 2 | **translation + language normalisation** (when the set must change language) | the largest single workstream |
| 3 | **figures** — add the missing, redraw the ugly, make every label legible | 129 redraw scripts, 275 figures |
| 4 | **classification, archiving and reversibility** | 2,459 files |
| 5 | **navigation** — prospectus, index, portal, maps | one pass |
| — | *(optional, only if asked)* content verification | separate deliverable, §above |

**Formatting is the cheap part — and effort drifts to it for three predictable reasons:**
it is finite and visible, so it produces a screenshot and a sense of completion; deep content
work is open-ended, invisible, and mostly delivers bad news; and nobody notices on the day
that you skipped the hard part, whereas a bad font is obvious immediately.

Expect this drift in yourself and in every agent you brief. State the ranking rather than
assuming it, and give every phase a **named artefact**, because an intention without an
artefact is an intention that gets skipped.

## The one idea that makes this tractable

**The only trustworthy instrument is the artefact the reader receives.** Canvas units,
source scripts, filenames, folder names, your own memory of a brief — all are proxies, and
every proxy in this method's history has lied at least once. So: figures are measured from
the **rendered page**, brand tokens from the **shipped stylesheet**, counts from the
**delivered bytes**, and facts from a **named source with a retrieval date**.

## Phase 0 — Make it reversible before you touch anything

1. `git init` if needed, commit, tag (`pre-reorg-baseline`).
2. **Record what the tag does NOT cover.** In the source engagement it held 690 of 2,459
   entries — many documents had never been committed. A tag is not a backup.
3. Deletion is never destructive: move to `99_Archive/` with a **reason code** and a
   `superseded_by` pointer. `ARCHIVE_MANIFEST.csv` = `archived_path,reason,superseded_by,original_location`.
4. Log every move to `MOVE_MANIFEST.csv` (src → dst per action) so any single move can be
   reverted individually.
5. **Backups live in one tooling directory that verification skips** — never in the live
   tree. 119 backups at the repository root once made a count check report 98 documents and
   25 phantom "new" ones instead of 73 and 0.
6. Write **`REBUILD_LOG.md`** as you go: the problem, what was done, corrections found by
   re-verification, what was **deliberately not done**, defects found in shared engines,
   premises that turned out wrong, **known open gaps (verified, not fixed)**, and **how to
   undo everything**. This document is how a successor trusts the set.

## Phase 1 — Extract the design system, do not invent it

Read tokens off **shipped artefacts**: the site's compiled CSS for colour and font stacks;
a delivered file's `word/styles.xml` for what is truly in use. Put them in one module as
the single source of truth and derive the chart theme from it, so documents and figures
cannot drift.

Write **`DESIGN_SYSTEM.md`** covering: design intent; core colour tokens and accents;
typography including **the signature move** (state it exactly, and say "copy this exactly" —
a repeatable signature carries more identity than a whole palette); the type scale; layout;
diagrams and charts; any **sub-theme** (the source engagement needed a distinct financial
treatment, J.P. Morgan-styled, for all financial figures); the **confidence and provenance
notation**; document furniture; naming and language conventions.

A brand built on a single font weight (400, no bold) forces you to express emphasis another
way — size, space, one accent, italic. **Write the emphasis ladder into the standard**, or
every document will invent its own.

## Phase 2 — Write the contract, then enforce it

Write `DOCUMENT_STANDARD.md` with **a number for every decision**: per-level type size,
line-height and space-after on one grid unit; alignment; indent (usually none); letter
spacing; the emphasis ladder; page furniture; table rules (fixed layout, horizontal
hairlines only, no row-level border overrides — they defeat cell borders); figure width cap
and type floor; caption and source format; and the **hygiene list** for conversion residue.

Enforce in code. Two properties matter more than they look: it must be **idempotent** (a
second run must not add a second cover or revision block) and must leave furniture it did
not create **byte-identical**. Key any skip-set on **XPath**, never on `id(element)` —
lxml hands out fresh proxies and the set will match nothing.

## Phase 3 — Translate and normalise content, preserving formatting

See `reference/TRANSLATION.md`. The shape: every filename and every word of content to the
target language, **formatting preserved exactly**; a **glossary** fixed up front so renderings
are consistent across dozens of files; **bilingual exceptions only where legally required**
(legal and commercial documents, with a "the original language prevails" note); and a sweep
for residual characters that make a document read as machine-written — CJK left in
footnotes, headers, footers, text boxes and document metadata, plus conversion residue
(`**`, `##`, `---`) and invisible spacing characters.

**Footnotes, endnotes, headers, footers and text boxes are separate story parts.** A
language gate that scans only `document.xml` will miss text that prints on the page. This
has shipped before: 793 CJK characters in five documents' footnotes.

## Phase 4 — Classify and consolidate

Derive the taxonomy from **content**, not from old folder names. Every document lands in
exactly one bucket. Move with a manifest; archive duplicates with a reason code; never
delete.

## Phase 5 — Redraw schematics to a house style

See `reference/SCHEMATICS.md`. The source engagement redrew **129 figures** from a shared
Canvas toolkit — never hand-written SVG — with a stated house style and an explicit
preserve/drop list. Note the failure mode that wastes a day if nobody warns you, and require
each agent to report **defects it found in the documents while working**: that reporting
convention is how the ten-fold revenue error surfaced.

## Phase 6 — Not used

Skipped deliberately. See the scope section above: suspect data is **reported, never
edited**, and fact-checking is a separate engagement that does not live in this skill.

Every workstream report should still carry a *"Facts that look wrong or unsourced"* section.
It costs an agent nothing to note something it noticed while reading, and it hands the owner
a list to act on themselves. **Report; do not edit.**

Every substantive claim gets a row in an **append-only** ledger:
`figure_id, claim, value, unit, document, source, source_url, confidence, retrieved, note`
with confidence restricted to **`VERIFIED` / `ESTIMATED` / `UNVERIFIED`** — and a fourth
tag, `INTERPRETATION`, removed because it let an opinion hide among measurements.

* The ledger is **append-only and concurrently owned**: every generator must **MERGE, never
  rewrite**. Two workstreams overwriting each other's rows will silently lose corrections.
* **Mark retrieval dates.** A figure without a date is not verifiable next quarter.
* **Correct the document, and record the correction.** In the source engagement this found a
  revenue figure wrong by ~10× and a company whose financials were printed throughout in the
  wrong currency. Where a number cannot be trusted, **do not build a chart on it** — say so.
* **Record disagreements rather than resolving them silently.** Two sources giving 7% and 8%
  for the same royalty is a finding; pick one and it becomes an invisible error.
* Watch for documents that **contradict themselves** — two risk registers, two due-diligence
  checklists, a model whose own tables disagree by 45%. Report these; do not average them.

## Phase 7 — The scale law, then measure figures from the page

```
on-page pt = authored_pt × display_width_pt ÷ canvas_width_pt
```

See `reference/SCALE_LAW.md`. Set a floor (6.0 pt is defensible) and **target floor × 1.08**
(6.5 pt) because the instrument's spread is ±0.06 pt — **a floor met by 0.05 pt is not met**.

Measure with `tools/measure_page.py` (+ `render.py`, `locate.py`, `ink.py`): Word → PDF,
locate each figure's rect, crop, classify ink, invert the smallest text line. Three things
decide whether it is worth anything: **never render the page above the embedded raster's
resolution** (up-sampling costs 38 %), **cross-check against arithmetic**, and **read the
band at 1:1 before believing a dramatic number**.

## Phase 8 — Fix figures by lever order

1. **Widen the display extent** — every label grows proportionally; no re-render, no
   clipping, no text change, no collision risk. Check the paragraph's **real** column first:
   a `<w:ind>` indent can leave far less than the nominal width.
2. **Set the canvas to an explicit union box** containing all ink, grown until a margin-box
   render finds nothing outside. Never `bbox_inches="tight"` (shrink the canvas → shrink
   every label), never blindly `None` on an overhanging figure (clips real ink).
3. **Raise the authored type**, pinned against collisions **and against re-wrapping**.
4. **Re-layout inside the figure.** In scope: it changes no document text.

## Phase 9 — Verify, and verify the verifiers

Capture the baseline **before** the fixes so "unchanged" is a comparison, then require:

| check | requirement |
|---|---|
| document gates | every gate in your standard passes |
| **Word opens every document** | 0 failures — as the **sole** Word driver |
| **counts unchanged** | words / tables / images / paragraphs identical to baseline |
| structure | every file parses; every drawing tag balanced |
| language | no residual source-language text in any story part |
| ledger | every claim names a source and carries a valid confidence tag |
| cleanliness | no backup or scratch files in the live tree |

`reference/DEFECTS.md` records **nine occasions** where an instrument reported clean or
damning while the artefact was fine or the input was stale. Read it before trusting any
"clean" — including your own.

## Working with subagents at this scale

Parallelism is what makes this tractable, and it introduces two specific failures:

* **One owner per document.** Two agents wrote the same `.docx`; it survived only because
  the edits touched disjoint media parts. Word COM must be serialised, **and so must
  document writes.**
* **Give each agent a reliable target list, not a plausible one.** An agent working from a
  list whose numbers are wrong does careful, verified, **wrong** work. Confirm the list's
  internal consistency first: one list disagreed with itself in **83 of 281 rows**.

Brief every agent with the hard constraints (no text change, no count change, use the
sanctioned tools, back up, do not commit), the method, and the requirement to **report what
it could not fix and why**. Say out loud: *"measure and report, do not fake a fix"* — and
add *"report defects you find in the documents while working"*, because that is how the
content corrections in Phase 6 actually get found.

## Adapting to a new set

1. Copy `tools/` beside the set; point `DOCSET_ROOT` at it (`tools/_paths.py`).
2. Phase 1: extract tokens from **your** artefacts; rewrite `brand.py` constants.
3. Phase 2: write **your** standard, with numbers.
4. Phase 3: fix **your** glossary before translating anything.
5. Phases 5–9 run as-is, but **re-run the dpi stability sweep** — the embedded raster
   resolution depends on whatever produced the figures.

## Reference

`reference/TRANSLATION.md` · `reference/SCHEMATICS.md` · `reference/SCALE_LAW.md` ·
`reference/DEFECTS.md` · `reference/RULEBOOK.md` · `reference/PATTERNS.md`

**Deliberately NOT in this skill: the provenance-ledger specification.** It was written
during the source engagement and then removed, for one reason — **a skill's contents are its
instructions.** Leaving a spec for fact-checking inside the skill would make the next run
perform fact-checking, which is now out of scope. It lives with the document set it belongs
to (`_admin/PROVENANCE_LEDGER_SPEC.md`) rather than in the reusable toolkit.

**Also set per document set, not in the toolkit:** `BRAND_NAME` and `DOCSET_TITLE` in
`tools/_paths.py`. These were once hard-coded inside the cover builder, which meant the
tool would stamp one client's name onto another client's documents.
