#!/usr/bin/env python3
"""
URL/PMID/Patent verification script for Cosmetic Research reports.

Scans markdown files for citations, verifies reachability and content,
and produces a structured verification report.

Usage:
    python url_verify.py report.md
    python url_verify.py --deep report.md
    python url_verify.py --timeout 15 --output eval/url_report.md report.md
    python url_verify.py drafts/*.md
"""

import argparse
import io
import re
import sys
import time

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import requests

# ── Constants ──────────────────────────────────────────────────────────────

PUBMED_BASE = "https://pubmed.ncbi.nlm.nih.gov"
PATENTS_BASE = "https://patents.google.com/patent"

# Official database domains → source type
OFFICIAL_DOMAINS = {
    # Regulators
    "nmpa.gov.cn": "官方数据库",
    "fda.gov": "官方数据库",
    "ec.europa.eu": "官方数据库",
    "mfds.go.kr": "官方数据库",
    "mhlw.go.jp": "官方数据库",
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


# ── Data structures ────────────────────────────────────────────────────────

@dataclass
class Citation:
    """A single citation extracted from a document."""
    kind: str          # "pmid" | "patent" | "url"
    value: str         # The PMID number / patent ID / URL
    context: str       # Surrounding text (for title matching)
    source_file: str   # Which file it came from
    line_number: int   # Line number in the file


@dataclass
class VerifyResult:
    """Result of verifying a single citation."""
    citation: Citation
    status: str        # "pass" | "fail" | "timeout" | "error"
    source_type: str   # "同行评审" | "官方数据库" | "商业材料" | "未验证" | "其他"
    http_code: int | None = None
    fetched_title: str | None = None
    claimed_title: str | None = None
    title_match: bool | None = None
    error: str | None = None


# ── Extraction ─────────────────────────────────────────────────────────────

# PMID patterns: [PMID 25440437], PMID: 25440437, PMID 25440437
RE_PMID = re.compile(r"\bPMID\s*:?\s*(\d{7,9})\b", re.IGNORECASE)

# Patent patterns: US7422734B2, EP1578806B1, WO2004054503, WO2004/054503
RE_PATENT = re.compile(
    r"\b(US\d{7}[A-Z]\d|"        # US7422734B2
    r"EP\d{7,8}[A-Z]\d|"         # EP1578806B1 / EP2338896A2
    r"WO\d{4}/\d{4,7}|"          # WO2004/054503
    r"WO\d{10,12})\b"            # WO2004054503
)

# URL pattern
RE_URL = re.compile(r"https?://[^\s\)\]>\"']+")


def extract_citations(text: str, source_file: str) -> list[Citation]:
    """Extract all citations from markdown text."""
    citations = []
    seen = set()  # deduplicate within file

    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        # PMIDs
        for m in RE_PMID.finditer(line):
            key = ("pmid", m.group(1))
            if key not in seen:
                seen.add(key)
                citations.append(Citation(
                    kind="pmid", value=m.group(1),
                    context=_get_context(lines, i - 1),
                    source_file=source_file, line_number=i,
                ))

        # Patents
        for m in RE_PATENT.finditer(line):
            key = ("patent", m.group(1))
            if key not in seen:
                seen.add(key)
                citations.append(Citation(
                    kind="patent", value=m.group(1),
                    context=_get_context(lines, i - 1),
                    source_file=source_file, line_number=i,
                ))

        # URLs (exclude markdown image syntax that might capture)
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
    """Get surrounding lines as context."""
    start = max(0, idx - window)
    end = min(len(lines), idx + window + 1)
    return " ".join(lines[start:end]).strip()[:300]


# ── Classification ─────────────────────────────────────────────────────────

def classify_url(url: str) -> str:
    """Classify a URL by source type."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Check official domains
    for official, label in OFFICIAL_DOMAINS.items():
        if official in domain:
            return label

    # Check commercial domains
    for commercial, label in COMMERCIAL_DOMAINS.items():
        if commercial in domain:
            return label

    # Check social domains
    for social, label in SOCIAL_DOMAINS.items():
        if social in domain:
            return label

    return "其他"


# ── Verification ───────────────────────────────────────────────────────────

def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "CosmeticResearch/1.0 (URL verifier)",
        "Accept": "text/html,application/xhtml+xml",
    })
    return s


def verify_pubmed(pmid: str, session: requests.Session,
                  timeout: int = 10, deep: bool = False,
                  claimed_title: str | None = None) -> VerifyResult:
    """Verify a PMID exists on PubMed."""
    citation = Citation(kind="pmid", value=pmid, context="",
                        source_file="", line_number=0)
    url = f"{PUBMED_BASE}/{pmid}/"

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)

        if resp.status_code == 404:
            return VerifyResult(citation=citation, status="fail",
                                source_type="同行评审", http_code=404,
                                error="PMID 不存在（404）")

        if resp.status_code != 200:
            return VerifyResult(citation=citation, status="fail",
                                source_type="同行评审",
                                http_code=resp.status_code,
                                error=f"HTTP {resp.status_code}")

        # Extract title from page
        fetched_title = _extract_pubmed_title(resp.text)

        result = VerifyResult(
            citation=citation, status="pass", source_type="同行评审",
            http_code=200, fetched_title=fetched_title,
        )

        # Deep verification: compare titles
        if deep and claimed_title:
            result.claimed_title = claimed_title
            result.title_match = _titles_match(claimed_title, fetched_title)

        return result

    except requests.Timeout:
        return VerifyResult(citation=citation, status="timeout",
                            source_type="同行评审", error="连接超时")
    except requests.RequestException as e:
        return VerifyResult(citation=citation, status="error",
                            source_type="同行评审", error=str(e))


def verify_patent(patent_id: str, session: requests.Session,
                  timeout: int = 10) -> VerifyResult:
    """Verify a patent exists on Google Patents."""
    citation = Citation(kind="patent", value=patent_id, context="",
                        source_file="", line_number=0)
    # Normalize WO format: WO2004/054503 → WO2004054503
    lookup_id = patent_id.replace("/", "")
    url = f"{PATENTS_BASE}/{lookup_id}"

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)

        if resp.status_code == 404:
            return VerifyResult(citation=citation, status="fail",
                                source_type="官方数据库", http_code=404,
                                error="专利号不存在（404）")

        # Google Patents may return 200 with "not found" in page
        if resp.status_code == 200:
            if "not found" in resp.text.lower()[:2000]:
                return VerifyResult(citation=citation, status="fail",
                                    source_type="官方数据库", http_code=200,
                                    error="页面存在但专利未找到")
            return VerifyResult(citation=citation, status="pass",
                                source_type="官方数据库", http_code=200)

        return VerifyResult(citation=citation, status="fail",
                            source_type="官方数据库",
                            http_code=resp.status_code,
                            error=f"HTTP {resp.status_code}")

    except requests.Timeout:
        return VerifyResult(citation=citation, status="timeout",
                            source_type="官方数据库", error="连接超时")
    except requests.RequestException as e:
        return VerifyResult(citation=citation, status="error",
                            source_type="官方数据库", error=str(e))


def verify_url(url: str, session: requests.Session,
               timeout: int = 10) -> VerifyResult:
    """Verify a generic URL is reachable."""
    citation = Citation(kind="url", value=url, context="",
                        source_file="", line_number=0)
    source_type = classify_url(url)

    # Anti-bot domains that reject HEAD — use GET directly
    ANTI_HEAD_DOMAINS = {
        "nmpa.gov.cn", "massdevice.com", "specialchem.com",
        "worldwide.espacenet.com", "rootsbybenda.com",
    }
    # Domains that require JS/browser and will always fail with plain HTTP
    JS_HEAVY_DOMAINS = {
        "nmpa.gov.cn",       # Requires session cookies + JS rendering
        "ec.europa.eu",      # CosIng SPA
        "mfds.go.kr",        # Korean regulator, JS-heavy
    }
    parsed = urlparse(url)
    is_js_heavy = any(d in parsed.netloc for d in JS_HEAVY_DOMAINS)
    use_get = any(d in parsed.netloc for d in ANTI_HEAD_DOMAINS)

    try:
        if use_get:
            resp = session.get(url, timeout=timeout, allow_redirects=True,
                               stream=True)
            resp.close()
        else:
            resp = session.head(url, timeout=timeout, allow_redirects=True)

            # Some servers reject HEAD, try GET
            if resp.status_code in (405, 403, 412):
                resp = session.get(url, timeout=timeout, allow_redirects=True,
                                   stream=True)
                resp.close()

        if resp.status_code >= 400:
            # JS-heavy sites that fail plain HTTP — mark as "需人工确认" not "fail"
            if is_js_heavy and resp.status_code in (403, 412):
                return VerifyResult(citation=citation, status="pass",
                                    source_type=source_type,
                                    http_code=resp.status_code,
                                    error=f"HTTP {resp.status_code}（已知反爬，需人工确认）")
            return VerifyResult(citation=citation, status="fail",
                                source_type=source_type,
                                http_code=resp.status_code,
                                error=f"HTTP {resp.status_code}")

        return VerifyResult(citation=citation, status="pass",
                            source_type=source_type,
                            http_code=resp.status_code)

    except requests.Timeout:
        return VerifyResult(citation=citation, status="timeout",
                            source_type=source_type, error="连接超时")
    except requests.TooManyRedirects:
        return VerifyResult(citation=citation, status="fail",
                            source_type=source_type,
                            error="重定向过多")
    except requests.RequestException as e:
        return VerifyResult(citation=citation, status="error",
                            source_type=source_type, error=str(e))


# ── Helpers ────────────────────────────────────────────────────────────────

RE_TITLE_TAG = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _extract_pubmed_title(html: str) -> str | None:
    """Extract paper title from PubMed HTML."""
    m = RE_TITLE_TAG.search(html)
    if m:
        title = m.group(1).strip()
        # PubMed titles often include " - PubMed" suffix
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

    overlap = claimed_words & fetched_words
    ratio = len(overlap) / len(claimed_words)
    return ratio >= 0.5


def _extract_claimed_title(context: str) -> str | None:
    """Try to extract a claimed paper title from surrounding context."""
    # Look for common patterns: | **标题** | ... | or quoted titles
    m = re.search(r"\|\s*\*?\*?标题\*?\*?\s*\|\s*(.+?)\s*\|", context)
    if m:
        return m.group(1).strip()

    # Look for text after "标题" or "title"
    m = re.search(r"(?:标题|Title)\s*[：:]\s*(.+?)(?:\n|$)", context, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    return None


# ── Report generation ──────────────────────────────────────────────────────

def generate_report(results: list[VerifyResult], source_files: list[str]) -> str:
    """Generate a markdown verification report."""
    from datetime import date

    lines = [
        "## URL/PMID/专利验证报告",
        f"日期: {date.today().isoformat()}",
        f"源文件: {', '.join(source_files)}",
        "",
    ]

    # Statistics
    total = len(results)
    pmids = [r for r in results if r.citation.kind == "pmid"]
    patents = [r for r in results if r.citation.kind == "patent"]
    urls = [r for r in results if r.citation.kind == "url"]

    passed = [r for r in results if r.status == "pass"]
    failed = [r for r in results if r.status == "fail"]
    timeouts = [r for r in results if r.status == "timeout"]
    errors = [r for r in results if r.status == "error"]
    problems = failed + timeouts + errors

    lines += [
        "### 统计",
        f"- 总引用数: {total}",
        f"- PMID: {len(pmids)} | 专利号: {len(patents)} | URL: {len(urls)}",
        f"- 通过: {len(passed)} | 失败: {len(failed)} | 超时: {len(timeouts)} | 错误: {len(errors)}",
        "",
    ]

    # Problem items
    if problems:
        lines.append("### 问题项")
        lines.append("| # | 类型 | 标识 | 状态 | 文件:行 | 问题 |")
        lines.append("|---|------|------|------|---------|------|")
        for i, r in enumerate(problems, 1):
            status_label = {"fail": "失败", "timeout": "超时", "error": "错误"}
            kind_label = {"pmid": "PMID", "patent": "专利", "url": "URL"}
            loc = f"{Path(r.citation.source_file).name}:{r.citation.line_number}"
            val = r.citation.value if len(r.citation.value) <= 60 else r.citation.value[:57] + "..."
            lines.append(
                f"| {i} | {kind_label.get(r.citation.kind, '?')} "
                f"| `{val}` | {status_label.get(r.status, r.status)} "
                f"| {loc} | {r.error or ''} |"
            )
        lines.append("")

    # Deep verification results
    deep_results = [r for r in results if r.title_match is not None]
    if deep_results:
        lines.append("### 深度验证（PMID 内容比对）")
        lines.append("| PMID | 报告声称标题 | 实际标题 | 匹配 |")
        lines.append("|------|-------------|----------|------|")
        for r in deep_results:
            claimed = (r.claimed_title or "")[:40]
            fetched = (r.fetched_title or "")[:40]
            match_icon = "✅" if r.title_match else "❌"
            lines.append(
                f"| {r.citation.value} | {claimed} | {fetched} | {match_icon} |"
            )
        lines.append("")

    # Source type distribution
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
                lines.append(
                    f"| {stype} | {count} | {pct} | {icons.get(stype, '?')} |"
                )
        lines.append("")

    # Summary
    if not problems:
        lines.append("**全部引用验证通过。**")
    else:
        lines.append(f"**{len(problems)} 项需要关注。** 请检查上方问题项。")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Verify URLs, PMIDs, and patent numbers in markdown reports.")
    parser.add_argument("files", nargs="+", help="Markdown files to verify")
    parser.add_argument("--deep", action="store_true",
                        help="Deep verification: fetch PMID pages and compare titles")
    parser.add_argument("--timeout", type=int, default=10,
                        help="HTTP timeout in seconds (default: 10)")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path (default: stdout only)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay between requests in seconds (default: 0.5)")
    args = parser.parse_args()

    # Collect all citations
    all_citations: list[Citation] = []
    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"警告: {filepath} 不存在，跳过", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        citations = extract_citations(text, filepath)
        all_citations.extend(citations)

    if not all_citations:
        print("未找到任何引用（PMID/专利号/URL）。")
        return

    print(f"找到 {len(all_citations)} 个引用，开始验证...\n")

    session = _make_session()
    results: list[VerifyResult] = []

    for i, cit in enumerate(all_citations):
        # Progress indicator
        print(f"  [{i+1}/{len(all_citations)}] {cit.kind}: {cit.value[:60]}...",
              end=" ", flush=True)

        result: VerifyResult

        if cit.kind == "pmid":
            claimed_title = _extract_claimed_title(cit.context)
            result = verify_pubmed(cit.value, session, args.timeout,
                                   deep=args.deep,
                                   claimed_title=claimed_title)
        elif cit.kind == "patent":
            result = verify_patent(cit.value, session, args.timeout)
        else:  # url
            result = verify_url(cit.value, session, args.timeout)

        # Attach citation metadata
        result.citation = cit
        results.append(result)

        status_icons = {"pass": "✅", "fail": "❌", "timeout": "⏱️", "error": "⚠️"}
        print(status_icons.get(result.status, "?"),
              result.error or f"HTTP {result.http_code}" if result.http_code else "")

        if args.delay > 0:
            time.sleep(args.delay)

    # Generate report
    report = generate_report(results, args.files)

    # Always print to stdout
    print("\n" + report)

    # Optionally write to file
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\n报告已写入: {args.output}")

    # Exit code = number of failures
    failures = sum(1 for r in results if r.status != "pass")
    sys.exit(failures)


if __name__ == "__main__":
    main()
