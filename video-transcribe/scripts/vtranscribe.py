#!/usr/bin/env python3
"""VideoTranscribe 命令行：视频链接/音频 → 转写 → 帧分析 → 邮件。

用法：
  python vtranscribe.py url <视频链接> [--analyze] [--no-email]
  python vtranscribe.py audio <音频文件> [--no-diarize] [--no-email]
  python vtranscribe.py analyze <图片...> [--prompt "提示词"]
  python vtranscribe.py understand <本地视频> [--mode auto|whole|frames] [--prompt "提示词"]
  python vtranscribe.py email-test
  python vtranscribe.py status
  python vtranscribe.py config

URL 模式支持 B站/YouTube/抖音等 yt-dlp 可下载的站点；不播放、不打开页面也能转写。
understand 用 qwen3.8 整段直传（≤2h/≤2GB）或场景抽帧帧列表精控，无需先转写。
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402


def wait_job(jm, jid):
    last = -1
    while True:
        job = jm.get(jid)
        for line in (job.get("log") or [])[last + 1:]:
            print("  " + line)
        last = len(job.get("log") or []) - 1
        if job["status"] in ("done", "failed", "interrupted", "canceled"):
            return job
        time.sleep(3)


def show_result(job):
    if job["status"] != "done":
        print(f"\n❌ 任务失败: {job.get('error')}", file=sys.stderr)
        sys.exit(1)
    r = job.get("result") or {}
    print("\n✅ 完成")
    for f in r.get("files", []):
        print("  " + f)
    if r.get("harvest"):
        h = r["harvest"]
        print(f"  🖼 收集素材 {h['count']} 条（{h['frames']} 个镜头）→ {h['assets_dir']}")
        print(f"     素材索引: {h['index_md']}")
    em = r.get("email") or {}
    if em.get("sent"):
        print(f"  📧 已发送邮箱: {em.get('to')}")
    elif em.get("reason"):
        print(f"  ⚠ 未发邮件: {em.get('reason')}")
    md = r.get("md") or (r.get("files") or [""])[0]
    if md and Path(md).exists():
        text = Path(md).read_text(encoding="utf-8")
        lines = text.splitlines()
        print("\n―― 转写稿概要 ――")
        print("\n".join(lines[:14]))
        if len(lines) > 14:
            print(f"  …（共 {len(lines)} 行，完整内容见文件）")


def main():
    ap = argparse.ArgumentParser(description="VideoTranscribe 视频转写命令行")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_url = sub.add_parser("url", help="转写视频链接（B站/YouTube/抖音等）")
    p_url.add_argument("link")
    p_url.add_argument("--analyze", action="store_true", help="转写 + 素材收集一起做")
    p_url.add_argument("--assets", action="store_true",
                       help="只做素材收集：镜头切分抽帧→检测 logo/截图/图表→抠图归档（需 ffmpeg）")
    p_url.add_argument("--frame-count", type=int, default=None, help="素材收集抽帧上限")
    p_url.add_argument("--no-email", action="store_true")
    p_url.add_argument("--no-diarize", action="store_true")

    p_audio = sub.add_parser("audio", help="转写本地音频文件")
    p_audio.add_argument("file")
    p_audio.add_argument("--no-diarize", action="store_true")
    p_audio.add_argument("--no-email", action="store_true")
    p_audio.add_argument("--language-hints", default=None, help="如 zh,en")

    p_anl = sub.add_parser("analyze", help="用视觉模型分析图片（截图/帧）")
    p_anl.add_argument("images", nargs="+")
    p_anl.add_argument("--prompt", default=None, help="自定义分析提示词")
    p_anl.add_argument("--transcript", default=None, help="关联的转写稿 md 路径")
    p_anl.add_argument("-o", "--out", default=None, help="报告输出路径")

    p_vu = sub.add_parser("understand", help="整段/抽帧理解一个本地视频（qwen3.8，无需先转写）")
    p_vu.add_argument("video")
    p_vu.add_argument("--prompt", default=None, help="分析提示词")
    p_vu.add_argument("--mode", choices=["auto", "whole", "frames"], default="auto",
                      help="auto=整段直传 whole=强制整段 frames=场景抽帧+帧列表精控")
    p_vu.add_argument("--model", default=None, help="默认 video_understand_model（qwen3.8-flash）")
    p_vu.add_argument("--fps", type=float, default=None, help="整段采样频率或帧列表注解")
    p_vu.add_argument("--max-frames", type=int, default=None, help="frames 模式抽帧上限")
    p_vu.add_argument("-o", "--out", default=None, help="报告输出路径")

    sub.add_parser("email-test", help="发送测试邮件")
    sub.add_parser("status", help="显示服务/配置状态")
    sub.add_parser("config", help="打印掩码后的配置")

    args = ap.parse_args()
    cfg = engine.load_config()
    engine.set_logfile(engine.workdir(cfg) / "cli.log")

    if args.cmd == "status":
        print(json.dumps(engine.status_report(cfg), ensure_ascii=False, indent=2))
        return
    if args.cmd == "config":
        print(json.dumps(engine.masked_config(cfg), ensure_ascii=False, indent=2))
        return
    if args.cmd == "email-test":
        to = engine.send_email(cfg, "【视频转写】测试邮件 ✅",
                               "这是 VideoTranscribe 的测试邮件，收到即代表 SMTP 配置成功。")
        print(f"✅ 已发送到 {to}")
        return

    if args.cmd == "analyze":
        imgs = [Path(p) for p in args.images]
        for p in imgs:
            if not p.is_file():
                sys.exit(f"图片不存在: {p}")
        transcript = None
        if args.transcript:
            transcript = Path(args.transcript).read_text(encoding="utf-8")
        report, _ = engine.analyze_frames_files(cfg, imgs, transcript, prompt=args.prompt)
        out = Path(args.out) if args.out else engine.workdir(cfg) / "out" / f"分析_{time.strftime('%m%d_%H%M%S')}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"# 画面分析报告\n\n- 图片数：{len(imgs)}\n- 模型：{cfg['vlm_model']}\n\n---\n\n{report}",
                       encoding="utf-8")
        print(f"✅ 报告已保存: {out}")
        print("\n" + report[:1500])
        return

    if args.cmd == "understand":
        video = Path(args.video).expanduser().resolve()
        if not video.is_file():
            sys.exit(f"视频不存在: {video}")
        prompt = args.prompt or "用中文总结这个视频：内容类型、主要事件、出现的关键画面及其时间点。"
        text = engine.video_understand(cfg, video, prompt, mode=args.mode,
                                       model=args.model, fps=args.fps,
                                       max_frames=args.max_frames)
        model_used = args.model or cfg.get("video_understand_model", "qwen3.8-flash")
        out = Path(args.out) if args.out else engine.workdir(cfg) / "out" / f"视频理解_{time.strftime('%m%d_%H%M%S')}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"# 视频理解报告\n\n- 视频：{video.name}\n- 模式：{args.mode} · 模型：{model_used}\n\n---\n\n{text}",
                       encoding="utf-8")
        print(f"✅ 报告已保存: {out}")
        print("\n" + text[:2000])
        return

    jm = engine.JobManager(cfg, echo_console=False)
    if args.cmd == "url":
        if not engine.find_ytdlp():
            sys.exit("未找到 yt-dlp：pip install -U yt-dlp")
        print(f"提交 URL 任务: {args.link}")
        mode = "assets" if args.assets else ("both" if args.analyze else "transcribe")
        job = jm.create("url", url=args.link, title=args.link,
                        options={"mode": mode,
                                 "max_frames": args.frame_count,
                                 "diarize": not args.no_diarize,
                                 "email": not args.no_email})
    else:  # audio
        path = Path(args.file).expanduser().resolve()
        if not path.is_file():
            sys.exit(f"文件不存在: {path}")
        print(f"提交音频转写: {path.name}")
        job = jm.create("audio", title=path.stem,
                        options={"path": str(path), "diarize": not args.no_diarize,
                                 "language_hints": ([x.strip() for x in args.language_hints.split(",")] if args.language_hints else None),
                                 "email": not args.no_email})

    print(f"任务 {job['id']} 启动…")
    done = wait_job(jm, job["id"])
    show_result(done)


if __name__ == "__main__":
    main()
