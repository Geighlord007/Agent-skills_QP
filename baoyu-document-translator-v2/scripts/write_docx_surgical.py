# -*- coding: utf-8 -*-
"""Surgical DOCX write-back — thin shim (v2.2, engine relocated).

引擎内核已迁至 docx 技能的 scripts/engine_surgical/(单一属主,本包不持副本);
本脚本只负责翻译流水线的 CLI 适配:translated.json -> key->parts -> 引擎写回。

历史(v2.1 内核)要点,细节见 engine_surgical 模块 docstring:
- 只动 <w:t> 文字节点,保留 w:br/w:ptab/w:fldChar/w:instrText/w:drawing 等;
- key 寻址与 extract_docx_v2.py 精确配对(修改 extract 枚举必须同步引擎);
- 覆盖 body/tables/headers/footers/textboxes/sdt/footnotes/endnotes。

用法:python write_docx_surgical.py input.docx output.docx translated.json [--consolidate-max N]
"""
import sys
import json


def _docx_scripts_dir():
    # 与 engine_select.py 同一套定位策略;此处独立实现以避免执行其 main()
    from pathlib import Path
    import os
    here = Path(__file__).resolve().parent
    cands = [
        here.parent.parent / "docx" / "scripts",
        Path.home() / ".agents" / "skills" / "docx" / "scripts",
        Path(os.environ.get("DSH_SKILLS_DIR", "")) / "docx" / "scripts" if os.environ.get("DSH_SKILLS_DIR") else None,
        Path("/root/agent-skills/skills/docx/scripts"),
    ]
    for c in cands:
        if c and (c / "engine_surgical" / "__init__.py").exists():
            return c
    return None


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    src, dst, js = sys.argv[1], sys.argv[2], sys.argv[3]
    cons_max = 80
    if "--consolidate-max" in sys.argv:
        cons_max = int(sys.argv[sys.argv.index("--consolidate-max") + 1])

    sd = _docx_scripts_dir()
    if sd is None:
        print("engine_surgical not found: docx skill scripts dir not located. "
              "Install/locate the docx skill first.")
        return 2
    sys.path.insert(0, str(sd))
    from engine_surgical import apply_keyed_parts

    els = {e["key"]: e for e in json.load(open(js, encoding="utf-8"))["elements"]}
    apply_keyed_parts(src, dst, els, consolidate_max=cons_max)
    return 0


if __name__ == "__main__":
    sys.exit(main())
