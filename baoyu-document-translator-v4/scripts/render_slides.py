import argparse
import sys
from pathlib import Path

import win32com.client


def main():
    ap = argparse.ArgumentParser(description="PPTX 逐页导出 JPG（PowerPoint COM）")
    ap.add_argument("pptx", help="源 PPTX")
    ap.add_argument("out_dir", help="输出目录（每页一张 slide-NN.jpg）")
    ap.add_argument("--width", type=int, default=1600, help="导出宽度像素（默认 1600）")
    ap.add_argument("--prefix", default="slide", help="文件名前缀（默认 slide）")
    args = ap.parse_args()

    pptx = Path(args.pptx).resolve()
    out = Path(args.out_dir).resolve()
    if not pptx.is_file():
        sys.exit(f"文件不存在: {pptx}")
    out.mkdir(parents=True, exist_ok=True)

    app = win32com.client.Dispatch("PowerPoint.Application")
    try:
        pres = app.Presentations.Open(str(pptx), ReadOnly=True, WithWindow=False)
        ratio = pres.PageSetup.SlideHeight / pres.PageSetup.SlideWidth
        height = int(args.width * ratio)
        count = pres.Slides.Count
        for i in range(1, count + 1):
            target = out / f"{args.prefix}-{i:02d}.jpg"
            pres.Slides(i).Export(str(target), "JPG", args.width, height)
            if not target.is_file() or target.stat().st_size == 0:
                sys.exit(f"导出失败: 第 {i} 页")
        print(f"[render_slides] 导出 {count} 页 -> {out}（宽 {args.width}）")
        pres.Close()
    finally:
        app.Quit()


if __name__ == "__main__":
    main()
