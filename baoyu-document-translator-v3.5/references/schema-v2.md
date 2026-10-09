# JSON Schema v2 for Document Translation

The v2 intermediate format is backward-compatible with v1 in spirit but adds keys stable across stories, explicit story identifiers, hyperlink metadata, and better table context.

## Top-level structure

```json
{
  "file_type": "docx|pptx",
  "source_file": "/path/to/input.docx",
  "elements": [...],
  "total_elements": 42,
  "total_runs": 156,
  "stories": ["body", "header1", "footer1", "footnotes", "endnotes"]
}
```

## Common fields

Every element has:

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | Stable unique identifier |
| `type` | string | `paragraph`, `table_cell`, `shape`, `footnote`, `endnote` |
| `runs` | int | Number of text runs |
| `text` | string | Original full text (for reference) |
| `parts` | string[] | Run texts; after translation, translated run texts |
| `story` | string | `body`, `header:{id}`, `footer:{id}`, `footnote:{n}`, `endnote:{n}`, `shape` |

## DOCX elements

### Body paragraph

```json
{
  "key": "p_body_0",
  "type": "paragraph",
  "story": "body",
  "index": 0,
  "style": "Heading 1",
  "runs": 3,
  "text": "Original text",
  "parts": ["run0", "run1", "run2"]
}
```

### Body table cell

```json
{
  "key": "t_body_0_r0_c0",
  "type": "table_cell",
  "story": "body",
  "table": 0,
  "row": 0,
  "col": 0,
  "runs": 1,
  "text": "Cell text",
  "parts": ["Cell text"]
}
```

### Header/footer paragraph

```json
{
  "key": "p_header_0_0",
  "type": "paragraph",
  "story": "header:1",
  "section": 0,
  "index": 0,
  "runs": 1,
  "text": "Confidential",
  "parts": ["Confidential"]
}
```

### Footnote / endnote paragraph

```json
{
  "key": "fn_0_p0",
  "type": "paragraph",
  "story": "footnote:0",
  "footnote_id": 0,
  "index": 0,
  "runs": 2,
  "text": "See also ...",
  "parts": ["See also ", "reference"]
}
```

### Hyperlink

Hyperlinks are represented as paragraph-level elements with a `hyperlink` field:

```json
{
  "key": "p_body_5",
  "type": "paragraph",
  "story": "body",
  "runs": 2,
  "hyperlink": {
    "runs": [1],
    "url": "https://example.com"
  },
  "text": "Click here to learn more",
  "parts": ["Click here ", "to learn more"]
}
```

The translator translates only the text; the writer re-applies the URL to the specified run indices.

### Text box / shape

```json
{
  "key": "shape_body_0_p0",
  "type": "paragraph",
  "story": "shape",
  "shape_id": 0,
  "index": 0,
  "runs": 1,
  "text": "Text box content",
  "parts": ["Text box content"]
}
```

## PPTX elements

### Shape

```json
{
  "key": "s_0_3",
  "type": "shape",
  "slide": 0,
  "shape": 3,
  "runs": 2,
  "text": "Title\nSubtitle",
  "parts": ["Title", "Subtitle"]
}
```

### Table cell

```json
{
  "key": "t_0_5_r1_c2",
  "type": "table_cell",
  "slide": 0,
  "shape": 5,
  "table_row": 1,
  "table_col": 2,
  "runs": 1,
  "text": "Cell text",
  "parts": ["Cell text"]
}
```

### Notes

```json
{
  "key": "n_0_p0",
  "type": "paragraph",
  "story": "notes",
  "slide": 0,
  "index": 0,
  "runs": 1,
  "text": "Speaker note",
  "parts": ["Speaker note"]
}
```

## Critical rules

1. `parts.length` MUST equal `runs` after translation.
2. `key` MUST be unique within the document.
3. `story` MUST be set so the writer knows where to write back.
4. Empty elements (no text) are skipped during extraction but their keys must not be re-used.
5. For merged table cells (DOCX), only physical cells are extracted; all references share the same translated text.
