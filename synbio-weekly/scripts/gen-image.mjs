#!/usr/bin/env node
// 生图脚本：豆包 Seedream（火山方舟 Ark API）——synbio-weekly 技能包自带
// 用法: node gen-image.mjs <workspace> "<主题提示词>" [尺寸=1512x648] [输出文件]
// 提示词自动前置工作区 config.json 的 style_anchor（--raw 跳过）。
// 密钥取工作区 config.json 的 image_gen.api_key，或环境变量 ARK_API_KEY。
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

const args = process.argv.slice(2);
const raw = args.includes('--raw');
const rest = args.filter(a => a !== '--raw');
const ws = resolve(rest[0] || '.');
const theme = rest[1];
if (!theme) {
  console.error('用法: node gen-image.mjs <workspace> "<主题提示词>" [size] [outfile] [--raw]');
  process.exit(1);
}
const cfgPath = join(ws, 'config.json');
if (!existsSync(cfgPath)) { console.error('工作区缺 config.json:', cfgPath); process.exit(1); }
const g = JSON.parse(readFileSync(cfgPath, 'utf8')).image_gen;
if (!g || !g.enabled) { console.error('image_gen 未启用或未配置'); process.exit(1); }
const apiKey = g.api_key || process.env.ARK_API_KEY;
if (!apiKey) { console.error('缺 API key：写入工作区 config.json 的 image_gen.api_key 或设置环境变量 ARK_API_KEY'); process.exit(1); }

const size = rest[2] || g.default_size || '1512x648';
const prompt = raw ? theme : `${g.style_anchor}, ${theme}`;
const outDir = join(ws, 'briefings', 'assets');
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });
const outPath = rest[3] ? resolve(rest[3]) : join(outDir, `cover-${Date.now()}.png`);

const res = await fetch(`${g.base_url}${g.endpoint}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
  body: JSON.stringify({ model: g.model, prompt, size, response_format: 'b64_json', watermark: false }),
});
if (!res.ok) {
  console.error(`Ark API ${res.status}: ${(await res.text()).slice(0, 500)}`);
  process.exit(1);
}
const json = await res.json();
const item = json.data && json.data[0];
if (!item) { console.error('响应无 data[0]:', JSON.stringify(json).slice(0, 500)); process.exit(1); }
let bytes;
if (item.b64_json) {
  bytes = Buffer.from(item.b64_json, 'base64');
} else if (item.url) {
  bytes = Buffer.from(await (await fetch(item.url)).arrayBuffer());
} else {
  console.error('data[0] 既无 b64_json 也无 url'); process.exit(1);
}
writeFileSync(outPath, bytes);
console.log(`saved: ${outPath} (${(bytes.length / 1024).toFixed(0)} KB, ${size})`);
