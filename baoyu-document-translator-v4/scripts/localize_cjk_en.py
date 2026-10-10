# -*- coding: utf-8 -*-
"""CJK->EN localization pass (v2.1): deterministic fixes for Chinese layout parameters
that become visual defects in English. Subcommands (all operate on a .docx in place):

  fonts      replace CJK fonts in w:ascii/w:hAnsi (run+style level) with the doc's
             Latin default (docDefaults); w:eastAsia untouched
  numbering  decimalFullWidth/chineseCounting -> decimal; CJK lvlText punctuation -> '.'
  tracking   remove rPr character spacing (w:spacing w:val) above threshold (default 40)
  justify    set jc=left on table-cell paragraphs that inherit justify (keep center/right)

Usage: python localize_cjk_en.py <cmd> file.docx [--threshold N]
Always follow with verify_structure.py + render QA.
"""
import sys, re, zipfile, shutil

CJK_FONTS = ("宋体", "黑体", "等线", "楷体", "仿宋", "微软雅黑", "SimSun", "SimHei",
             "DengXian", "KaiTi", "FangSong", "Microsoft YaHei")
XML_PARTS = None  # all word/*.xml + styles


def _edit(zip_path, fn):
    tmp = zip_path + ".tmp"
    with zipfile.ZipFile(zip_path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml") and item.filename.startswith("word/"):
                data = fn(item.filename, data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, zip_path)


def cmd_fonts(path):
    stats = {}
    def fn(name, x):
        # latin default from styles docDefaults
        if name == "word/styles.xml":
            m = re.search(r'<w:docDefaults>.*?<w:rFonts w:ascii="([^"]+)"', x, re.S)
            latin = m.group(1) if m else "Times New Roman"
        else:
            latin = getattr(fn, "_latin", None)
            if not latin:
                return x
        def repl(m):
            tag = m.group(0)
            for attr in ("w:ascii", "w:hAnsi"):
                mm = re.search(attr + r'="([^"]*)"', tag)
                if mm and mm.group(1) in CJK_FONTS:
                    tag = tag.replace(mm.group(0), attr + '="%s"' % latin)
                    stats["fonts"] = stats.get("fonts", 0) + 1
            return tag
        return re.sub(r"<w:rFonts[^>]*/>", repl, x)
    # two passes: first read latin default
    with zipfile.ZipFile(path) as z:
        s = z.read("word/styles.xml").decode("utf-8")
    m = re.search(r'<w:docDefaults>.*?<w:rFonts w:ascii="([^"]+)"', s, re.S)
    fn._latin = m.group(1) if m else "Times New Roman"
    _edit(path, fn)
    print("fonts replaced:", stats.get("fonts", 0), "->", fn._latin)


def cmd_numbering(path):
    stats = {}
    def fn(name, x):
        if name != "word/numbering.xml":
            return x
        for old, new in (('<w:numFmt w:val="decimalFullWidth"/>', '<w:numFmt w:val="decimal"/>'),
                         ('<w:numFmt w:val="chineseCounting"/>', '<w:numFmt w:val="decimal"/>'),
                         ('<w:numFmt w:val="chineseCountingThousand"/>', '<w:numFmt w:val="decimal"/>')):
            n = x.count(old)
            x = x.replace(old, new)
            stats["numFmt"] = stats.get("numFmt", 0) + n
        def lt(m):
            v = m.group(1)
            if re.search(r"[、，。；]", v):
                stats["lvlText"] = stats.get("lvlText", 0) + 1
                return '<w:lvlText w:val="%s"/>' % re.sub(r"[、，。；]", ".", v)
            return m.group(0)
        x = re.sub(r'<w:lvlText w:val="([^"]*)"/>', lt, x)
        return x
    _edit(path, fn)
    print("numbering:", stats)


def cmd_tracking(path, thr=40):
    stats = {}
    def fn(name, x):
        def repl(m):
            if int(m.group(1)) > thr:
                stats["tracking"] = stats.get("tracking", 0) + 1
                return ""
            return m.group(0)
        return re.sub(r'<w:spacing w:val="(\d+)"/>', repl, x)
    _edit(path, fn)
    print("tracking removed:", stats.get("tracking", 0))


def cmd_justify(path):
    stats = {}
    def fn(name, x):
        if name != "word/document.xml":
            return x
        def fix_tc(m):
            tc = m.group(0)
            def fix_p(pm):
                p = pm.group(0)
                if "<w:jc" in p:
                    return p  # explicit alignment wins
                if "<w:pPr>" in p:
                    stats["jc"] = stats.get("jc", 0) + 1
                    return p.replace("<w:pPr>", '<w:pPr><w:jc w:val="left"/>', 1)
                return re.sub(r"(<w:p\b[^>]*>)", r'\1<w:pPr><w:jc w:val="left"/></w:pPr>', p, count=1)
            return re.sub(r"<w:p\b[^>]*>(?:(?!</w:p>).)*</w:p>", fix_p, tc, flags=re.S)
        return re.sub(r"<w:tc>.*?</w:tc>", fix_tc, x, flags=re.S)
    _edit(path, fn)
    print("table-cell paragraphs left-aligned:", stats.get("jc", 0))


def cmd_fields(path):
    """Sanitize CJK date/format switches inside field instrText (WPS fused fields keep
    Chinese switches; Word re-evaluates or caches them)."""
    stats = {}
    MAP = [("yyyy\\u5e74M\\u6708d\\u65e5", "MMMM d, yyyy"),
           ("yyyy\\u5e74M\\u6708", "MMMM yyyy"),
           ("yyyy\\u5e74", "yyyy")]
    def fn(name, x):
        if "<w:instrText" not in x:
            return x
        def repl(m):
            s = m.group(0)
            for a, b in (( "yyyy年M月d日", "MMMM d, yyyy"), ("yyyy年M月", "MMMM yyyy"), ("yyyy年", "yyyy")):
                if a in s:
                    stats["switch"] = stats.get("switch", 0) + 1
                    s = s.replace(a, b)
            # WPS emits "Time" field name; Word only knows TIME (else: Error! Unrecognized switch)
            s = re.sub(r"\bTime\b", "TIME", s)
            # Chinese SEQ/TOC sequence identifiers break Word field parsing
            for a, b in (("SEQ 表", "SEQ Table"), ("SEQ 图", "SEQ Figure"),
                         ('\\c "表"', '\\c "Table"'), ('\\c "图"', '\\c "Figure"')):
                if a in s:
                    stats["seq"] = stats.get("seq", 0) + 1
                    s = s.replace(a, b)
            return s
        x = re.sub(r"<w:instrText[^>]*>[^<]*</w:instrText>", repl, x)
        # renumber cached SEQ field results (WPS cached Chinese error strings otherwise show)
        counters = {}
        state = {"instr": None, "in_result": False, "runs": []}
        edits = []  # (start, end, new_run_xml)
        for m in re.finditer(r"<w:r>(?:(?!</w:r>).)*</w:r>", x, re.S):
            run = m.group(0)
            fld = re.search(r'<w:fldChar w:fldCharType="(\w+)"', run)
            instr = re.search(r"<w:instrText[^>]*>([^<]*)</w:instrText>", run)
            if fld and fld.group(1) == "begin":
                state = {"instr": None, "in_result": False, "runs": []}
            elif instr is not None:
                state["instr"] = instr.group(1).strip()
            elif fld and fld.group(1) == "separate":
                state["in_result"] = True
            elif fld and fld.group(1) == "end":
                if state["instr"] and state["instr"].upper().startswith("SEQ") and state["runs"]:
                    # blank cached SEQ results: the caption number now comes from the
                    # translated static text; a live cached number would double it
                    for i, (rs, re_) in enumerate(state["runs"]):
                        rr = re.search(r"(<w:t[^>]*>)[^<]*(</w:t>)", x[rs:re_])
                        if rr:
                            newrun = (x[rs:re_][:rr.start()] + rr.group(1) + rr.group(2)
                                      + x[rs:re_][rr.end():])
                            edits.append((rs, re_, newrun))
                state = {"instr": None, "in_result": False, "runs": []}
            elif state["in_result"]:
                state["runs"].append((m.start(), m.end()))
        for rs, re_, newrun in reversed(edits):
            x = x[:rs] + newrun + x[re_:]
        # NOTE: TOC \c unwrapping was REMOVED (v2.1.4): dropping field runs changes node
        # counts and breaks the structure gate contract. Stale WPS TOC caches are handled
        # by render_pdf.ps1 updating TOC/SEQ fields at export time instead.
        return x
    _edit(path, fn)
    print("field switches sanitized:", stats.get("switch", 0), "| seq renamed:", stats.get("seq", 0),
          "| toc-c unwrapped runs:", stats.get("toc_unwrapped", 0))


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    thr = 40
    if "--threshold" in sys.argv:
        thr = int(sys.argv[sys.argv.index("--threshold") + 1])
    {"fonts": cmd_fonts, "numbering": cmd_numbering,
     "tracking": lambda p: cmd_tracking(p, thr), "justify": cmd_justify,
     "fields": cmd_fields}[cmd](path)


if __name__ == "__main__":
    main()
