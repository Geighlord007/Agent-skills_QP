#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Replace an embedded figure inside a .docx, in place.

The document already has a relationship and a drawing pointing at a media part. So the
safest possible replacement is to overwrite that part's BYTES and fix the display extent —
no run rebuilding, no risk of losing the anchor, the caption or the surrounding text.

    from replace_figure import replace_figure
    replace_figure(docx_path, "71abd55c032d28a6", "new_figure.png")

The extent is rescaled to the new aspect ratio at the ORIGINAL display width, so a tall
schematic does not get stretched to a wide one.

CLI:
    python _tools/replace_figure.py <docx> <sha16> <new_image.png> [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import zipfile

from PIL import Image

REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def find_media_part(docx: str, key: str) -> str | None:
    """Which word/media/... part to replace.

    `key` is EITHER a sha256 prefix of the part's current bytes, OR a part name such as
    "image4.png" / "word/media/image4.png".

    Part names matter for a SECOND pass: the first swap replaces the bytes, so the original
    hash no longer exists and a hash lookup fails. Two redraw workstreams hit this and each
    wrote their own workaround; the capability belongs here.
    """
    with zipfile.ZipFile(docx) as z:
        names = [n for n in z.namelist() if n.startswith("word/media/")]
        k = key.strip().lstrip("/")
        if not re.fullmatch(r"[0-9a-fA-F]{6,64}", k):          # looks like a part name
            cand = k if k.startswith("word/") else "word/media/" + os.path.basename(k)
            return cand if cand in names else None
        for n in names:                                         # looks like a hash
            if hashlib.sha256(z.read(n)).hexdigest().startswith(k.lower()):
                return n
    return None


def rel_ids_for(docx: str, part: str) -> list[str]:
    """rIds whose rels target is this media part."""
    target = part.split("word/", 1)[-1]
    ids = []
    with zipfile.ZipFile(docx) as z:
        name = "word/_rels/document.xml.rels"
        if name not in z.namelist():
            return ids
        xml = z.read(name).decode("utf-8", "replace")
    for m in re.finditer(r'<Relationship\b[^>]*/>', xml):
        tag = m.group(0)
        i = re.search(r'Id="([^"]+)"', tag)
        t = re.search(r'Target="([^"]+)"', tag)
        if i and t and t.group(1).lstrip("/").endswith(target):
            ids.append(i.group(1))
    return ids


def rescale_extents(xml: str, rids: list[str], new_w: int, new_h: int,
                    max_width_emu: int = 5_800_000) -> tuple[str, int]:
    """Rescale every drawing that references these rIds to the new aspect ratio."""
    new_h = max(1, new_h)
    new_w = max(1, new_w)
    changed = 0
    for rid in rids:
        # locate each blip with this embed id, then walk up to its <wp:extent .../>
        for m in re.finditer(r'<a:blip[^>]*r:embed="%s"' % re.escape(rid), xml):
            start = xml.rfind("<w:drawing", 0, m.start())
            if start == -1:
                continue
            end = xml.find("</w:drawing>", m.start())
            if end == -1:
                continue
            end += len("</w:drawing>")
            block = xml[start:end]
            ext = re.search(r'<wp:extent\s+cx="(\d+)"\s+cy="(\d+)"\s*/>', block)
            if not ext:
                continue
            cx = int(ext.group(1))
            cy = int(cx * new_h / new_w)
            if cy > 8_000_000:                      # never taller than a page
                cy = 8_000_000
                cx = int(cy * new_w / new_h)
            if cx > max_width_emu:                  # never wider than the text column,
                cx = max_width_emu                  # or Word clips it at the page edge
                cy = int(cx * new_h / new_w)
            newblock = re.sub(
                r'<wp:extent\s+cx="\d+"\s+cy="\d+"\s*/>',
                f'<wp:extent cx="{cx}" cy="{cy}"/>', block, count=1)
            # the inner a:ext must match
            newblock = re.sub(
                r'<a:ext\s+cx="\d+"\s+cy="\d+"\s*/>',
                f'<a:ext cx="{cx}" cy="{cy}"/>', newblock)
            xml = xml[:start] + newblock + xml[end:]
            changed += 1
    return xml, changed


def replace_figure(docx: str, sha16: str, new_image: str, dry_run: bool = False) -> dict:
    part = find_media_part(docx, sha16)
    if not part:
        return {"ok": False, "reason": f"no embedded image matching {key!r} "\
                                       f"(tried both a hash and a part name)"}
    rids = rel_ids_for(docx, part)
    if not rids:
        return {"ok": False, "reason": f"{part} has no relationship in document.xml.rels"}

    with Image.open(new_image) as im:
        nw, nh = im.size

    with zipfile.ZipFile(docx) as z:
        probe = z.read("word/document.xml").decode("utf-8")
    _, probe_changed = rescale_extents(probe, rids, nw, nh)
    result = {"ok": True, "docx": docx, "part": part, "rids": rids,
              "new_size": f"{nw}x{nh}", "extents_updated": probe_changed}
    if dry_run:
        return result

    tmp = docx + ".tmp_swap"
    shutil.copy2(docx, tmp)
    try:
        with zipfile.ZipFile(tmp) as zin:
            items = {n: zin.read(n) for n in zin.namelist()}
        # 1. swap the image bytes. Word keys off the part NAME, so the bytes must match its
        #    format: replacing a .jpeg part with PNG bytes renders as a blank box.
        with open(new_image, "rb") as fh:
            payload = fh.read()
        want_jpeg = part.lower().endswith((".jpeg", ".jpg"))
        is_jpeg = payload[:3] == b"\xff\xd8\xff"
        if want_jpeg and not is_jpeg:
            import io as _io
            from PIL import Image as _Image
            with _Image.open(_io.BytesIO(payload)) as im:
                buf = _io.BytesIO()
                im.convert("RGB").save(buf, format="JPEG", quality=95)
            payload = buf.getvalue()
            result["converted"] = "png->jpeg"
        elif is_jpeg and not want_jpeg:
            import io as _io
            from PIL import Image as _Image
            with _Image.open(_io.BytesIO(payload)) as im:
                buf = _io.BytesIO()
                im.convert("RGBA").save(buf, format="PNG")
            payload = buf.getvalue()
            result["converted"] = "jpeg->png"
        items[part] = payload
        # 2. fix the display extent so the new aspect ratio is respected
        doc_xml = items["word/document.xml"].decode("utf-8")
        doc_xml, changed = rescale_extents(doc_xml, rids, nw, nh)
        items["word/document.xml"] = doc_xml.encode("utf-8")
        result["extents_updated"] = changed
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for n, data in items.items():
                zout.writestr(n, data)
        os.replace(tmp, docx)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("key", help="sha256 prefix OR media part name, e.g. image4.png")
    ap.add_argument("image")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    r = replace_figure(a.docx, a.key, a.image, a.dry_run)
    print(r)
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
