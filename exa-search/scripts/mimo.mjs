#!/usr/bin/env node
// Xiaomi MiMo web_search CLI — zero dependencies, Node 18+.
// Calls the OpenAI-compatible chat completions endpoint with the server-side
// `web_search` tool (requires the 联网服务 plugin on the MiMo account) and
// prints the synthesized cited answer plus the citation list.
// Key resolution: MIMO_API_KEY env > config.json `mimoApiKey` > ~/.agents/keys/mimo.key.
// The key value must never be echoed in output.

import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = join(__dirname, '..', 'config.json');
const FALLBACK_KEY_PATH = join(homedir(), '.agents', 'keys', 'mimo.key');
const TIMEOUT_MS = 60_000;

const HELP = `
MiMo web search CLI (server-side web_search tool; account needs the 联网服务 plugin)
  mimo.mjs search "query" [--model flash|pro|<model-id>] [--maxkw N] [--limit N]
                          [--no-force] [--cites] [--json]

  --model      flash (default: cheap/fast) | pro | a full model id
  --maxkw N    max search keywords per call, 1-50 (default 5)
  --limit N    max results per search, 1-50 (default 5)
  --no-force   let the model decide whether to search (default: force search)
  --cites      print only the citation list (raw source rows)
  --json       print the raw API response
  -h, --help   show this help message
`;

const MODEL_ALIASES = {
	flash: 'mimo-v2.6-flash',
	pro: 'mimo-v2.6-pro',
};

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
	if (process.env.MIMO_API_KEY && process.env.MIMO_API_KEY.trim().length > 0) {
		return { key: process.env.MIMO_API_KEY.trim(), source: 'MIMO_API_KEY env' };
	}
	if (config.mimoApiKey && String(config.mimoApiKey).trim().length > 0) {
		return { key: String(config.mimoApiKey).trim(), source: 'config.json' };
	}
	try {
		const raw = readFileSync(FALLBACK_KEY_PATH, 'utf8').trim();
		if (raw.length > 0) return { key: raw, source: '~/.agents/keys/mimo.key' };
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
		else if (a === '--model') flags.model = argv[++i];
		else if (a === '--maxkw') flags.maxkw = posInt(a, argv[++i]);
		else if (a === '--limit') flags.limit = posInt(a, argv[++i]);
		else if (a === '--no-force') flags.noforce = true;
		else if (a === '--cites') flags.cites = true;
		else if (a === '--json') flags.json = true;
		else if (a.startsWith('-')) { console.error(`ERROR: unknown option "${a}"`); process.exit(2); }
		else positional.push(a);
	}
	return { positional, flags };
}

function clampInt(value, lo, hi, fallback) {
	if (!Number.isFinite(value)) return fallback;
	return Math.min(hi, Math.max(lo, Math.floor(value)));
}

function trim(s, n = 240) {
	const line = String(s || '').replace(/\s+/g, ' ').trim();
	return line.length > n ? `${line.slice(0, n)}…` : line;
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

	if (cmd !== 'search') {
		console.error(`ERROR: unknown command "${cmd}".`);
		console.log(HELP);
		process.exit(2);
	}
	const query = positional.join(' ');
	if (!query) { console.log(HELP); process.exit(2); }
	if (!keyInfo.key) {
		console.error('ERROR: no MiMo API key. Set MIMO_API_KEY, put mimoApiKey in config.json, or create ~/.agents/keys/mimo.key.');
		process.exit(2);
	}

	const model = MODEL_ALIASES[flags.model] || flags.model || config.mimoModel || MODEL_ALIASES.flash;
	const base = (config.mimoBaseUrl || 'https://api.xiaomimimo.com').replace(/\/+$/, '');
	const body = {
		model,
		messages: [{ role: 'user', content: query }],
		tools: [{
			type: 'web_search',
			force_search: !flags.noforce,
			max_keyword: clampInt(flags.maxkw, 1, 50, 5),
			limit: clampInt(flags.limit, 1, 50, 5),
		}],
	};

	let res, raw;
	const t0 = Date.now();
	try {
		res = await fetch(`${base}/v1/chat/completions`, {
			method: 'POST',
			headers: {
				'content-type': 'application/json',
				authorization: `Bearer ${keyInfo.key}`,
			},
			body: JSON.stringify(body),
			signal: AbortSignal.timeout(TIMEOUT_MS),
		});
		raw = await res.text();
	} catch (err) {
		if (err && err.name === 'TimeoutError') {
			console.error(`ERROR: MiMo request timed out after ${Math.round(TIMEOUT_MS / 1000)}s.`);
		} else {
			console.error(`ERROR: network failure calling MiMo: ${err.message}`);
		}
		process.exit(1);
	}
	const elapsed = Date.now() - t0;

	if (!res.ok) {
		let detail = raw.slice(0, 500);
		try {
			const parsed = JSON.parse(raw);
			detail = parsed.error?.message || parsed.error?.code || detail;
		} catch { /* keep raw slice */ }
		console.error(`ERROR: MiMo API returned HTTP ${res.status}: ${detail}`);
		if (res.status === 401) {
			console.error(`Hint: your MiMo API key (from ${keyInfo.source}) is invalid or expired (check https://mimo.mi.com).`);
		}
		if (/联网|plugin/i.test(detail)) console.error('Hint: web_search needs the 联网服务 plugin enabled on the MiMo account.');
		process.exit(1);
	}

	let data;
	try {
		data = JSON.parse(raw);
	} catch {
		console.error('ERROR: MiMo returned a non-JSON body.');
		process.exit(1);
	}
	if (flags.json) { console.log(JSON.stringify(data, null, 2)); return; }

	const msg = data.choices?.[0]?.message || {};
	const cites = (msg.annotations || []).filter((a) => a && a.type === 'url_citation');
	const wsu = data.usage?.web_search_usage || {};

	if (!flags.cites) {
		console.log(`MiMo web search: "${query}" — ${model}, ${elapsed} ms`);
		console.log('');
		console.log(msg.content || '(empty answer)');
	}

	if (cites.length) {
		console.log(`\nCitations (${cites.length}):`);
		cites.forEach((c, i) => {
			const meta = [c.site_name, (c.publish_time || '').slice(0, 10)].filter(Boolean).join(', ');
			console.log(`  [${i + 1}] ${trim(c.title || '(no title)', 80)}${meta ? ` — ${meta}` : ''}`);
			console.log(`      ${c.url}`);
		});
	}

	const usageBits = [];
	if (wsu.tool_usage !== undefined) usageBits.push(`searches ${wsu.tool_usage}`);
	if (wsu.page_usage !== undefined) usageBits.push(`pages ${wsu.page_usage}`);
	if (data.usage?.prompt_tokens !== undefined) usageBits.push(`tokens in ${data.usage.prompt_tokens} / out ${data.usage.completion_tokens}`);
	if (usageBits.length) console.log(`\nusage: ${usageBits.join(', ')}`);
}

main();
