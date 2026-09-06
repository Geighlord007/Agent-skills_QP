#!/usr/bin/env python3
"""小红书用户搜索（xiaohongshu-mcp 没有用户搜索工具，用本脚本补充）。

用法: python3 xhs_search_user.py 美杜莎

输出: 用户ID / 昵称 / 小红书号 / 粉丝数，以及带 xsec_token 的主页链接
      （user_id + xsec_token 可直接传给 `mcporter call 'xiaohongshu.user_profile(...)'`）。

原理: 小红书 web API 需要 x-s 签名，本地算法已失效。这里用 Playwright 打开搜索页，
点"用户"标签，让页面自己的 JS 完成签名请求，再从 DOM 读取结果。
"""
import json
import sys
import time
import urllib.parse

from playwright.sync_api import sync_playwright

CHROME = '/home/adam/.cache/xiaohongshu-mcp/browser/148.0.7778.215/browser/chrome'
COOKIES_JSON = '/home/adam/.agent-reach/xhs-cookies.json'
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')


def main():
    keyword = sys.argv[1]
    cookies_raw = json.load(open(COOKIES_JSON))
    cookies = [{'name': c['name'], 'value': c['value'],
                'domain': c['domain'], 'path': c.get('path', '/')} for c in cookies_raw]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'])
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900}, user_agent=UA)
        ctx.add_cookies(cookies)
        page = ctx.new_page()
        page.goto('https://www.xiaohongshu.com/search_result?keyword='
                  + urllib.parse.quote(keyword), timeout=60000)
        time.sleep(6)
        page.click('div.channel:has-text("用户")', timeout=10000)
        time.sleep(6)
        cards = page.evaluate("""() => {
            return [...document.querySelectorAll('a[href*="/user/profile/"]')].map(a => {
                const card = a.closest('div[class*=user], li, div[class*=card]') || a.parentElement;
                return {href: a.href,
                        text: (card.innerText || '').slice(0, 150).replace(/\\n/g, ' | ')};
            });
        }""")
        browser.close()

    seen = set()
    for c in cards:
        m = c['href'].split('/user/profile/')[1]
        uid, _, qs = m.partition('?')
        if uid in seen:
            continue
        seen.add(uid)
        token = ''
        for part in qs.split('&'):
            if part.startswith('xsec_token='):
                token = urllib.parse.unquote(part.split('=', 1)[1])
        if '小红书号' not in c['text']:  # 跳过侧边栏"我"等无关链接
            continue
        print(f"uid: {uid}\n  {c['text']}\n  xsec_token: {token}\n")


if __name__ == '__main__':
    main()
