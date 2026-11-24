#!/usr/bin/env python3
"""
Unified Word document post-processing module for footnotes & endnotes with NOTEREF cross-references.

Replaces the duplicated `docx_footnote.py` + `docx_endnote.py` twins (438 lines -> ~185 lines)
and uses `tempfile.TemporaryDirectory()` so temp extraction dirs never leak on error.
"""
import logging
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from docx.oxml.ns import qn
from docx_utils import ensure_footnote_styles, update_content_types, update_document_rels
from lxml import etree

logger = logging.getLogger(__name__)

NSMAP = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def _create_notes_xml(kind: str, citation_numbers, citation_db: dict):
    """Build footnotes.xml or endnotes.xml with bookmarks for NOTEREF cross-references."""
    is_fn = kind == "footnote"
    root_tag = "w:footnotes" if is_fn else "w:endnotes"
    item_tag = "w:footnote" if is_fn else "w:endnote"
    ref_tag = "w:footnoteRef" if is_fn else "w:endnoteRef"
    bm_prefix = "_Ref_Footnote_" if is_fn else "_Edn"

    root = etree.Element(qn(root_tag), nsmap=NSMAP)

    if not is_fn:
        endnote_pr = etree.SubElement(root, qn("w:endnotePr"))
        etree.SubElement(endnote_pr, qn("w:numFmt"), {qn("w:val"): "decimal"})

    for sep_type, sep_id, sep_tag in (
        ("separator", "-1", qn("w:separator")),
        ("continuationSeparator", "0", qn("w:continuationSeparator")),
    ):
        node = etree.SubElement(root, qn(item_tag), {qn("w:type"): sep_type, qn("w:id"): sep_id})
        p = etree.SubElement(node, qn("w:p"))
        r = etree.SubElement(p, qn("w:r"))
        etree.SubElement(r, sep_tag)

    for num in sorted(citation_numbers):
        node = etree.SubElement(root, qn(item_tag), {qn("w:id"): str(num)})
        p = etree.SubElement(node, qn("w:p"))

        if is_fn:
            pPr = etree.SubElement(p, qn("w:pPr"))
            etree.SubElement(pPr, qn("w:pStyle"), {qn("w:val"): "FootnoteText"})
            etree.SubElement(
                pPr,
                qn("w:spacing"),
                {qn("w:before"): "0", qn("w:after"): "0", qn("w:line"): "200", qn("w:lineRule"): "exact"},
            )

        etree.SubElement(p, qn("w:bookmarkStart"), {qn("w:id"): str(num + 10000), qn("w:name"): f"{bm_prefix}{num}"})

        r1 = etree.SubElement(p, qn("w:r"))
        rPr1 = etree.SubElement(r1, qn("w:rPr"))
        if is_fn:
            etree.SubElement(rPr1, qn("w:rStyle"), {qn("w:val"): "FootnoteReference"})
        etree.SubElement(rPr1, qn("w:vertAlign"), {qn("w:val"): "superscript"})
        etree.SubElement(r1, qn(ref_tag))

        r2 = etree.SubElement(p, qn("w:r"))
        if is_fn:
            rPr2 = etree.SubElement(r2, qn("w:rPr"))
            etree.SubElement(rPr2, qn("w:sz"), {qn("w:val"): "18"})
            etree.SubElement(rPr2, qn("w:szCs"), {qn("w:val"): "18"})
        t2 = etree.SubElement(r2, qn("w:t"))
        t2.set(qn("xml:space"), "preserve")
        info = citation_db.get(num, {})
        site = info.get("page", {}).get("site_name", "")
        url = info.get("url", "")
        t2.text = f" {site}. {url}" if (site and url) else (f" {url}" if url else "")

        etree.SubElement(p, qn("w:bookmarkEnd"), {qn("w:id"): str(num + 10000)})

    return root


def _note_ref_run(kind: str, num: int):
    ref_tag = "w:footnoteReference" if kind == "footnote" else "w:endnoteReference"
    run = etree.Element(qn("w:r"))
    rPr = etree.SubElement(run, qn("w:rPr"))
    etree.SubElement(rPr, qn("w:vertAlign"), {qn("w:val"): "superscript"})
    etree.SubElement(run, qn(ref_tag), {qn("w:id"): str(num)})
    return run


def _noteref_field(kind: str, num: int):
    bm_prefix = "_Ref_Footnote_" if kind == "footnote" else "_Edn"
    fld = etree.Element(qn("w:fldSimple"), {qn("w:instr"): f"NOTEREF {bm_prefix}{num} \\h \\f"})
    run = etree.SubElement(fld, qn("w:r"))
    rPr = etree.SubElement(run, qn("w:rPr"))
    etree.SubElement(rPr, qn("w:vertAlign"), {qn("w:val"): "superscript"})
    t = etree.SubElement(run, qn("w:t"))
    t.text = str(num)
    return fld


def process_word_document_notes(
    docx_path: str,
    kind: str = "footnote",
    output_path: str = None,
    citation_db: dict = None,
) -> bool:
    """Replace superscript citation numbers with footnote/endnote refs + NOTEREF cross-references."""
    if kind not in ("footnote", "endnote"):
        raise ValueError(f"Unsupported note kind: {kind}")
    output_path = output_path or docx_path
    is_fn = kind == "footnote"
    xml_filename = "footnotes.xml" if is_fn else "endnotes.xml"

    with tempfile.TemporaryDirectory(prefix=f"docx_{kind}_") as temp_dir:
        temp_path = Path(temp_dir)
        with ZipFile(docx_path, "r") as zip_ref:
            zip_ref.extractall(temp_path)

        doc_xml_path = temp_path / "word" / "document.xml"
        tree = etree.parse(str(doc_xml_path))
        root = tree.getroot()

        occurrences = defaultdict(list)
        first_seen = {}
        for para in root.findall(".//w:p", NSMAP):
            for run in para.findall(".//w:r", NSMAP):
                va = run.find(".//w:vertAlign", NSMAP)
                if va is not None and va.get(qn("w:val")) == "superscript":
                    t = run.find(".//w:t", NSMAP)
                    if t is not None and t.text and re.match(r"^\d+$", t.text.strip()):
                        num = int(t.text.strip())
                        occurrences[num].append(run)
                        first_seen.setdefault(num, run)

        logger.info("Found %d unique citation numbers (%d positions)", len(first_seen), sum(len(v) for v in occurrences.values()))

        notes_root = _create_notes_xml(kind, first_seen.keys(), citation_db or {})
        etree.ElementTree(notes_root).write(
            str(temp_path / "word" / xml_filename),
            encoding="utf-8",
            xml_declaration=True,
            standalone=True,
        )

        update_document_rels(temp_path, NSMAP)
        if is_fn:
            ensure_footnote_styles(temp_path, NSMAP)

        ref_cnt = noteref_cnt = 0
        for num, runs in occurrences.items():
            for idx, run in enumerate(runs):
                parent = run.getparent()
                if idx == 0:
                    parent.replace(run, _note_ref_run(kind, num))
                    ref_cnt += 1
                else:
                    parent.replace(run, _noteref_field(kind, num))
                    noteref_cnt += 1

        if not is_fn:
            sect_prs = root.findall(".//w:sectPr", NSMAP)
            if sect_prs and sect_prs[-1].find(".//w:endnotePr", NSMAP) is None:
                ep = etree.Element(qn("w:endnotePr"))
                etree.SubElement(ep, qn("w:numFmt"), {qn("w:val"): "decimal"})
                sect_prs[-1].insert(0, ep)

        tree.write(str(doc_xml_path), encoding="utf-8", xml_declaration=True, standalone=True)
        update_content_types(temp_path, NSMAP)

        with ZipFile(output_path, "w") as zout:
            for fp in temp_path.rglob("*"):
                if fp.is_file():
                    zout.write(fp, fp.relative_to(temp_path))

    logger.info("Created %d %s refs + %d NOTEREF cross-refs -> %s", ref_cnt, kind, noteref_cnt, output_path)
    return True


def process_word_document_with_noteref(docx_path: str, output_path: str = None, citation_db: dict = None) -> bool:
    return process_word_document_notes(docx_path, kind="footnote", output_path=output_path, citation_db=citation_db)


def process_word_document_with_endnotes(docx_path: str, output_path: str = None, citation_db: dict = None) -> bool:
    return process_word_document_notes(docx_path, kind="endnote", output_path=output_path, citation_db=citation_db)
