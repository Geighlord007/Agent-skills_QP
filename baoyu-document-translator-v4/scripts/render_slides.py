# -*- coding: utf-8 -*-
"""PPTX 逐页导出 JPG。

Windows 优先使用 PowerPoint COM；非 Windows 或未安装 PowerPoint/pywin32 时，
自动回退到 LibreOffice（soffice）转 PDF + PyMuPDF 逐页渲染。
"""
import argparse
import io
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")


def render_via_powerpoint_com(pptx: Path, out: Path, width: int, prefix: str) -> int:
    import win32com.client  # type: ignore

    app = win32com.client.Dispatch("PowerPoint.Application")
    pres = None
    try:
        pres = app.Presentations.Open(str(pptx), ReadOnly=True, WithWindow=False)
        ratio = pres.PageSetup.SlideHeight / pres.PageSetup.SlideWidth
        height = int(width * ratio)
        count = pres.Slides.Count
        for i in range(1, count + 1):
            target = out / f"{prefix}-{i:02d}.jpg"
            pres.Slides(i).Export(str(target), "JPG", width, height)
            if not target.is_file() or target.stat().st_size == 0:
                sys.exit(f"导出失败: 第 {i} 页")
        return count
    finally:
        if pres is not None:
            pres.Close()
        app.Quit()


def render_via_libreoffice(pptx: Path, out: Path, width: int, prefix: str) -> int:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit(
            "无法渲染 PPTX：PowerPoint COM 不可用，且未找到 LibreOffice（soffice / libreoffice）。"
        )
    try:
        import fitz  # PyMuPDF
    except ImportError:
        sys.exit("LibreOffice 回退路径需要 PyMuPDF，请先运行: pip install PyMuPDF")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(pptx)],
            check=True,
        )
        pdf_path = tmp / f"{pptx.stem}.pdf"
        if not pdf_path.is_file():
            sys.exit(f"LibreOffice 未产出 PDF: {pdf_path}")
        doc = fitz.open(str(pdf_path))
        try:
            count = len(doc)
            for i, page in enumerate(doc, start=1):
                scale = width / max(page.rect.width, 1.0)
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                target = out / f"{prefix}-{i:02d}.jpg"
                pix.save(str(target))
                if not target.is_file() or target.stat().st_size == 0:
                    sys.exit(f"导出失败: 第 {i} 页")
            return count
        finally:
            doc.close()


def main():
    ap = argparse.ArgumentParser(description="PPTX 逐页导出 JPG（PowerPoint COM / LibreOffice 回退）")
    ap.add_argument("pptx", help="源 PPTX")
    ap.add_argument("out_dir", help="输出目录（每页一张 slide-NN.jpg）")
    ap.add_argument("--width", type=int, default=1600, help="导出宽度像素（默认 1600）")
    ap.add_argument("--prefix", default="slide", help="文件名前缀（默认 slide）")
    ap.add_argument(
        "--backend",
        choices=["auto", "com", "libreoffice"],
        default="auto",
        help="渲染后端（默认 auto：Windows 优先 COM，失败或非 Windows 回退 LibreOffice）",
    )
    args = ap.parse_args()

    pptx = Path(args.pptx).resolve()
    out = Path(args.out_dir).resolve()
    if not pptx.is_file():
        sys.exit(f"文件不存在: {pptx}")
    out.mkdir(parents=True, exist_ok=True)

    backend_used = None
    count = 0
    if args.backend in ("auto", "com") and sys.platform == "win32":
        try:
            count = render_via_powerpoint_com(pptx, out, args.width, args.prefix)
            backend_used = "PowerPoint COM"
        except Exception as e:
            if args.backend == "com":
                sys.exit(f"PowerPoint COM 渲染失败: {type(e).__name__}: {e}")
            print(f"[render_slides] PowerPoint COM 不可用（{type(e).__name__}: {e}），回退 LibreOffice", flush=True)

    if backend_used is None:
        count = render_via_libreoffice(pptx, out, args.width, args.prefix)
        backend_used = "LibreOffice + PyMuPDF"

    print(f"[render_slides] 导出 {count} 页 -> {out}（宽 {args.width}，后端: {backend_used}）")


if __name__ == "__main__":
    main()
