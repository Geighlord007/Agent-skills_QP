#!/usr/bin/env python3
"""VideoTranscribe 共享引擎：URL/音频 → 百炼 Qwen ASR 转写 → VLM 帧分析 → 邮件投递。

被两方消费：
  - server/companion.py（本地伴侣服务，供 Chrome 扩展调用）
  - skill/video-transcribe/scripts/vtranscribe.py（命令行 skill）

仅依赖：Python 标准库 + oss2（可选，缺省用内置 stdlib OSS 实现）+ yt-dlp（URL 模式）
        + ffmpeg（可选，用于音频转码与视频截帧）。

设计约定：
  - 全部函数抛异常而非 sys.exit，方便服务端捕获后转成任务错误。
  - 配置合并顺序：内置默认 < ~/.config/qwen-asr/env（旧凭据，只读继承） < ~/.config/video-transcribe/config.json
  - 所有产出落在 workdir（默认 ~/VideoTranscribe）。
"""
from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import json
import os
import re
import shutil
import struct
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import wave
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

VERSION = "1.0.0"

CONFIG_DIR = Path.home() / ".config" / "video-transcribe"
CONFIG_FILE = CONFIG_DIR / "config.json"
LEGACY_ENV = Path.home() / ".config" / "qwen-asr" / "env"

# 站点能力表：哪些 URL 模式可被 yt-dlp 直接下载（"不播放也能转写"）
URL_SITES = {
    "bilibili": [r"https?://(www\.)?bilibili\.com/video/"],
    "youtube": [r"https?://(www\.|m\.)?youtube\.com/(watch|shorts)/", r"https?://youtu\.be/"],
    "douyin": [r"https?://(www\.)?douyin\.com/video/"],
}
LIVE_SITES = {
    "bilibili_live": [r"https?://live\.bilibili\.com/\d+"],
    "youtube_live": [r"https?://(www\.)?youtube\.com/live/"],
    "douyin_live": [r"https?://(live\.)?douyin\.com/follow|live\.douyin\.com/\d+"],
}
MEETING_HOSTS = ["zoom.us", "meet.google.com", "meeting.tencent.com", "teams.microsoft.com",
                 "teams.live.com", "voovmeeting.com", "feishu.cn"]


# ---------------------------------------------------------------- 配置

_DEFAULTS = {
    "server_host": "127.0.0.1",
    "server_port": 8765,
    "workdir": str(Path.home() / "VideoTranscribe"),
    "dashscope_api_key": "",
    "dashscope_workspace_id": "",
    "asr_model": "qwen-audio-3.0-asr-flash-filetrans",
    "vlm_model": "qwen-vl-plus",
    "language_hints": "zh,en",
    "diarize": True,
    "oss_access_key_id": "",
    "oss_access_key_secret": "",
    "oss_bucket": "",
    "oss_endpoint": "https://oss-cn-beijing.aliyuncs.com",
    "ytdlp_cookies_browser": "",
    "harvest_model": "qwen3-vl-plus",
    "harvest_max_frames": 24,
    "video_understand_model": "qwen3.8-flash",
    "email": {
        "enabled": False,
        "smtp_host": "",
        "smtp_port": 465,
        "smtp_ssl": True,
        "smtp_user": "",
        "smtp_pass": "",
        "to": "",
    },
    "token": "",
}

_LEGACY_MAP = {
    "DASHSCOPE_API_KEY": "dashscope_api_key",
    "DASHSCOPE_WORKSPACE_ID": "dashscope_workspace_id",
    "OSS_ACCESS_KEY_ID": "oss_access_key_id",
    "OSS_ACCESS_KEY_SECRET": "oss_access_key_secret",
    "OSS_BUCKET": "oss_bucket",
    "OSS_ENDPOINT": "oss_endpoint",
}


def load_config() -> dict:
    cfg = copy.deepcopy(_DEFAULTS)
    # 继承旧 qwen-asr 凭据（只读）
    if LEGACY_ENV.exists():
        for line in LEGACY_ENV.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                mk = _LEGACY_MAP.get(k.strip())
                if mk and not cfg.get(mk):
                    cfg[mk] = v.strip()
    # 环境变量优先
    for k in _LEGACY_MAP:
        if os.getenv(k):
            cfg[_LEGACY_MAP[k]] = os.environ[k]
    # 本项目配置
    if CONFIG_FILE.exists():
        try:
            stored = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            stored = {}
        for k, v in stored.items():
            if k == "email" and isinstance(v, dict):
                cfg["email"].update(v)
            elif k in cfg:
                cfg[k] = v
    if not cfg["token"]:
        cfg["token"] = uuid.uuid4().hex
        save_config(cfg)
    return cfg


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {k: v for k, v in cfg.items() if k in _DEFAULTS}
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, CONFIG_FILE)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


def masked_config(cfg: dict) -> dict:
    def mask(s: str) -> str:
        if not s:
            return ""
        return s[:4] + "****" + s[-4:] if len(s) > 10 else "****"
    out = copy.deepcopy(cfg)
    for k in ("dashscope_api_key", "oss_access_key_id", "oss_access_key_secret", "token"):
        out[k] = mask(out.get(k, ""))
    em = out.get("email", {})
    em["smtp_pass"] = mask(em.get("smtp_pass", ""))
    out["oss_bucket"] = cfg.get("oss_bucket", "")  # bucket 不敏感，方便核对
    return out


def workdir(cfg: dict) -> Path:
    wd = Path(cfg["workdir"]).expanduser()
    for sub in ("media", "out", "jobs"):
        (wd / sub).mkdir(parents=True, exist_ok=True)
    return wd


def status_report(cfg: dict) -> dict:
    ytdlp = find_ytdlp()
    return {
        "version": VERSION,
        "workdir": str(workdir(cfg)),
        "asr_ready": bool(cfg.get("dashscope_api_key") and cfg.get("oss_bucket")
                          and cfg.get("oss_access_key_id") and cfg.get("oss_access_key_secret")),
        "email_ready": bool(cfg["email"].get("enabled") and cfg["email"].get("smtp_host")
                            and cfg["email"].get("to")),
        "ytdlp": ytdlp[0] if ytdlp else None,
        "ffmpeg": shutil.which("ffmpeg"),
        "oss_mode": "oss2" if _try_oss2() else "stdlib",
    }


# ---------------------------------------------------------------- HTTP 基础

def http_json(url, api_key=None, payload=None, timeout=60, extra_headers=None):
    headers = {"User-Agent": f"VideoTranscribe/{VERSION}"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra_headers:
        headers.update(extra_headers)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:500]
        except Exception:
            pass
        raise RuntimeError(f"DashScope HTTP {e.code} ({url.split('/api/')[0].split('//')[1]}/…): {body}") from None


def api_base(cfg):
    ws = cfg.get("dashscope_workspace_id")
    if ws:
        return f"https://{ws}.cn-beijing.maas.aliyuncs.com/api/v1"
    return "https://dashscope.aliyuncs.com/api/v1"


# ---------------------------------------------------------------- OSS（oss2 优先，stdlib 兜底）

_oss2_checked = None


def _try_oss2():
    global _oss2_checked
    if _oss2_checked is None:
        try:
            import oss2  # noqa: F401
            _oss2_checked = True
        except Exception:
            _oss2_checked = False
    return _oss2_checked


def _oss_bucket_oss2(cfg):
    import oss2
    auth = oss2.Auth(cfg["oss_access_key_id"], cfg["oss_access_key_secret"])
    return oss2.Bucket(auth, cfg["oss_endpoint"], cfg["oss_bucket"])


def _gmt_now() -> str:
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")


def _oss_stdlib_put(cfg, key: str, data: bytes, content_type: str) -> None:
    bucket, host = cfg["oss_bucket"], urllib.parse.urlparse(cfg["oss_endpoint"]).hostname
    date = _gmt_now()
    string_to_sign = f"PUT\n\n{content_type}\n{date}\n/{bucket}/{key}"
    sig = base64.b64encode(hmac.new(cfg["oss_access_key_secret"].encode(),
                                    string_to_sign.encode(), hashlib.sha1).digest()).decode()
    url = f"https://{host}/{bucket}/{key}"
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Date": date, "Content-Type": content_type,
        "Authorization": f"OSS {cfg['oss_access_key_id']}:{sig}",
    })
    with urllib.request.urlopen(req, timeout=300) as r:
        if r.status not in (200, 201):
            raise RuntimeError(f"OSS PUT HTTP {r.status}")


def _oss_stdlib_sign(cfg, key: str, expires: int = 7200) -> str:
    bucket, host = cfg["oss_bucket"], urllib.parse.urlparse(cfg["oss_endpoint"]).hostname
    expire = str(int(time.time()) + expires)
    string_to_sign = f"GET\n\n\n{expire}\n/{bucket}/{key}"
    sig = base64.b64encode(hmac.new(cfg["oss_access_key_secret"].encode(),
                                    string_to_sign.encode(), hashlib.sha1).digest()).decode()
    q = urllib.parse.urlencode({
        "OSSAccessKeyId": cfg["oss_access_key_id"], "Expires": expire, "Signature": sig,
    })
    return f"https://{host}/{bucket}/{key}?{q}"


def _oss_stdlib_delete(cfg, key: str) -> None:
    bucket, host = cfg["oss_bucket"], urllib.parse.urlparse(cfg["oss_endpoint"]).hostname
    date = _gmt_now()
    string_to_sign = f"DELETE\n\n\n{date}\n/{bucket}/{key}"
    sig = base64.b64encode(hmac.new(cfg["oss_access_key_secret"].encode(),
                                    string_to_sign.encode(), hashlib.sha1).digest()).decode()
    req = urllib.request.Request(f"https://{host}/{bucket}/{key}", method="DELETE", headers={
        "Date": date, "Authorization": f"OSS {cfg['oss_access_key_id']}:{sig}",
    })
    urllib.request.urlopen(req, timeout=60)


_CONTENT_TYPES = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
                  ".aac": "audio/aac", ".amr": "audio/amr", ".ogg": "audio/ogg",
                  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                  ".webp": "image/webp", ".zip": "application/zip",
                  ".mp4": "video/mp4", ".mov": "video/quicktime", ".mkv": "video/x-matroska",
                  ".avi": "video/x-msvideo", ".webm": "video/webm", ".flv": "video/x-flv"}


def oss_upload(cfg, path: Path, key_prefix: str = "vt") -> str:
    """上传本地文件到 OSS，返回 2 小时有效的签名 GET URL。"""
    path = Path(path)
    key = f"{key_prefix}/{uuid.uuid4().hex[:12]}{path.suffix.lower()}"
    ctype = _CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
    if _try_oss2():
        b = _oss_bucket_oss2(cfg)
        b.put_object(key, path.read_bytes(), headers={"Content-Type": ctype})
        url = b.sign_url("GET", key, 7200, slash_safe=True)
    else:
        _oss_stdlib_put(cfg, key, path.read_bytes(), ctype)
        url = _oss_stdlib_sign(cfg, key, 7200)
    req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status not in (200, 206):
            raise RuntimeError(f"签名 URL 校验失败: HTTP {r.status}")
    return url


def oss_key_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path  # /bucket/key[.ext]
    return path.lstrip("/")


def oss_upload_large(cfg, path: Path, key_prefix: str = "vt") -> str:
    """流式上传大文件（视频）到 OSS，返回 2 小时有效的签名 GET URL。不整读进内存。"""
    path = Path(path)
    key = f"{key_prefix}/{uuid.uuid4().hex[:12]}{path.suffix.lower()}"
    ctype = _CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
    if _try_oss2():
        b = _oss_bucket_oss2(cfg)
        b.put_object_from_file(key, str(path), headers={"Content-Type": ctype})
        url = b.sign_url("GET", key, 7200, slash_safe=True)
    else:
        bucket, host = cfg["oss_bucket"], urllib.parse.urlparse(cfg["oss_endpoint"]).hostname
        date = _gmt_now()
        string_to_sign = f"PUT\n\n{ctype}\n{date}\n/{bucket}/{key}"
        sig = base64.b64encode(hmac.new(cfg["oss_access_key_secret"].encode(),
                                        string_to_sign.encode(), hashlib.sha1).digest()).decode()
        with open(path, "rb") as f:
            req = urllib.request.Request(
                f"https://{host}/{bucket}/{key}", data=f, method="PUT",
                headers={"Date": date, "Content-Type": ctype,
                         "Content-Length": str(path.stat().st_size),
                         "Authorization": f"OSS {cfg['oss_access_key_id']}:{sig}"})
            with urllib.request.urlopen(req, timeout=1800) as r:
                if r.status not in (200, 201):
                    raise RuntimeError(f"OSS PUT HTTP {r.status}")
        url = _oss_stdlib_sign(cfg, key, 7200)
    req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status not in (200, 206):
            raise RuntimeError(f"签名 URL 校验失败: HTTP {r.status}")
    return url


def oss_delete(cfg, url_or_key: str) -> None:
    key = oss_key_from_url(url_or_key)
    if not key:
        return
    try:
        if _try_oss2():
            _oss_bucket_oss2(cfg).delete_object(key)
        else:
            _oss_stdlib_delete(cfg, key)
    except Exception as e:  # 清理失败不致命
        log(f"OSS 清理失败（可手动删除）: {e}")


# ---------------------------------------------------------------- 日志

_LOG_PATH = None


def set_logfile(path: Path):
    global _LOG_PATH
    _LOG_PATH = Path(path)


def log(msg: str):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    try:
        print(line, flush=True)
    except OSError:
        pass
    if _LOG_PATH:
        try:
            with open(_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass


# ---------------------------------------------------------------- yt-dlp 下载

def find_ytdlp():
    exe = shutil.which("yt-dlp")
    if exe:
        return [exe]
    try:
        import yt_dlp  # noqa: F401
        return [sys_executable(), "-m", "yt_dlp"]
    except ImportError:
        return None


def sys_executable() -> str:
    return shutil.which("python") or shutil.which("python3") or "python"


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def ytdlp_meta(cfg, url: str) -> dict:
    """仅取元数据（标题/时长），不下载。"""
    ytdlp = find_ytdlp()
    if not ytdlp:
        raise RuntimeError("未找到 yt-dlp，无法按 URL 下载。请安装：pip install -U yt-dlp")
    cmd = ytdlp + ["--no-playlist", "--skip-download", "--no-warnings",
                   "--print", "%(title)s|||%(duration|0)s|||%(id)s|||%(uploader|-)s", url]
    if cfg.get("ytdlp_cookies_browser"):
        cmd += ["--cookies-from-browser", cfg["ytdlp_cookies_browser"]]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120, creationflags=_subprocess_flags())
    for line in reversed((r.stdout or "").splitlines()):
        if "|||" in line:
            t, dur, vid, up = (line.split("|||") + ["-"] * 4)[:4]
            try:
                dur = int(float(dur))
            except ValueError:
                dur = 0
            return {"title": t.strip() or vid.strip(), "duration": dur,
                    "id": vid.strip(), "uploader": up.strip()}
    raise RuntimeError(f"获取视频信息失败: {(r.stderr or r.stdout or '').strip()[:400]}")


def ytdlp_download(cfg, url: str, outdir: Path, want_video: bool = False,
                   progress=None) -> tuple[Path, dict]:
    """下载音频（want_video=True 时连同视频用于截帧）。返回 (媒体文件, 元数据)。"""
    meta = ytdlp_meta(cfg, url)
    outdir.mkdir(parents=True, exist_ok=True)
    ytdlp = find_ytdlp()
    has_ffmpeg = ffmpeg_available()
    if want_video:
        # B站/YouTube 多为 DASH 分离流，需要 bv+ba 合并（ffmpeg 存在时 yt-dlp 自动合并）
        fmt = ("bestvideo[height<=720]+bestaudio/best[height<=720]/"
               "bestvideo+bestaudio/best" if has_ffmpeg else "best[height<=720]/best")
        ext_rule = "-o", str(outdir / "video.%(ext)s")
    elif has_ffmpeg:
        fmt = "bestaudio/best"
        ext_rule = ("-x", "--audio-format", "mp3", "-o", str(outdir / "audio.%(ext)s"))
    else:
        fmt = "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best"
        ext_rule = ("-o", str(outdir / "audio.%(ext)s"))
    cmd = ytdlp + ["--no-playlist", "--no-warnings", "-f", fmt, *ext_rule, url,
                   "--retries", "20", "--fragment-retries", "20",
                   "--socket-timeout", "30", "--continue"]
    if cfg.get("ytdlp_cookies_browser"):
        cmd += ["--cookies-from-browser", cfg["ytdlp_cookies_browser"]]
    log(f"下载: {cmd}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace",
                            creationflags=_subprocess_flags())
    for line in proc.stdout or []:
        if progress and "[download]" in line and "%" in line:
            try:
                progress(min(99.0, float(re.search(r"(\d+(?:\.\d+)?)%", line).group(1))))
            except (ValueError, AttributeError):
                pass
        log("  " + line.rstrip())
    proc.wait(timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp 下载失败（exit {proc.returncode}），详见服务日志")

    prefix = "video" if want_video else "audio"
    for p in sorted(outdir.glob(f"{prefix}.*"), key=lambda p: p.stat().st_size, reverse=True):
        if p.suffix.lower() not in (".part", ".ytdl", ".json"):
            return p, meta
    raise RuntimeError("下载完成但未找到输出文件")


def _subprocess_flags():
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


# ---------------------------------------------------------------- ffmpeg 工具

def pcm_to_wav(pcm_path: Path, wav_path: Path, rate: int = 16000, channels: int = 1) -> Path:
    """把裸 PCM(s16le) 包装成 WAV（扩展录音的分块累积场景）。"""
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        with open(pcm_path, "rb") as src:
            while True:
                chunk = src.read(1 << 20)
                if not chunk:
                    break
                w.writeframes(chunk)
    return wav_path


def extract_frames(video: Path, outdir: Path, count: int = 6) -> list[Path]:
    """用 ffmpeg 从视频均匀取帧。"""
    if not ffmpeg_available():
        return []
    outdir.mkdir(parents=True, exist_ok=True)
    probe = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True,
                           creationflags=_subprocess_flags())
    try:
        dur = float(probe.stdout.strip())
    except ValueError:
        dur = 0.0
    if dur <= 0:
        return []
    frames = []
    for i in range(count):
        t = dur * (i + 0.5) / count
        out = outdir / f"frame_{i + 1:02d}.png"
        r = subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                            "-frames:v", "1", "-q:v", "2", str(out)],
                           capture_output=True, creationflags=_subprocess_flags())
        if r.returncode == 0 and out.exists() and out.stat().st_size > 1000:
            frames.append(out)
    return frames


# ---------------------------------------------------------------- ASR（百炼 filetrans，与 qwen-asr-transcribe 同源）

def submit_transcription(cfg, file_url: str, diarize: bool | None = None,
                         language_hints: list[str] | None = None) -> str:
    payload = {
        "model": cfg.get("asr_model", "qwen-audio-3.0-asr-flash-filetrans"),
        "input": {"file_urls": [file_url]},
        "parameters": {
            "channel_id": [0],
            "enable_itn": True,
            "diarization_enabled": cfg["diarize"] if diarize is None else diarize,
            "language_hints": language_hints or [x.strip() for x in cfg["language_hints"].split(",") if x.strip()],
        },
    }
    resp = http_json(f"{api_base(cfg)}/services/audio/asr/transcription",
                     cfg["dashscope_api_key"], payload,
                     extra_headers={"X-DashScope-Async": "enable"})
    task_id = resp.get("output", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"转写任务提交失败: {json.dumps(resp, ensure_ascii=False)[:400]}")
    return task_id


def wait_transcription(cfg, task_id: str, timeout=3600, progress=None) -> dict:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        resp = http_json(f"{api_base(cfg)}/tasks/{task_id}", cfg["dashscope_api_key"])
        out = resp.get("output", {})
        status = out.get("task_status")
        if status != last:
            log(f"  ASR 状态: {status}")
            last = status
        if progress:
            progress({"SUCCEEDED": 100, "RUNNING": None}.get(status))
        if status == "SUCCEEDED":
            results = out.get("results") or ([out["result"]] if out.get("result") else [])
            for res in results:
                if res and res.get("transcription_url"):
                    return http_json(res["transcription_url"])
            raise RuntimeError(f"任务成功但无结果 URL: {json.dumps(out, ensure_ascii=False)[:400]}")
        if status in ("FAILED", "UNKNOWN", "CANCELED"):
            raise RuntimeError(f"转写任务失败: {json.dumps(out, ensure_ascii=False)[:600]}")
        time.sleep(8)
    raise TimeoutError("转写轮询超时（1 小时）")


def ts(ms, srt=False):
    total_s, rem = divmod(int(ms), 1000)
    m, s = divmod(total_s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{rem:03d}" if srt else f"{h:02d}:{m:02d}:{s:02d}"


def render_transcript(result: dict, title: str, out_dir: Path, stem: str,
                      engine_name: str = "") -> dict:
    """转写结果 JSON → Markdown 纪要 + SRT。返回 {md, srt, json, meta}。"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sents = result["transcripts"][0]["sentences"]
    has_speaker = any("speaker_id" in s for s in sents)
    speakers = sorted({s.get("speaker_id") for s in sents}) if has_speaker else []
    dur_ms = result.get("properties", {}).get("original_duration_in_milliseconds", 0)

    def label(spk):
        return f"说话人{spk + 1}" if has_speaker else ""

    lines = [f"# 视频转写：{title}", "",
             f"- 音频时长：{dur_ms // 60000} 分 {dur_ms // 1000 % 60} 秒",
             (f"- 识别说话人数量：{len([s for s in speakers if s is not None])}"
              if has_speaker else "- 未开启说话人分离"),
             f"- 转写引擎：阿里云百炼 {engine_name or cfg_asr_model()}",
             f"- 生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
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

    srt_lines = []
    for i, s in enumerate(sents, 1):
        tag = f"[{label(s['speaker_id'])}] " if has_speaker and "speaker_id" in s else ""
        srt_lines.append(f"{i}\n{ts(s['begin_time'], True)} --> {ts(s['end_time'], True)}\n{tag}{s['text'].strip()}\n")
    srt_path = out_dir / f"{stem}.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    json_path = out_dir / f"{stem}_transcription.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"md": md_path, "srt": srt_path, "json": json_path,
            "meta": {"duration_ms": dur_ms, "speakers": len([s for s in speakers if s is not None]) or 0,
                     "has_speaker": has_speaker}}


_ASR_MODEL_REF = {}


def cfg_asr_model() -> str:
    return _ASR_MODEL_REF.get("model", "qwen-audio-3.0-asr-flash-filetrans")


def set_asr_model_ref(cfg):
    _ASR_MODEL_REF["model"] = cfg.get("asr_model", "qwen-audio-3.0-asr-flash-filetrans")


# ---------------------------------------------------------------- VLM 帧分析

COMPAT_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"

_IMG_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".webp": "image/webp", ".gif": "image/gif"}


def image_to_part(im) -> dict:
    """本地路径 / http URL / dataURL → OpenAI 兼容的 image_url part。"""
    s = str(im)
    if s.startswith("data:") or s.startswith("http"):
        return {"type": "image_url", "image_url": {"url": s}}
    p = Path(s)
    mime = _IMG_MIME.get(p.suffix.lower(), "image/png")
    b64 = base64.b64encode(p.read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def vlm_analyze(cfg, prompt: str, images) -> str:
    """视觉模型分析图片（OpenAI 兼容端点；images 为本地路径/URL/dataURL 列表）。"""
    content = [image_to_part(im) for im in images]
    content.append({"type": "text", "text": prompt})
    payload = {
        "model": cfg.get("vlm_model", "qwen-vl-plus"),
        "messages": [{"role": "user", "content": content}],
    }
    resp = http_json(f"{COMPAT_BASE}/chat/completions", cfg["dashscope_api_key"],
                     payload, timeout=180)
    try:
        msg = resp["choices"][0]["message"]
    except (KeyError, IndexError):
        raise RuntimeError(f"VLM 响应异常: {json.dumps(resp, ensure_ascii=False)[:400]}") from None
    c = msg.get("content", "")
    if isinstance(c, list):
        c = "\n".join(p.get("text", "") for p in c if isinstance(p, dict))
    text = (c or "").strip() or (msg.get("reasoning_content") or "").strip()
    if not text:
        raise RuntimeError(f"VLM 返回为空: {json.dumps(resp, ensure_ascii=False)[:400]}")
    return text


FRAME_ANALYSIS_PROMPT = """你是一名视频内容策划助手。请结合下面的视频转写稿，对这些视频帧（按时间顺序）进行分析，输出一份中文 Markdown 报告，包含：
1. **画面内容概述**：每帧一句话说明场景。
2. **封面建议**：从帧中选出最适合做封面的 2-3 张（说明帧序号），给出理由，并为每张写 2 个吸睛的封面标题文案。
3. **插图候选**：选出信息量最大、适合做文章插图的 2-4 张，说明适合配什么文字。
4. **文档要点**：按时间轴提炼 5-8 条核心要点，可直接用于整理文档。

要求：引用帧时用「帧1」「帧2」等编号；语气实用、直接。
"""

# 客户端截帧（无 bbox 抠图）时的素材分析提示词
ASSET_ANALYSIS_PROMPT = """你是一名内容素材整理助手。这些画面按时间顺序截取自同一个视频（如项目推荐/评测类），转写稿可能附后。
请输出中文 Markdown 素材清单：
1. **素材清单**：逐帧列出画面中值得收藏的视觉素材（项目 logo、软件截图、图表、演示画面、幻灯片、字卡），每条注明「帧N」、素材名称（结合转写稿给出真实名称，如项目名）、类型。
2. **按主题归组**：把素材按讨论对象（如各项目）归组，每组给一句话说明。
3. **可复用建议**：哪些适合做插图、哪些适合做封面、哪些适合配文档。
"""

# 逐帧素材检测（返回 JSON + bbox，0-1000 归一化坐标）
ASSET_DETECT_PROMPT = """你在分析视频的一个画面帧。视频当前话题背景：{context}
列出画面中值得收藏的视觉素材（logo、软件界面截图、图表、演示画面、幻灯片、标题字卡等）。
每个素材输出：type（logo/screenshot/chart/demo/slide/card/other）、name（结合话题背景的真实名称，如项目名，不要只写"图标"）、bbox（0-1000 归一化 [x1,y1,x2,y2]，x1y1 左上 x2y2 右下）。
注意：整屏截图或整张幻灯片本身是素材时，bbox 给 [0,0,1000,1000]；画面只是说话人头像或没有可收藏素材时输出 {{"assets": []}}；同屏多个素材分别列出，bbox 各自贴边。
只输出 JSON，格式：{{"assets": [{{"type": "...", "name": "...", "bbox": [x1,y1,x2,y2]}}]}}"""


def _extract_json(text: str):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------- 视频理解（qwen3.8 整段直传 / 帧列表精控）
#
# 实测结论（2026-10）：
#   - qwen3.8 系在 DashScope 原生端点支持整段视频文件直传（≤2h/≤2GB，≤10MB 可走 base64），
#     内部按默认 fps 采样读全片；OpenAI 兼容端点不收文件，只收 4-8000 张帧列表。
#   - 帧列表必须带 fps 注解，否则模型内部合并相邻帧、隔帧漏读；间隔建议 ≤2s。
#   - qwen3.8 默认开思考模式，小输出额度会被思考耗尽（content 为空），统一显式关闭。

_VIDEO_MIME = {".mp4": "video/mp4", ".mov": "video/quicktime", ".mkv": "video/x-matroska",
               ".avi": "video/x-msvideo", ".webm": "video/webm", ".flv": "video/x-flv"}


def video_duration_s(video: Path) -> float:
    """ffprobe 取视频时长（秒），失败返回 0.0。"""
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(video)], capture_output=True, text=True,
                       creationflags=_subprocess_flags())
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _video_input_url(cfg, video: Path) -> str:
    """≤10MB 直接 base64 data URL；更大则临时传 OSS 换签名 URL（2 小时有效，用后即删）。"""
    if video.stat().st_size <= 10 * 1024 * 1024:
        mime = _VIDEO_MIME.get(video.suffix.lower(), "video/mp4")
        return "data:" + mime + ";base64," + base64.b64encode(video.read_bytes()).decode()
    return oss_upload_large(cfg, video, key_prefix="vu")


def video_understand_whole(cfg, video: Path, prompt: str, model: str | None = None,
                           fps: float | None = None) -> str:
    """整段直传：qwen3.8 原生端点，平台内部采样读全片。上限 2 小时 / 2GB。"""
    video = Path(video)
    model = model or cfg.get("video_understand_model", "qwen3.8-flash")
    url = _video_input_url(cfg, video)
    content = [{"video": url, **({"fps": fps} if fps is not None else {})},
               {"text": prompt}]
    payload = {"model": model,
               "input": {"messages": [{"role": "user", "content": content}]},
               "parameters": {"max_tokens": 4096, "enable_thinking": False}}
    try:
        resp = http_json(f"{api_base(cfg)}/services/aigc/multimodal-generation/generation",
                         cfg["dashscope_api_key"], payload, timeout=1800)
    finally:
        if url.startswith("http") and "OSSAccessKeyId" in url:
            try:
                oss_delete(cfg, url)
            except Exception:
                pass
    choices = (resp.get("output", {}) or {}).get("choices") or resp.get("choices") or []
    if not choices:
        raise RuntimeError(f"视频理解响应异常: {json.dumps(resp, ensure_ascii=False)[:400]}")
    msg = choices[0].get("message", {})
    c = msg.get("content", "")
    if isinstance(c, list):
        c = "".join(p.get("text", "") for p in c if isinstance(p, dict))
    text = (c or "").strip()
    if not text:
        raise RuntimeError(f"视频理解返回为空: {json.dumps(resp, ensure_ascii=False)[:400]}")
    return text


def video_understand_frames(cfg, frames, fps: float, prompt: str,
                            model: str | None = None) -> str:
    """帧列表精控：OpenAI 兼容端点，4-8000 张自带帧，fps 注解必填。

    平台单请求 data-uri 上限 250，超长列表自动分块（每块 ≤240 张）后拼接结果。
    """
    model = model or cfg.get("video_understand_model", "qwen3.8-flash")
    if len(frames) < 4:
        raise RuntimeError(f"帧列表至少 4 张（平台下限），当前 {len(frames)}")
    if len(frames) > 8000:
        raise RuntimeError(f"帧列表最多 8000 张（平台上限），当前 {len(frames)}")
    urls = []
    for f in frames:
        s = str(f)
        if s.startswith("data:") or s.startswith("http"):
            urls.append(s)
        else:
            p = Path(s)
            mime = _IMG_MIME.get(p.suffix.lower(), "image/jpeg")
            urls.append("data:" + mime + ";base64," + base64.b64encode(p.read_bytes()).decode())
    fps_eff = max(0.1, min(10.0, fps))
    chunks = [urls[i:i + 240] for i in range(0, len(urls), 240)]
    parts = []
    for chunk in chunks:
        content = [{"type": "video", "video": chunk, "fps": fps_eff},
                   {"type": "text", "text": prompt}]
        payload = {"model": model,
                   "messages": [{"role": "user", "content": content}],
                   "max_completion_tokens": 4096,
                   "enable_thinking": False}
        resp = http_json(f"{COMPAT_BASE}/chat/completions", cfg["dashscope_api_key"],
                         payload, timeout=1800)
        try:
            msg = resp["choices"][0]["message"]
        except (KeyError, IndexError):
            raise RuntimeError(f"视频理解响应异常: {json.dumps(resp, ensure_ascii=False)[:400]}") from None
        c = msg.get("content", "")
        if isinstance(c, list):
            c = "\n".join(p.get("text", "") for p in c if isinstance(p, dict))
        text = (c or "").strip()
        if not text:
            raise RuntimeError(f"视频理解返回为空: {json.dumps(resp, ensure_ascii=False)[:400]}")
        parts.append(text)
    return "\n\n".join(parts)


def measure_video_dynamism(video: Path, probe_seconds: float = 60.0) -> dict:
    """探测视频运动强度：取中段 probe_seconds 秒，1fps 抽 160 宽灰度帧，
    计算相邻帧平均像素差（0-255 尺度 MAD）与分钟级切换次数。

    返回 {"motion_median", "motion_mean", "motion_p90", "cuts_per_min"}。判据要点：
    量"运动"而非"切换"，且主判据用中位数——游戏画面持续在动（中位数高），会议桌面只有
    翻页瞬间跳变（均值/分位被尖峰拉高，中位数接近 0）。
    经验阈值（0-255 MAD 中位数）：会议桌面 < 1，游戏/运动 > 3，中间为过渡带。
    """
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(video)], capture_output=True, text=True,
                       creationflags=_subprocess_flags())
    try:
        dur = float(r.stdout.strip())
    except ValueError:
        raise RuntimeError(f"无法读取视频时长: {video}") from None
    if dur <= 0:
        raise RuntimeError(f"无法读取视频时长: {video}")
    start = max(0.0, (dur - probe_seconds) / 2)
    w, h = 160, 90
    cmd = ["ffmpeg", "-hide_banner", "-ss", f"{start:.1f}", "-t", f"{probe_seconds:.1f}",
           "-i", str(video), "-vf", f"fps=1,scale={w}:{h},format=gray",
           "-f", "rawvideo", "pipe:1"]
    p = subprocess.run(cmd, capture_output=True, creationflags=_subprocess_flags())
    frame_size = w * h
    data = p.stdout
    frames = [data[i:i + frame_size] for i in range(0, len(data) - frame_size + 1, frame_size)]
    frames = [f for f in frames if len(f) == frame_size]
    if len(frames) < 4:
        raise RuntimeError("运动强度探测失败（抽帧不足）")
    mads = []
    for a, b in zip(frames, frames[1:]):
        diff = sum(abs(x - y) for x, y in zip(a, b)) / frame_size
        mads.append(diff)
    mads.sort()
    # 主判据用中位数：均值/分位会被翻页等切换尖峰拉高，中位数反映"画面是否持续在动"
    med = mads[len(mads) // 2]
    # 切换次数：MAD 尖峰（超过中位数 8 倍且绝对值 > 8）
    cuts = sum(1 for m in mads if m > max(8.0, med * 8))
    return {
        "motion_median": round(med, 2),
        "motion_mean": round(sum(mads) / len(mads), 2),
        "motion_p90": round(mads[int(len(mads) * 0.9)], 2),
        "cuts_per_min": round(cuts * 60.0 / probe_seconds, 1),
    }


def adaptive_extract_frames(video: Path, outdir: Path, max_frames: int | None = None) -> list:
    """混合抽帧：一半预算均匀覆盖全片，一半预算给场景切换点，合并去重后按时间排序。

    不做"动态/静态"二分类——实测低分辨率探测（切换分数、运动 MAD 的中位数/均值）都无法
    可靠区分游戏与会议画面：游戏镜头平滑运动的中位数接近静态桌面，会议翻页的均值/分位数
    又接近游戏。混合策略对两者都成立：均匀部分保底全片覆盖，切换点部分捕捉转场与高潮。

    返回 [{"path", "t"}]。
    """
    video = Path(video)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    max_frames = max_frames or 24
    dur = video_duration_s(video)
    if dur <= 0:
        raise RuntimeError(f"无法读取视频时长: {video}")
    n_uniform = max(2, max_frames // 2)
    step = dur / n_uniform
    chosen = []
    for i in range(n_uniform):
        t = round(step * (i + 0.5), 2)
        p = outdir / f"uni_{i + 1:03d}.png"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                        "-frames:v", "1", str(p)],
                       capture_output=True, creationflags=_subprocess_flags())
        if p.exists() and p.stat().st_size > 1000:
            chosen.append({"path": p, "t": t})
    scene_dir = outdir / "scene"
    scene_frames = extract_scenes(video, scene_dir, max_frames=max_frames)
    min_gap = max(2.0, dur / max_frames / 2)
    hashes = [frame_hash(c["path"]) for c in chosen]
    for f in scene_frames:
        if len(chosen) >= max_frames:
            break
        if any(abs(f["t"] - c["t"]) < min_gap for c in chosen):
            continue
        h = frame_hash(f["path"])
        if any(hamming_hex(h, x) < 10 for x in hashes):
            continue
        chosen.append(f)
        hashes.append(h)
    chosen.sort(key=lambda x: x["t"])
    return chosen


def select_key_frames(frame_paths, k: int = 5) -> list:
    """按内容选 k 张关键图（用于 docx 嵌图）：清晰度（灰度梯度均值）优先，
    感知哈希保证互不重复。缺 PIL 时退化为均匀抽样。"""
    try:
        from PIL import Image
    except ImportError:
        paths = [Path(p) for p in frame_paths]
        step = max(1, len(paths) // max(1, k))
        return paths[::step][:k]
    w, h = 160, 90
    scored = []
    for p in frame_paths:
        try:
            img = Image.open(p).convert("L").resize((w, h))
            px = list(img.getdata())
            grad = 0
            for y in range(1, h - 1, 2):
                base = y * w
                for x in range(1, w - 1, 2):
                    i = base + x
                    grad += abs(px[i] - px[i + 1]) + abs(px[i] - px[i + w])
            scored.append((grad, Path(p)))
        except Exception:
            continue
    if not scored:
        return []
    scored.sort(reverse=True)
    picked, hashes = [], []
    for _, p in scored:
        hsh = frame_hash(p)
        if any(hamming_hex(hsh, s) < 12 for s in hashes):
            continue
        picked.append(p)
        hashes.append(hsh)
        if len(picked) >= k:
            break
    if len(picked) < k:
        for _, p in scored:
            if p not in picked:
                picked.append(p)
            if len(picked) >= k:
                break
    picked.sort(key=lambda p: p.name)
    return picked


def video_understand(cfg, video, prompt: str, mode: str = "auto", model: str | None = None,
                     fps: float | None = None, max_frames: int | None = None) -> str:
    """视频理解统一入口。

    auto   整段直传（≤2h/≤2GB；≤10MB 走 base64，更大临时传 OSS，用后即删）
    whole  强制整段直传
    frames 自适应抽帧后送帧列表：动态视频（游戏/运动）密集均匀，静态视频（会议/桌面）
           场景检测+去重；帧保留在 workdir/vu/ 下可复用作截图
    """
    video = Path(video)
    if not video.is_file():
        raise RuntimeError(f"视频不存在: {video}")
    if mode == "frames":
        out_dir = workdir(cfg) / "vu" / f"{_safe_name(video.stem, 40)}-{uuid.uuid4().hex[:8]}"
        frames_dir = out_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        frames = adaptive_extract_frames(video, frames_dir, max_frames=max_frames)
        paths = [f["path"] for f in frames]
        if len(paths) < 4:
            while len(paths) < 4 and frames:
                paths.append(frames[len(paths) % len(frames)]["path"])
        dur = video_duration_s(video)
        eff = fps or (max(0.1, min(10.0, round(len(paths) / dur, 2))) if dur > 0 else 1.0)
        text = video_understand_frames(cfg, paths, eff, prompt, model=model)
        return text + f"\n\n（帧已保留：{frames_dir}）"
    dur = video_duration_s(video)
    if dur > 7200:
        raise RuntimeError("视频超过 2 小时：请先用 ffmpeg 分段（qwen3.8 整段直传上限 2 小时）")
    if video.stat().st_size > 2 * 1024 ** 3:
        raise RuntimeError("视频超过 2GB：请先转码压缩（qwen3.8 整段直传上限 2GB）")
    return video_understand_whole(cfg, video, prompt, model=model, fps=fps)


def extract_scenes(video: Path, outdir: Path, max_frames: int = 24,
                   threshold: float = 0.25) -> list[dict]:
    """按镜头切换抽帧（带时间戳）。返回 [{"path", "t"}] 按时间升序，≤ max_frames。"""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    flags = [_subprocess_flags()]

    def probe_size():
        r = subprocess.run(["ffprobe", "-v", "quiet", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True, creationflags=flags[0])
        try:
            w, h = r.stdout.strip().split(",")[:2]
            return int(w), int(h)
        except (ValueError, IndexError):
            return 0, 0

    size = probe_size()
    frames: list[dict] = []

    # 第 0 秒固定取一帧
    first = outdir / "frame_000.png"
    subprocess.run(["ffmpeg", "-y", "-ss", "0", "-i", str(video), "-frames:v", "1", str(first)],
                   capture_output=True, creationflags=flags[0])
    if first.exists() and first.stat().st_size > 1000:
        frames.append({"path": first, "t": 0.0})

    # 场景切换检测 + showinfo 拿时间戳
    seq = outdir / "scene_%03d.png"
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", str(video), "-vf",
         f"select='gt(scene,{threshold})',showinfo", "-vsync", "vfr", "-frames:v",
         str(max_frames * 3), str(seq)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        creationflags=flags[0])
    times = [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr or "")]
    scene_files = sorted(outdir.glob("scene_*.png"))
    for p, t in zip(scene_files, times):
        if p.stat().st_size > 1000:
            frames.append({"path": p, "t": t})

    # 场景太少（低于阈值或检测失败）→ 均匀补帧
    if len(frames) < 4:
        for old in outdir.glob("scene_*.png"):
            old.unlink()
        frames = [f for f in frames if f["t"] == 0.0]
        probe = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(video)], capture_output=True, text=True,
                               creationflags=flags[0])
        try:
            dur = float(probe.stdout.strip())
        except ValueError:
            dur = 0.0
        n = max_frames if dur > 0 else 0
        for i in range(n):
            t = dur * (i + 0.5) / n
            p = outdir / f"scene_{i + 1:03d}.png"
            rr = subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                                 "-frames:v", "1", str(p)], capture_output=True,
                                creationflags=flags[0])
            if rr.returncode == 0 and p.exists():
                frames.append({"path": p, "t": t})
        frames.sort(key=lambda f: f["t"])

    # 超 max_frames → 均匀抽稀
    if len(frames) > max_frames:
        step = len(frames) / max_frames
        frames = [frames[int(i * step)] for i in range(max_frames)]
    return frames


def frame_hash(path: Path) -> str | None:
    """16x16 灰度均值哈希（aHash），用于相邻镜头去重。无 ffmpeg 时退化为文件 md5。"""
    if not ffmpeg_available():
        return "md5:" + hashlib.md5(Path(path).read_bytes()).hexdigest()
    try:
        r = subprocess.run(
            ["ffmpeg", "-v", "quiet", "-i", str(path), "-vf", "scale=16:16,format=gray",
             "-f", "rawvideo", "-"],
            capture_output=True, creationflags=_subprocess_flags(), timeout=20)
        if len(r.stdout) != 256:
            return "md5:" + hashlib.md5(Path(path).read_bytes()).hexdigest()
        avg = sum(r.stdout) / 256
        bits = "".join("1" if b > avg else "0" for b in r.stdout)
        return f"{int(bits, 2):064x}"
    except Exception:
        return "md5:" + hashlib.md5(Path(path).read_bytes()).hexdigest()


def hamming_hex(a: str, b: str) -> int:
    if a.startswith("md5:") or b.startswith("md5:"):
        return 0 if a == b else 256
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def detect_assets_in_frame(cfg, frame_path: Path, context: str = "") -> list[dict]:
    """单帧素材检测，返回 [{"type","name","bbox"}]，bbox 为 0-1000 归一化或 None。"""
    prompt = ASSET_DETECT_PROMPT.format(context=context or "（未知，按画面内容判断）")
    models = [cfg.get("harvest_model", "qwen3-vl-plus"), cfg.get("vlm_model", "qwen-vl-plus")]
    last_err = None
    for model in models:
        try:
            content = [image_to_part(frame_path), {"type": "text", "text": prompt}]
            resp = http_json(f"{COMPAT_BASE}/chat/completions", cfg["dashscope_api_key"],
                             {"model": model, "messages": [{"role": "user", "content": content}]},
                             timeout=120)
            msg = resp["choices"][0]["message"]
            text = msg.get("content", "")
            if isinstance(text, list):
                text = "\n".join(p.get("text", "") for p in text if isinstance(p, dict))
            data = _extract_json(text or "")
            if data is None:
                return []
            out = []
            for a in (data.get("assets") or []):
                bbox = a.get("bbox")
                if isinstance(bbox, list) and len(bbox) == 4 and all(
                        isinstance(v, (int, float)) and 0 <= v <= 1000 for v in bbox):
                    if bbox[2] - bbox[0] < 5 or bbox[3] - bbox[1] < 5:
                        bbox = None
                else:
                    bbox = None
                out.append({"type": str(a.get("type", "other"))[:16], "name": str(a.get("name", "素材"))[:40],
                            "bbox": bbox})
            return out
        except Exception as e:
            last_err = e
    raise RuntimeError(f"素材检测失败: {last_err}")


def crop_bbox(frame_path: Path, bbox: list, out_path: Path, frame_size: tuple) -> Path:
    """按 0-1000 归一化 bbox 用 ffmpeg 抠图。"""
    w, h = frame_size
    if w <= 0 or h <= 0:
        shutil.copy(frame_path, out_path)
        return out_path
    x1, y1, x2, y2 = [max(0, min(1000, int(v))) for v in bbox]
    px, py = int(w * x1 / 1000), int(h * y1 / 1000)
    pw, ph = max(8, int(w * (x2 - x1) / 1000)), max(8, int(h * (y2 - y1) / 1000))
    pw, ph = min(pw, w - px), min(ph, h - py)
    if pw < 8 or ph < 8 or (pw * ph) < 0.001 * w * h:
        shutil.copy(frame_path, out_path)
        return out_path
    subprocess.run(["ffmpeg", "-y", "-i", str(frame_path), "-vf",
                    f"crop={pw}:{ph}:{px}:{py}", str(out_path)],
                   capture_output=True, creationflags=_subprocess_flags())
    if not out_path.exists() or out_path.stat().st_size < 500:
        shutil.copy(frame_path, out_path)
    return out_path


def transcript_context(sents: list[dict], t: float, window: float = 20.0) -> str:
    """取帧时间戳附近的转写文本作为话题背景。"""
    if not sents:
        return ""
    ctx = [s["text"] for s in sents
           if s.get("begin_time", 0) / 1000 <= t + window and s.get("end_time", 0) / 1000 >= t - window]
    return " ".join(ctx)[:400]


def harvest_assets(cfg, video: Path, out_dir: Path, sents: list[dict] | None = None,
                   max_frames: int | None = None, progress=None, title: str = "") -> dict:
    """素材收集主流程：镜头抽帧 → 去重 → 逐帧检测 → 抠图 → 命名 → 索引 → zip。

    返回 {"index_md", "zip", "assets_dir", "count", "frames", "log"}。
    """
    video = Path(video)
    out_dir = Path(out_dir)
    frames_dir = out_dir / "frames"
    assets_dir = out_dir / "assets"
    frames_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    max_frames = max_frames or cfg.get("harvest_max_frames", 24)
    model = cfg.get("harvest_model", "qwen3-vl-plus")

    def pct(x):
        if progress:
            progress(x)

    pct(2)
    frames = extract_scenes(video, frames_dir, max_frames=max_frames)
    log_lines = [f"镜头抽帧 {len(frames)} 张（模型 {model}）"]
    pct(12)

    # 感知去重：相邻哈希
    uniq = []
    last_h = None
    for f in frames:
        h = frame_hash(f["path"])
        if last_h and hamming_hex(h, last_h) < 12:
            continue
        uniq.append({**f, "hash": h})
        last_h = h
    log_lines.append(f"去重后 {len(uniq)} 帧")
    pct(18)

    size = (0, 0)
    if ffmpeg_available():
        r = subprocess.run(["ffprobe", "-v", "quiet", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True, creationflags=_subprocess_flags())
        try:
            w, h = r.stdout.strip().split(",")[:2]
            size = (int(w), int(h))
        except (ValueError, IndexError):
            size = (0, 0)

    # 逐帧检测 + 抠图
    records = []
    tmp_crops = []
    for i, f in enumerate(uniq):
        ctx = transcript_context(sents or [], f["t"])
        try:
            assets = detect_assets_in_frame(cfg, f["path"], ctx)
        except Exception as e:
            log_lines.append(f"帧{i + 1}@{f['t']:.0f}s 检测失败: {e}")
            continue
        for a in assets:
            tmp = assets_dir / f"tmp_{len(tmp_crops):03d}.png"
            if a.get("bbox"):
                crop_bbox(f["path"], a["bbox"], tmp, size)
            else:
                shutil.copy(f["path"], tmp)
            tmp_crops.append({"tmp": tmp, **a, "t": f["t"], "frame_t": f["t"], "ctx": ctx})
        log_lines.append(f"帧{i + 1}@{f['t']:.0f}s: {len(assets)} 素材")
        pct(18 + 62 * (i + 1) / len(uniq))

    # 素材级去重（同 logo 多帧重复）
    kept, seen = [], []
    for c in tmp_crops:
        h = frame_hash(c["tmp"])
        if any(hamming_hex(h, s) < 20 for s in seen):
            c["tmp"].unlink(missing_ok=True)
            continue
        seen.append(h)
        kept.append(c)

    # 命名 + 索引
    lines = [f"# 视频素材收集：{title or video.stem}", "",
             f"- 来源视频：{video.name}",
             f"- 镜头帧：{len(frames)} → 去重 {len(uniq)} → 素材 {len(kept)} 条",
             f"- 检测模型：{model}",
             f"- 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
    final_files = []
    for i, c in enumerate(kept, 1):
        name = _safe_name(c["name"], 30) or "素材"
        fname = f"{i:02d}_{c['type']}_{name}.png"
        final = assets_dir / fname
        shutil.move(str(c["tmp"]), final)
        final_files.append(final)
        mm, ss = divmod(int(c["t"]), 60)
        lines.append(f"{i}. `{fname}` — **{c['name']}**（{c['type']}）· 出现于 {mm:02d}:{ss:02d}"
                     + (f" · 当时讲到：{c['ctx'][:80]}…" if c["ctx"] else ""))
    if not kept:
        lines.append("（本视频未检测到可收藏的独立素材，完整帧保留在 frames/ 目录）")

    index = out_dir / "素材索引.md"
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pct(95)

    zip_path = out_dir / f"{_safe_name(video.stem)}_素材包.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(index, index.name)
        for f in final_files:
            z.write(f, f"assets/{f.name}")
    pct(99)
    return {"index_md": str(index), "zip": str(zip_path), "assets_dir": str(assets_dir),
            "count": len(kept), "frames": len(frames), "log": log_lines, "files": [str(index), str(zip_path)]}




def analyze_frames_files(cfg, frame_paths: list[Path], transcript_md: str | None = None,
                         prompt: str | None = None) -> tuple[str, list[str]]:
    """帧图本地路径 → VLM 分析（base64 内联，无需 OSS 中转）。返回 (报告, 图片引用列表)。"""
    p = prompt or FRAME_ANALYSIS_PROMPT
    if transcript_md:
        p += "\n\n--- 视频转写稿（节选前 6000 字）---\n" + transcript_md[:6000]
    report = vlm_analyze(cfg, p, [Path(f) for f in frame_paths])
    return report, [str(f) for f in frame_paths]


# ---------------------------------------------------------------- 邮件

SMTP_PRESETS = {
    "qq": ("smtp.qq.com", 465), "163": ("smtp.163.com", 465),
    "126": ("smtp.126.com", 465), "gmail": ("smtp.gmail.com", 465),
    "outlook": ("smtp.office365.com", 587), "sina": ("smtp.sina.com", 465),
}


def send_email(cfg, subject: str, body: str, attachments: list[Path] | None = None,
               to: str | None = None) -> str:
    em = cfg["email"]
    to = to or em.get("to")
    if not (em.get("smtp_host") and em.get("smtp_user") and to):
        raise RuntimeError("邮件未配置完整（需要 smtp_host / smtp_user / 收件地址），请在配置中填写")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = em["smtp_user"]
    msg["To"] = to
    msg.set_content(body)
    total = 0
    for p in attachments or []:
        p = Path(p)
        data = p.read_bytes()
        total += len(data)
        if total > 20 * 1024 * 1024:
            log(f"  附件总量超 20MB，跳过 {p.name}")
            continue
        ext = p.suffix.lower()
        if ext in (".md", ".txt", ".srt", ".json"):
            msg.add_attachment(data, maintype="text", subtype="plain", filename=p.name)
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            msg.add_attachment(data, maintype="image",
                               subtype={"png": "png", "jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}[ext],
                               filename=p.name)
        elif ext == ".zip":
            msg.add_attachment(data, maintype="application", subtype="zip", filename=p.name)
        else:
            msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=p.name)

    import smtplib
    port = int(em.get("smtp_port", 465))
    if em.get("smtp_ssl", True):
        with smtplib.SMTP_SSL(em["smtp_host"], port, timeout=30) as s:
            s.login(em["smtp_user"], em["smtp_pass"])
            s.send_message(msg)
    else:
        with smtplib.SMTP(em["smtp_host"], port, timeout=30) as s:
            s.ehlo()
            s.starttls()
            s.login(em["smtp_user"], em["smtp_pass"])
            s.send_message(msg)
    return to


# ---------------------------------------------------------------- 任务管道

class JobError(RuntimeError):
    pass


class JobManager:
    """内存任务表 + 磁盘持久化（workdir/jobs/<id>.json）。"""

    def __init__(self, cfg: dict, max_workers: int = 2, echo_console: bool = True):
        self.cfg = cfg
        self.echo_console = echo_console
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: dict[str, dict] = {}
        self.lock = threading.Lock()
        wd = workdir(cfg)
        for jf in (wd / "jobs").glob("*.json"):
            try:
                j = json.loads(jf.read_text(encoding="utf-8"))
                if j.get("status") in ("running", "pending"):  # 服务重启后标记中断
                    j["status"], j["error"] = "interrupted", "服务重启，任务中断"
                self.jobs[j["id"]] = j
            except Exception:
                pass

    # ---- 状态管理 ----
    def _persist(self, job: dict):
        p = workdir(self.cfg) / "jobs" / f"{job['id']}.json"
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, p)

    def _update(self, job_id: str, **fields):
        with self.lock:
            job = self.jobs[job_id]
            job.update(fields)
            job["updated"] = time.time()
            self._persist(job)
        return job

    def log(self, job_id: str, msg: str):
        with self.lock:
            job = self.jobs.get(job_id)
            if job is not None:
                job.setdefault("log", []).append(f"[{time.strftime('%H:%M:%S')}] {msg}")
                if len(job["log"]) > 300:
                    del job["log"][:100]
                self._persist(job)
        if self.echo_console:
            log(f"[{job_id[:8]}] {msg}")

    def get(self, job_id: str) -> dict | None:
        return self.jobs.get(job_id)

    def list(self, limit: int = 30) -> list[dict]:
        js = sorted(self.jobs.values(), key=lambda j: j.get("created", 0), reverse=True)[:limit]
        return [{k: v for k, v in j.items() if k != "log"} for j in js]

    # ---- 创建 ----
    def create(self, jtype: str, title: str = "", url: str = "", options: dict | None = None,
               source: str = "extension") -> dict:
        jid = uuid.uuid4().hex[:16]
        job = {"id": jid, "type": jtype, "title": title or url or jtype, "url": url,
               "options": options or {}, "source": source, "status": "pending",
               "progress": 0.0, "error": None, "result": None, "created": time.time(),
               "updated": time.time(), "log": []}
        with self.lock:
            self.jobs[jid] = job
            self._persist(job)
        (workdir(self.cfg) / "media" / jid).mkdir(parents=True, exist_ok=True)
        if jtype == "record":
            # 录音任务：等待扩展分块上传，POST /jobs/<id>/finalize 时才启动管道
            self._update(jid, status="recording")
        else:
            self.executor.submit(self._run, jid)
        return {k: v for k, v in job.items() if not k.startswith("_")}

    def append_chunk(self, job_id: str, pcm_bytes: bytes) -> int:
        job = self.jobs.get(job_id)
        if not job:
            raise JobError("任务不存在")
        pcm = workdir(self.cfg) / "media" / job_id / "audio.pcm"
        with open(pcm, "ab") as f:
            f.write(pcm_bytes)
            n = f.tell()
        return n

    # ---- 执行 ----
    def _run(self, job_id: str):
        try:
            self._update(job_id, status="running")
            job = self.jobs[job_id]
            options = job.get("options") or {}
            if job["type"] == "url":
                result = self._pipeline_url(job, options)
            elif job["type"] == "record":
                result = self._pipeline_record(job, options)
            elif job["type"] == "audio":
                result = self._pipeline_audio(job, options)
            elif job["type"] == "analyze":
                result = self._pipeline_analyze(job, options)
            else:
                raise JobError(f"未知任务类型: {job['type']}")
            self._update(job_id, status="done", progress=100.0, result=result)
            self.log(job_id, "✅ 任务完成")
        except Exception as e:
            self.log(job_id, f"❌ 失败: {e}")
            self._update(job_id, status="failed", error=str(e)[:800])

    # 公共：上传→转写→渲染（不含邮件与帧分析）
    def _transcribe(self, job_id: str, audio: Path, title: str, options: dict,
                    pbase: float = 30.0, pspan: float = 58.0) -> dict:
        cfg = self.cfg
        out_dir = workdir(cfg) / "out" / job_id
        self.log(job_id, f"上传音频到 OSS: {audio.name}（{audio.stat().st_size // 1024 // 1024}MB）")
        self._update(job_id, progress=pbase + 0.05 * pspan)
        url = oss_upload(cfg, audio, key_prefix="vt/asr")
        try:
            self.log(job_id, "提交百炼转写任务…")
            self._update(job_id, progress=pbase + 0.15 * pspan)
            task_id = submit_transcription(cfg, url, diarize=options.get("diarize"),
                                           language_hints=options.get("language_hints"))
            self.log(job_id, f"task_id={task_id}，等待云端转写…")
            self._update(job_id, progress=pbase + 0.25 * pspan)
            result = wait_transcription(cfg, task_id, progress=lambda p: (
                self._update(job_id, progress=pbase + (0.25 + 0.6 * p / 100) * pspan) if p else None))
            self.log(job_id, "转写完成，渲染 Markdown/SRT…")
            set_asr_model_ref(cfg)
            rendered = render_transcript(result, title, out_dir, f"{_safe_name(title)}_转写",
                                         engine_name=cfg.get("asr_model", ""))
            self._update(job_id, progress=pbase + pspan)
            return rendered
        finally:
            oss_delete(cfg, url)
            self.log(job_id, "已清理 OSS 临时音频")

    def _email_deliver(self, job_id, title, source_url, files, subject_prefix,
                       body_intro: list[str] | None = None) -> dict:
        cfg = self.cfg
        if not cfg["email"].get("enabled"):
            self.log(job_id, "邮件未启用，跳过发送（在配置中开启并填写 SMTP 即可自动发邮箱）")
            return {"sent": False, "reason": "邮件未启用"}
        body_lines = [f"《{title}》处理完成。", "",
                      f"来源：{source_url or '本地/录音'}",
                      f"完成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
        body_lines += list(body_intro or [])
        body_lines += ["全部结果见附件。", ""]
        for f in files:
            p = Path(f)
            if p.suffix == ".md" and "转写" in p.name:
                body_lines += ["―― 转写稿开头 ――"]
                body_lines.append("\n".join(p.read_text(encoding="utf-8").splitlines()[:20]))
                break
        try:
            to = send_email(cfg, f"{subject_prefix}{title}", "\n".join(body_lines), files)
            self.log(job_id, f"📧 已发送邮件 → {to}")
            return {"sent": True, "to": to}
        except Exception as e:
            self.log(job_id, f"邮件发送失败: {e}")
            return {"sent": False, "reason": str(e)[:300]}

    # url 任务：yt-dlp 下载 → 按模式转写 / 素材收集 → 统一邮件
    def _pipeline_url(self, job, options):
        url, jid = job["url"], job["id"]
        mode = options.get("mode") or ("both" if options.get("analyze") else "transcribe")
        if mode not in ("transcribe", "assets", "both"):
            mode = "transcribe"
        media = workdir(self.cfg) / "media" / jid
        self.log(jid, f"yt-dlp 获取: {url}（模式: {mode}）")
        self._update(jid, progress=2.0)

        title, audio, video, sents = None, None, None, None
        if mode in ("transcribe", "both"):
            span = 0.14 if mode == "both" else 0.28
            audio, meta = ytdlp_download(self.cfg, url, media, want_video=False,
                                         progress=lambda p: self._update(jid, progress=2 + p * span))
            self.log(jid, f"音频下载完成: {audio.name}")
            title = options.get("title") or meta["title"]
            self._update(jid, title=title)
        if mode in ("assets", "both"):
            base = 16.0 if mode == "both" else 2.0
            video, meta2 = ytdlp_download(self.cfg, url, media / "vid", want_video=True,
                                          progress=lambda p: self._update(jid, progress=base + p * 0.14))
            self.log(jid, f"视频下载完成: {video.name}")
            title = title or options.get("title") or meta2["title"]
            self._update(jid, title=title)

        files, result = [], {"title": title, "url": url, "meta": {}, "md": None, "srt": None,
                             "analysis_md": None, "harvest": None}
        if mode in ("transcribe", "both"):
            rendered = self._transcribe(jid, audio, title, options,
                                        pbase=30.0, pspan=58.0 if mode == "transcribe" else 55.0)
            files += [rendered["md"], rendered["srt"], rendered["json"]]
            result.update({"md": str(rendered["md"]), "srt": str(rendered["srt"]),
                           "meta": rendered["meta"]})
            try:
                tj = json.loads(Path(rendered["json"]).read_text(encoding="utf-8"))
                sents = tj["transcripts"][0]["sentences"]
            except Exception:
                sents = None
        if mode in ("assets", "both"):
            if not ffmpeg_available():
                raise JobError("素材收集需要 ffmpeg（未检测到，请安装后重试）")
            out_dir = workdir(self.cfg) / "out" / jid
            pbase, pspan = (85.0, 12.0) if mode == "both" else (30.0, 65.0)
            harvest = harvest_assets(self.cfg, video, out_dir, sents=sents,
                                     max_frames=options.get("max_frames"),
                                     progress=lambda p: self._update(jid, progress=pbase + p * pspan / 100),
                                     title=title)
            for line in harvest["log"]:
                self.log(jid, line)
            files += harvest["files"]
            result["harvest"] = {k: harvest[k] for k in ("index_md", "zip", "count", "frames", "assets_dir")}
            result["analysis_md"] = Path(harvest["index_md"]).read_text(encoding="utf-8")

        result["files"] = [str(f) for f in files]
        prefix = "【视频素材】" if mode == "assets" else "【视频转写】"
        intro = []
        if result["harvest"]:
            intro.append(f"收集素材 {result['harvest']['count']} 条（来自 {result['harvest']['frames']} 个镜头），"
                         "素材包 zip 见附件。")
        m = result["meta"]
        if m.get("duration_ms"):
            intro.append(f"时长：{m['duration_ms'] // 60000} 分 {m['duration_ms'] // 1000 % 60} 秒　"
                         f"说话人：{m.get('speakers', '-')} 人")
        result["email"] = self._email_deliver(jid, title, url, result["files"], prefix, intro)
        return result

    # record 任务：PCM 已由扩展分块上传，finalize 后包装 WAV → 转写 → 邮件
    def _pipeline_record(self, job, options):
        jid = job["id"]
        media = workdir(self.cfg) / "media" / jid
        pcm = media / "audio.pcm"
        if not pcm.exists() or pcm.stat().st_size < 16000:
            raise JobError("录音数据为空")
        wav = pcm_to_wav(pcm, media / "audio.wav", rate=options.get("rate", 16000))
        secs = wav.stat().st_size // 32000
        self.log(jid, f"录音 {secs} 秒，开始转写流程")
        title = job.get("title") or "网页录音转写"
        rendered = self._transcribe(jid, wav, title, options)
        files = [rendered["md"], rendered["srt"], rendered["json"]]
        m = rendered["meta"]
        result = {"title": title, "url": job.get("url", ""), "md": str(rendered["md"]),
                  "srt": str(rendered["srt"]), "meta": m, "analysis_md": None, "harvest": None,
                  "files": [str(f) for f in files]}
        result["email"] = self._email_deliver(jid, title, job.get("url", ""), files, "【录音转写】",
                                              [f"时长：{m['duration_ms'] // 60000} 分 {m['duration_ms'] // 1000 % 60} 秒　"
                                               f"说话人：{m.get('speakers', '-')} 人"])
        return result

    # audio 任务：服务端已有音频文件
    def _pipeline_audio(self, job, options):
        path = Path(options.get("path", ""))
        if not path.is_file():
            raise JobError(f"音频文件不存在: {path}")
        title = options.get("title") or path.stem
        rendered = self._transcribe(job["id"], path, title, options)
        files = [rendered["md"], rendered["srt"], rendered["json"]]
        m = rendered["meta"]
        result = {"title": title, "url": "", "md": str(rendered["md"]),
                  "srt": str(rendered["srt"]), "meta": m, "analysis_md": None, "harvest": None,
                  "files": [str(f) for f in files]}
        result["email"] = self._email_deliver(job["id"], title, "", files, "【视频转写】",
                                              [f"时长：{m['duration_ms'] // 60000} 分 {m['duration_ms'] // 1000 % 60} 秒　"
                                               f"说话人：{m.get('speakers', '-')} 人"])
        return result

    # analyze 任务：扩展截帧（dataURL）→ VLM 分析 → 报告落盘 → 可选邮件
    def _pipeline_analyze(self, job, options):
        cfg = self.cfg
        jid = job["id"]
        images = options.get("images") or []
        if not images:
            raise JobError("没有收到任何截帧图片")
        self.log(jid, f"收到 {len(images)} 帧，调用视觉模型分析…")
        self._update(jid, progress=20.0)
        prompt = options.get("prompt") or ASSET_ANALYSIS_PROMPT
        transcript = options.get("transcript")
        if transcript:
            prompt += "\n\n--- 视频转写稿（节选前 6000 字）---\n" + transcript[:6000]
        report = vlm_analyze(cfg, prompt, images)
        self._update(jid, progress=80.0)
        out_dir = workdir(cfg) / "out" / jid
        out_dir.mkdir(parents=True, exist_ok=True)
        title = job.get("title") or "画面分析"
        report_path = out_dir / f"{_safe_name(title)}_分析.md"
        header = (f"# 视频画面分析：{title}\n\n"
                  f"- 帧数：{len(images)}（客户端截取）\n"
                  f"- 分析模型：{cfg.get('vlm_model')}\n"
                  f"- 来源：{job.get('url') or '-'}\n"
                  f"- 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
        report_path.write_text(header + report, encoding="utf-8")
        self._update(jid, progress=90.0)
        email_hint = {"sent": False, "reason": "邮件未启用"}
        if cfg["email"].get("enabled") and options.get("email", True):
            try:
                to = send_email(cfg, f"【画面分析】{title}",
                                f"《{title}》的画面分析完成，报告如下。\n\n{report}",
                                [report_path])
                email_hint = {"sent": True, "to": to}
                self.log(jid, f"📧 分析报告已发邮件 → {to}")
            except Exception as e:
                email_hint = {"sent": False, "reason": str(e)[:300]}
                self.log(jid, f"分析报告邮件失败: {e}")
        return {"title": title, "url": job.get("url", ""), "files": [str(report_path)],
                "md": str(report_path), "analysis_md": report, "email": email_hint,
                "meta": {"frames": len(images)}}


def _safe_name(s: str, limit: int = 60) -> str:
    s = re.sub(r'[\\/:*?"<>|\r\n]+', "_", s).strip(" ._")
    return s[:limit] or "untitled"
