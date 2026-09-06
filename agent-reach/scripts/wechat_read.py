#!/usr/bin/env python3
"""读取微信公众号文章正文（绕过微信反爬验证墙）。

用法: python3 wechat_read.py "https://mp.weixin.qq.com/s/..."

原理: 微信对未验证请求弹 TCaptcha 验证码墙，curl/普通 Chrome 都过不去。
Camoufox（反指纹 Firefox）能自动完成微信的 poc_token 工作量证明挑战。
注意: 本机 Camoufox 有两处手动修复（uBlock 插件手动解压安装、pkgman 版本门补丁），
若 pip 升级 camoufox 包后失效，需查看 ~/.kimi-code/skills/agent-reach/SKILL.md 的本机备注。
"""
import sys
import time

from camoufox.sync_api import Camoufox


def main():
    url = sys.argv[1]
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_selector('#js_content', timeout=30000)
        time.sleep(2)
        title = page.title()
        author = page.locator('#js_name').inner_text().strip() if page.locator('#js_name').count() else ''
        publish = page.locator('#publish_time').inner_text().strip() if page.locator('#publish_time').count() else ''
        body = page.locator('#js_content').inner_text().strip()
    print(f"标题: {title}\n公众号: {author}  {publish}\n\n{body}")


if __name__ == '__main__':
    main()
