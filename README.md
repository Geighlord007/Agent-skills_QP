# Agent Skills

> 备份 + 版本控制 agent skills。**这个仓库就是 skill 的家**:仓库根目录即 skills 根,
> 本机把它 clone 到 `~/.agents/skills`,DeepSeek Harness(DSH)等 agent 即可自动发现。
> 技能跟某个具体 agent 不绑定,部署到谁是你本地的事(软链),仓库只管版本和备份。

## 部署模型

仓库根 = skills 根。每个技能是一个独立目录 `<name>/SKILL.md`,DSH 按 `~/.agents/skills/<name>/SKILL.md`
实时发现(带 watcher,改了即生效,无需重启)。

本机直接 clone 到 DSH 的标准技能根:

```bash
git clone https://github.com/Geighlord007/Agent-skills_QP.git ~/.agents/skills
```

### 各 agent 的技能目录

| Agent | 技能目录 | 备注 |
|---|---|---|
| DeepSeek Harness | `~/.agents/skills` | 本仓库就是它;另扫 `~/.dsh/skills`、项目级 `.agents/skills`/`.dsh/skills` |
| Claude Code | `~/.claude/skills` | 个人级;项目级 `.claude/skills` |
| Codex CLI | `~/.codex/skills` | |
| opencode | `~/.config/opencode/skills` | |
| Kimi CLI / Kimi Code | `~/.kimi-code/skills` | |
| 任意 agent(项目级) | `<项目>/.agents/skills` | 跨工具共享的仓库内约定 |

> `~/.agents/skills` 不是通用标准,多数 CLI 只读上表自己那一行——想让它们用本仓库,建软链即可。

## 怎么用

**加新 skill / 改 skill**(DSH 实时生效,改完 push 备份):

```bash
cd ~/.agents/skills
mkdir -p my-new-skill            # 写 my-new-skill/SKILL.md(frontmatter 见下)
git add my-new-skill && git commit -m "add my-new-skill" && git push
```

**让其它 agent 也用(一份源码、多 agent 共享):**

```bash
# 整目录链(注意:目标目录若已有真实副本,先备份再删)
ln -s ~/.agents/skills ~/.claude/skills
ln -s ~/.agents/skills ~/.config/opencode/skills
ln -s ~/.agents/skills ~/.codex/skills
ln -s ~/.agents/skills ~/.kimi-code/skills
```

不想给某个 agent 用就跳过;只想给一部分,按技能逐个链(自动跳过无 SKILL.md 的目录):

```bash
for s in ~/.agents/skills/*/; do
  [ -f "$s/SKILL.md" ] && ln -s "$s" ~/.claude/skills/"$(basename "$s")"
done
```

**改了 agent 里的 skill,同步回仓库:** 软链场景下本来就是同一份文件,没有"回拷"这一步;
若是历史遗留的 copy 部署,则 `cp -r ~/.config/opencode/skills/<name> ~/.agents/skills/` 再 commit。

**新机器:**

```bash
git clone https://github.com/Geighlord007/Agent-skills_QP.git ~/.agents/skills
cd ~/.agents/skills && git pull   # 日常更新
```

## 仓库结构

```
~/.agents/skills/
├── README.md
├── .gitignore
├── agent-reach/               ← 技能(每个含 SKILL.md)
├── baoyu-document-translator/        ← DEPRECATED（2026-09-23，改用 v2；见 DEPRECATIONS.md）
├── baoyu-document-translator-v2/
├── baoyu-translate/
├── bio-research/
├── company-bg-info/
├── cosmetic-research/
├── deep-research/
├── docx/
├── exhibition-notes/
├── find-skills/
├── literature-search/
├── paddleocr-doc-parsing/
├── pubmed-database/
├── qwen-asr-transcribe/
├── scienceskillscommon/       ← 共享 Python 库(非独立技能,见 frontmatter 规范)
├── wechat-bridge/
└── tools/                     ← 本机工具(如 cli-in-wechat),不进 git,需手动保留
```

## 技能规范(SKILL.md frontmatter)

DSH/Claude/opencode 等按同一套规则解析,目录必须是仓库根的直接子目录:

- `name`(必填):小写字母+连字符,与目录名一致
- `description`(必填):说明何时用、触发词
- 可选:`whenToUse`、`metadata`、`user-invocable`
- `disable-model-invocation: true`:声明"不要被模型直接调用"——共享库类技能
  (如 `scienceskillscommon`)应加上,避免被当成独立技能触发

注意:仓库根目录不要放散落的 `.md`(会被当 flat skill 尝试解析)。

## 关于 agent 目录

仓库**不关心** agent。每个 agent 读自己约定位置的 `<name>/SKILL.md`;让它们共享本仓库 = 软链,
不用再手动拷贝。不想给某个 agent 用的技能,跳过那个软链/那一次 `ln -s` 即可。
