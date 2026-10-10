# -*- coding: utf-8 -*-
"""WIR-engine write-back (v2.1.2, Linux-only in practice).

Applies translated parts to the source DOCX via the `docx` skill WIR engine
(TextEdit old->new replacements per story), preserving every non-text node.
Run `engine_select.py` first; use this script only when it reports
engine_importable=true. On any API mismatch the script prints the engine's
TextEdit signature and exits 3 so the operator can adapt on the target machine.

Usage: python write_docx_wir.py input.docx output.docx translated.json
"""
import sys, json, shutil
from pathlib import Path

def main():
    src, dst, js = sys.argv[1], sys.argv[2], sys.argv[3]
    import engine_select
    sd = engine_select.docx_scripts_dir()
    ok, why = engine_select.engine_importable(sd)
    if not ok:
        print("WIR engine not importable here (%s). Use write_docx_surgical.py." % why)
        return 2
    import inspect
    from engine import WIRSession, TextEdit, OldStringNotFoundError  # noqa
    sig = str(inspect.signature(TextEdit.__init__))
    els = {e["key"]: e for e in json.load(open(js, encoding="utf-8"))["elements"]}
    shutil.copy(src, dst)
    try:
        session = WIRSession.open(dst)
    except Exception as e:
        print("WIRSession.open failed: %r" % e)
        return 3
    applied = failed = 0
    try:
        for part in ["document"]:
            edits = []
            for e in els.values():
                if e.get("story", "body") != "body":
                    continue
                src_text = e.get("text", "")
                new_text = "".join(e.get("parts", []))
                if not src_text.strip() or src_text == new_text:
                    continue
                edits.append(TextEdit(src_text, new_text))
            try:
                session.apply(part, edits) if hasattr(session, "apply") else \
                    session.edit(part, edits)
                applied += len(edits)
            except OldStringNotFoundError as e:
                failed += 1
                print("old-string not found: %r" % e)
        session.save(dst) if hasattr(session, "save") else session.close()
    except TypeError as e:
        print("WIR API mismatch (%s). TextEdit signature: %s" % (e, sig))
        print("Adapt this wrapper on the target machine to the printed signature.")
        return 3
    print("WIR write-back applied=%d failed=%d" % (applied, failed))
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
