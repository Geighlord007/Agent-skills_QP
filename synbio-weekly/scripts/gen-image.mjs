#!/usr/bin/env node
// 生图脚本：豆包 Seedream（火山方舟 Ark API）
// 用法: node scripts/gen-image.mjs <workspace> "<主题提示词>" [size=1512x648] [outfile] [--raw]
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { homedir } from 'node:os';

const TIMEOUT_MS = 60_000;
const args = process.argv.slice(2);
if (!args.length || args.includes('-h') || args.includes('--help')) {
  console.log('用法: node scripts/gen-image.mjs <workspace> "<主题提示词>" [size=1512x648] [outfile] [--raw]');
  process.exit(0);
}

const raw = args.includes('--raw');
const rest = args.filter((a) => a !== '--raw');
const ws = resolve(rest[0] || '.');
const theme = rest[1];
if (!theme) { console.error('缺少主题提示词'); process.exit(2); }

const g = JSON.parse(readFileSync(join(ws, 'config.json'), 'utf8')).image_gen;
if (!g?.enabled) { console.error('image_gen 未启用'); process.exit(1); }

const keyFile = join(homedir(), '.agents', 'keys', 'ark.key');
const apiKey = g.api_key?.trim() || process.env.ARK_API_KEY?.trim() || (existsSync(keyFile) ? readFileSync(keyFile, 'utf8').trim() : '');
if (!apiKey) { console.error('缺 ARK_API_KEY（工作区 config.json / 环境变量 / ~/.agents/keys/ark.key）'); process.exit(2); }

const size = rest[2] || g.default_size || '1512x648';
const prompt = raw ? theme : `${g.style_anchor}, ${theme}`;
const outPath = rest[3] ? resolve(rest[3]) : join(ws, 'briefings', 'assets', `cover-${Date.now()}.png`);
mkdirSync(dirname(outPath), { recursive: true });

const url = `${String(g.base_url).replace(/\/+$/, '')}/${String(g.endpoint).replace(/^\/+/, '')}`;
const res = await fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
  body: JSON.stringify({ model: g.model, prompt, size, response_format: 'b64_json', watermark: false }),
  signal: AbortSignal.timeout(TIMEOUT_MS),
});
if (!res.ok) { console.error(`Ark API ${res.status}: ${(await res.text()).slice(0, 400)}`); process.exit(1); }

const item = (await res.json()).data?.[0];
let bytes;
if (item?.b64_json) {
  bytes = Buffer.from(item.b64_json, 'base64');
} else if (item?.url) {
  const imgRes = await fetch(item.url, { signal: AbortSignal.timeout(TIMEOUT_MS) });
  if (!imgRes.ok) { console.error(`图片下载失败 HTTP ${imgRes.status}`); process.exit(1); }
  bytes = Buffer.from(await imgRes.arrayBuffer());
} else {
  console.error('响应无有效图片数据');
  process.exit(1);
}

writeFileSync(outPath, bytes);
console.log(`saved: ${outPath} (${(bytes.length / 1024).toFixed(0)} KB, ${size})`);
