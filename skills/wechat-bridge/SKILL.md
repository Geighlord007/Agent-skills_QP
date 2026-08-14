---
name: wechat-bridge
description: >
  微信 ↔ 本地 AI CLI 桥接服务（cli-in-wechat）的运维说明：启动、停止、配置、排错。
  让用户可以在微信里和本机的 Kimi Code / Claude Code / Codex / Gemini CLI / OpenCode 对话。
  触发词：微信桥、微信控制 Kimi、cli-in-wechat、ClawBot、iLink、
  "在微信里和你对话"、"启动微信桥"、"微信桥挂了"。
---

# WeChat Bridge (cli-in-wechat) 运维指南

桥接服务：[cli-in-wechat](https://github.com/sgaofen/cli-in-wechat)，
走微信官方 ClawBot 插件的 iLink Bot API（`ilinkai.weixin.qq.com`，腾讯官方域名，合规不封号）。

## 本机安装位置

- 代码：`~/agent-skills/tools/cli-in-wechat/`（**不进 git**，`.gitignore` 已排除 `tools/`；
  升级用 `git -C 该目录 pull && npm install`）
- 配置：`~/.wx-ai-bridge/config.json`（首次运行后生成）
- 依赖已装好（`npm install` 已完成，含可选依赖 undici 代理支持）

## 前提

- 微信已启用 ClawBot 插件：微信 → 我 → 设置 → 插件 → 微信 ClawBot
- 至少一个 CLI 已登录（Kimi Code 已 `kimi login`，开箱即用）

## 启动 / 停止

```bash
# 前台调试（首次启动用前台，会显示登录二维码，用微信扫码）
cd ~/agent-skills/tools/cli-in-wechat && npm run dev

# 日常后台运行
cd ~/agent-skills/tools/cli-in-wechat && nohup npm run dev > /tmp/wechat-bridge.log 2>&1 &

# 停止
pkill -f cli-in-wechat

# 看日志 / 调试模式（带网络诊断）
tail -f /tmp/wechat-bridge.log
npm run dev:debug
```

登录 token 过期（errcode -14/-13）会自动重新出示二维码，需重新扫码。

## 微信侧用法（装好后的日常操作）

- 直接打字 → 发给上次用的工具；`@kimi 做什么` → 指定 Kimi Code（另有 @claude/@codex/@gemini/@opencode）
- `/resume` 浏览历史会话、`/new` 新会话、`/cancel` 取消、`/send <路径>` 发本地文件到微信
- `/km` 快速切到 Kimi；`>>` 把上条结果传给下个工具
- 完整命令见项目 README

## 配置项（~/.wx-ai-bridge/config.json）

```jsonc
{
  "defaultTool": "kimi",        // 建议改成 kimi
  "workDir": "/home/adam",
  "allowedUsers": [],           // 留空 = 只允许扫码登录者本人（保持默认！）
  "allowAllUsers": false        // 永远不要开，开了等于把电脑 root 给所有微信好友
}
```

## ⚠️ 安全须知

- Kimi 的 `-p` 非交互模式**恒为 auto 权限**（`/mode` 对 Kimi 无效）：微信里一句话就能让 agent
  读写本机文件、执行命令。这是设计如此，发指令时要有"这就是远程操作自己电脑"的意识。
- 不要把 bridge 暴露给其他人（allowedUsers 保持只含本人）。

## 排错

- **连不上 ilinkai.weixin.qq.com**：这是国内域名，直连即可，**不要走代理**。
  若系统里全局设了代理变量反而可能出问题，启动前 `unset HTTPS_PROXY HTTP_PROXY ALL_PROXY`。
- **ECONNRESET / fetch failed**：内置超时+退避重试，瞬时抖动会自动恢复；
  持续失败用 `npm run dev:debug` 看诊断日志。
- **Kimi 无响应**：先确认终端里 `kimi -p "hello"` 能正常出结果（OAuth 未登录则先 `kimi login`）。
