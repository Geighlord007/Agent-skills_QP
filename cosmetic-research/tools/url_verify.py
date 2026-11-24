#!/usr/bin/env python3
"""
URL/PMID/Patent verification script for Cosmetic Research reports.

Scans markdown files for citations, verifies reachability and content
(using NCBI E-utilities batch API for PMIDs and domain-throttled concurrent
workers for patents/URLs), and produces a structured verification report.

Usage:
    python url_verify.py report.md
    python url_verify.py --deep report.md
    python url_verify.py --timeout 15 --output eval/url_report.md report.md
    python url_verify.py drafts/*.md
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
import glob
import io
from pathlib import Path
import re
import sys
import threading
import time
from urllib.parse import urlparse

import requests

# Fix Windows console encoding safely (never close underlying buffer on import)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# ── Constants ──────────────────────────────────────────────────────────────

PUBMED_BASE = "https://pubmed.ncbi.nlm.nih.gov"
NCBI_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PATENTS_BASE = "https://patents.google.com/patent"

OFFICIAL_DOMAINS = {
    # Regulators
    "nmpa.gov.cn": "官方数据库",
    "fda.gov": "官方数据库",
    "ec.europa.eu": "官方数据库",
    "mfds.go.kr": "官方数据库",
    "mhlw.go.jp": "官方数据库",
    "kca.or.kr": "官方数据库",
    "kca.go.kr": "官方数据库",
    "sec.gov": "官方数据库",
    # Academic
    "pubmed.ncbi.nlm.nih.gov": "同行评审",
    "ncbi.nlm.nih.gov": "同行评审",
    "doi.org": "同行评审",
    "scholar.google.com": "同行评审",
    # Patent offices
    "patents.google.com": "官方数据库",
    "uspto.gov": "官方数据库",
    "epo.org": "官方数据库",
    "wipo.int": "官方数据库",
}

COMMERCIAL_DOMAINS = {
    "prnewswire.com": "商业材料",
    "businesswire.com": "商业材料",
    "globenewswire.com": "商业材料",
    "biospace.com": "商业材料",
    "pressrelease": "商业材料",
}

SOCIAL_DOMAINS = {
    "mp.weixin.qq.com": "未验证",
    "weibo.com": "未验证",
    "xiaohongshu.com": "未验证",
    "reddit.com": "未验证",
    "twitter.com": "未验证",
    "x.com": "未验证",
    "youtube.com": "未验证",
    "bilibili.com": "未验证",
    "blogspot": "未验证",
    "medium.com": "未验证",
}

ANTI_HEAD_DOMAINS = {
    "nmpa.gov.cn",
    "massdevice.com",
    "specialchem.com",
    "worldwide.espacenet.com",
    "rootsbybenda.com",
}

JS_HEAVY_DOMAINS = {
    "nmpa.gov.cn",   # Requires session cookies + JS rendering
    "ec.europa.eu",  # CosIng SPA
    "mfds.go.kr",    # Korean regulator, JS-heavy
}


# ── Data structures ────────────────────────────────────────────────────────

@dataclass
class Citation:
    """A single citation extracted from a document."""
    kind: str          # "pmid" | "patent" | "url"
    value: str         # The PMID number / patent ID / URL
    context: str       # Surrounding text (newline-preserved for title matching)
    source_file: str   # Which file it came from
    line_number: int   # Line number in the file


@dataclass
class VerifyResult:
    """Result of verifying a single citation."""
    citation: Citation
    status: str        # "pass" | "manual_check" | "fail" | "timeout" | "error"
    source_type: str   # "同行评审" | "官方数据库" | "商业材料" | "未验证" | "其他"
    http_code: int | None = None
    fetched_title: str | None = None
    claimed_title: str | None = None
    title_match: bool | None = None
    error: str | None = None


# ── Extraction ─────────────────────────────────────────────────────────────

# PMID patterns: [PMID 25440437], PMID: 25440437, PMID 25440437
RE_PMID = re.compile(r"\bPMID\s*:?\s*(\d{7,9})\b", re.IGNORECASE)

# Patent patterns: US (7-8 digit granted, 11 digit pub), EP, WO, CN, JP, KR
RE_PATENT = re.compile(
    r"\b("
    r"US\d{11}[A-Z]\d?|"                  # US20210123456A1
    r"US\d{7,8}[A-Z]\d?|"                 # US7422734B2 / US10123456B2
    r"EP\d{7,8}[A-Z]\d?|"                 # EP1578806B1 / EP2338896A2
    r"WO\d{4}/\d{4,7}(?:[A-Z]\d)?|"       # WO2004/054503 / WO2020/123456A1
    r"WO\d{10,12}(?:[A-Z]\d)?|"           # WO2004054503 / WO2020123456A1
    r"CN\d{8,13}[A-Z]\d?|"                # CN112345678A / CN101234567B
    r"JP\d{7,12}[A-Z]\d?|"                # JP2020123456A / JP6789012B2
    r"KR\d{9,13}[A-Z]\d?"                 # KR1020200123456A / KR101234567B1
    r")\b"
)

# URL pattern
RE_URL = re.compile(r"https?://[^\s\)\]>\"']+")


def extract_citations(text: str, source_file: str) -> list[Citation]:
    """Extract all citations from markdown text."""
    citations: list[Citation] = []
    seen: set[tuple[str, str]] = set()

    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        for m in RE_PMID.finditer(line):
            key = ("pmid", m.group(1))
            if key not in seen:
                seen.add(key)
                citations.append(Citation(
                    kind="pmid", value=m.group(1),
                    context=_get_context(lines, i - 1),
                    source_file=source_file, line_number=i,
                ))

        for m in RE_PATENT.finditer(line):
            key = ("patent", m.group(1))
            if key not in seen:
                seen.add(key)
                citations.append(Citation(
                    kind="patent", value=m.group(1),
                    context=_get_context(lines, i - 1),
                    source_file=source_file, line_number=i,
                ))

        for m in RE_URL.finditer(line):
            url = m.group(0).rstrip(".,;:")
            key = ("url", url)
            if key not in seen:
                seen.add(key)
                citations.append(Citation(
                    kind="url", value=url,
                    context=_get_context(lines, i - 1),
                    source_file=source_file, line_number=i,
                ))

    return citations


def _get_context(lines: list[str], idx: int, window: int = 3) -> str:
    """Get surrounding lines as newline-preserved context."""
    start = max(0, idx - window)
    end = min(len(lines), idx + window + 1)
    return "\n".join(lines[start:end]).strip()[:500]


# ── Classification & Rate Limiting ─────────────────────────────────────────

def classify_url(url: str) -> str:
    """Classify a URL by source type."""
    domain = urlparse(url).netloc.lower()
    for official, label in OFFICIAL_DOMAINS.items():
        if official in domain:
            return label
    for commercial, label in COMMERCIAL_DOMAINS.items():
        if commercial in domain:
            return label
    for social, label in SOCIAL_DOMAINS.items():
        if social in domain:
            return label
    return "其他"


class DomainThrottle:
    """Thread-safe per-domain request throttler."""

    def __init__(self, delay: float):
        self.delay = max(0.0, delay)
        self._guard = threading.Lock()
        self._locks: dict[str, threading.Lock] = {}
        self._last_ts: dict[str, float] = {}

    def wait(self, domain: str) -> None:
        if self.delay <= 0:
            return
        with self._guard:
            lock = self._locks.setdefault(domain, threading.Lock())
        with lock:
            now = time.monotonic()
            last = self._last_ts.get(domain, 0.0)
            wait_s = self.delay - (now - last)
            if wait_s > 0:
                time.sleep(wait_s)
            self._last_ts[domain] = time.monotonic()


def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "CosmeticResearch/1.1 (URL verifier)",
        "Accept": "text/html,application/xhtml+xml,application/json",
    })
    return s


# ── Verification ───────────────────────────────────────────────────────────

def verify_pmids_batch(
    citations: list[Citation],
    session: requests.Session,
    timeout: int = 15,
    deep: bool = False,
) -> list[VerifyResult]:
    """Batch-verify PMIDs via NCBI E-utilities esummary.fcgi (up to 100/req)."""
    results: list[VerifyResult] = []
    chunk_size = 100

    for start in range(0, len(citations), chunk_size):
        chunk = citations[start:start + chunk_size]
        ids = ",".join(c.value for c in chunk)
        try:
            resp = session.get(
                NCBI_ESUMMARY,
                params={"db": "pubmed", "id": ids, "retmode": "json"},
                timeout=timeout,
            )
            if resp.status_code != 200:
                raise requests.RequestException(f"HTTP {resp.status_code}")
            payload = resp.json().get("result", {})
        except Exception:
            # Fallback to single-page PubMed HTML verification for this chunk
            for cit in chunk:
                claimed = _extract_claimed_title(cit.context) if deep else None
                res = verify_pubmed(cit.value, session, timeout=timeout,
                                    deep=deep, claimed_title=claimed)
                res.citation = cit
                results.append(res)
            continue

        for cit in chunk:
            entry = payload.get(cit.value)
            if not entry or "error" in entry:
                results.append(VerifyResult(
                    citation=cit, status="fail", source_type="同行评审",
                    http_code=404, error="PMID 不存在或已被移除",
                ))
                continue

            fetched_title = (entry.get("title") or "").strip().rstrip(".")
            res = VerifyResult(
                citation=cit, status="pass", source_type="同行评审",
                http_code=200, fetched_title=fetched_title or None,
            )
            if deep:
                claimed = _extract_claimed_title(cit.context)
                if claimed:
                    res.claimed_title = claimed
                    res.title_match = _titles_match(claimed, res.fetched_title)
            results.append(res)

    return results


def verify_pubmed(
    pmid: str,
    session: requests.Session,
    timeout: int = 10,
    deep: bool = False,
    claimed_title: str | None = None,
) -> VerifyResult:
    """Verify a single PMID via PubMed HTML page (fallback)."""
    citation = Citation(kind="pmid", value=pmid, context="", source_file="", line_number=0)
    url = f"{PUBMED_BASE}/{pmid}/"

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        if resp.status_code == 404:
            return VerifyResult(citation=citation, status="fail", source_type="同行评审",
                                http_code=404, error="PMID 不存在（404）")
        if resp.status_code != 200:
            return VerifyResult(citation=citation, status="fail", source_type="同行评审",
                                http_code=resp.status_code, error=f"HTTP {resp.status_code}")

        fetched_title = _extract_pubmed_title(resp.text)
        result = VerifyResult(citation=citation, status="pass", source_type="同行评审",
                              http_code=200, fetched_title=fetched_title)
        if deep and claimed_title:
            result.claimed_title = claimed_title
            result.title_match = _titles_match(claimed_title, fetched_title)
        return result
    except requests.Timeout:
        return VerifyResult(citation=citation, status="timeout", source_type="同行评审", error="连接超时")
    except requests.RequestException as e:
        return VerifyResult(citation=citation, status="error", source_type="同行评审", error=str(e))


def verify_patent(
    patent_id: str,
    session: requests.Session,
    timeout: int = 10,
) -> VerifyResult:
    """Verify a patent exists on Google Patents."""
    citation = Citation(kind="patent", value=patent_id, context="", source_file="", line_number=0)
    lookup_id = patent_id.replace("/", "")
    url = f"{PATENTS_BASE}/{lookup_id}"

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        if resp.status_code == 404:
            return VerifyResult(citation=citation, status="fail", source_type="官方数据库",
                                http_code=404, error="专利号不存在（404）")
        if resp.status_code == 200:
            if "not found" in resp.text.lower()[:2000]:
                return VerifyResult(citation=citation, status="fail", source_type="官方数据库",
                                    http_code=200, error="页面存在但专利未找到")
            return VerifyResult(citation=citation, status="pass", source_type="官方数据库", http_code=200)
        return VerifyResult(citation=citation, status="fail", source_type="官方数据库",
                            http_code=resp.status_code, error=f"HTTP {resp.status_code}")
    except requests.Timeout:
        return VerifyResult(citation=citation, status="timeout", source_type="官方数据库", error="连接超时")
    except requests.RequestException as e:
        return VerifyResult(citation=citation, status="error", source_type="官方数据库", error=str(e))


def verify_url(
    url: str,
    session: requests.Session,
    timeout: int = 10,
) -> VerifyResult:
    """Verify a generic URL is reachable."""
    citation = Citation(kind="url", value=url, context="", source_file="", line_number=0)
    source_type = classify_url(url)

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    is_js_heavy = any(d in host for d in JS_HEAVY_DOMAINS)
    use_get = any(d in host for d in ANTI_HEAD_DOMAINS)

    try:
        if use_get:
            resp = session.get(url, timeout=timeout, allow_redirects=True, stream=True)
            resp.close()
        else:
            resp = session.head(url, timeout=timeout, allow_redirects=True)
            if resp.status_code in (405, 403, 412):
                resp = session.get(url, timeout=timeout, allow_redirects=True, stream=True)
                resp.close()

        if resp.status_code >= 400:
            if is_js_heavy and resp.status_code in (403, 412):
                return VerifyResult(
                    citation=citation, status="manual_check", source_type=source_type,
                    http_code=resp.status_code,
                    error=f"HTTP {resp.status_code}（已知反爬/JS 站点，需浏览器人工确认）",
                )
            return VerifyResult(citation=citation, status="fail", source_type=source_type,
                                http_code=resp.status_code, error=f"HTTP {resp.status_code}")

        return VerifyResult(citation=citation, status="pass", source_type=source_type,
                            http_code=resp.status_code)
    except requests.Timeout:
        return VerifyResult(citation=citation, status="timeout", source_type=source_type, error="连接超时")
    except requests.TooManyRedirects:
        return VerifyResult(citation=citation, status="fail", source_type=source_type, error="重定向过多")
    except requests.RequestException as e:
        return VerifyResult(citation=citation, status="error", source_type=source_type, error=str(e))


# ── Helpers ────────────────────────────────────────────────────────────────

RE_TITLE_TAG = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _extract_pubmed_title(html: str) -> str | None:
    """Extract paper title from PubMed HTML."""
    m = RE_TITLE_TAG.search(html)
    if m:
        title = m.group(1).strip()
        title = re.sub(r"\s*[-–]\s*PubMed\s*$", "", title)
        return title
    return None


def _titles_match(claimed: str, fetched: str | None) -> bool:
    """Check if claimed and fetched titles roughly match."""
    if not fetched:
        return False

    def normalize(s: str) -> set[str]:
        return set(re.findall(r"[a-zA-Z]{3,}", s.lower()))

    claimed_words = normalize(claimed)
    fetched_words = normalize(fetched)
    if not claimed_words:
        return False
    return (len(claimed_words & fetched_words) / len(claimed_words)) >= 0.5


def _extract_claimed_title(context: str) -> str | None:
    """Try to extract a claimed paper title from newline-preserved surrounding context."""
    m = re.search(r"\|\s*\*?\*?标题\*?\*?\s*\|\s*([^\|\n]+?)\s*\|", context)
    if m:
        return m.group(1).strip()

    m = re.search(r"(?:标题|Title)\s*[：:]\s*([^\n]+)", context, re.IGNORECASE)
    if m:
        return m.group(1).strip().strip("*`")

    return None


def _expand_input_files(patterns: list[str]) -> list[str]:
    """Expand shell globs for Windows compatibility."""
    resolved: list[str] = []
    for pat in patterns:
        if any(ch in pat for ch in ("*", "?", "[")):
            matches = sorted(glob.glob(pat))
            if matches:
                resolved.extend(matches)
            else:
                resolved.append(pat)
        else:
            resolved.append(pat)
    return resolved


# ── Report generation ──────────────────────────────────────────────────────

def generate_report(results: list[VerifyResult], source_files: list[str]) -> str:
    """Generate a markdown verification report."""
    lines = [
        "## URL/PMID/专利验证报告",
        f"日期: {date.today().isoformat()}",
        f"源文件: {', '.join(source_files)}",
        "",
    ]

    total = len(results)
    pmids = [r for r in results if r.citation.kind == "pmid"]
    patents = [r for r in results if r.citation.kind == "patent"]
    urls = [r for r in results if r.citation.kind == "url"]

    passed = [r for r in results if r.status == "pass"]
    manual_checks = [r for r in results if r.status == "manual_check"]
    failed = [r for r in results if r.status == "fail"]
    timeouts = [r for r in results if r.status == "timeout"]
    errors = [r for r in results if r.status == "error"]
    problems = failed + timeouts + errors

    lines += [
        "### 统计",
        f"- 总引用数: {total}",
        f"- PMID: {len(pmids)} | 专利号: {len(patents)} | URL: {len(urls)}",
        f"- 通过: {len(passed)} | 需人工确认: {len(manual_checks)} | 失败: {len(failed)} | 超时: {len(timeouts)} | 错误: {len(errors)}",
        "",
    ]

    kind_label = {"pmid": "PMID", "patent": "专利", "url": "URL"}

    if problems:
        lines.append("### 问题项")
        lines.append("| # | 类型 | 标识 | 状态 | 文件:行 | 问题 |")
        lines.append("|---|------|------|------|---------|------|")
        status_label = {"fail": "失败", "timeout": "超时", "error": "错误"}
        for i, r in enumerate(problems, 1):
            loc = f"{Path(r.citation.source_file).name}:{r.citation.line_number}"
            val = r.citation.value if len(r.citation.value) <= 60 else r.citation.value[:57] + "..."
            lines.append(
                f"| {i} | {kind_label.get(r.citation.kind, '?')} "
                f"| `{val}` | {status_label.get(r.status, r.status)} "
                f"| {loc} | {r.error or ''} |"
            )
        lines.append("")

    if manual_checks:
        lines.append("### 需人工确认（反爬/JS 站点）")
        lines.append("| # | 类型 | 标识 | 文件:行 | 说明 |")
        lines.append("|---|------|------|---------|------|")
        for i, r in enumerate(manual_checks, 1):
            loc = f"{Path(r.citation.source_file).name}:{r.citation.line_number}"
            val = r.citation.value if len(r.citation.value) <= 60 else r.citation.value[:57] + "..."
            lines.append(
                f"| {i} | {kind_label.get(r.citation.kind, '?')} "
                f"| `{val}` | {loc} | {r.error or ''} |"
            )
        lines.append("")

    deep_results = [r for r in results if r.title_match is not None]
    title_mismatches = [r for r in deep_results if r.title_match is False]
    if deep_results:
        lines.append("### 深度验证（PMID 标题比对）")
        lines.append("| PMID | 报告声称标题 | 实际标题 | 匹配 |")
        lines.append("|------|-------------|----------|------|")
        for r in deep_results:
            claimed = (r.claimed_title or "")[:40]
            fetched = (r.fetched_title or "")[:40]
            match_icon = "✅" if r.title_match else "❌"
            lines.append(f"| {r.citation.value} | {claimed} | {fetched} | {match_icon} |")
        lines.append("")

    type_counts: dict[str, int] = {}
    for r in results:
        type_counts[r.source_type] = type_counts.get(r.source_type, 0) + 1

    if type_counts:
        lines.append("### 来源类型分布")
        lines.append("| 类型 | 数量 | 占比 | 图标 |")
        lines.append("|------|------|------|------|")
        icons = {
            "同行评审": "✅", "官方数据库": "✅",
            "商业材料": "📋", "未验证": "🔍", "其他": "❓",
        }
        for stype in ["同行评审", "官方数据库", "商业材料", "未验证", "其他"]:
            count = type_counts.get(stype, 0)
            if count > 0:
                pct = f"{count / total * 100:.0f}%"
                lines.append(f"| {stype} | {count} | {pct} | {icons.get(stype, '?')} |")
        lines.append("")

    if problems or title_mismatches:
        parts = []
        if problems:
            parts.append(f"{len(problems)} 项验证失败/异常")
        if title_mismatches:
            parts.append(f"{len(title_mismatches)} 项 PMID 标题不匹配")
        if manual_checks:
            parts.append(f"{len(manual_checks)} 项需人工确认")
        lines.append(f"**需要关注：{'，'.join(parts)}。** 请检查上方明细。")
    elif manual_checks:
        lines.append(f"**无硬性失败，但有 {len(manual_checks)} 项反爬站点需浏览器人工确认。**")
    else:
        lines.append("**全部引用验证通过。**")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify URLs, PMIDs, and patent numbers in markdown reports."
    )
    parser.add_argument("files", nargs="+", help="Markdown files or globs to verify")
    parser.add_argument("--deep", action="store_true",
                        help="Deep verification: compare claimed vs actual PMID titles")
    parser.add_argument("--timeout", type=int, default=10,
                        help="HTTP timeout in seconds (default: 10)")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path (default: stdout only)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Per-domain delay between requests in seconds (default: 0.5)")
    parser.add_argument("--workers", type=int, default=6,
                        help="Concurrent worker threads for patents/URLs (default: 6)")
    args = parser.parse_args()

    input_files = _expand_input_files(args.files)
    all_citations: list[Citation] = []
    for filepath in input_files:
        path = Path(filepath)
        if not path.exists():
            print(f"警告: {filepath} 不存在，跳过", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        all_citations.extend(extract_citations(text, filepath))

    if not all_citations:
        print("未找到任何引用（PMID/专利号/URL）。")
        return

    print(f"找到 {len(all_citations)} 个引用，开始验证...\n")

    pmid_cits = [(idx, c) for idx, c in enumerate(all_citations) if c.kind == "pmid"]
    other_cits = [(idx, c) for idx, c in enumerate(all_citations) if c.kind != "pmid"]
    ordered_results: list[VerifyResult | None] = [None] * len(all_citations)
    status_icons = {
        "pass": "✅",
        "manual_check": "🔎",
        "fail": "❌",
        "timeout": "⏱️",
        "error": "⚠️",
    }

    def _log_result(idx: int, result: VerifyResult) -> None:
        detail = result.error or (f"HTTP {result.http_code}" if result.http_code else "")
        print(
            f"  [{idx + 1}/{len(all_citations)}] {result.citation.kind}: "
            f"{result.citation.value[:60]}... {status_icons.get(result.status, '?')} {detail}",
            flush=True,
        )

    # 1) Batch verify PMIDs via NCBI E-utilities
    if pmid_cits:
        batch_session = _make_session()
        batch_res = verify_pmids_batch(
            [c for _, c in pmid_cits], batch_session, timeout=max(args.timeout, 15), deep=args.deep
        )
        for (idx, _), res in zip(pmid_cits, batch_res):
            ordered_results[idx] = res
            _log_result(idx, res)

    # 2) Concurrently verify patents and generic URLs with per-domain throttling
    if other_cits:
        throttle = DomainThrottle(args.delay)
        thread_local = threading.local()

        def _worker(idx: int, cit: Citation) -> tuple[int, VerifyResult]:
            sess = getattr(thread_local, "session", None)
            if sess is None:
                sess = _make_session()
                thread_local.session = sess
            domain = "patents.google.com" if cit.kind == "patent" else urlparse(cit.value).netloc.lower()
            throttle.wait(domain)
            if cit.kind == "patent":
                res = verify_patent(cit.value, sess, args.timeout)
            else:
                res = verify_url(cit.value, sess, args.timeout)
            res.citation = cit
            return idx, res

        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = [pool.submit(_worker, idx, cit) for idx, cit in other_cits]
            for fut in as_completed(futures):
                idx, res = fut.result()
                ordered_results[idx] = res
                _log_result(idx, res)

    results = [r for r in ordered_results if r is not None]
    report = generate_report(results, input_files)
    print("\n" + report)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\n报告已写入: {args.output}")

    hard_failures = sum(
        1 for r in results
        if r.status in ("fail", "timeout", "error") or r.title_match is False
    )
    sys.exit(hard_failures)


if __name__ == "__main__":
    main()
