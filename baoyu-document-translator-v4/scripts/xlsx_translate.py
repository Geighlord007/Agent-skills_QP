# -*- coding: utf-8 -*-
"""XLSX translation without touching anything but the text (v2.2.2).

Rewrites ONLY `xl/sharedStrings.xml` text nodes and `xl/workbook.xml` sheet names, so
styles, number formats, charts, images, column widths and pivot definitions survive.
(An .xlsx is the same kind of zip+XML container as .docx; cell text lives in the shared
string table, which is why a text-level edit is enough.)

Usage:
  python xlsx_translate.py <src.xlsx> <dst.xlsx> <map.json>

map.json:
  {
    "strings":     {"<source text>": "<translated text>", ...},
    "sheet_names": {"<source sheet name>": "<translated sheet name>"}
  }

Notes / gotchas baked into this tool:
  * Excel limits sheet names to 31 characters — longer names make Excel refuse the file.
    Use "&amp;" (not a bare "&") if a translated sheet name contains an ampersand.
  * shared strings are indexed: two cells showing the same source text share one entry,
    so a translation applies to all of them.
  * the CJK scan below reports what is left before/after; images are not text and will
    keep their original language (report that to the user).
"""
import json, re, sys, zipfile

CJK = re.compile(r"[\u4e00-\u9fff]")


def scan(label, path):
    z = zipfile.ZipFile(path)
    hits = {}
    for n in z.namelist():
        if not n.endswith(".xml"):
            continue
        t = z.read(n).decode("utf-8", "ignore")
        flat = "".join(a or b for a, b in re.findall(
            r"<(?:w:)?t[^>]*>([^<]*)</(?:w:)?t>|<a:t>([^<]*)</a:t>", t))
        c = len(CJK.findall(flat))
        samples = [x for x in re.findall(r"<t[^>]*>([^<]*)</t>", t) if CJK.search(x)][:4]
        names = [x for x in re.findall(r'<sheet name="([^"]+)"', t) if CJK.search(x)]
        if c or names:
            hits[n] = (c, samples + ["sheet:" + x for x in names])
    print("[%s] CJK remaining: %s" % (label, hits or "none"))
    return hits


def patch_shared_strings(xml, mapping):
    out, pos, seen = [], 0, 0
    for m in re.finditer(r"<si>(.*?)</si>", xml, re.S):
        body = m.group(1)
        tm = re.search(r"(<t[^>]*>)([^<]*)(</t>)", body)
        new_body = body
        if tm and tm.group(2) in mapping:
            new_body = body[:tm.start(2)] + mapping[tm.group(2)] + body[tm.end(2):]
        out.append(xml[pos:m.start()])
        out.append("<si>" + new_body + "</si>")
        pos = m.end()
        seen += 1
    out.append(xml[pos:])
    return "".join(out), seen


def main():
    src, dst, mapf = sys.argv[1], sys.argv[2], sys.argv[3]
    M = json.load(open(mapf, encoding="utf-8"))
    s_map, n_map = M.get("strings", {}), M.get("sheet_names", {})
    scan("before", src)

    with zipfile.ZipFile(src) as zin:
        items = zin.infolist()
        data = {i.filename: zin.read(i.filename) for i in items}

    n_str = 0
    for name in list(data):
        if name == "xl/sharedStrings.xml":
            xml, n_str = patch_shared_strings(data[name].decode("utf-8"), s_map)
            data[name] = xml.encode("utf-8")
        elif name == "xl/workbook.xml":
            xml = data[name].decode("utf-8")
            for cn, en in n_map.items():
                xml = xml.replace('name="%s"' % cn, 'name="%s"' % en)
            data[name] = xml.encode("utf-8")

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for i in items:
            zi = zipfile.ZipInfo(i.filename, date_time=i.date_time)
            zi.compress_type = i.compress_type
            zi.external_attr = i.external_attr
            zout.writestr(zi, data[i.filename])

    print("shared strings patched: %d | sheet names mapped: %d" % (n_str, len(n_map)))
    scan("after", dst)

    z = zipfile.ZipFile(dst)
    print("strings  :", re.findall(r"<t[^>]*>([^<]*)</t>", z.read("xl/sharedStrings.xml").decode("utf-8")))
    print("sheets   :", re.findall(r'<sheet name="([^"]+)"', z.read("xl/workbook.xml").decode("utf-8")))
    for nm in [n for n in z.namelist() if n.endswith((".xml", ".rels"))]:
        try:
            from lxml import etree
            etree.fromstring(z.read(nm))
        except ImportError:
            break
        except Exception as e:
            print("!! XML INVALID:", nm, e)


if __name__ == "__main__":
    main()
