#!/usr/bin/env python3
"""雪球个股讨论区抓取（绕过 WAF）。

用法: python3 xueqiu_stock_comments.py HK01810 [条数]

原理: 雪球讨论接口 (xueqiu.com/query/v1/symbol/search/status.json) 有 WAF JS 挑战，
直接 requests 只能拿到挑战页。这里用 Playwright 驱动真实 Chrome（复用 xiaohongshu-mcp
下载的浏览器），登录 Cookie 从 agent-reach 配置读取，在页面上下文内 fetch API。
"""
import json
import re
import sys
import time

from playwright.sync_api import sync_playwright

CHROME = '/home/adam/.cache/xiaohongshu-mcp/browser/148.0.7778.215/browser/chrome'
CONFIG = '/home/adam/.agent-reach/config.yaml'
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'HK01810'
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    ck = re.search(r"xueqiu_cookie:\s*[\"']?([^\"'\n]+)", open(CONFIG).read()).group(1)
    cookies = [{'name': n, 'value': v, 'domain': '.xueqiu.com', 'path': '/'}
               for n, v in (p.split('=', 1) for p in ck.split('; '))]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'])
        ctx = browser.new_context(user_agent=UA)
        ctx.add_cookies(cookies)
        page = ctx.new_page()
        page.goto(f'https://xueqiu.com/S/{symbol}', timeout=60000)
        time.sleep(8)  # 等 WAF 挑战自动完成
        data = page.evaluate("""async ([symbol, count]) => {
            const r = await fetch(
                `/query/v1/symbol/search/status.json?count=${count}&comment=0&symbol=${symbol}&hl=0&source=all&sort=time&q=&type=11`,
                {headers: {'Accept': 'application/json'}});
            return await r.text();
        }""", [symbol, count])
        browser.close()

    if not data.strip().startswith('{'):
        print('WAF 未通过或 Cookie 过期，请重新登录雪球并更新 Cookie。', file=sys.stderr)
        sys.exit(1)

    for it in json.loads(data).get('list', []):
        text = re.sub(r'<[^>]+>', '', it.get('description') or it.get('text', ''))
        user = it.get('user', {}).get('screen_name', '?')
        print(f"[{user}] {text}\n  💬{it.get('reply_count', 0)} 👍{it.get('like_count',0)}\n")


if __name__ == '__main__':
    main()
