# 坑位清单（2026-10-02 全部实测踩过）

## jev 侧

1. **目标日期必须是未来**。官方示例写死的 2026-09-20 已成过去式后，日历选不了目标日，agent 在"上一月/下一月"里打转最后 BLOCKED。改 `flights.py` 的 GOALS 时同步改 `verify()` 和 tests 夹具。
2. **菜单/下拉挂载 ~1.5s 竞态**。GF 菜单打开后 DOM 快照先是旧页面、再是空态（只剩 Scroll/Wait 伪动作）、1-1.5s 后才出现选项。jev 的 `browser.py observe()` 已带"无可执行动作且正文为空则 250ms 重试"补丁，别删。弱模型在空态会 BLOCKED 或反复点开关。
3. **DOM 读取器盲区**：自定义日历格子（携程实证：AX 树可见、jev 快照不可见）、canvas、shadow DOM、iframe。盲区控件 = 升级接管的主战场。
4. **双态标签的"Open"开关诱导打转**。jev 用 `label → Open label` 双态格式存元素（元素表只显示前半段），模型爱反复点开合开关。`TYPESAFE_DROP_LABELS` 用 `→ open` 子串通杀（匹配时把词条和 label 都 lower）。
5. **单候选 choice**：官方 API 无所谓，中转网关要求 criteria ≥2 项——用 `TYPESAFE_PAD_SINGLETON` 别名键填充，validate_choice 要先把别名归一化再严格比对。
6. **中转网关 token 预算**是"state×投机头数"展开（32768 上限），与页面正文基本无关——裁正文没用，要裁元素表（`fit_action_space` 按目标词面相关度排头，支持中文 `\w+`）。
7. **MAX_STEPS=60**：单任务动作预算，超额 predict 报错——长流程把"卡点"部分交给接管者做。

## 环境/工程侧

8. **uv venv 不可搬移**：项目迁目录后必须重跑 `uv sync` 重建（scripts 里是绝对路径）。
9. **daemon 与浏览器绑定**：`BU_CDP_URL` 在 daemon 启动时生效——换端口先 `uv run browser-harness --reload` 再跑任务，否则连的是旧浏览器。
10. **hh.cdp 不带 session_id** 路由到 daemon 默认标签页；对已附加目标重复 `Target.attachToTarget` 会拿不到 session（KeyError: session）。
11. **截图调用要重试包装**：重页面 `Page.captureScreenshot` 会超时 5s，裸调用会炸掉整个 runner。
12. **cmd 的 `if exist X && 后续命令`**：条件为假时整条链短路，`&&` 后的命令不执行。清理+启动分开写。多行 python -c 一律写脚本文件。
13. **DeepSeek 已无 deepseek-chat**：现有型号 deepseek-flash / deepseek-v4-pro。
14. **坐标系**：截图物理像素 vs 点击 CSS 像素，先查 innerWidth/dpr（见 hybrid-protocol.md）。

## 平台侧

15. **携程深链必被弹**到 `/online/channel`（与 IP 无关）：列表页只认"站内表单发起的搜索会话"。
16. **Skyscanner 的 PerimeterX**：深链直进全拦，先逛首页暖 cookie 再进；登录态对盾无效。
17. **Trip.com 无摩擦**但计价币种跟随代理出口国；与国内版同货盘、价差 <1%。
18. **中转站 key（sk- 格式）不是官方 key**：官方端点 401 属正常，要在对应网关端点测（tokendance 实测可用但为自训 clone checkpoint，质量弱于官方）。

## 价格提取与交付（2026-10-02 澳洲三地实战新增）

19. **弹性日期条错配**：Trip.com 把邻日低价渲染在相邻行（单程页 "Sat, Dec 19 / US$240"，往返页 "Dec 22–Jan 2 / US$832"），全页正则会把邻日价错配给目标日期。日期归属校验必须同时认 `12-19` 数字格式和 `Sat, Dec 19` 英文格式。
20. **侧栏汇总 ≠ 卡片价**：同一页面价格来自三种区块（弹性日期条 / 侧栏航司联盟汇总 / 航班卡片），数字一模一样但含义不同。输出必须标注来源；侧栏"Cheapest nonstop"是当日官方直飞最低价，适合做 headline。
21. **"无直飞"假阴性**：提取口径太严会误杀侧栏航司最低价——那是当日口径可信值（如 SYD↔MEL 侧栏 "Jetstar (24) US$89"=当日 24 班直飞最低）。clean_sample 为空时先看侧栏有没有带班次计数的航司价，再下"无直飞"结论。
22. **需求清单前置**：直飞/转机、舱等、行李、日期刚性、预算——开工前问清，别让"我偏好直飞"变成事后推翻整份分析的理由。
23. **交付抽查协议**：报告交付前自己点开 1-2 条链接核对页面当日口径（汇总价 vs 实卡价），价格数字旁标来源区块。假设（天数分配、转机可接受、机场范围）必须写进"假设区块"。
