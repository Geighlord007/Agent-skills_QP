# Skill 速查卡

> 别背，理解一次就够。用的时候 `cat ~/agent-skills/CHEATSHEET.md`。

## 每天用到的 4 个命令

### 1. 同步到最新（开机第一件事）
```bash
cd ~/agent-skills && git pull
```

### 2. 装新 skill（从网上下载别人的）
```bash
cd ~/agent-skills/skills
git clone https://github.com/某组织/某skill.git
bash ~/agent-skills/bootstrap.sh    # 让本机所有 agent 立刻看到
cd ~/agent-skills && git add . && git commit -m "加了 某skill" && git push
```

### 3. 改了 skill 文件（你手动改了 SKILL.md）
```bash
cd ~/agent-skills
git add . && git commit -m "说清楚你改了什么" && git push
# 例子：-m "优化 find-skills 的中文描述"
```

### 4. 撤销改坏的文件
```bash
cd ~/agent-skills
git checkout .                  # 撤销所有未提交的改动
```

---

## shell 小词典（看到不认识的查这里）

| 命令 | 意思 | 类比 Windows |
|---|---|---|
| `cd 路径` | 进入文件夹 | 资源管理器打开文件夹 |
| `cd ..` | 回到上一级 | 点地址栏的 ↑ |
| `ls` | 列出当前文件夹内容 | 看一眼文件列表 |
| `cp a b` | 拷贝 a 成 b | 复制粘贴 |
| `cp -r a b` | 拷整个文件夹 | 复制粘贴文件夹 |
| `rm 文件` | 删除（不进回收站！） | 永久删除 |
| `bash 脚本.sh` | 跑一个脚本 | 双击 .bat |
| `.` | "当前目录" | "这个文件夹" |
| `~` | "/home/你的用户名/" | "C:\Users\你\" |
| `-m` | message（消息） | 微信发朋友圈的配文 |

---

## git 命令（只列你需要的）

| 命令 | 干啥 | 你会用到吗 |
|---|---|---|
| `git clone URL` | 第一次下载仓库 | ✓ 新机器配置 |
| `git pull` | 拉最新 | ✓ 每天 |
| `git status` | 看哪些文件改了 | 忘了就敲 |
| `git add .` | 暂存所有改动 | ✓ 提交前 |
| `git add 文件名` | 暂存某个文件 | 想精细控制时 |
| `git commit -m "..."` | 打包成新版本 | ✓ 改完 |
| `git push` | 上传到 GitHub | ✓ 改完 |
| `git checkout .` | 撤销改动 | 手贱时 |
| `git log --oneline` | 看历史记录 | 偶尔 |
| `git remote -v` | 看云端地址 | 只看一次 |

> **不用学的：** branch、merge、rebase、stash、reset、cherry-pick —— **这辈子不用碰**。

---

## 用 lazygit 替代手动命令（推荐，已装）

在 `~/agent-skills/` 目录里敲 `lazygit` 起来，5 个键搞定一切：

| 按键 | 干啥 |
|---|---|
| `空格` | 暂存/取消暂存文件 |
| `c` | 提交（弹窗输入 message） |
| `p` | 推送到云端 |
| `P` (大写) | 拉取最新 |
| `d` | 看文件具体改了什么 |
| `?` | 看所有快捷键 |
| `q` | 退出 |

典型流程：`cd ~/agent-skills` → 改文件 → `lazygit` → 空格 + c + p → q

---

## 出错先看这里

| 看到 | 怎么办 |
|---|---|
| `fatal: not a git repository` | 你不在仓库目录里，先 `cd ~/agent-skills` |
| `nothing to commit, working tree clean` | 没改东西，不用 commit |
| `Please tell me who you are` | 没设用户名，跑：<br>`git config --global user.name "你的名字"`<br>`git config --global user.email "你的邮箱"` |
| `Updates were rejected` | 你落后了，先 `git pull` 再 `git push` |
| `CONFLICT (...) Merge conflict` | 两台机器改了同一段，找我处理 |
| `Permission denied` | 文件权限问题，复制错误信息给我 |

---

## 三条铁律

1. **改之前 `git pull`，改完立刻 `git push`**
2. **commit message 用大白话**——比如 "修了 typo"、"加了 baoyu-X"、"更新到 v2"
3. **删 `rm -rf` 之前三思**，没回收站

---

**觉得太长？只看第一段"每天用到的 4 个命令"就够了。** 其他都是词典，出事再查。
