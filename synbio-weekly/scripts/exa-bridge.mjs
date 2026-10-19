// 临时：Exa API 的 curl 桥（node fetch 不通时的传输层绕行；引擎仍是 Exa）
// 用法: node tmp-exa-bridge.mjs "<query>" [numResults]
// 密钥在运行时从 exa-search 技能配置读取，不在脚本或命令行中出现。
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { homedir } from 'node:os';

const cfg = JSON.parse(readFileSync(join(homedir(), '.agents', 'skills', 'exa-search', 'config.json'), 'utf8'));
const key = cfg.apiKey || process.env.EXA_API_KEY;
if (!key) { console.error('缺 EXA_API_KEY'); process.exit(1); }
const query = process.argv[2];
const num = Number(process.argv[3] || 6);
const body = JSON.stringify({ query, numResults: num, type: 'auto', contents: { highlights: true, maxCharacters: 300 } });
const out = execFileSync('curl', [
  '-s', '--connect-timeout', '10', '--retry', '3', '--retry-delay', '4',
  '-X', 'POST', 'https://api.exa.ai/search',
  '-H', 'Content-Type: application/json', '-H', `x-api-key: ${key}`,
  '-d', body,
], { maxBuffer: 20 * 1024 * 1024 });
const j = JSON.parse(out.toString());
if (!j.results) { console.error('响应异常:', out.toString().slice(0, 300)); process.exit(1); }
for (const [i, r] of j.results.entries()) {
  console.log(`[${i + 1}] ${r.title}`);
  console.log(`    ${r.url} · ${r.publishedDate || ''}`);
  console.log(`    ${(r.highlights || []).join(' ').slice(0, 260)}`);
}
