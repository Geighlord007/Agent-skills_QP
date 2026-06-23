# JSON Schema for Document Translation

## Overview

The JSON intermediate format bridges the original document and the translated output. It preserves:
- Element identity (`key`)
- Run-level structure (`runs`, `parts`)
- Text content (`text`)
- Document hierarchy (`type`, `style`, `table`, `row`, `col`, etc.)

## Top-Level Structure

```json
{
  "file_type": "docx|pptx",
  "source_file": "/path/to/input.docx",
  "elements": [...],
  "total_elements": 42,
  "total_runs": 156
}
```

## Element Types

### DOCX Paragraph

```json
{
  "key": "p0",
  "type": "paragraph",
  "index": 0,
  "style": "Heading 1",
  "runs": 3,
  "text": "Original text content",
  "parts": ["run0 text", "run1 text", "run2 text"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | Unique identifier: `p{index}` |
| `type` | string | `"paragraph"` |
| `index` | int | Paragraph index in document body |
| `style` | string | Paragraph style name (e.g., "Heading 1", "Normal") |
| `runs` | int | Number of runs with text |
| `text` | string | Full concatenated text |
| `parts` | string[] | Array of run texts, length == runs |

### DOCX Table Cell

```json
{
  "key": "t0_r1_c2",
  "type": "table_cell",
  "table": 0,
  "row": 1,
  "col": 2,
  "runs": 2,
  "text": "Cell text content",
  "parts": ["part1", "part2"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | `t{table}_r{row}_c{col}` |
| `type` | string | `"table_cell"` |
| `table` | int | Table index |
| `row` | int | Row index |
| `col` | int | Column index |
| `runs` | int | Number of runs |
| `text` | string | Cell text |
| `parts` | string[] | Run texts |

### PPTX Shape

```json
{
  "key": "(2, 5)",
  "type": "shape",
  "slide": 2,
  "shape": 5,
  "runs": 4,
  "text": "Shape text content",
  "parts": ["run0", "run1", "run2", "run3"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | `({slide}, {shape})` |
| `type` | string | `"shape"` or `"table_cell"` |
| `slide` | int | Slide index (0-based) |
| `shape` | int | Shape index on slide |
| `runs` | int | Total runs across all paragraphs |
| `text` | string | Full text (paragraphs joined by `\n`) |
| `parts` | string[] | Flattened run texts |

### PPTX Table Cell

```json
{
  "key": "(1, 3, 0, 2)",
  "type": "table_cell",
  "slide": 1,
  "shape": 3,
  "table_row": 0,
  "table_col": 2,
  "runs": 1,
  "text": "Cell text",
  "parts": ["Cell text"]
}
```

## Critical Rules

1. **`parts.length` MUST equal `runs`** — One translation per run
2. **`key` MUST be unique** — Used for mapping translations back to document
3. **Order matters** — Elements are in document reading order
4. **Empty elements are skipped** — Elements with no text are not included

## Translation Output Format

After translation, the JSON is updated with translated `parts`:

```json
{
  "elements": [
    {
      "key": "p0",
      "type": "paragraph",
      "runs": 3,
      "text": "Original text",
      "parts": ["Translated", "run0", "text"]
    }
  ]
}
```

The `text` field remains the original (for reference), while `parts` contains the translation.
