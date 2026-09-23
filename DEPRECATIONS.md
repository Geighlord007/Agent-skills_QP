# 废弃登记（Deprecations）

本文件记录**已标记废弃**的技能：为什么废弃、谁来替代、验证过什么、以及删除时的检查清单。
目的是让以后回看时能还原"当时发生了什么"，而不是突然发现某个目录没了。

## 处理流程（三步走）

```
① 标记废弃  →  ② 缓冲观察（确认无人依赖）  →  ③ 删除并留痕
```

- **① 标记**：改该技能的 `SKILL.md`（`description` 前缀 + 正文顶部横幅），并在本文件登记一行。
- **② 缓冲**：保留目录不动，继续能看、能对照；期间如发现仍被引用，回到 ① 修正说明。
- **③ 删除**：`git rm -r <目录>` 单独提交，提交信息引用本文件的对应条目；**删除时必须同步更新根 `README.md` 的目录树**。
  删除不会丢历史：随时可用 `git checkout <删除前的提交> -- <目录>` 取回。

---

## 登记表

| 技能 | 标记日期 | 替代者 | 状态 | 实际删除 |
|---|---|---|---|---|
| `baoyu-document-translator` (v1, 1.0.0) | 2026-09-23 | `baoyu-document-translator-v2` (v2.2.2) | **已删除** | 2026-09-23（当日，所有者决定） |

### 条目：`baoyu-document-translator` (v1)

**为什么废弃**

- 它的写回方式是 `python-docx` 的 `run.text = ...`，会**静默丢掉**域（`w:fldChar`/`w:instrText`）、分页符、`w:tab`/`w:ptab`、锚定图片与 `w:pict`——这一类损失正是 v2 的 `write_docx_surgical.py` / WIR 写回要避免的。
- 合并单元格、页眉页脚（首页/偶数页变体）、文本框、内容控件等覆盖不全。
- 没有质检能力（只有很弱的 `validate.py`），出错时不会报红。

**替代者的优势（v2）**

- 只改文字节点（surgical）或在 Linux/WSL2 上用 WIR 引擎；结构、样式、图片、域全部保留。
- 可选质检包：结构门禁、渲染 QA（空白页/残留源语言/目录页码）、中→英版式本地化、分页预 pass、23 项回归自测。
- 另加 XLSX 支持（`scripts/xlsx_translate.py`）。

**验证：没有任何东西在调用它**

- 全仓库检索 `baoyu-document-translator`（排除 `-v2`）共 **11 处**，逐条核对后全部是：
  - v1 自身的 `SKILL.md`（name / homepage / 自己的目录树）——3 处
  - v2 的文档里**讲历史**（"v2 是 v1 的优化分支"、"v1 有哪些毛病"、"若要回馈上游"）——7 处
  - 根 `README.md` 的目录树——1 处
- **没有任何脚本、流程或其它技能调用 v1 的脚本。**

**删除时的检查清单**（已于 2026-09-23 全部执行）

- [x] `git rm -r baoyu-document-translator`
- [x] 更新根 `README.md` 目录树里那一行（已移除）
- [x] 提交信息写明：`remove deprecated baoyu-document-translator (v1, see DEPRECATIONS.md)`
- [x] 删除后按下方命令验证仍可取回

**删除记录**

- **实际删除日期**：2026-09-23（与标记同日，**缓冲期 0 天**）
- **为什么没有缓冲**：仓库所有者当天决定立即删除；依赖核查（见上）已确认无任何调用方，因此风险可接受。
  这是对 `DEPRECATIONS.md` 默认流程（标记 → 缓冲 → 删除）的一次有意偏离，记录在此以便回看时不误判。
- **删除内容**：11 个文件 / 43.4 KB（`SKILL.md`、`references/schema.md`、`scripts/` 下 9 个脚本）
- **删除提交**：`remove deprecated baoyu-document-translator (v1, see DEPRECATIONS.md)`；
  用 `git log --diff-filter=D --name-only -- baoyu-document-translator` 可定位（不写死哈希，避免后续改动失效）
- **删除后的影响**：无。v2 的文档里仍有 7 处提到 v1，那些是**历史说明**（"v2 是 v1 的优化分支"等），不是调用。

**如何取回（删除之后）**

```bash
# 找到删除前的提交
git log --diff-filter=D --name-only -- "baoyu-document-translator"
# 把目录恢复出来
git checkout <删除前的提交>^ -- baoyu-document-translator
```

**备份位置**：GitHub 上游 `JimLiu/baoyu-skills#baoyu-document-translator`；本仓库 git 历史。
