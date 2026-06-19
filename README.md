# agent-skills

个人 Agent Skills 同步仓库 —— 跨机器、跨 agent 保持一致。

> **TL;DR**：本仓库是所有 skill 的"原件仓库"。每台机器上 `git pull` 拉下来，跑 `bootstrap.sh` 自动给所有 agent 建快捷方式（symlink）。

---

## 这是什么 / 不是什么

- ✅ **是**：所有 skill 的权威来源（source of truth）
- ❌ **不是**：agent 实际读 skill 的位置。agent 还是从 `~/.config/opencode/skills/` 等自己的目录读，我们只是把那个目录**指向**本仓库的原件
- ✅ **是**：跨机器同步用的（git push / pull）
- ✅ **是**：跨 agent 共享用的（同一个 skill 一次安装、所有 agent 自动可见）

---

## 目录结构

```
agent-skills/
├── README.md           ← 本文件
├── bootstrap.sh        ← 装机脚本（每台机器跑一次）
├── .gitignore
└── skills/             ← 所有 skill 放这里
    ├── find-skills/    ← 第三方 skill 示例
    │   └── SKILL.md
    ├── my-skill/       ← 自己写的 skill
    │   └── SKILL.md
    └── ...
```

**每个 skill 必须是 `skills/<skill-name>/` 这种格式的子目录，里面要有 `SKILL.md` 文件。** `bootstrap.sh` 会自动扫这些子目录。

---

## 你只需要会 4 个 git 命令

| 命令 | 干嘛的 | 频率 |
|---|---|---|
| `git pull` | 拉最新版本 | 几天一次 |
| `git status` | 看哪些文件还没上传 | 不确定就敲 |
| `git add . && git commit -m "说明" && git push` | 上传你的改动 | 改完就 push |
| `git checkout .` | 撤销本地未提交的改动 | 手贱改坏了用 |

> 程序员用的 `branch`、`merge`、`rebase` 这些 —— **你不用学**。

---

## 一台新机器怎么配置（一次性）

```bash
# 1. 拉仓库到本地
cd ~
git clone https://github.com/你的用户名/agent-skills.git

# 2. 跑装机脚本（自动给所有 agent 建快捷方式）
bash ~/agent-skills/bootstrap.sh
```

完事。

---

## 日常使用

### 场景 A：装新 skill（在任意一台机器上）

```bash
cd ~/agent-skills/skills

# 方法 1：clone 别人的 skill 仓库
git clone https://github.com/some-org/cool-skill.git

# 方法 2：自己写一个
mkdir my-skill
# ... 写 SKILL.md ...

# 让当前机器的所有 agent 立即识别
bash ~/agent-skills/bootstrap.sh

# 传到云端，让其他机器也能用
cd ~/agent-skills
git add .
git commit -m "加了 my-skill"
git push
```

### 场景 B：其他机器同步最新 skill

```bash
cd ~/agent-skills
git pull
bash bootstrap.sh
```

### 场景 C：手贱改坏了

```bash
cd ~/agent-skills
git status              # 看哪些文件被改过
git checkout .          # 一键撤销所有本地改动
# 或者只撤销某个文件
git checkout skills/find-skills/SKILL.md
```

---

## 跨平台说明

- **Linux / macOS / WSL**：直接用，`bootstrap.sh` 正常工作
- **Windows 原生**（不是 WSL）：symlink 需要开发者模式或管理员权限。如果遇到问题，告诉我

---

## 常见问题

**Q: 我装在 `~/.config/opencode/skills/baoyu-document-translator/` 这种是手动装的老 skill，要不要迁进来？**
A: 看心情。本仓库只管以后新装的和要跨机器同步的。手动装的留着也行。

**Q: 改了 `~/agent-skills/skills/<x>/SKILL.md`，agent 立刻能看到吗？**
A: 大多数 agent 是启动时扫描的，需要重启 agent 会话或 reload。文件本身 symlink 是实时的。

**Q: bootstrap.sh 跑错了怎么办？**
A: 它是幂等的（safe to re-run），不会破坏已有 symlink。出错会有明确提示。

**Q: 我不想用 symlink，想要真拷贝？**
A: 暂时不支持。如有需求告诉我。
