# The rulebook

Ordered by how badly each rule bites. Every one cost real work to learn.

## 1. Changing a face on a width-wrapped note silently changes drawn strings

Raising a font size caused a source note — measured and wrapped to a width — to re-wrap,
changing one drawn string per figure. Same words, different line breaks; **but a changed
string is a changed string**, and it violates "no label text may change". It was invisible
in the rendered image.

* **Pin the wrap size** whenever type grows, so the break does not follow the new face size.
* **Prove a no-text-change claim by diffing the drawn-text multiset**, not the picture:
  `fig.findobj(Text)` for matplotlib, the `<text>` element multiset for SVG. Compare old vs
  new exactly. OCR cannot do this job — it misread `Evolva`→`Evolve`, `Vivici`→`Vividi` and
  dropped a repeated label in real runs. **The multiset is the authority; OCR corroborates.**
* `tools/facediff.py` does exactly this and exits non-zero on a changed string.

## 2. Read the resolved state, never the source text

A grep of `fontsize=` gave 6.6 where the built figure resolves to 6.85. **A correct
multiplication by a stale factor yields a confident wrong answer.** Rebuild the figure and
query the artist. Grepping misses scale knobs, per-figure overrides, rcParams, and later
commits that changed them all.

## 3. Never render a page above the embedded raster's resolution

See `DEFECTS.md` — up-sampling costs 38 %. Sweep the dpi and confirm stability before
trusting any pixel reading.

## 4. Backups do not belong in the live tree

119 backup files at the repository root, mirroring the document structure, made a count
check report **98 documents and 25 phantom "new" ones** instead of 73 and 0. Keep backups
under the tooling directory that verification skips. Verify by *copy, once* — a polling
reader holds a large file open and **blocks an atomic `os.replace`** on Windows, which is
how a well-intentioned atomic write failed.

## 5. Serialise writes to a single document, not just to Word

Two agents wrote the same `.docx` in one window. It survived only because the edits touched
*disjoint* media parts and the read-modify-write commuted. That is luck. **Word COM is a
shared single-instance resource and must be serialised; document writes must be too.** One
owner per file.

## 6. Give workers a reliable target list, not a plausible one

An agent working from a list whose numbers are wrong will do careful, verified, **wrong**
work. Confirm the list's internal consistency before delegating: one list disagreed with
itself in **83 of 281 rows**, because the verdict thresholded a column the file did not
contain. Then state the hard constraints explicitly — no text change, no count change, use
the sanctioned swap tool, back up, do not commit — and **require the agent to report what it
could not fix and why**. "Measure and report, do not fake a fix" must be said out loud; the
temptation to make a number pass is real.

## 7. A file extension is not a format

`image2.jpeg` held PNG bytes. `replace_figure.py` re-encodes any part named `.jpeg`, so a
PNG-under-a-JPEG-name silently became a lossy JPEG (disclosed: ink-weighted mean delta
3.786/255, p99 = 3, max 145 on 0.17 % of pixels). **Read the magic bytes.**

## 8. `NO_DISK_FILE` means "no editable source outside the package", not "missing"

52 parts carried that label and **all 52 were present inside their own `.docx`**, sizes
4,801–2,054,438 B, none empty. Those — and any JPEG with no source — are **measured and
reported, never redrawn**: re-rendering substitutes a different drawing for the author's.

## 9. An extension is not a width

A paragraph carrying `<w:ind w:left="1260"/>` (63 pt) has a usable column of
`470.55 − 63 = 407.55 pt`, not 470.55. Widening a figure to the nominal column put it
**41.5 pt into the right margin**. Check the paragraph's real column first.

## 10. Idempotency, keyed on the right thing

A placement script keyed its "already done?" test on the figure number computed from what
already existed — so it could never match, and it silently inserted duplicate blocks into
two documents. **Key on stable content** (the caption body, the media part name), and verify
you inserted no duplicates.

## 11. Preserve furniture you did not create

A style pass must leave covers, revision blocks and headers **byte-identical**. Two traps: a
style applicator that is not idempotent adds a second cover; and a skip-set built from
`id(element)` matches nothing, because lxml hands out fresh proxies — **use XPath keys**.

## 12. `git add -A` needs a `.gitignore` first

It swept 111 backup files (64.6 MB) into history once, and a 5.3 MB measurement JSON later.
Ignore backups, dumps and large intermediates *before* the first broad add.

## 13. Commit messages with quotes or CJK

Use `git commit -F <file>`. Inline `-m` with escaped quotes or non-ASCII breaks.
