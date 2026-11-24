# -*- coding: utf-8 -*-
"""合一写回器 v4.3：DOCX（Linux/WSL2 强制优先 WIR .so，其余平台 surgical）与 PPTX（含组合形状、表格、备注）。

用法: python write_v3.py input.docx|input.pptx output translated.json [--engine auto|wir|surgical]
"""
import importlib
import io
import json
import sys
from pathlib import Path

from pptx import Presentation

if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")

SCRIPTS = Path(__file__).resolve().parent


def resolve_shape(shapes, path):
    sh = shapes[path[0]]
    for idx in path[1:]:
        sh = sh.shapes[idx]
    return sh


def set_runs_in_text_frame(text_frame, parts):
    run_map = [
        (pi, ri)
        for pi, para in enumerate(text_frame.paragraphs)
        for ri, _ in enumerate(para.runs)
    ]
    if len(run_map) != len(parts):
        raise ValueError(f"run 数量 {len(run_map)} 与 parts 数量 {len(parts)} 不一致")
    for pi, ri in run_map:
        text_frame.paragraphs[pi].runs[ri].text = ""
    for i, (pi, ri) in enumerate(run_map):
        text_frame.paragraphs[pi].runs[ri].text = parts[i]


def write_pptx(input_path: Path, output_path: Path, data: dict):
    prs = Presentation(str(input_path))
    written = 0
    for elem in data["elements"]:
        key, parts = elem["key"], elem.get("parts", [])
        if key.startswith("s_"):
            segs = key.split("_")[1:]
            sh = resolve_shape(prs.slides[int(segs[0])].shapes, [int(x) for x in segs[1:]])
            if not sh.has_text_frame:
                raise ValueError(f"{key}：形状没有文本框")
            set_runs_in_text_frame(sh.text_frame, parts)
        elif key.startswith("t_"):
            segs = key.split("_")[1:]
            slide_idx = int(segs[0])
            row, col = int(segs[-2]), int(segs[-1])
            sh = resolve_shape(prs.slides[slide_idx].shapes, [int(x) for x in segs[1:-2]])
            set_runs_in_text_frame(sh.table.cell(row, col).text_frame, parts)
        elif key.startswith("n_"):
            _, slide_idx, para_idx = key.split("_")
            para = prs.slides[int(slide_idx)].notes_slide.notes_text_frame.paragraphs[int(para_idx)]
            if len(para.runs) != len(parts):
                raise ValueError(f"{key}：run 数量与 parts 数量不一致")
            for r in para.runs:
                r.text = ""
            for r, p in zip(para.runs, parts):
                r.text = p
        else:
            raise ValueError(f"无法识别的 key: {key}")
        written += 1
    prs.save(str(output_path))
    print(f"PPTX 写回 {written} 个元素 -> {output_path}")


def write_docx(input_path: Path, output_path: Path, json_path: Path, engine_mode: str = "auto"):
    scripts_str = str(SCRIPTS)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)

    import engine_select

    if engine_mode == "auto":
        decision = engine_select.decide()
        engine = decision["recommended"]
    elif engine_mode in ("wir", "surgical"):
        engine = engine_mode
    else:
        raise ValueError(f"未知写回引擎: {engine_mode}（仅支持 auto|wir|surgical）")

    mod_name = "write_docx_wir" if engine == "wir" else "write_docx_surgical"
    print(f"DOCX 写回引擎: {engine}（{mod_name}.py）")

    writer_mod = importlib.import_module(mod_name)
    saved_argv = sys.argv[:]
    try:
        sys.argv = [
            str(SCRIPTS / f"{mod_name}.py"),
            str(input_path),
            str(output_path),
            str(json_path),
        ]
        rc = writer_mod.main()
    finally:
        sys.argv = saved_argv

    if rc not in (None, 0):
        raise SystemExit(rc)


def run_write(src: Path, dst: Path, js: Path, engine_mode: str = "auto"):
    suffix = src.suffix.lower()
    if suffix == ".pptx":
        data = json.loads(js.read_text(encoding="utf-8"))
        write_pptx(src, dst, data)
    elif suffix == ".docx":
        write_docx(src, dst, js, engine_mode=engine_mode)
    else:
        raise SystemExit(f"不支持的文件类型: {src.suffix}（仅 .docx / .pptx）")


def main():
    args = sys.argv[1:]
    engine_mode = "auto"
    if "--engine" in args:
        idx = args.index("--engine")
        engine_mode = args[idx + 1]
        args = args[:idx] + args[idx + 2:]
    if len(args) < 3:
        raise SystemExit("用法: python write_v3.py input.docx|input.pptx output translated.json [--engine auto|wir|surgical]")
    run_write(Path(args[0]), Path(args[1]), Path(args[2]), engine_mode=engine_mode)


if __name__ == "__main__":
    main()
