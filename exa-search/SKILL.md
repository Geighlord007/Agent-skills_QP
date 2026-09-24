---
name: exa-search
description: Dual-engine web search — Xiaomi MiMo server-side web_search (Chinese/CN web) and Exa (global/semantic). ROUTING — Chinese-language or China-topic queries (国内新闻/天气/政策/公司/人物/价格/.cn) go to mimo.mjs FIRST (preferred default); overseas/English/semantic/technical queries go to exa.mjs; an explicit user override ("用 exa" / "用 mimo") always wins. Use for ANY web search need — weather, news, facts, prices, docs — plus Exa-only extras (page contents, similar pages, cited answers). Use when built-in WebSearch is insufficient or unavailable.
---

# Web Search: MiMo + Exa

Zero-dependency Node CLIs (Node 18+), two engines behind one skill:

- **MiMo** (`scripts/mimo.mjs`) — Xiaomi MiMo server-side `web_search` tool. Returns a
  synthesized cited answer in one call. Cheap (¥16/1000 次 per official pay-as-you-go),
  strong on the Chinese web. Account must have the 联网服务 plugin enabled.
- **Exa** (`scripts/exa.mjs`) — api.exa.ai. Returns raw results with highlights; strong
  on overseas/English/semantic search. Dynamic Highlights on by default (~4x token saving).

## Routing — follow this EVERY time

1. User names an engine ("用 exa 搜…" / "用 mimo 搜…") → use exactly that engine. No
   re-routing, no fallback without asking.
2. Query is in Chinese OR about the Chinese web (国内新闻、天气、政策、公司、人物、
   价格、.cn sites) → `mimo.mjs search`.
3. Anything else (English, overseas sources, semantic/technical search, papers) → `exa.mjs search`.
4. Unsure → `mimo.mjs` (user preference: MiMo first).

When you need raw source rows instead of a synthesized answer (to read sources yourself,
or to fetch pages afterwards), prefer Exa even for Chinese topics — unless the user said
MiMo. When one engine errors, say so and offer the other; never silently swap engines.

## MiMo commands

```bash
# Cited answer + citation list (default: force search, mimo-v2.6-flash)
node "%USERPROFILE%\.agents\skills\exa-search\scripts\mimo.mjs" search "上海今天天气"

# Pro model, wider coverage
node mimo.mjs search "2026年合成生物学最新政策" --model pro --maxkw 8 --limit 10

# Raw citation rows only, or the full API response
node mimo.mjs search "今天有什么科技新闻" --cites
node mimo.mjs search "小米 SU7 销量" --json
```

| Flag | Meaning |
|---|---|
| `--model flash\|pro\|<model-id>` | `flash` (default, cheap/fast) or `pro` |
| `--maxkw N` | max search keywords per call, 1–50 (default 5) |
| `--limit N` | max results per search, 1–50 (default 5) |
| `--no-force` | let the model decide whether to search (default: force) |
| `--cites` | print only the citation list |
| `--json` | print the raw API response |

Output: answer text, then `Citations (n)` with title/site/date/URL, then `usage:` line
(`searches`, `pages`, token counts) — the usage line tells you what the call may cost.

## Exa commands

```bash
# Web search (default: 6 results, type=auto, Dynamic Highlights on)
node "%USERPROFILE%\.agents\skills\exa-search\scripts\exa.mjs" search "how do Cloudflare Workers free tier limits work"

# More results, neural mode, include full page text
node exa.mjs search "TiDB Cloud serverless free tier" --num 10 --type neural --text

# Category-focused search (news | github | pdf | paper | tweet | company | ...)
node exa.mjs search "GLM-5.2 release notes" --category news

# Fetch contents of specific URLs (full text / highlights)
node exa.mjs contents "https://vercel.com/docs/functions" "https://developers.cloudflare.com/d1/" --text

# Find pages similar to a URL
node exa.mjs similar "https://developers.cloudflare.com/d1/" --num 5

# Synthesized answer with citations
node exa.mjs answer "which free database tiers support MySQL in 2026"
```

| Flag | Applies to | Meaning |
|---|---|---|
| `--num N` / `-n N` | search, similar | Number of results (default 6) |
| `--type T` | search | `auto` (default), `keyword`, `neural`, `fast`, `instant`, `deep-lite`, `deep`, `deep-reasoning` (slow: 4–40 s, avoid in daily use) |
| `--text` | search, contents, similar | Include full page text (capped by `--maxchars`, default 1000) |
| `--maxchars N` | search, contents | Max characters of page text per result |
| `--no-dynamic` | search, contents, similar | Turn Dynamic Highlights off (default: ON via `Exa-Beta: dynamic-highlights-2026-08-28`) |
| `--hlchars N` | search, contents, similar | Per-page highlight cap with dynamic off (mutually exclusive with dynamic) |
| `--category C` | search | Exa category filter |
| `--json` | all | Print raw JSON instead of formatted text |
| `--livecrawl` | search, contents | Force live crawl instead of cached content |

Dynamic Highlights allocates one shared highlight budget across all returned pages
(measured ~4x fewer highlight chars than Exa's default). Do not combine it with a static
per-page cap — the CLI enforces this: `--hlchars` implies `--no-dynamic`.

## Output (Exa text mode)

Each result: index, title, URL, publish date, then highlight snippet(s) and optionally a
text excerpt. `--json` prints the raw Exa response.

## Config & keys

`config.json` next to this file (git-ignored — NEVER commit it; see `config.example.json`).
Resolution order:

| Engine | Key sources (first wins) |
|---|---|
| Exa | `EXA_API_KEY` env → `config.json` `apiKey` |
| MiMo | `MIMO_API_KEY` env → `config.json` `mimoApiKey` → `~/.agents/keys/mimo.key` |

Never print key values in chat, logs, or docs. Optional config fields: `baseUrl`,
`defaultNumResults`, `defaultType`, `mimoBaseUrl`, `mimoModel`.

## Error handling

- `401` — key invalid/expired: check the engine's key source (do not echo its value).
- MiMo `web_search` errors mentioning 联网/plugin — the account lacks the 联网服务 plugin.
- `429` — rate limited; wait and retry, reduce `--num` / `--limit`.
- `5xx` / network error — retry once; if persistent, offer the OTHER engine and let the
  user decide (built-in WebSearch is unavailable in this setup).
