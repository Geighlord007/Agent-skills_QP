# nice-baogao

> 把一堆散乱、风格各异的文档，整理成一套统一、好看、图表看得清的报告。
> 不改一个字，不改一个数字。

一个给 AI 用的**文档整理工作流**。你只要说"帮我整理这批文档"，它按固定套路从头做到尾。

## 它解决什么问题

手上有几十份报告：字体各不相同、封面五花八门、图表有的糊有的小到看不清、没图的地方干巴巴全是字、文件命名混乱、想找东西只能一个个打开。

**这个流程把这些变成一套东西。**

## 它会替你做的八件事

| | |
|---|---|
| 1 | **先做可回滚** —— 在动任何文件之前。包括告诉你这一步只保护了哪些、没保护哪些 |
| 2 | **定出一套统一的样子** —— 字体、颜色、图表画法，写成一页标准。从你现有的资料里提取，不是它自己编的 |
| 3 | **按标准套到每一份文档上** —— 文字内容一个字不动 |
| 4 | **需要换语言时全树转换，版式一点不变** —— 合同、商务文件保持双语并加说明 |
| 5 | **按内容重新归档** —— 重复的、过时的收进归档区，每条都写明原因，能单独退回 |
| 6 | **补图、重画图** —— 没图的补上；丑的、字太小的重画；放大到印在纸上看得清为止 |
| 7 | **做一份能直接打开的总览页** 和目录，不用一个个开文件 |
| 8 | **出一份交付报告** —— 哪些做完了、哪些没做、为什么没做 |

## 它**不做**什么（这条最重要）

**它不改你的数字，不改你的结论，哪怕它认为那是错的。**

这不是偷懒，是三条硬理由：

1. **改了等于多一层没人核实过的说法。** 真实案例：这个流程曾经把某公司营收"更正"为约 36 亿瑞士法郎；对着该公司自己公布的业绩一查，真实数字是 **30 亿——那个更正本身错了 20%**。一个自己没被核实的更正，比原来的数字更糟，因为它带着"已经查过"的权威感。
2. **改了会切断和作者出处的联系。** 作者可能有你看不到的依据。你一覆盖，读者既看不到原文，也不知道你依据什么。
3. **改了责任就模糊了。** 数字是作者的责任。将来出问题，没人说得清是谁写的。

**觉得哪个数字可疑？它会单独写一份清单给你，不动文档。** 怎么处理你定。

## 它什么时候会停下来问你

- 一个专业名词不知道该翻成什么
- 一张图**找不到原始文件** → 只报告，不重画（重画等于把作者选的那张图换成另一张）
- 一个标签的字**装不下** → 不会偷偷改成缩写
- 某种样式你没有偏好

## 你会拿到什么

整理好的文档全套 · 一页样式标准 · 能离线打开的网页总览 · 交付报告（含"怎么全部退回原样"）

## 安装

放进 DSH 的 skills 目录即可：

```bash
git clone https://github.com/Geighlord007/nice-baogao.git \
  ~/.dsh/skills/nice-baogao
```

然后对 AI 说 `skill nice-baogao`，或者直接说"帮我整理这批文档"。

## 目录里有什么

```
SKILL.md              说明书：范围、10 个阶段、决策规则
reference/            6 份参考：比例律、工具失灵记录、硬规则、翻译、示意图、模式
tools/                15 个可运行脚本（不是示例代码）
  _paths.py           唯一的配置入口：文档夹路径、字号下限、品牌名
  measure_page.py     从印出来的页面真实测量图上的字有多大
  figcheck.py         画布契约 + 字号下限断言
  docx_brand.py       把规范套到文档上（幂等，不碰非自己创建的部分）
  widen_extent.py     改图片显示尺寸（原子写，写完先验 XML）
  facediff.py         比对图上文字是否被改过
  verify_*.py         收尾验证：计数不变、文档能开、结构完整
```

## 换到你的文档集上

只改一处：`tools/_paths.py` 里的路径、字号下限、页宽，以及 `BRAND_NAME` / `DOCSET_TITLE`。其余按 `SKILL.md` 的阶段走。

---

## English

**nice-baogao** is a reusable AI workflow for hardening a large document set: unify the
layout, apply a design system, add missing figures, redraw ugly or illegible ones — and
prove the result with measurements rather than assertions.

**It does not touch your words or your numbers.** Suspect data is reported separately, in
writing, and never edited into a document. The reason is not caution but experience: an
audit "corrected" a company's revenue to CHF 3.6bn when the published figure was CHF 3.0bn —
the correction was itself wrong by 20%, while carrying the authority of having been checked.

Everything here was learned on a real engagement: 2,459 files, 73 delivered documents,
275 figures, 129 redraw scripts. `reference/DEFECTS.md` records **nine occasions where an
instrument reported clean while the artefact was fine or the input was stale** — including
three times where the faulty instrument was me.

## License

MIT
