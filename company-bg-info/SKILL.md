---
name: company-bg-info
description: Use when the user asks for a background-info / BG-info / company-profile Word document on a potential partner or customer (e.g., "写一个 [公司] 的 BG info" / "company background brief"). Generates a concise, fact-packed .docx summarising company overview, strategic relevance, operating divisions, key brands, financials, technology layout, recent M&A, and a collaboration hook — with inline hyperlinks and a Sources section.
---

# Partner Company Background Info (BG Info) Skill

Generates a single `.docx` fact-pack on a potential partner or customer: who they are, why they matter strategically, what they sell, how they are organised, recent M&A, and a one-paragraph collaboration hook — with inline hyperlinks and a bulleted Sources section.

## 1. Output structure (follow this order)

1. **Document title** — `[Company] BG info` (plus optional top-right company logo)
2. **Main heading** — `[Company]`
3. **Company overview** — 1–2 paragraphs: HQ, revenue, market position, listing status, division structure.
4. **Strategic context** — 1 short paragraph on relevance to the user's platform/technology; insert a key investor slide or chart if available.
5. **Operating divisions** — 4-column table: Division, Description, Key brands / products, Revenue / EBITDA.
6. **Selected ingredient / product brands** — Grouped by category with short factual descriptions.
7. **Key financials** — Multi-year table (Metric + last 2 fiscal years / guidance).
8. **Alternative proteins / precision fermentation / relevant technology layout** — Public statements, internal initiatives, partnerships/JVs, investments, M&A. If none, state: *"No public internal platform announced; strategic interest signalled by X."*
9. **Recent M&A / transactions** — 4-column table: Year, Target / asset, Transaction amount, Description.
10. **Innovation & partnership landscape** — Open innovation / R&D facilities, relevant product lines, stance on precision fermentation / synbio, and a **one-paragraph proposed collaboration hook**.
11. **Sources** — Bulleted list of all URLs used, rendered as blue underlined hyperlinks.

## 2. Workflow

1. **Confirm target & existing files** — Check any user-supplied reports, URLs, or existing files under `output/sources/`.
2. **Collect public facts** — Follow `references/data-collection-checklist.md` (annual report/CMD deck, financials, divisions, M&A, VC/CVC, alt-protein/PF signals, leadership quotes, product pages, logo).
3. **Extract key investor slide (optional)** — Render a PDF page to PNG:
   ```bash
   python scripts/extract_pdf_page.py --input output/sources/investor-deck.pdf --page 3 --output output/tmp/key-slide.png --dpi 200
   ```
4. **Prepare JSON** — Populate `output/tmp/data.json` following `references/schema.json`. Use Markdown-style `[anchor text](https://...)` inside any narrative field to emit blue inline hyperlinks; repeat all referenced URLs in `sources`.
5. **Validate & generate DOCX**:
   ```bash
   python scripts/validate_bg_json.py --input output/tmp/data.json
   python scripts/generate_bg_doc.py --input output/tmp/data.json --output output/Company_BG_info.docx
   ```
   (`generate_bg_doc.py` also runs schema validation automatically before rendering and fails fast if a referenced image/logo file is missing.)
6. **Verify deliverable** — Confirm the `.docx` opens cleanly, hyperlinks work, and all tables/images render properly.

## 3. Visual & content conventions

- Full visual typography, colour palette (`#333333`, `#617D24`, `#0563C1`, `#E5E5E5`), spacing, and table rules are defined in `references/format-spec.md`.
- **Font note**: Documents specify `Schibsted Grotesk`. On Windows/macOS machines where it is not installed, Word automatically falls back to the system sans-serif (e.g., Calibri/Aptos); install the Google Font locally if exact metric fidelity is required.
- **Keep analysis minimal**: BG Info is a concise fact pack, not a long strategic essay. Distill lengthy source reports into the 11-section structure above.
- **Language**: Respond to the user in their prompt language; default the generated `.docx` to English unless requested otherwise.
- **Custom template override**: If the user supplies an existing `.docx` and asks to match its exact layout, use the `docx` skill instead of building from scratch.

## 4. Quality checklist

- [ ] Document opens without corruption; `Heading 1` / `Heading 2` outline appears in Word navigation pane
- [ ] All tables have `#E5E5E5` shaded headers and 9 pt text; headings are 10 pt bold `#617D24`
- [ ] Inline hyperlinks and bulleted `Sources` links are clickable
- [ ] Relevant investor slide / logo embedded when available (no broken image placeholders)
- [ ] Technology layout section explicitly populated or marked *"none publicly announced"*
- [ ] Saved under `output/[Company]_BG_info.docx`

## 5. Reference files

| File | Purpose |
|------|---------|
| `references/schema.json` | JSON Schema (draft-07) for `generate_bg_doc.py` input |
| `references/format-spec.md` | Exact typography, margins, table, image, and hyperlink styling |
| `references/data-collection-checklist.md` | Research targets, URL priorities, and source quality gates |
| `scripts/validate_bg_json.py` | Standalone JSON validator (also called by `generate_bg_doc.py`) |
| `scripts/generate_bg_doc.py` | Deterministic JSON → `.docx` generator |
| `scripts/extract_pdf_page.py` | PDF slide-to-PNG extractor (PyMuPDF) |
