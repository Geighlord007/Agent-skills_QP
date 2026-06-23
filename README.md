# skills

> 备份 + 版本控制 agent skills。Skills 跟 agent 没关系，**这个仓库就是 skill 的家**。

## 怎么用

仓库里 `skills/<name>/` 放所有 skill。**部署到哪个 agent 是你本地的事**（手动拷），仓库只管版本和备份。

## 典型工作流

**加新 skill：**
```bash
mkdir -p ~/agent-skills/skills/my-new-skill
# 写 SKILL.md 等文件
cd ~/agent-skills && lazygit   # 或 git add . && git commit -m "..."
```

**改了 agent 里的 skill，同步回仓库：**
```bash
# 比如改了 OpenCode 里的 baoyu-translate
rm -rf ~/agent-skills/skills/baoyu-translate
cp -r ~/.config/opencode/skills/baoyu-translate ~/agent-skills/skills/
cd ~/agent-skills && lazygit
```

**在 agent 里用仓库里的 skill：**
```bash
# 手动拷到想用的 agent
cp -r ~/agent-skills/skills/<name> ~/.config/opencode/skills/
# 不想给这个 agent 用就跳过
```

**新机器：**
```bash
git clone https://github.com/Geighlord007/Agent-skills_QP.git ~/agent-skills
# 然后按需 cp -r 到各 agent
```

## 仓库结构

```
agent-skills/
├── README.md
├── .gitignore
└── skills/                 ← 所有 skill
    ├── baoyu-translate/
    ├── docx/
    ├── find-skills/
    └── ...
```

每个 skill 是一个独立目录，里面必须有 `SKILL.md`。

## 关于 agent 目录

仓库**不关心** agent。`~/.config/opencode/skills/`、`~/.kimi-code/skills/`、`~/.openclaw/skills/` 这些是 agent 自己读的位置，你想用哪个 skill 就手动拷过去。
