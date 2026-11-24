#!/usr/bin/env node
// Exa API 的 curl 传输层桥（node fetch 不通时绕行；引擎仍是 Exa）
// 用法: node scripts/exa-bridge.mjs "<query>" [num=6] [--category news] [--days 10] [--json]
import { existsSync, readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { homedir } from 'node:os';

function resolveKey() {
  if (process.env.EXA_API_KEY?.trim()) return process.env.EXA_API_KEY.trim();
  const cfgPath = join(homedir(), '.agents', 'skills', 'exa-search', 'config.json');
  if (existsSync(cfgPath)) {
    try {
      const k = JSON.parse(readFileSync(cfgPath, 'utf8'))?.apiKey?.trim();
      if (k) return k;
    } catch { /* fallback */ }
  }
  const keyFile = join(homedir(), '.agents', 'keys', 'exa.key');
  if (existsSync(keyFile)) return readFileSync(keyFile, 'utf8').trim();
  return '';
}

const argv = process.argv.slice(2);
if (!argv.length || argv.includes('-h') || argv.includes('--help')) {
  console.log('用法: node scripts/exa-bridge.mjs "<query>" [num=6] [--category news] [--days 10] [--json]');
  process.exit(0);
}

const pos = [];
let category = '', days = 0, rawJson = false;
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--category') category = argv[++i] || '';
  else if (argv[i] === '--days') days = Number.parseInt(argv[++i], 10) || 0;
  else if (argv[i] === '--json') rawJson = true;
  else if (argv[i].startsWith('-')) { console.error(`未知参数: ${argv[i]}`); process.exit(2); }
  else pos.push(argv[i]);
}

const query = (pos[0] || '').trim();
const key = resolveKey();
if (!query || !key) {
  console.error(!query ? '缺少查询词 query' : '缺 EXA_API_KEY（请设环境变量、~/.agents/keys/exa.key 或 exa-search/config.json）');
  process.exit(2);
}

const payload = {
  query,
  numResults: Math.max(1, Number.parseInt(pos[1] || '6', 10) || 6),
  type: 'auto',
  contents: { highlights: { dynamic: true } },
};
if (category) payload.category = category;
if (days > 0) payload.startPublishedDate = new Date(Date.now() - days * 86_400_000).toISOString().slice(0, 10) + 'T00:00:00.000Z';

const esc = key.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
const curlCfg = [
  'header = "Content-Type: application/json"',
  'header = "Accept: application/json"',
  `header = "Authorization: Bearer ${esc}"`,
  'header = "Exa-Beta: dynamic-highlights-2026-08-28"',
  '',
].join('\n');

const out = execFileSync(
  'curl',
  ['-sS', '--connect-timeout', '10', '--max-time', '30', '--retry', '2', '-K', '-', '-X', 'POST', 'https://api.exa.ai/search', '-d', JSON.stringify(payload)],
  { input: curlCfg, maxBuffer: 20 * 1024 * 1024 }
).toString('utf8');

const j = JSON.parse(out);
if (!Array.isArray(j.results)) { console.error('响应异常:', out.slice(0, 300)); process.exit(1); }
if (rawJson) { console.log(JSON.stringify(j, null, 2)); process.exit(0); }

for (const [i, r] of j.results.entries()) {
  console.log(`[${i + 1}] ${r.title || '(no title)'}`);
  console.log(`    ${r.url} · ${(r.publishedDate || '').slice(0, 10)}`);
  console.log(`    ${(r.highlights || []).join(' ').replace(/\s+/g, ' ').trim().slice(0, 400)}`);
}
