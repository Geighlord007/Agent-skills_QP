# -*- coding: utf-8 -*-
"""Environment-adaptive DOCX write-back engine selection (v4.3).

Decides the DOCX write-back engine for the current machine:
  - WIR (`docx/scripts/engine/_core...linux-gnu.so`) on Linux / WSL2 whenever importable
    (first-class default on Linux per dual-machine routing policy)
  - surgical (`write_docx_surgical.py`) on native Windows / macOS when WIR is not importable

Usage:
  python engine_select.py           # prints JSON decision
  python engine_select.py --path    # prints resolved docx scripts directory path only
"""
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path


def docx_scripts_dir():
    here = Path(__file__).resolve().parent
    env_docx = os.environ.get("DOCX_SKILLS_DIR", "").strip()
    env_dsh = os.environ.get("DSH_SKILLS_DIR", "").strip()
    cands = [
        Path(env_docx) / "scripts" if env_docx else None,
        Path(env_docx) if env_docx else None,
        here.parent.parent / "docx" / "scripts",
        Path.home() / ".agents" / "skills" / "docx" / "scripts",
        Path(env_dsh) / "docx" / "scripts" if env_dsh else None,
    ]
    for c in cands:
        if c and ((c / "engine" / "__init__.py").exists() or (c / "engine_surgical" / "__init__.py").exists()):
            return c
    return None


def engine_importable(scripts_dir):
    if not scripts_dir:
        return False, "docx skill scripts dir not found"
    sd_str = str(scripts_dir)
    if sd_str not in sys.path:
        sys.path.insert(0, sd_str)
    try:
        spec = importlib.util.find_spec("engine")
        if spec is None:
            return False, "engine package not found"
        import engine  # noqa: F401
        return True, "ok"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def decide() -> dict:
    plat = platform.system()
    py = platform.python_version()
    sd = docx_scripts_dir()
    ok, why = engine_importable(sd)
    return {
        "platform": plat,
        "python": py,
        "docx_scripts": str(sd) if sd else None,
        "engine_importable": ok,
        "engine_error": None if ok else why,
        "recommended": "wir" if ok else "surgical",
    }


def main() -> int:
    if "--path" in sys.argv[1:]:
        sd = docx_scripts_dir()
        if sd:
            print(sd)
            return 0
        print("docx skill scripts dir not found", file=sys.stderr)
        return 1
    decision = decide()
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
