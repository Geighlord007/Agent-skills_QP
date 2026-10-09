# 子域配方：查价/比价（2026-10-02 实测）

> 本文件是 jev-browser skill 的一个**子域**配方（网页控制引擎的查价应用）。主骨架（通用入口/混合协议）在 SKILL.md。
> **查价五问（开工前问清）**：直飞还是转机可接受、舱等、行李、日期刚性（±几天）、预算上限。

城市码一律用 IATA（上海 pvg、布宜诺斯艾利斯 bue、苏黎世 zrh、伦敦 lhr/lgw/任何机场 lON…），日期格式看各节。

## 1. Trip.com（携程国际版）— 快速报价首选

```
https://www.trip.com/flights/showfarefirst?dcity=pvg&acity=bue&ddate=2026-11-05&rdate=2026-12-01&triptype=rt&class=y&quantity=1
```
- 深链直达、零反爬摩擦、3-6 秒出价；**用 `search_trip2.py` 抓**（v1 的 search_trip.py 有日期错配 bug 已弃用）：
  `uv run --env-file .env python search_trip2.py <dep> <arr> <d1> <d2|--ow> [--direct]`
- **页面三种价格区块必须区分**（v2 已自动甄别，输出到证据字段）：
  1. **弹性日期条**（"Sat, Dec 19 / US$240" 邻日低价、RT 页显示 "Dec 22–Jan 2 / US$832" 邻对价）——**绝不采信**，曾把 12/19 的价错配给 12/22；
  2. **侧栏航司/联盟汇总**（"Star Alliance US$832 / China Southern (5) US$870"）——当日口径的最低价，**可用但须标注"汇总条"**；其中"Cheapest nonstop"汇总条是官方当日直飞最低价，很适合当 headline；
  3. **航班卡片**——可订实价，首选采信；
- 证据字段阅读：`clean_sample` = 双校验通过价（日期归属 + 直飞标记），`dropped_promo` = 剔除项及原因（date-ctx=弹性条/邻日，nonstop-check=侧栏/经停卡），`stop_lines` = 直飞/经停标记；
- **`--direct` 直飞过滤是客户端校验**（卡片上下文须含 Nonstop 且无经停标记），不点 UI 勾选框（React 勾选不生效）；注意甄别"无直飞"假阴性——SYD↔MEL 这类高频航线侧栏显示 Jetstar(24) US$89 即当日直飞最低价，若 clean_sample 为空但侧栏有航司计数，说明是提取口径问题不是真无直飞；
- **直飞口径的航线现实**：上海区域洲际直飞只有浦东（PVG）；杭/宁/南京无澳洲直飞。澳内陆 SYD/MEL↔PPP 全直飞（捷星/维珍/澳航）；
- 与携程国内版同一货盘，价差 <1%，但看不到国内版专属 CNY 促销票。

## 2. Google Flights — jev 全栈自动化

- 跑法：改 `examples/flights.py` 的 `GOALS`（航线 + **未来日期**）和 `verify()`（日期/星期/URL 校验同步改），tests 夹具同步改，`uv run --env-file .env python examples/flights.py`；
- 实测 14.4s 完整查价：17 次决策 + 2 次填字，7 项独立验证；票价在结果卡片 aria-label 里（"From 47 US dollars…"）；
- 页面干净、语义化好，jev 的主场；菜单/下拉有 ~1.5s 挂载竞态，browser.py observe() 的空快照重试补丁覆盖此问题；
- 适合走 proxied Chrome（9333）。低频使用无需登录 Google 账号（登录反而把自动化风险引向账号）。

## 3. Skyscanner — 暖 PX cookie

- 有 PerimeterX 盾：裸请求/深链直进全部被 captcha-v2 拦。**先导航到首页**（PX JS 挑战自动放行、种 cookie），**再进深链**（范式：`skyscanner_bue.py`，项目根）；
- 深链：`https://www.skyscanner.com/transport/flights/{dep}/{arr}/{YYMMDD}/{YYMMDD}/?adultsv2=1&cabinclass=economy&rtn=1`（如 pvg/ar/261105/261201）；
- 目的地国家级页面的 ¥ 数字是**酒店夜价**，不是机票价——真行程价必须进具体城市的 dated 搜索页；
- 价格显示币种跟随代理出口国（JP 出口=日元）。登录态对 PX 盾无效，别在登录上浪费时间。

## 4. 携程国内版 — 混合协议（唯一能拿 CNY 促销价的路）

- 深链（`/online/list/round-...`）无论 IP 一律被弹到 `/online/channel` 频道页——必须走站内表单；
- jev 官方模型能进频道页、能摸到日期字段、能打开日历，但**日历格子不在其 DOM 读取器里**（AX 树里有、jev 快照里没有）→ BLOCKED → 升级接管（见 hybrid-protocol.md）；
- 用直连 Chrome（9334）才有国内版人民币价；结果页 URL 形如 `/online/list/round-sha-bue?depdate=2026-11-05_2026-12-01`；
- 页面两段式选择：先"选去程"（价格即往返含税总价）再"选返程"；日历本身会标每日往返总价（比价利器）。

## 5. 高频盯价/批量任务

- 单次查询成本 $0.004 量级 → jev + 定时器（cron）即可构建盯价服务；降价阈值 + 通知渠道（微信机器人见 task-surveillance-and-notify 记忆）；
- 批量 N 条航线 = N 次独立跑（可并行 browser-harness 云浏览器）；卡点升级参照混合协议，但无人值守场景接管者要换成 API 视觉模型（当前会话只有在场时才可用）。
