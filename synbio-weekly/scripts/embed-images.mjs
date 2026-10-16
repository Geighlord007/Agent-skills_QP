#!/usr/bin/env node
// 把 HTML 内联为自包含单文件：① <img data-embed> 的相对 src → base64；② <style> 中 url(...) 本地资源（打包字体等）→ base64。
// 用法: node embed-images.mjs <html文件>   （原地替换；data: 引用与无 data-embed 图片不动）
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const htmlPath = resolve(process.argv[2] || '');
if (!htmlPath || !existsSync(htmlPath)) { console.error('用法: node embed-images.mjs <html文件>'); process.exit(1); }
const dir = dirname(htmlPath);
let html = readFileSync(htmlPath, 'utf8');
let n = 0;
html = html.replace(/<img\b[^>]*?\bdata-embed\b[^>]*?>/gi, (tag) => {
  const m = tag.match(/src="([^"]+)"/);
  if (!m || m[1].startsWith('data:')) return tag;
  const p = resolve(dir, m[1]);
  if (!existsSync(p)) { console.warn('缺图:', p); return tag; }
  const ext = p.split('.').pop().toLowerCase();
  const mime = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp', gif: 'image/gif', svg: 'image/svg+xml' }[ext] || 'application/octet-stream';
  n++;
  return tag.replace(/src="[^"]+"/, `src="data:${mime};base64,${readFileSync(p).toString('base64')}"`);
});
// ② 内联 <style> 中 url(...) 引用的本地资源（打包字体等），相对 HTML 路径解析
html = html.replace(/url\(["']([^"')]+)["']\)/g, (m, u) => {
  if (u.startsWith('data:')) return m;
  const p = resolve(dir, u);
  if (!existsSync(p)) { console.warn('缺资源:', p); return m; }
  const ext = u.split('.').pop().toLowerCase();
  const mime = { woff2: 'font/woff2', woff: 'font/woff', ttf: 'font/ttf', otf: 'font/otf', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp', svg: 'image/svg+xml' }[ext] || 'application/octet-stream';
  n++;
  return `url("data:${mime};base64,${readFileSync(p).toString('base64')}")`;
});
writeFileSync(htmlPath, html);
console.log(`embedded ${n} asset(s) -> ${htmlPath}`);
