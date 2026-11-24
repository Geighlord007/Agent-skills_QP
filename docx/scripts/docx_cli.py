#!/usr/bin/env python3
"""
docx_cli.py - Cross-platform creation & validation entry point for the docx skill.
Replaces the Linux-only Bash `scripts/docx` script; works on Windows, macOS, and Linux.

Usage:
    python scripts/docx_cli.py env
    python scripts/docx_cli.py init [--work-dir DIR]
    python scripts/docx_cli.py build <output.docx> [--work-dir DIR]
    python scripts/docx_cli.py validate <file.docx>
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_WORK_DIR = Path(os.environ.get("DOCX_WORK_DIR") or (Path(tempfile.gettempdir()) / "docx-work"))

MIN_DOTNET_MAJOR = 8

ERROR_HINTS = [
    (re.compile(r"CS0246.*'Separator'"), "Use 'SeparatorMark' instead of 'Separator'"),
    (re.compile(r"CS0246.*'ContinuationSeparator'"), "Use 'ContinuationSeparatorMark'"),
    (re.compile(r"CS1009"), 'Unrecognized escape -> Use @"..." verbatim string'),
    (re.compile(r"CS1010"), 'Newline in constant -> Use @"..." for multiline'),
    (re.compile(r"CS0103.*'WordprocessingDocument'"), "Add: using DocumentFormat.OpenXml.Packaging;"),
    (re.compile(r"CS0103.*'Body'"), "Add: using DocumentFormat.OpenXml.Wordprocessing;"),
    (re.compile(r"CS0103.*'Paragraph'"), "Add: using DocumentFormat.OpenXml.Wordprocessing;"),
    (re.compile(r"CS0029.*cannot implicitly convert"), "Type mismatch: check int vs string for IDs"),
    (
        re.compile(r"CS1056.*Unexpected character"),
        'Use ASCII " for C# string delimiters, not Chinese curly quotes. Chinese text inside strings is fine as-is.',
    ),
]

CJK_RANGES = [
    (0x3000, 0x303F),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFF00, 0xFFEF),
]


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def find_dotnet() -> Optional[str]:
    """Locate the dotnet executable across Windows, macOS, and Linux."""
    found = shutil.which("dotnet")
    if found:
        return found

    home = Path.home()
    candidates = []
    if os.name == "nt":
        prog_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        candidates.extend([
            prog_files / "dotnet" / "dotnet.exe",
            home / ".dotnet" / "dotnet.exe",
        ])
    else:
        candidates.extend([
            home / ".dotnet" / "dotnet",
            Path("/usr/local/share/dotnet/dotnet"),
            Path("/usr/share/dotnet/dotnet"),
            Path("/opt/dotnet/dotnet"),
        ])

    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def check_dotnet_status() -> Tuple[str, Optional[str], Optional[str], Optional[int]]:
    """Return (state, binary_path, version_str, major_int). state in {ok, outdated, broken, missing}."""
    dotnet_bin = find_dotnet()
    if not dotnet_bin:
        return "missing", None, None, None

    try:
        proc = subprocess.run(
            [dotnet_bin, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return "broken", dotnet_bin, None, None

    if proc.returncode != 0:
        return "broken", dotnet_bin, None, None

    ver = proc.stdout.strip()
    m = re.match(r"^(\d+)\.", ver)
    if not m:
        return "broken", dotnet_bin, ver, None

    major = int(m.group(1))
    if major >= MIN_DOTNET_MAJOR:
        return "ok", dotnet_bin, ver, major
    return "outdated", dotnet_bin, ver, major


def require_dotnet() -> Tuple[str, str, int]:
    """Return (dotnet_bin, version, major) or exit with actionable install instructions."""
    state, bin_path, ver, major = check_dotnet_status()
    if state == "ok" and bin_path and ver and major is not None:
        return bin_path, ver, major

    if state == "outdated":
        print(f"[ERROR] dotnet {ver} is outdated (need .NET {MIN_DOTNET_MAJOR}+).", file=sys.stderr)
    elif state == "broken":
        print(f"[ERROR] dotnet at {bin_path} failed to run.", file=sys.stderr)
    else:
        print("[ERROR] .NET SDK not found on PATH.", file=sys.stderr)

    print("Install a supported .NET SDK (e.g. .NET 10 LTS):", file=sys.stderr)
    if os.name == "nt":
        print("  winget install Microsoft.DotNet.SDK.10", file=sys.stderr)
    else:
        print("  https://dotnet.microsoft.com/download", file=sys.stderr)
    sys.exit(1)


def _sync_csproj_tfm(csproj_path: Path, installed_major: int) -> None:
    """Align TargetFramework in workspace Docx.csproj with installed SDK major version when needed."""
    text = csproj_path.read_text(encoding="utf-8")
    m = re.search(r"<TargetFramework>net(\d+)\.0</TargetFramework>", text)
    if not m:
        return
    declared_major = int(m.group(1))
    if installed_major != declared_major and installed_major >= MIN_DOTNET_MAJOR:
        updated = re.sub(
            r"<TargetFramework>net\d+\.0</TargetFramework>",
            f"<TargetFramework>net{installed_major}.0</TargetFramework>",
            text,
            count=1,
        )
        csproj_path.write_text(updated, encoding="utf-8")


def ensure_workspace(work_dir: Path, installed_major: Optional[int] = None) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    templates_dir = SKILL_DIR / "assets" / "templates"

    csproj_dst = work_dir / "Docx.csproj"
    if not csproj_dst.exists():
        shutil.copy2(templates_dir / "Docx.csproj", csproj_dst)

    if installed_major is not None and csproj_dst.exists():
        _sync_csproj_tfm(csproj_dst, installed_major)

    program_dst = work_dir / "Program.cs"
    if not program_dst.exists():
        program_src = templates_dir / "Program.cs"
        if program_src.exists():
            shutil.copy2(program_src, program_dst)


def enhance_error(line: str) -> Optional[str]:
    for pattern, hint in ERROR_HINTS:
        if pattern.search(line):
            return hint
    return None


def check_cjk_unicode_abuse(work_dir: Path) -> None:
    """Warn if .cs files encode CJK characters as \\uXXXX escapes instead of UTF-8 literals."""
    pat = re.compile(r"\\u([0-9a-fA-F]{4})")
    total = 0
    examples = []
    for cs_file in sorted(work_dir.glob("*.cs")):
        try:
            text = cs_file.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in pat.finditer(text):
            cp = int(m.group(1), 16)
            if any(lo <= cp <= hi for lo, hi in CJK_RANGES):
                total += 1
                if len(examples) < 3:
                    start = max(0, m.start() - 20)
                    end = min(len(text), m.end() + 20)
                    examples.append(text[start:end].replace("\n", " ").strip())

    if total >= 50:
        print()
        print(f"[WARNING] Detected {total} CJK characters written as Unicode escapes (\\uXXXX).")
        print("  This causes code-point errors and garbled text.")
        print('  FIX: Write Chinese directly as UTF-8 literals. Escape ASCII quotes as \\".')
        for ex in examples:
            print(f"  Example: ...{ex}...")
        print()


def _check_module(mod_name: str) -> bool:
    try:
        __import__(mod_name)
        return True
    except ImportError:
        return False


def cmd_env(work_dir: Path) -> int:
    print("=== Dependencies ===")
    state, bin_path, ver, _ = check_dotnet_status()
    if state == "ok":
        print(f"  [OK] dotnet {ver} ({bin_path})")
    elif state == "outdated":
        print(f"  [WARN] dotnet {ver} (need {MIN_DOTNET_MAJOR}+)")
    elif state == "broken":
        print(f"  [ERR] dotnet broken ({bin_path})")
    else:
        print("  [--] dotnet not installed (required for C# creation & OpenXML schema validation)")

    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  [OK] python {py_ver} ({sys.executable})")

    # Check editing engines
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        import engine  # noqa: F401
        print("  [OK] engine (WIR native core available)")
    except ImportError:
        print("  [--] engine (WIR native core unavailable on this platform; Linux/WSL2 + Py3.12 only)")

    if _check_module("docx") and _check_module("lxml"):
        print("  [OK] engine_surgical (python-docx + lxml available)")
    else:
        print("  [--] engine_surgical (install: pip install python-docx lxml)")

    pandoc_bin = shutil.which("pandoc")
    if pandoc_bin:
        print(f"  [OK] pandoc ({pandoc_bin})")
    else:
        print("  [--] pandoc (optional, for md2docx & word count)")

    for opt_mod, desc in (("playwright", "cover backgrounds"), ("matplotlib", "complex charts")):
        if _check_module(opt_mod):
            print(f"  [OK] {opt_mod}")
        else:
            print(f"  [--] {opt_mod} (optional, for {desc})")

    print()
    print("=== Workspace ===")
    if work_dir.is_dir():
        print(f"  [OK] {work_dir}")
        if (work_dir / "Program.cs").exists():
            print("       Program.cs exists")
    else:
        print(f"  [--] {work_dir} (run 'python scripts/docx_cli.py init')")
    return 0


def cmd_init(work_dir: Path) -> int:
    print("=== Checking dependencies ===")
    dotnet_bin, ver, major = require_dotnet()
    print(f"  [OK] dotnet {ver} ({dotnet_bin})")
    print(f"  [OK] python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    print()
    print("=== Setting up workspace ===")
    ensure_workspace(work_dir, installed_major=major)
    print(f"  [OK] {work_dir}")

    print()
    print("Done!")
    print(f"  Edit:  {work_dir / 'Program.cs'}")
    print(f"  Build: python scripts/docx_cli.py build <output-path>")
    return 0


def do_validate(docx_path: Path, dotnet_bin: Optional[str] = None) -> bool:
    """Run validate_all.py (element order + business rules) and Validator.dll (OpenXML XSD)."""
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{SCRIPT_DIR}{os.pathsep}{existing_pp}" if existing_pp else str(SCRIPT_DIR)

    # 1. Python unified validator (auto-fixes element order + checks business rules)
    proc_py = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "validate_all.py"), str(docx_path)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc_py.stdout:
        print(proc_py.stdout, end="")
    if proc_py.stderr:
        print(proc_py.stderr, end="", file=sys.stderr)
    if proc_py.returncode != 0:
        return False

    # 2. OpenXML SDK schema validator (cross-platform Validator.dll via dotnet)
    validator_dll = SKILL_DIR / "validator" / "Validator.dll"
    if not validator_dll.exists():
        print(f"[WARN] Validator.dll not found at {validator_dll}; skipping XSD schema validation.")
        return True

    if dotnet_bin is None:
        state, bin_path, _, _ = check_dotnet_status()
        dotnet_bin = bin_path if state == "ok" else None

    if not dotnet_bin:
        print("[WARN] dotnet not available; skipping Validator.dll XSD schema validation.")
        return True

    proc_val = subprocess.run(
        [dotnet_bin, str(validator_dll), str(docx_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc_val.stdout:
        print(proc_val.stdout, end="")
    if proc_val.stderr:
        print(proc_val.stderr, end="", file=sys.stderr)
    return proc_val.returncode == 0


def _report_stats(output_path: Path) -> None:
    """Inspect generated .docx via Python zipfile (and optional pandoc) for delivery checks."""
    images = 0
    has_revisions = False
    has_comments = False
    try:
        with zipfile.ZipFile(output_path, "r") as zf:
            names = zf.namelist()
            images = sum(1 for n in names if n.startswith("word/media/") and not n.endswith("/"))
            has_comments = "word/comments.xml" in names
            if "word/document.xml" in names:
                doc_xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
                has_revisions = bool(re.search(r"<w:(?:ins|del)\b", doc_xml))
    except zipfile.BadZipFile:
        return

    pandoc_bin = shutil.which("pandoc")
    if pandoc_bin:
        proc = subprocess.run(
            [pandoc_bin, str(output_path), "-t", "plain"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0:
            text = proc.stdout
            chars = len(text)
            words = len(text.split())
            if images == 0:
                print(
                    f"  [WARN] {chars} chars, {words} words, 0 images"
                    " - if charts were generated, verify AddInlineImage() was called"
                )
            else:
                print(f"  [STATS] {chars} chars, {words} words, {images} images")
            print(f'  [TIP] Structure validated. Verify content with: pandoc "{output_path}" -t plain')
            if has_revisions or has_comments:
                print("        Revisions/comments detected - use --track-changes=all to verify marker positions")
            return

    print(f"  [STATS] {images} images (install pandoc for char/word counts)")


def cmd_build(output_arg: str, work_dir: Path) -> int:
    dotnet_bin, _, major = require_dotnet()
    ensure_workspace(work_dir, installed_major=major)

    output_path = Path(output_arg).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    check_cjk_unicode_abuse(work_dir)

    print(">> Compiling...")
    proc_build = subprocess.run(
        [dotnet_bin, "build", str(work_dir / "Docx.csproj"), "--verbosity", "quiet"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc_build.returncode != 0:
        print("[ERROR] Compile failed\n")
        combined = (proc_build.stdout or "") + "\n" + (proc_build.stderr or "")
        printed_any = False
        for line in combined.splitlines():
            if re.search(r"error CS\d+", line):
                print(f"  {line}")
                printed_any = True
                hint = enhance_error(line)
                if hint:
                    print(f"  -> FIX: {hint}")
        if not printed_any:
            print(combined.strip())
        return 1
    print("  [OK] Compiled")

    print(">> Running...")
    proc_run = subprocess.run(
        [dotnet_bin, "run", "--no-build", "--", str(output_path)],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc_run.stdout:
        print(proc_run.stdout, end="")
    if proc_run.stderr:
        print(proc_run.stderr, end="", file=sys.stderr)
    if proc_run.returncode != 0:
        print("[ERROR] Generation failed")
        return 1

    if not output_path.is_file():
        print(f"[ERROR] Output not found: {output_path}")
        print("  Check your Program.cs output path (args[0]).")
        return 1
    print("  [OK] Generated")

    print(">> Validating...")
    if not do_validate(output_path, dotnet_bin=dotnet_bin):
        print()
        print("[WARN] VALIDATION FAILED - Document saved but may have issues")
        print("-" * 60)
        print(f"Document saved to: {output_path}")
        print("Due to the errors above, it may not open cleanly in Word/WPS.")
        print("Check the error messages above and fix your code before delivering.")
        print("-" * 60)
        return 1

    _report_stats(output_path)
    print()
    print(f"[OK] Done: {output_path}")
    return 0


def cmd_validate(file_arg: str) -> int:
    docx_path = Path(file_arg).resolve()
    if not docx_path.is_file():
        print(f"[ERROR] File not found: {docx_path}", file=sys.stderr)
        return 1

    print(f">> Validating: {docx_path}")
    if not do_validate(docx_path):
        return 1
    print("[OK] Valid")
    return 0


def main() -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        prog="docx_cli.py",
        description="Cross-platform C# OpenXML creation & validation CLI for the docx skill.",
    )
    sub = parser.add_subparsers(dest="command")

    p_env = sub.add_parser("env", help="Show environment & dependency status")
    p_env.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)

    p_init = sub.add_parser("init", help="Setup C# workspace (Docx.csproj + Program.cs)")
    p_init.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)

    p_build = sub.add_parser("build", help="Compile, generate, auto-fix, and validate .docx")
    p_build.add_argument("output", help="Output .docx path")
    p_build.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)

    p_val = sub.add_parser("validate", help="Validate an existing .docx file")
    p_val.add_argument("file", help="Path to .docx file")

    args = parser.parse_args()
    if args.command == "env":
        return cmd_env(args.work_dir)
    if args.command == "init":
        return cmd_init(args.work_dir)
    if args.command == "build":
        return cmd_build(args.output, args.work_dir)
    if args.command == "validate":
        return cmd_validate(args.file)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
