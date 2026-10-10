# -*- coding: utf-8 -*-
"""Environment-adaptive engine selection (v2.1.2).

Decides the write-back engine for the current machine:
  - WIR (docx skill engine) when the native extension actually imports (Linux build
    shipped as cpython-312-x86_64-linux-gnu.so; importable on matching Linux only)
  - surgical (write_docx_surgical.py) otherwise (Windows/macOS/missing engine)

Usage: python engine_select.py            -> prints JSON decision
       python engine_select.py --path     -> also prints resolved docx scripts dir
"""
import sys, os, json, platform, importlib.util
from pathlib import Path

def docx_scripts_dir():
    here = Path(__file__).resolve().parent
    cands = [
        here.parent.parent / "docx" / "scripts",          # sibling skill
        Path.home() / ".agents" / "skills" / "docx" / "scripts",
        Path(os.environ.get("DSH_SKILLS_DIR", "")) / "docx" / "scripts" if os.environ.get("DSH_SKILLS_DIR") else None,
        Path("/root/agent-skills/skills/docx/scripts"),
    ]
    for c in cands:
        if c and (c / "engine" / "__init__.py").exists():
            return c
    return None

def engine_importable(scripts_dir):
    if not scripts_dir:
        return False, "docx skill scripts dir not found"
    sys.path.insert(0, str(scripts_dir))
    try:
        spec = importlib.util.find_spec("engine")
        if spec is None:
            return False, "engine package not found"
        import engine  # noqa: F401  (triggers _core native import)
        return True, "ok"
    except Exception as e:  # ModuleNotFoundError on wrong platform/ABI
        return False, "%s: %s" % (type(e).__name__, e)

def main():
    plat = platform.system()
    py = platform.python_version()
    sd = docx_scripts_dir()
    ok, why = engine_importable(sd)
    decision = {
        "platform": plat,
        "python": py,
        "docx_scripts": str(sd) if sd else None,
        "engine_importable": ok,
        "engine_error": None if ok else why,
        "recommended": "wir" if ok else "surgical",
    }
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if ok or plat != "Linux" else 0

if __name__ == "__main__":
    sys.exit(main())
