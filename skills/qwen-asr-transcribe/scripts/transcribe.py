#!/usr/bin/env python3
"""会议/长音频转写：阿里云百炼 qwen-audio-3.0-asr-flash-filetrans + OSS 签名 URL。

流程：上传音频到 OSS → 生成签名 URL → 提交异步转写任务（说话人分离）→
轮询任务 → 下载结果 JSON → 生成 Markdown 纪要 + SRT 字幕。

配置（环境变量优先，缺省读 ~/.config/qwen-asr/env，格式 KEY=VALUE）：
  DASHSCOPE_API_KEY        百炼 API Key（sk-... 或 sk-ws-...）
  DASHSCOPE_WORKSPACE_ID   可选，工作空间 ID（如 llm-xxxx）；不填走默认端点
  OSS_ACCESS_KEY_ID        阿里云 AccessKey ID
  OSS_ACCESS_KEY_SECRET    阿里云 AccessKey Secret
  OSS_BUCKET               OSS bucket 名
  OSS_ENDPOINT             可选，默认 https://oss-cn-beijing.aliyuncs.com
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import uuid
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "qwen-asr" / "env"
REQUIRED = ("DASHSCOPE_API_KEY", "OSS_ACCESS_KEY_ID", "OSS_ACCESS_KEY_SECRET", "OSS_BUCKET")


def load_config():
    cfg = {}
    if CONFIG_PATH.exists():
        for line in CONFIG_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    for k in list(REQUIRED) + ["DASHSCOPE_WORKSPACE_ID", "OSS_ENDPOINT"]:
        if os.getenv(k):
            cfg[k] = os.environ[k]
    missing = [k for k in REQUIRED if not cfg.get(k)]
    if missing:
        sys.exit(
            f"缺少配置: {', '.join(missing)}\n"
            f"请设置环境变量，或写入 {CONFIG_PATH}（每行 KEY=VALUE）。"
        )
    cfg.setdefault("OSS_ENDPOINT", "https://oss-cn-beijing.aliyuncs.com")
    return cfg


def api_base(cfg):
    ws = cfg.get("DASHSCOPE_WORKSPACE_ID")
    if ws:
        return f"https://{ws}.cn-beijing.maas.aliyuncs.com/api/v1"
    return "https://dashscope.aliyuncs.com/api/v1"


def http_json(url, api_key=None, payload=None, async_submit=False):
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if async_submit:
        headers["X-DashScope-Async"] = "enable"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def upload_and_sign(cfg, audio_path):
    import oss2  # pip install --user oss2

    auth = oss2.Auth(cfg["OSS_ACCESS_KEY_ID"], cfg["OSS_ACCESS_KEY_SECRET"])
    bucket = oss2.Bucket(auth, cfg["OSS_ENDPOINT"], cfg["OSS_BUCKET"])
    key = f"asr/{uuid.uuid4().hex[:12]}{audio_path.suffix.lower()}"
    print(f"[1/4] 上传 {audio_path.name} → oss://{cfg['OSS_BUCKET']}/{key}", flush=True)
    oss2.resumable_upload(bucket, key, str(audio_path), num_threads=4)
    url = bucket.sign_url("GET", key, 7200, slash_safe=True)
    # 用 GET Range 验证公网可访问（HEAD 与 GET 签名不通用，会误判 403）
    req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status not in (200, 206):
            sys.exit(f"签名 URL 校验失败: HTTP {r.status}")
    return url


def submit_task(cfg, file_url, diarize, language_hints):
    payload = {
        "model": "qwen-audio-3.0-asr-flash-filetrans",
        "input": {"file_urls": [file_url]},
        "parameters": {
            "channel_id": [0],
            "enable_itn": True,
            "diarization_enabled": diarize,
            "language_hints": language_hints,
        },
    }
    print("[2/4] 提交转写任务（说话人分离: {}）".format("开" if diarize else "关"), flush=True)
    resp = http_json(f"{api_base(cfg)}/services/audio/asr/transcription",
                     cfg["DASHSCOPE_API_KEY"], payload, async_submit=True)
    task_id = resp.get("output", {}).get("task_id")
    if not task_id:
        sys.exit(f"任务提交失败: {json.dumps(resp, ensure_ascii=False)}")
    print(f"      task_id: {task_id}", flush=True)
    return task_id


def wait_task(cfg, task_id, timeout=3600):
    print("[3/4] 等待转写完成...", flush=True)
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        resp = http_json(f"{api_base(cfg)}/tasks/{task_id}", cfg["DASHSCOPE_API_KEY"])
        out = resp.get("output", {})
        status = out.get("task_status")
        if status != last:
            print(f"      [{time.strftime('%H:%M:%S')}] {status}", flush=True)
            last = status
        if status == "SUCCEEDED":
            results = out.get("results") or ([out["result"]] if out.get("result") else [])
            for res in results:
                if res and res.get("transcription_url"):
                    return http_json(res["transcription_url"])
            sys.exit(f"任务成功但无结果 URL: {json.dumps(out, ensure_ascii=False)[:500]}")
        if status in ("FAILED", "UNKNOWN", "CANCELED"):
            sys.exit(f"任务失败: {json.dumps(out, ensure_ascii=False)}")
        time.sleep(10)
    sys.exit("轮询超时（1 小时）")


def ts(ms, srt=False):
    total_s, rem = divmod(int(ms), 1000)
    m, s = divmod(total_s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{rem:03d}" if srt else f"{h:02d}:{m:02d}:{s:02d}"


def render(result, title, out_dir, stem):
    sents = result["transcripts"][0]["sentences"]
    has_speaker = any("speaker_id" in s for s in sents)
    n_speakers = len({s.get("speaker_id") for s in sents}) if has_speaker else 0
    dur_min = result["properties"]["original_duration_in_milliseconds"] // 60000

    def label(spk):
        return f"说话人{spk + 1}" if has_speaker else ""

    lines = [f"# 会议转写：{title}", "",
             f"- 音频时长：{dur_min} 分钟",
             f"- 识别说话人数量：{n_speakers}" if has_speaker else "- 未开启说话人分离",
             "- 转写引擎：阿里云百炼 qwen-audio-3.0-asr-flash-filetrans", ""]
    cur, buf, start = object(), [], None

    def flush():
        if buf:
            tag = f" {label(cur)}" if has_speaker else ""
            lines.append(f"**[{ts(start)}]{tag}：** " + "".join(buf).strip())
            lines.append("")

    for s in sents:
        spk = s.get("speaker_id")
        if spk != cur:
            flush()
            cur, buf, start = spk, [], s["begin_time"]
        buf.append(s["text"])
    flush()
    md_path = out_dir / f"{stem}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    srt = []
    for i, s in enumerate(sents, 1):
        tag = f"[{label(s['speaker_id'])}] " if has_speaker and "speaker_id" in s else ""
        srt.append(f"{i}\n{ts(s['begin_time'], True)} --> {ts(s['end_time'], True)}\n{tag}{s['text'].strip()}\n")
    srt_path = out_dir / f"{stem}.srt"
    srt_path.write_text("\n".join(srt), encoding="utf-8")
    return md_path, srt_path


def main():
    ap = argparse.ArgumentParser(description="阿里云百炼长音频转写（含说话人分离）")
    ap.add_argument("audio", help="音频文件路径（mp3/wav/m4a/aac 等，≤2GB、≤12 小时）")
    ap.add_argument("-o", "--outdir", help="输出目录（默认：音频同级的 transcript/）")
    ap.add_argument("--no-diarize", action="store_true", help="关闭说话人分离")
    ap.add_argument("--language-hints", default="zh,en", help="语言提示，逗号分隔（默认 zh,en）")
    ap.add_argument("--keep-oss", action="store_true", help="转写完成后保留 OSS 上的音频副本")
    args = ap.parse_args()

    audio = Path(args.audio).expanduser().resolve()
    if not audio.is_file():
        sys.exit(f"文件不存在: {audio}")
    out_dir = Path(args.outdir).expanduser().resolve() if args.outdir else audio.parent / "transcript"
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config()
    url = upload_and_sign(cfg, audio)
    task_id = submit_task(cfg, url, not args.no_diarize,
                          [x.strip() for x in args.language_hints.split(",") if x.strip()])
    result = wait_task(cfg, task_id)

    json_path = out_dir / f"{audio.stem}_transcription.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path, srt_path = render(result, audio.stem, out_dir, audio.stem + "_转写")
    print(f"[4/4] 完成：\n  {md_path}\n  {srt_path}\n  {json_path}", flush=True)

    if not args.keep_oss:
        try:
            import oss2
            auth = oss2.Auth(cfg["OSS_ACCESS_KEY_ID"], cfg["OSS_ACCESS_KEY_SECRET"])
            bucket = oss2.Bucket(auth, cfg["OSS_ENDPOINT"], cfg["OSS_BUCKET"])
            key = url.split(".com/", 1)[1].split("?", 1)[0]
            bucket.delete_object(key)
            print("  已清理 OSS 临时文件", flush=True)
        except Exception as e:
            print(f"  警告：OSS 临时文件清理失败（可手动删除）: {e}", flush=True)


if __name__ == "__main__":
    main()
