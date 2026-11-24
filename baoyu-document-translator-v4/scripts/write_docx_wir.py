# -*- coding: utf-8 -*-
"""WIR-engine DOCX write-back (v4.3, Linux / WSL2 native .so engine).

Applies translated elements to the source DOCX via the `docx` skill's compiled WIR
engine (`WIRSession.open -> read -> edit -> save`), aligned with
`docx/references/wir-reference.md`:
- Uses real window handle `w, wir, next_cursor = session.read(part=..., cursor=...)`
  and `session.edit(w, edits)` across paginated windows (no `hasattr` guessing).
- Covers all stories: `document`, `footnotes`, `endnotes`, and all `header:rId*` /
  `footer:rId*` parts discovered from `word/_rels/document.xml.rels`.
- Preserves all non-text OOXML nodes and falls back to `namespace_guard_enabled=False`
  when legacy source documents trigger `E_NAMESPACE_IGNORABLE_MISSING_USED_PREFIX`.

Usage:
  python write_docx_wir.py input.docx output.docx translated.json
"""
import json
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from lxml import etree


def _discover_parts(docx_path: Path):
    """Discover WIR part names present in the DOCX package (document, headers, footers, notes)."""
    parts = ["document"]
    with zipfile.ZipFile(docx_path, "r") as zf:
        names = set(zf.namelist())
        if "word/_rels/document.xml.rels" in names:
            rel_root = etree.fromstring(zf.read("word/_rels/document.xml.rels"))
            for rel in rel_root:
                rtype = rel.get("Type", "")
                rid = rel.get("Id", "")
                target = rel.get("Target", "")
                if not rid or not target:
                    continue
                if rtype.endswith("/header"):
                    parts.append(f"header:{rid}")
                elif rtype.endswith("/footer"):
                    parts.append(f"footer:{rid}")
        if "word/footnotes.xml" in names:
            parts.append("footnotes")
        if "word/endnotes.xml" in names:
            parts.append("endnotes")
    return parts


def _part_matches_story(part: str, story: str) -> bool:
    if part == "document":
        return story in ("body", "textbox", "sdt")
    if part.startswith("header:"):
        return story.startswith("header") or story == "textbox"
    if part.startswith("footer:"):
        return story.startswith("footer") or story == "textbox"
    if part == "footnotes":
        return story.startswith("footnote")
    if part == "endnotes":
        return story.startswith("endnote")
    return False


def _build_window_edits(wir: str, elements: list, TextEdit):
    """Build exact TextEdit list for entries present in the current WIR window."""
    edits = []
    consumed = set()
    for e in elements:
        key = e["key"]
        src_parts = e.get("src_parts")
        tgt_parts = e.get("parts") or []
        src_text = e.get("text", "")
        tgt_text = "".join(tgt_parts)
        if not src_text.strip() or src_text == tgt_text:
            continue

        # Prefer per-run <r>...</r> exact replacement when src_parts align with tgt_parts
        if src_parts and len(src_parts) == len(tgt_parts):
            matched_all = True
            run_edits = []
            for sp, tp in zip(src_parts, tgt_parts):
                if not sp or sp == tp:
                    continue
                old_r = f"<r>{xml_escape(sp)}</r>"
                new_r = f"<r>{xml_escape(tp)}</r>"
                if old_r in wir:
                    run_edits.append(TextEdit(old_string=old_r, new_string=new_r))
                else:
                    matched_all = False
                    break
            if matched_all and run_edits:
                edits.extend(run_edits)
                consumed.add(key)
                continue

        # Whole-element <r>...</r> or escaped text fallback within this window
        old_wrapped = f"<r>{xml_escape(src_text)}</r>"
        if old_wrapped in wir:
            edits.append(TextEdit(old_string=old_wrapped, new_string=f"<r>{xml_escape(tgt_text)}</r>"))
            consumed.add(key)
            continue
        old_plain = xml_escape(src_text)
        if old_plain in wir:
            edits.append(TextEdit(old_string=old_plain, new_string=xml_escape(tgt_text)))
            consumed.add(key)
    return edits, consumed


def write_docx_wir(src_path: Path, dst_path: Path, json_path: Path) -> int:
    import engine_select

    sd = engine_select.docx_scripts_dir()
    ok, why = engine_select.engine_importable(sd)
    if not ok:
        print(f"WIR engine not importable ({why}). Use Linux/WSL2 Python 3.12 or surgical fallback.", file=sys.stderr)
        return 2

    if str(sd) not in sys.path:
        sys.path.insert(0, str(sd))

    from engine import TextEdit, WIRSession  # noqa: E402

    src_abs = src_path.resolve()
    dst_abs = dst_path.resolve()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    elements = data.get("elements", [])
    parts_list = _discover_parts(src_abs)

    applied = 0
    failed = 0
    remaining = {e["key"]: e for e in elements if e.get("text", "").strip() and e.get("text", "") != "".join(e.get("parts", []))}

    with WIRSession.open(str(src_abs)) as session:
        for part in parts_list:
            part_elems = [e for e in remaining.values() if _part_matches_story(part, e.get("story", "body"))]
            if not part_elems:
                continue
            cursor = None
            seen_cursors = set()
            while True:
                try:
                    w, wir, next_cursor = (
                        session.read(part=part, cursor=cursor)
                        if cursor is not None
                        else session.read(part=part)
                    )
                except Exception as exc:
                    print(f"[WIR] skip part={part}: {exc}", file=sys.stderr)
                    break

                pending = [e for e in part_elems if e["key"] in remaining]
                edits, consumed = _build_window_edits(wir, pending, TextEdit)
                if edits:
                    try:
                        session.edit(w, edits)
                        applied += len(edits)
                        for k in consumed:
                            remaining.pop(k, None)
                    except Exception as exc:
                        # Fallback to one-by-one within this window so one mismatch does not drop the batch
                        for ed in edits:
                            try:
                                w_cur, _, _ = (
                                    session.read(part=part, cursor=cursor)
                                    if cursor is not None
                                    else session.read(part=part)
                                )
                                session.edit(w_cur, [ed])
                                applied += 1
                            except Exception as item_exc:
                                failed += 1
                                print(f"[WIR] edit failed in {part}: {item_exc}", file=sys.stderr)

                if not next_cursor or next_cursor in seen_cursors:
                    break
                seen_cursors.add(next_cursor)
                cursor = next_cursor

        try:
            session.save(str(dst_abs))
        except Exception as save_exc:
            if "E_NAMESPACE_IGNORABLE_MISSING_USED_PREFIX" in str(save_exc):
                session.package.save(str(dst_abs), namespace_guard_enabled=False)
            else:
                raise

    print(f"WIR write-back -> {dst_abs}: applied={applied}, failed={failed}, unmatched={len(remaining)}")
    return 0 if failed == 0 else 1


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python write_docx_wir.py input.docx output.docx translated.json", file=sys.stderr)
        return 2
    return write_docx_wir(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))


if __name__ == "__main__":
    sys.exit(main())
