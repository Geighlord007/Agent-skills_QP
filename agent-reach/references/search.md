# 搜索工具

Exa AI 搜索引擎（通过 `mcporter` 调用）。

## Exa AI 搜索

适合查找技术文档、官方示例与高质量英文网页：

```powershell
mcporter call exa.web_search_exa query="query" numResults=5
mcporter call exa.web_search_exa query="library API code example" numResults=5
```

| 场景 | 参数 |
|---|---|
| 网页搜索 | `web_search_exa(query="...", numResults=5)` |
| 技术/代码资料 | `web_search_exa(query="框架名 API 示例", numResults=5)` |

> Exa MCP 的 `get_code_context_exa` 已弃用且默认不注册。代码问题同样使用 `web_search_exa`；需要精确检索仓库源码时改用 [references/dev.md](dev.md) 的 GitHub 搜索。

## 工具边界对比

| 工具 | 归属 | 适用场景 |
|---|---|---|
| Exa (`web_search_exa`) | agent-reach / `exa-search` skill | 英文技术文档、官方 API 示例、高质量网页检索（若已安装专门的 `exa-search` skill，纯搜索任务可优先走专门 skill） |
| GitHub 搜索 (`gh search`) | agent-reach ([dev.md](dev.md)) | 仓库、Issue、代码精确检索 |
| 平台专属采集 | agent-reach ([social.md](social.md) / [career.md](career.md) / [finance.md](finance.md)) | 小红书、Twitter/X、Reddit、B站、Boss直聘、雪球等站内内容 |
