#!/usr/bin/env node
// Exa REST API CLI — zero dependencies, Node 18+.
// Key resolution: EXA_API_KEY env var > config.json in the skill root.
// The key value must never be echoed in output.
//
// Highlights default to Exa **Dynamic Highlights** (beta): one shared budget
// allocated across all returned pages (measured ~4x fewer highlight chars than
// Exa's default bulk output). Every `dynamic: true` request must carry the
// `Exa-Beta: dynamic-highlights-2026-08-28` header or Exa answers HTTP 400.
// `highlightsPerUrl` is deliberately NOT sent — measured dead (Exa ignores it;
// values 1 and 5 return byte-identical payloads).

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = join(__dirname, '..', 'config.json');
const DYNAMIC_BETA_HEADER = 'Exa-Beta';
const DYNAMIC_BETA_VALUE = 'dynamic-highlights-2026-08-28';
const HELP = `
Exa search CLI
  exa.mjs search  "query"  [--num N] [--type auto|keyword|neural|fast|instant|deep-lite|deep|deep-reasoning]
                           [--text] [--maxchars N] [--no-dynamic | --hlchars N]
                           [--category news|github|pdf|paper|tweet|company|...]
                           [--livecrawl] [--json]
  exa.mjs contents "url" ["url2" ...] [--text] [--maxchars N] [--no-dynamic | --hlchars N] [--livecrawl] [--json]
  exa.mjs similar  "url"   [--num N] [--text] [--maxchars N] [--no-dynamic | --hlchars N] [--json]
  exa.mjs answer   "query" [--json]

  --no-dynamic   turn Dynamic Highlights off (default: on, sends the Exa-Beta header)
  --hlchars N    per-page highlight cap when dynamic is off (the two are mutually exclusive)
`;

function loadConfig() {
	try {
		return JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
	} catch {
		return {};
	}
}

function resolveKey(config) {
	if (process.env.EXA_API_KEY && process.env.EXA_API_KEY.length > 0) return process.env.EXA_API_KEY;
	if (config.apiKey && config.apiKey.length > 0) return config.apiKey;
	return '';
}

function parseArgs(argv) {
	const positional = [];
	const flags = {};
	for (let i = 0; i < argv.length; i++) {
		const a = argv[i];
		if (a === '--num' || a === '-n') flags.num = Number(argv[++i]);
		else if (a === '--type') flags.type = argv[++i];
		else if (a === '--category') flags.category = argv[++i];
		else if (a === '--maxchars') flags.maxchars = Number(argv[++i]);
		else if (a === '--hlchars') flags.hlchars = Number(argv[++i]);
		else if (a === '--no-dynamic') flags.nodynamic = true;
		else if (a === '--text') flags.text = true;
		else if (a === '--livecrawl') flags.livecrawl = true;
		else if (a === '--json') flags.json = true;
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
	if (flags.text) spec.text = { maxCharacters: flags.maxchars || 1000 };
	if (flags.livecrawl) spec.livecrawl = 'always';
	return spec;
}

async function callExa(config, key, path, body, opts = {}) {
	if (!key) {
		console.error('ERROR: no Exa API key. Put it in config.json or set EXA_API_KEY.');
		process.exit(2);
	}
	let res;
	try {
		res = await fetch(`${(config.baseUrl || 'https://api.exa.ai').replace(/\/+$/, '')}${path}`, {
			method: 'POST',
			headers: {
				authorization: `Bearer ${key}`,
				'content-type': 'application/json',
				accept: 'application/json',
				...(opts.dynamicHighlights ? { [DYNAMIC_BETA_HEADER]: DYNAMIC_BETA_VALUE } : {}),
			},
			body: JSON.stringify(body),
		});
	} catch (err) {
		console.error(`ERROR: network failure calling Exa: ${err.message}`);
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
		if (res.status === 401) console.error('Hint: the key in config.json is invalid or expired (check https://dashboard.exa.ai).');
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
	for (const h of hl.slice(0, 2)) console.log(`    » ${trim(h)}`);
	if (flags.text && r.text) console.log(`    ▸ ${trim(r.text, 600)}`);
	if (!hl.length && !r.text) console.log('    » (no highlight returned)');
}

async function main() {
	const config = loadConfig();
	const key = resolveKey(config);
	const [cmd, ...rest] = process.argv.slice(2);
	if (!cmd || cmd === 'help' || cmd === '--help') {
		console.log(HELP);
		process.exit(0);
	}
	const { positional, flags } = parseArgs(rest);
	const num = flags.num || config.defaultNumResults || 6;
	const type = flags.type || config.defaultType || 'auto';
	const dynamic = dynamicHighlightsOn(flags);

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
		const data = await callExa(config, key, '/search', body, { dynamicHighlights: dynamic });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		const results = data.results || [];
		console.log(`Exa search: "${query}" — ${results.length} result(s), type=${type}${dynamic ? ', dynamic-highlights' : ''}`);
		if (data.costDollars) console.log(`cost: $${Number(data.costDollars.total || 0).toFixed(4)}`);
		results.forEach((r, i) => printResult(r, i + 1, flags));
	} else if (cmd === 'contents') {
		const urls = positional;
		if (!urls.length) { console.log(HELP); process.exit(2); }
		const body = { ids: urls, contents: contentsSpec(flags) };
		const data = await callExa(config, key, '/contents', body, { dynamicHighlights: dynamic });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		const results = data.results || [];
		console.log(`Exa contents: ${results.length}/${urls.length} page(s)`);
		results.forEach((r, i) => printResult(r, i + 1, flags));
	} else if (cmd === 'similar') {
		const url = positional[0];
		if (!url) { console.log(HELP); process.exit(2); }
		const body = { url, numResults: num, contents: contentsSpec(flags) };
		const data = await callExa(config, key, '/findSimilar', body, { dynamicHighlights: dynamic });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		const results = data.results || [];
		console.log(`Exa similar to ${url} — ${results.length} result(s)`);
		results.forEach((r, i) => printResult(r, i + 1, flags));
	} else if (cmd === 'answer') {
		const query = positional.join(' ');
		if (!query) { console.log(HELP); process.exit(2); }
		const data = await callExa(config, key, '/answer', { query, text: true });
		if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }
		console.log(`Q: ${query}\n`);
		console.log(data.answer || '(empty answer)');
		if (Array.isArray(data.citations) && data.citations.length) {
			console.log('\nCitations:');
			data.citations.forEach((c, i) => console.log(`  [${i + 1}] ${c.title || ''} ${c.url || ''}`));
		}
	} else {
		console.log(HELP);
		process.exit(2);
	}
}

main();
