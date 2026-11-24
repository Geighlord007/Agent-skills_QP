#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zerox_adapter.py — Thin adapter to invoke local zerox-thinkcell-charts as Tier-1 backend.

Keeps zerox-thinkcell-charts OUT of git-synced skills (no duplicate skill registration or
trigger collision). Locates zerox via ZEROX_DIR env var, vendor/zerox-thinkcell, or
the default Desktop checkout, then runs tc_advise / tc_validate / tc_render cleanly.

Usage:
  python scripts/zerox_adapter.py status
  python scripts/zerox_adapter.py advise data.csv [--intent "..."] -o draft.json
  python scripts/zerox_adapter.py validate spec.json
  python scripts/zerox_adapter.py render spec.json -o out.pptx [--html out.html] [--png out_png/] [--theme consulting_navy]
"""
import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent

if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")


def find_zerox_dir() -> Path | None:
    env_p = os.environ.get("ZEROX_DIR", "").strip()
    cands = [
        Path(env_p) if env_p else None,
        SKILL_ROOT / "vendor" / "zerox-thinkcell",
        Path.home() / "Desktop" / "zerox-skills-main" / "zerox-skills-main" / "zerox-thinkcell-charts",
    ]
    for c in cands:
        if c and (c / "scripts" / "tc_render.py").exists():
            return c
    return None


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = sys.argv[1]
    zdir = find_zerox_dir()
    if cmd == "status":
        if zdir:
            print(f"[OK] zerox-thinkcell backend located at: {zdir}")
            return 0
        print("[MISSING] zerox-thinkcell not found. Set ZEROX_DIR or place it under vendor/zerox-thinkcell/.", file=sys.stderr)
        return 1

    if not zdir:
        print("zerox-thinkcell backend unavailable; fall back to Tier-2 native SVG or Tier-3 composed SVG.", file=sys.stderr)
        return 2

    script_map = {
        "advise": "tc_advise.py",
        "validate": "tc_validate.py",
        "render": "tc_render.py",
    }
    if cmd not in script_map:
        print(f"Unknown zerox_adapter subcommand: {cmd} (choose status|advise|validate|render)", file=sys.stderr)
        return 2

    # Prefer zerox's own venv python if present, else current python
    py = sys.executable
    for vp in (zdir / ".venv" / "Scripts" / "python.exe", zdir / ".venv" / "bin" / "python"):
        if vp.exists():
            py = str(vp)
            break

    target = zdir / "scripts" / script_map[cmd]
    res = subprocess.run([py, str(target)] + sys.argv[2:])
    return res.returncode


if __name__ == "__main__":
    sys.exit(main())
