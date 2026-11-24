#!/usr/bin/env node
// 把 HTML 内联为自包含单文件：内联 <img data-embed> 与 <style>/inline style 里的本地图片和字体
// 优先查 HTML 同级目录，找不到自动回退到技能包根目录（如 assets/fonts/）
// 用法: node scripts/embed-images.mjs <html文件>
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const htmlArg = process.argv[2];
if (!htmlArg || htmlArg === '-h' || htmlArg === '--help') {
  console.log('用法: node scripts/embed-images.mjs <html文件>');
  process.exit(htmlArg ? 0 : 1);
}
const htmlPath = resolve(htmlArg);
const htmlDir = dirname(htmlPath);
const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const MIME = {
  png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp',
  gif: 'image/gif', svg: 'image/svg+xml', woff2: 'font/woff2', woff: 'font/woff',
  ttf: 'font/ttf', otf: 'font/otf',
};

const isSkip = (u) => /^(data:|https?:|\/\/|#)/i.test(u.trim());
const findAsset = (raw) => {
  const clean = raw.trim().split(/[?#]/)[0];
  for (const base of [htmlDir, skillRoot]) {
    const p = resolve(base, clean);
    if (existsSync(p)) return p;
  }
  return null;
};
const toDataUri = (p) => `data:${MIME[p.split('.').pop().toLowerCase()] || 'application/octet-stream'};base64,${readFileSync(p).toString('base64')}`;

let html = readFileSync(htmlPath, 'utf8');
let count = 0;

html = html.replace(/<img\b[^>]*?\bdata-embed\b[^>]*?>/gi, (tag) => {
  const m = tag.match(/\bsrc=(["'])([^"']+)\1/i);
  if (!m || isSkip(m[2])) return tag;
  const p = findAsset(m[2]);
  if (!p) { console.warn('缺图:', m[2]); return tag; }
  count++;
  return tag.replace(/\bsrc=(["'])[^"']+\1/i, `src="${toDataUri(p)}"`);
});

const inlineCssUrls = (css) => css.replace(/url\(\s*(["']?)([^"')]+)\1\s*\)/g, (full, _q, raw) => {
  if (isSkip(raw)) return full;
  const p = findAsset(raw);
  if (!p) { console.warn('缺资源:', raw); return full; }
  count++;
  return `url("${toDataUri(p)}")`;
});

html = html.replace(/(<style\b[^>]*>)([\s\S]*?)(<\/style>)/gi, (_, a, css, b) => `${a}${inlineCssUrls(css)}${b}`);
html = html.replace(/(\bstyle=)(["'])([\s\S]*?)\2/gi, (_, a, q, css) => `${a}${q}${inlineCssUrls(css)}${q}`);

writeFileSync(htmlPath, html, 'utf8');
const leftover = [...new Set(html.replace(/<!--[\s\S]*?-->/g, '').match(/\{\{[A-Z0-9_]+\}\}/g) || [])];
if (leftover.length) console.warn('残留占位符:', leftover.join(', '));
console.log(`embedded ${count} asset(s) -> ${htmlPath}`);
