# -*- coding: utf-8 -*-
"""
engine_surgical — 外科手术式 DOCX 保格式文字提取与写回引擎（纯 Python，全平台）

定位与边界：
- 适用场景：**保格式原地文本替换** 与 `baoyu-document-translator-v3.6 / v4` 翻译写回。
- 不适用场景：批注（comments）、修订（tracked changes）、增删段落/表格/节等结构性编辑。
  通用结构/批注/修订编辑请在 Linux/WSL2 下使用 WIR（`scripts/engine/`），或在原生
  Windows/macOS 下使用 `python-docx` + `lxml` 或 C# OpenXML SDK。

语义保证（强于 python-docx 的 `run.text = ...`）：
- 只修改 `<w:t>` 节点，完整保留 `w:br`、`w:ptab`、`w:fldChar`/`w:instrText` 域、
  `w:drawing`/`w:pict` 等非文字 run 子节点；
- WPS 融合域 run（fldChar+instrText+w:t 同 run）只替换缓存文本；
- 域控制 run 与纯数字域结果 run（SEQ/PAGEREF 缓存编号）永不接收文字。

覆盖 story：正文段落、正文表格、页眉页脚（含 default/first/even 变体）、
正文与页眉页脚文本框（含嵌套表格）、SDT 内容控件、脚注、尾注。

用法（独立提取 + 写回）：
    from engine_surgical import extract_elements, apply_keyed_parts, SurgicalSession

    with SurgicalSession.open("in.docx") as s:
        els = s.extract()
        els["p_body_0"]["parts"] = ["New Title"]
        s.write_elements(els)
        s.save("out.docx")
"""

import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Union

from docx import Document
from docx.table import Table
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XMLSPACE = "{http://www.w3.org/XML/1998/namespace}space"


def qn(t: str) -> str:
    return "{%s}%s" % (W, t)


def get_run_text(r_el) -> str:
    """Extract text from a run element, mirroring set_run_text's tab/br semantics."""
    t_elems = r_el.findall(qn("t"))
    if t_elems:
        return "".join(t.text or "" for t in t_elems)
    if r_el.find(qn("tab")) is not None:
        return "\t"
    if r_el.find(qn("br")) is not None:
        return "\n"
    return ""


def set_run_text(r_el, text: str) -> None:
    # Field runs: pure control runs (fldChar/instrText without w:t) never receive text.
    # WPS-style FUSED field runs (fldChar+instrText+w:t in one run) DO get their w:t
    # replaced: field nodes preserved, cached result updated.
    has_field = (
        r_el.find(qn("fldChar")) is not None
        or r_el.find(qn("instrText")) is not None
    )
    t = r_el.find(qn("t"))
    if has_field and t is None:
        return
    if text == "\t":
        if t is not None:
            t.text = ""
        if r_el.find(qn("tab")) is None:
            r_el.append(etree.Element(qn("tab")))
        return
    if text == "\n":
        if t is not None:
            t.text = ""
        if r_el.find(qn("br")) is None:
            r_el.append(etree.Element(qn("br")))
        return
    if t is None:
        if text == "":
            return
        t = etree.SubElement(r_el, qn("t"))
    t.text = text
    if text != text.strip():
        t.set(XMLSPACE, "preserve")
    elif t.get(XMLSPACE):
        del t.attrib[XMLSPACE]
    # WPS runs may carry multiple w:t nodes: blank extras so no source residue survives
    for extra in r_el.findall(qn("t")):
        if extra is not t:
            extra.text = ""


def para_run_elems(p_el) -> list:
    """Mirror of extract_docx_v2.para_runs: direct w:r + w:ins runs + w:hyperlink runs.
    Field control runs and numeric field RESULT runs (cached SEQ/PAGEREF numbers) are
    excluded; WPS FUSED runs (begin+instr+w:t in one run) ARE included."""
    runs = []
    state = {"mode": None}

    def consider(r):
        fc = r.find(qn("fldChar"))
        ftype = fc.get(qn("fldCharType")) if fc is not None else None
        has_t = r.find(qn("t")) is not None
        has_instr = r.find(qn("instrText")) is not None
        if ftype == "begin":
            if has_t:
                runs.append(r)  # fused WPS run: replace cached result
            state["mode"] = "inside"
            return
        if ftype == "separate":
            state["mode"] = "result"
            return
        if ftype == "end":
            state["mode"] = None
            return
        if has_instr:
            return
        if state["mode"] in ("inside", "result"):
            txt = "".join(t.text or "" for t in r.findall(qn("t")))
            if re.fullmatch(r"[\d\.\,\;\:\s\/\-\%]*", txt):
                return
        runs.append(r)

    def collect(container):
        for r in container:
            if r.tag == qn("r"):
                consider(r)

    for c in p_el:
        if c.tag == qn("r"):
            collect([c])
        elif c.tag == qn("ins"):
            collect(list(c))
        elif c.tag == qn("hyperlink"):
            collect(list(c))
    return runs


def write_para(p_el, parts: List[str]) -> None:
    runs = para_run_elems(p_el)
    for i, r in enumerate(runs):
        set_run_text(r, parts[i] if i < len(parts) else "")


def _extract_notes(xml_bytes: bytes, tag: str, prefix: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    root = etree.fromstring(xml_bytes)
    for note in root.findall(".//" + qn(tag)):
        if note.get(qn("type")) in ("separator", "continuationSeparator"):
            continue
        nid = note.get(qn("id"))
        pi = 0
        for p in note.findall(qn("p")):
            runs = p.findall(".//" + qn("r"))
            text_runs = [r for r in runs if r.find(qn("t")) is not None]
            parts = ["".join(t.text or "" for t in r.findall(qn("t"))) for r in text_runs]
            txt = "".join(parts)
            if not txt.strip():
                continue
            out["%s_%s_p%d" % (prefix, nid, pi)] = {"parts": parts, "text": txt}
            pi += 1
    return out


def write_notes(xml_bytes: bytes, els: Dict[str, dict], tag: str, prefix: str) -> bytes:
    root = etree.fromstring(xml_bytes)
    for note in root.findall(".//" + qn(tag)):
        if note.get(qn("type")) in ("separator", "continuationSeparator"):
            continue
        nid = note.get(qn("id"))
        pi = 0
        for p in note.findall(qn("p")):
            runs = p.findall(".//" + qn("r"))
            text_runs = [r for r in runs if r.find(qn("t")) is not None]
            txt = "".join((r.find(qn("t")).text or "") for r in text_runs)
            if not txt.strip():
                continue
            e = els.get("%s_%s_p%d" % (prefix, nid, pi))
            if e:
                if len(e["parts"]) > len(text_runs):
                    print(
                        "WARNING %s_%s_p%d: %d parts for %d text runs; extra dropped"
                        % (prefix, nid, pi, len(e["parts"]), len(text_runs))
                    )
                for i, r in enumerate(text_runs):
                    set_run_text(r, e["parts"][i] if i < len(e["parts"]) else "")
            pi += 1
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def extract_elements(src: Union[str, Path]) -> Dict[str, dict]:
    """Extract all editable stories into {key: {"parts": [...], "text": "..."}}.
    Exact mirror of `_walk_and_write` and `write_notes` so `engine_surgical` can be
    used standalone without requiring external extraction scripts."""
    src_path = Path(src)
    doc = Document(str(src_path))
    els: Dict[str, dict] = {}

    def _record_para(key: str, p_el) -> None:
        parts = [get_run_text(r) for r in para_run_elems(p_el)]
        text = "".join(parts)
        if text.strip():
            els[key] = {"parts": parts, "text": text}

    # Body paragraphs
    for i, p in enumerate(doc.paragraphs):
        _record_para("p_body_%d" % i, p._p)

    # Body tables
    for ti, t in enumerate(doc.tables):
        for ri, row in enumerate(t.rows):
            for ci, cell in enumerate(row.cells):
                parts = [
                    get_run_text(r)
                    for p in cell._tc.findall(qn("p"))
                    for r in para_run_elems(p)
                ]
                text = "".join(parts)
                if text.strip():
                    els["t_body_%d_r%d_c%d" % (ti, ri, ci)] = {"parts": parts, "text": text}

    # Header / footer variants (default + first + even)
    for si, section in enumerate(doc.sections):
        for attr, suffix, kind in (
            ("header", "", "header"),
            ("first_page_header", "first", "header"),
            ("even_page_header", "even", "header"),
            ("footer", "", "footer"),
            ("first_page_footer", "first", "footer"),
            ("even_page_footer", "even", "footer"),
        ):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            pre = "p_%s%s_%s_" % (kind, suffix, si)
            tpre = "t_%s%s_%s_" % (kind, suffix, si)
            pi = ti = 0
            for child in part._element:
                tag = child.tag.split("}")[-1]
                if tag == "p":
                    _record_para("%s%d" % (pre, pi), child)
                    pi += 1
                elif tag == "tbl":
                    t = Table(child, part)
                    for ri, row in enumerate(t.rows):
                        for ci, cell in enumerate(row.cells):
                            parts = [
                                get_run_text(r)
                                for p in cell._tc.findall(qn("p"))
                                for r in para_run_elems(p)
                            ]
                            text = "".join(parts)
                            if text.strip():
                                els["%s%d_r%d_c%d" % (tpre, ti, ri, ci)] = {
                                    "parts": parts,
                                    "text": text,
                                }
                    ti += 1

    # Text boxes in body + nested tables
    for n, tb in enumerate(doc.element.body.findall(".//" + qn("txbxContent"))):
        pi = 0
        for p in tb.findall(qn("p")):
            txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
            if not txt.strip():
                continue
            _record_para("txbx_%d_p%d" % (n, pi), p)
            pi += 1
        for ti, tbl in enumerate(tb.findall(qn("tbl"))):
            for ri, tr_el in enumerate(tbl.findall(qn("tr"))):
                seen_tc, ci = set(), 0
                for tc in tr_el.findall(qn("tc")):
                    if id(tc) in seen_tc:
                        continue
                    seen_tc.add(id(tc))
                    parts = [
                        get_run_text(r)
                        for p in tc.findall(".//" + qn("p"))
                        for r in para_run_elems(p)
                    ]
                    text = "".join(parts)
                    if text.strip():
                        els["t_txbx_%d_%d_r%d_c%d" % (n, ti, ri, ci)] = {
                            "parts": parts,
                            "text": text,
                        }
                    ci += 1

    # Text boxes inside header/footer parts
    for si, section in enumerate(doc.sections):
        for attr, scope in (
            ("header", "h"),
            ("footer", "f"),
            ("first_page_header", "hfirst"),
            ("first_page_footer", "ffirst"),
        ):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            for n, tb in enumerate(part._element.findall(".//" + qn("txbxContent"))):
                pi = 0
                for p in tb.findall(qn("p")):
                    txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
                    if not txt.strip():
                        continue
                    _record_para("txbx_%s%d_%d_p%d" % (scope, si, n, pi), p)
                    pi += 1

    # SDT content controls
    seen_sdt = set()
    for idx, sdt in enumerate(doc.element.body.findall(".//" + qn("sdt"))):
        if id(sdt) in seen_sdt:
            continue
        seen_sdt.add(id(sdt))
        pi = 0
        for p in sdt.findall(".//" + qn("p")):
            txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
            if not txt.strip():
                continue
            _record_para("p_sdt_%d_p%d" % (idx, pi), p)
            pi += 1

    # Footnotes & endnotes via zip inspection
    with zipfile.ZipFile(src_path, "r") as zin:
        names = set(zin.namelist())
        if "word/footnotes.xml" in names:
            els.update(_extract_notes(zin.read("word/footnotes.xml"), "footnote", "fn"))
        if "word/endnotes.xml" in names:
            els.update(_extract_notes(zin.read("word/endnotes.xml"), "endnote", "en"))

    return els


def _walk_and_write(doc, els: Dict[str, dict], consolidate_max: int = 80) -> Tuple[int, int]:
    """按 key 寻址写入全部 story；返回 (段落数, 单元格数)。"""
    np = nt = 0
    for i, p in enumerate(doc.paragraphs):
        e = els.get("p_body_%d" % i)
        if e:
            runs = para_run_elems(p._p)
            trs = [r for r in runs if r.find(qn("t")) is not None]
            sigs = {
                etree.tostring(r.find(qn("rPr"))) if r.find(qn("rPr")) is not None else b""
                for r in trs
            }
            if len(trs) >= 3 and len(sigs) >= 3 and sum(len(x) for x in e["parts"]) < consolidate_max:
                joined = "".join(e["parts"])
                newparts = [""] * len(runs)
                first = True
                for idx, r in enumerate(runs):
                    if r.find(qn("t")) is None:
                        newparts[idx] = e["parts"][idx] if idx < len(e["parts"]) else ""
                    elif first:
                        newparts[idx] = joined
                        first = False
                write_para(p._p, newparts)
            else:
                write_para(p._p, e["parts"])
            np += 1

    for ti, t in enumerate(doc.tables):
        for ri, row in enumerate(t.rows):
            for ci, cell in enumerate(row.cells):
                e = els.get("t_body_%d_r%d_c%d" % (ti, ri, ci))
                if not e:
                    continue
                k = 0
                for p in cell._tc.findall(qn("p")):
                    for r in para_run_elems(p):
                        set_run_text(r, e["parts"][k] if k < len(e["parts"]) else "")
                        k += 1
                nt += 1

    for si, section in enumerate(doc.sections):
        for attr, suffix, kind in (
            ("header", "", "header"),
            ("first_page_header", "first", "header"),
            ("even_page_header", "even", "header"),
            ("footer", "", "footer"),
            ("first_page_footer", "first", "footer"),
            ("even_page_footer", "even", "footer"),
        ):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            pre = "p_%s%s_%s_" % (kind, suffix, si)
            tpre = "t_%s%s_%s_" % (kind, suffix, si)
            pi = ti = 0
            for child in part._element:
                tag = child.tag.split("}")[-1]
                if tag == "p":
                    e = els.get("%s%d" % (pre, pi))
                    if e:
                        write_para(child, e["parts"])
                    pi += 1
                elif tag == "tbl":
                    t = Table(child, part)
                    for ri, row in enumerate(t.rows):
                        for ci, cell in enumerate(row.cells):
                            e = els.get("%s%d_r%d_c%d" % (tpre, ti, ri, ci))
                            if not e:
                                continue
                            k = 0
                            for p in cell._tc.findall(qn("p")):
                                for r in para_run_elems(p):
                                    set_run_text(r, e["parts"][k] if k < len(e["parts"]) else "")
                                    k += 1
                    ti += 1

    for n, tb in enumerate(doc.element.body.findall(".//" + qn("txbxContent"))):
        pi = 0
        for p in tb.findall(qn("p")):
            txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
            if not txt.strip():
                continue
            e = els.get("txbx_%d_p%d" % (n, pi))
            if e:
                write_para(p, e["parts"])
            pi += 1
        for ti, tbl in enumerate(tb.findall(qn("tbl"))):
            for ri, tr_el in enumerate(tbl.findall(qn("tr"))):
                seen_tc, ci = set(), 0
                for tc in tr_el.findall(qn("tc")):
                    if id(tc) in seen_tc:
                        continue
                    seen_tc.add(id(tc))
                    e = els.get("t_txbx_%d_%d_r%d_c%d" % (n, ti, ri, ci))
                    if e:
                        runs = [
                            r
                            for p in tc.findall(".//" + qn("p"))
                            for r in para_run_elems(p)
                        ]
                        for i, r in enumerate(runs):
                            set_run_text(r, e["parts"][i] if i < len(e["parts"]) else "")
                    ci += 1

    for si, section in enumerate(doc.sections):
        for attr, scope in (
            ("header", "h"),
            ("footer", "f"),
            ("first_page_header", "hfirst"),
            ("first_page_footer", "ffirst"),
        ):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            for n, tb in enumerate(part._element.findall(".//" + qn("txbxContent"))):
                pi = 0
                for p in tb.findall(qn("p")):
                    txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
                    if not txt.strip():
                        continue
                    e = els.get("txbx_%s%d_%d_p%d" % (scope, si, n, pi))
                    if e:
                        write_para(p, e["parts"])
                    pi += 1

    seen_sdt = set()
    for idx, sdt in enumerate(doc.element.body.findall(".//" + qn("sdt"))):
        if id(sdt) in seen_sdt:
            continue
        seen_sdt.add(id(sdt))
        pi = 0
        for p in sdt.findall(".//" + qn("p")):
            txt = "".join(t.text or "" for t in p.findall(".//" + qn("t")))
            if not txt.strip():
                continue
            e = els.get("p_sdt_%d_p%d" % (idx, pi))
            if e:
                write_para(p, e["parts"])
            pi += 1

    return np, nt


def apply_keyed_parts(
    src: Union[str, Path],
    dst: Union[str, Path],
    els: Dict[str, dict],
    consolidate_max: int = 80,
) -> Tuple[int, int]:
    """核心写回：按 key->{"parts": [...]} 寻址写入 src 的副本并安全存到 dst。
    兼容 baoyu-document-translator-v3.6 / v4 的 extract_docx_v2 键名体系，
    也可直接配合本包的 `extract_elements(src)` 使用。"""
    src_path = Path(src)
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    doc = Document(str(src_path))
    np, nt = _walk_and_write(doc, els, consolidate_max)

    fd, tmp_name = tempfile.mkstemp(dir=str(dst_path.parent), suffix=".docx.tmp")
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        doc.save(str(tmp_path))
        with zipfile.ZipFile(tmp_path, "r") as zin:
            names = zin.namelist()
            datas = {n: zin.read(n) for n in names}

        if "word/footnotes.xml" in datas:
            datas["word/footnotes.xml"] = write_notes(
                datas["word/footnotes.xml"], els, "footnote", "fn"
            )
        if "word/endnotes.xml" in datas:
            datas["word/endnotes.xml"] = write_notes(
                datas["word/endnotes.xml"], els, "endnote", "en"
            )

        with zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                zout.writestr(n, datas[n])
    finally:
        tmp_path.unlink(missing_ok=True)

    print("surgical write-back done: %d paragraphs, %d cells -> %s" % (np, nt, dst_path))
    return np, nt


class SurgicalSession:
    """保格式文字提取/写回会话（open / extract / write_elements / save + 上下文管理）。
    注意：edit 语义是 key->parts 寻址写回，不提供 WIR 的批注/修订/结构增删能力。"""

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self._els: Dict[str, dict] = {}
        self._cons = 80

    @classmethod
    def open(cls, path: Union[str, Path]) -> "SurgicalSession":
        return cls(path)

    def extract(self) -> Dict[str, dict]:
        return extract_elements(self.path)

    def write_elements(self, els: Dict[str, dict], consolidate_max: int = 80) -> "SurgicalSession":
        self._els = els
        self._cons = consolidate_max
        return self

    def save(self, out: Union[str, Path]) -> Tuple[int, int]:
        return apply_keyed_parts(self.path, out, self._els, self._cons)

    def __enter__(self) -> "SurgicalSession":
        return self

    def __exit__(self, *exc) -> bool:
        return False
