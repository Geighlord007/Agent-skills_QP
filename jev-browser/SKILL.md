---
name: jev-browser
description: jev-ultrafast 网页自动化引擎的任务手册（本地已部署，含"jev 主跑 + ZCode 接管"混合协议）。当用户要自动操作网站——自动填表、批量网页任务、数据抓取、盯价盯货、或点名用 jev / jev ultrafast / jev flights / 浏览器自动化，或 jev 任务卡住需要接管时使用；"某个网页任务每天都要跑/一次跑几十个"这类高频场景的方案设计也在内。查价/比价/查机票（Google Flights、Skyscanner、携程、Trip.com）是已沉淀的子域配方。触发词：jev、jev flights、jev-ultrafast、浏览器自动化、网页自动化、自动填表、批量网页任务、盯价、查机票、机票价格、机票比价、航班搜索、Google Flights、Skyscanner、携程、Trip.com、flight search、browser agent。
---

# jev-browser — jev-ultrafast 任务手册

## 0. 先判断用不用 jev

jev-ultrafast 是决策式浏览器 agent：TypeSafe Jev 小模型每步只做"选操作+选元素"的一次选择题（70-500ms/步），不截图、不生成文本，因此比大模型逐步驱动快一个数量级、便宜两个数量级，且可脱离聊天会话独立运行。

判据（三占其一就用 jev）：**任务重复/高频**、**对延迟敏感**、**无人值守**。反之（偶发一次性操作、页面刁钻需要现场理解）直接用 ZCode 自带浏览器控制（control-browser skill），不要为用而用。卡在两者之间 → 用 §4 混合协议。

**任务前置澄清**：开工前把关键约束问清再动手，不许默默假设。网页任务问：登录态/频率/容错边界；查价任务问五项（直飞/转机、舱等、行李、日期刚性、预算——见 references/flights.md）。2026-10-02 实战教训：漏问"直飞"让整份分析作废重跑。把没问到的假设显式写进交付物的"假设区块"。

## 1. 环境（已就绪，不要重建）

- 项目：`D:\CSsoftware\jev-ultrafast`（uv 项目，31 个离线测试须全绿：`uv run pytest -q`）
- Key：官方 TypeSafe key 在 `.env`（端点 `https://api.typesafe.ai/v1/systemone`，模型 `jev-latest`，实测 jev-1.13.0；$0.042/1M input、输出免费）；文本填字模型走环境变量 `DEEPSEEK_API_KEY` + `deepseek-flash`（deepseek-chat 已下线）
- 两个专用 Chrome（**别动用户主 Chrome**），都从 `C:\Program Files\Google\Chrome\Application\chrome.exe` 启动：
  - **proxied**（走系统代理，Google Flights / Skyscanner 用）：`--remote-debugging-port=9333 --user-data-dir=D:\CSsoftware\jev-ultrafast\.chrome-profile`；对应 `.env` 的 `BU_CDP_URL=http://127.0.0.1:9333`
  - **direct**（真实 CN IP，携程国内版用）：`--remote-debugging-port=9334 --user-data-dir=D:\CSsoftware\jev-ultrafast\.chrome-profile-cn --no-proxy-server`；对应 `.env-direct`
  - 切换浏览器 = `uv run browser-harness --reload`（daemon 重启后按当次 env 连接）；CDP 自检：`curl http://127.0.0.1:933x/json/version`

## 2. 通用入口（任何网站）

```bash
uv run --env-file .env python examples/run.py --url <URL> --goal '<自然语言目标>'
```
库调用：`from jev_ultrafast import Agent; Agent(url, goals)`。目标词写法：**分步清单优于一句话目标**（弱页面模式时差距巨大）；日期必须是未来；查询类任务加"只查询，绝不预订/下单"。运行打印逐 tick 状态（`ready/blocked/done` + 最后动作），产物存 `artifacts/`。

## 3. 子域配方路由（引擎的具体战场；通用任务直接走 §2）

jev-ultrafast 本质是**网页控制引擎**，对任何网站通用（§2 是它的万能入口）。以下是已沉淀实战的**子域**——配方放 `references/<domain>.md`，主文件只留这张路由表；未来批量填表、数据抓取、盯货盯号等按同格式增补，勿让子域侵占主骨架。

| 子域 | 走法 | 状态 |
|---|---|---|
| **查价/比价** → `references/flights.md` | Trip.com 深链 + `search_trip2.py` 证据化抓价；GF 用 `examples/flights.py` 全栈；Skyscanner 暖 cookie；携程国内版走 §4 混合协议 | 已沉淀（27 次实测 + 防呆协议） |
| 高频盯价/批量 | jev + cron；卡点升级走 §4 | 方案就绪 |
| 批量填表 / 数据抓取 / 盯货盯号 | §2 通用入口 + §4 混合协议 | 随用随沉淀 |

查价子域一句话要害：**价格必须绑定日期与来源区块**（弹性日期条／侧栏汇总／卡片三分区——v1 曾把邻日价错配给目标日期），规则细节全在 flights.md。

## 4. 混合协议：jev 主跑 + ZCode 接管（本 skill 核心）

jev 卡住时（`blocked` 状态或"重复 3 次无变化"自动 blocked），**接管者就是当前 ZCode 会话本身**（看截图给坐标，零额外 API、零新 key）。完整规格读 `references/hybrid-protocol.md`，速览：

1. runner 升级时存证 `.escalate/escalate_N.png` + `NEED_ACTION`，轮询 `.escalate/action.json`（5 分钟窗口）；
2. 会话读截图 → 写 `action.json`（`{"actions":[{"type":"click","x":..,"y":..},{"type":"type","text":..},...]}`，或 `{"type":"finish"}`）；
3. runner 执行后把 `agent.state["status"]` 重置 `"ready"` 再调 `agent.run()` → jev 从被外部改变过的页面无缝续跑；
4. **坐标铁律**：截图坐标 ÷ DPR = 点击坐标，先查 `check_viewport.py`（实测 direct Chrome 截图是物理像素）。

现成脚本（都在项目根，勿复制副本防漂移）：`hybrid_ctrip.py`（jev 主跑+升级协议）、`manual_finish.py`（纯接管通道，附身 daemon 默认会话）、`check_viewport.py`。

## 5. 高危坑位速查（全部踩过，详情读 references/pitfalls.md）

1. 目标日期必须未来——过期日期日历不可选，agent 无限打转；
2. GF 菜单/下拉挂载 ~1.5s 竞态（observe() 已带空快照重试，别删）；
3. jev 的 DOM 读取器盲区：自定义日历、画布、shadow DOM（携程日历实证）→ 这就是升级接管的主战场；
4. 中转网关（tokendance 类）：32k 展开预算 + choice 至少 2 选项，官方 API 无这些限制；
5. uv venv 不可搬移（迁目录必重跑 uv sync）；换 BU_CDP_URL 先 reload daemon；
6. DeepSeek 已无 deepseek-chat（用 deepseek-flash）。

## 6. 成本参考

jev 决策 $0.042/1M input（输出免费），GF 全程约 9 万 token ≈ $0.004/次；文本填字 $0.00003/次。高频场景的经济学是 jev 的全部意义，别用它跑一次性任务。
