#!/usr/bin/env node
// Exa REST API CLI — zero dependencies, Node 18+.
// Key resolution: EXA_API_KEY env var > config.json `apiKey` > ~/.agents/keys/exa.key.
// The key value must never be echoed in output.
//
// Highlights default to Exa **Dynamic Highlights** (beta): one shared budget
// allocated across all returned pages (measured ~4x fewer highlight chars than
// Exa's default bulk output). Every `dynamic: true` request must carry the
// `Exa-Beta: dynamic-highlights-2026-08-28` header or Exa answers HTTP 400.
// `highlightsPerUrl` is deliberately NOT sent — measured dead (Exa ignores it;
// values 1 and 5 return byte-identical payloads).

import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = join(__dirname, '..', 'config.json');
const FALLBACK_KEY_PATH = join(homedir(), '.agents', 'keys', 'exa.key');
const DYNAMIC_BETA_HEADER = 'Exa-Beta';
const DYNAMIC_BETA_VALUE = 'dynamic-highlights-2026-08-28';
const DEFAULT_TIMEOUT_MS = 30_000;
const SLOW_TIMEOUT_MS = 60_000;

const HELP = `
Exa search CLI
  exa.mjs search   "query"         [--num N] [--type auto|keyword|neural|fast|instant|deep-lite|deep|deep-reasoning]
                                   [--text] [--maxchars N] [--no-dynamic | --hlchars N]
                                   [--category news|github|pdf|paper|tweet|company|...]
                                   [--livecrawl] [--json]
  exa.mjs contents "url" ["url2"]  [--text] [--maxchars N] [--no-dynamic | --hlchars N] [--livecrawl] [--json]
  exa.mjs similar  "url"           [--num N] [--text] [--maxchars N] [--no-dynamic | --hlchars N] [--json]
  exa.mjs answer   "query"         [--json]

  --no-dynamic   turn Dynamic Highlights off (default: on, sends the Exa-Beta header)
  --hlchars N    per-page highlight cap when dynamic is off (the two are mutually exclusive)
  -h, --help     show this help message
`;

function loadConfig() {
	let raw;
	try {
		raw = readFileSync(CONFIG_PATH, 'utf8');
	} catch {
		return {};
	}
	try {
		return JSON.parse(raw);
	} catch (err) {
		console.error(`WARN: failed to parse ${CONFIG_PATH}: ${err.message}`);
		return {};
	}
}

function resolveKey(config) {
	if (process.env.EXA_API_KEY && process.env.EXA_API_KEY.trim().length > 0) {
		return { key: process.env.EXA_API_KEY.trim(), source: 'EXA_API_KEY env' };
	}
	if (config.apiKey && String(config.apiKey).trim().length > 0) {
		return { key: String(config.apiKey).trim(), source: 'config.json' };
	}
	try {
		const raw = readFileSync(FALLBACK_KEY_PATH, 'utf8').trim();
		if (raw.length > 0) return { key: raw, source: '~/.agents/keys/exa.key' };
	} catch { /* ignore */ }
	return { key: '', source: '' };
}

function posInt(flag, raw) {
	const n = Number(raw);
	if (!Number.isInteger(n) || n <= 0) { console.error(`ERROR: ${flag} must be a positive integer`); process.exit(2); }
	return n;
}

function parseArgs(argv) {
	const positional = [], flags = {};
	for (let i = 0; i < argv.length; i++) {
		const a = argv[i];
		if (a === '-h' || a === '--help') flags.help = true;
		else if (a === '--num' || a === '-n') flags.num = posInt(a, argv[++i]);
		else if (a === '--type') flags.type = argv[++i];
		else if (a === '--category') flags.category = argv[++i];
		else if (a === '--maxchars') flags.maxchars = posInt(a, argv[++i]);
		else if (a === '--hlchars') flags.hlchars = posInt(a, argv[++i]);
		else if (a === '--no-dynamic') flags.nodynamic = true;
		else if (a === '--text') flags.text = true;
		else if (a === '--livecrawl') flags.livecrawl = true;
		else if (a === '--json') flags.json = true;
		else if (a.startsWith('-')) { console.error(`ERROR: unknown option "${a}"`); process.exit(2); }
		else positional.push(a);
	}
	return { positional, flags };
}

// Dynamic Highlights on unless explicitly disabled or a static cap is requested:
// Exa's docs warn against sending `dynamic` and `maxCharacters` together.
function dynamicHighlightsOn(flags) {
	return !flags.nodynamic && flags.hlchars === undefined;
}

function contentsSpec(flags) {
	const spec = {};
	if (dynamicHighlightsOn(flags)) spec.highlights = { dynamic: true };
	else if (flags.hlchars !== undefined) spec.highlights = { maxCharacters: flags.hlchars };
	else spec.highlights = true;
	if (flags.text || flags.maxchars !== undefined) spec.text = { maxCharacters: flags.maxchars || 1000 };
	if (flags.livecrawl) spec.livecrawl = 'always';
	return spec;
}

async function callExa(config, keyInfo, path, body, opts = {}) {
	if (!keyInfo.key) {
		console.error('ERROR: no Exa API key. Set EXA_API_KEY, put apiKey in config.json, or create ~/.agents/keys/exa.key.');
		process.exit(2);
	}
	const timeoutMs = opts.timeoutMs || DEFAULT_TIMEOUT_MS;
	let res;
	try {
		res = await fetch(`${(config.baseUrl || 'https://api.exa.ai').replace(/\/+$/, '')}${path}`, {
			method: 'POST',
			headers: {
				authorization: `Bearer ${keyInfo.key}`,
				'content-type': 'application/json',
				accept: 'application/json',
				...(opts.dynamicHighlights ? { [DYNAMIC_BETA_HEADER]: DYNAMIC_BETA_VALUE } : {}),
			},
			body: JSON.stringify(body),
			signal: AbortSignal.timeout(timeoutMs),
		});
	} catch (err) {
		if (err && err.name === 'TimeoutError') {
			console.error(`ERROR: Exa request timed out after ${Math.round(timeoutMs / 1000)}s.`);
		} else {
			console.error(`ERROR: network failure calling Exa: ${err.message}`);
		}
		process.exit(1);
	}
	const raw = await res.text();
	if (!res.ok) {
		let detail = raw.slice(0, 500);
		try {
			const parsed = JSON.parse(raw);
			detail = parsed.error || parsed.message || parsed.detail || detail;
		} catch { /* keep raw slice */ }
		console.error(`ERROR: Exa API returned HTTP ${res.status}: ${detail}`);
		if (res.status === 401) {
			console.error(`Hint: your Exa API key (from ${keyInfo.source}) is invalid or expired (check https://dashboard.exa.ai).`);
		}
		if (res.status === 429) console.error('Hint: rate limited — wait a moment or lower --num.');
		process.exit(1);
	}
	try {
		return JSON.parse(raw);
	} catch {
		console.error('ERROR: Exa returned a non-JSON body.');
		process.exit(1);
	}
}

function trim(s, n = 280) {
	const line = String(s || '').replace(/\s+/g, ' ').trim();
	return line.length > n ? `${line.slice(0, n)}…` : line;
}

function printResult(r, i, flags) {
	console.log(`\n[${i}] ${r.title || '(no title)'}`);
	console.log(`    ${r.url}${r.publishedDate ? `  ·  ${r.publishedDate.slice(0, 10)}` : ''}`);
	const hl = (r.highlights || []).filter((h) => h && h.trim());
	const hlCap = flags.hlchars || (dynamicHighlightsOn(flags) ? 1200 : 280);
	const shownHl = (flags.hlchars || dynamicHighlightsOn(flags)) ? hl : hl.slice(0, 2);
	for (const h of shownHl) console.log(`    » ${trim(h, hlCap)}`);
	if ((flags.text || flags.maxchars !== undefined) && r.text) {
		const textCap = flags.maxchars || 1000;
		console.log(`    ▸ ${trim(r.text, textCap)}`);
	}
	if (!hl.length && !r.text) console.log('    » (no highlight returned)');
}

async function main() {
	const config = loadConfig();
	const keyInfo = resolveKey(config);
	const [cmd, ...rest] = process.argv.slice(2);
	if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') {
		console.log(HELP);
		process.exit(0);
	}
	const { positional, flags } = parseArgs(rest);
	if (flags.help) {
		console.log(HELP);
		process.exit(0);
	}

	const num = flags.num || config.defaultNumResults || 6;
	const type = flags.type || config.defaultType || 'auto';
	const dynamic = dynamicHighlightsOn(flags);
	const slow = flags.livecrawl || String(type).startsWith('deep');
	const timeoutMs = slow ? SLOW_TIMEOUT_MS : DEFAULT_TIMEOUT_MS;

	if (cmd === 'search') {
		const query = positional.join(' ');
		if (!query) { console.log(HELP); process.exit(2); }
		const body = {
			query,
			numResults: num,
			type,
			contents: contentsSpec(flags),
		};
		if (flags.category) body.category = flags.category;
		const data = await callExa(config, keyInfo, '/search', body, { dynamicHighlights: dynamic, timeoutMs });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		const results = data.results || [];
		console.log(`Exa search: "${query}" — ${results.length} result(s), type=${type}${dynamic ? ', dynamic-highlights' : ''}`);
		if (data.costDollars) console.log(`cost: $${Number(data.costDollars.total || 0).toFixed(4)}`);
		results.forEach((r, i) => printResult(r, i + 1, flags));
	} else if (cmd === 'contents') {
		const urls = positional;
		if (!urls.length) { console.log(HELP); process.exit(2); }
		// Exa /contents accepts highlights/text/livecrawl as top-level fields (not nested under `contents`)
		const body = { ids: urls, ...contentsSpec(flags) };
		const data = await callExa(config, keyInfo, '/contents', body, { dynamicHighlights: dynamic, timeoutMs });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		const results = data.results || [];
		console.log(`Exa contents: ${results.length}/${urls.length} page(s)`);
		results.forEach((r, i) => printResult(r, i + 1, flags));
	} else if (cmd === 'similar') {
		const url = positional[0];
		if (!url) { console.log(HELP); process.exit(2); }
		const body = { url, numResults: num, contents: contentsSpec(flags) };
		const data = await callExa(config, keyInfo, '/findSimilar', body, { dynamicHighlights: dynamic, timeoutMs });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		const results = data.results || [];
		console.log(`Exa similar to ${url} — ${results.length} result(s)`);
		results.forEach((r, i) => printResult(r, i + 1, flags));
	} else if (cmd === 'answer') {
		const query = positional.join(' ');
		if (!query) { console.log(HELP); process.exit(2); }
		const data = await callExa(config, keyInfo, '/answer', { query, text: true }, { timeoutMs: SLOW_TIMEOUT_MS });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		console.log(`Q: ${query}\n`);
		console.log(data.answer || '(empty answer)');
		if (Array.isArray(data.citations) && data.citations.length) {
			console.log('\nCitations:');
			data.citations.forEach((c, i) => console.log(`  [${i + 1}] ${c.title || ''} ${c.url || ''}`));
		}
	} else {
		console.error(`ERROR: unknown command "${cmd}".`);
		console.log(HELP);
		process.exit(2);
	}
}

main();
