# PPTX — key 规则、提取与写回

任务是 PPTX 时读本文件；DOCX 读 `docx.md`。

## Keys

- Shape: `s_0_3`（slide 0, shape 3；组合形状子级追加路径段，如 `s_11_17_1`）
- Table cell: `t_0_5_1_2`（slide 0、形状路径 5、行 1、列 2；含路径段时同理追加）
- Note: `n_0_0`（slide 0 的备注第 0 段）

键名规则：`t_{slide}_{形状路径}_{行}_{列}`、`n_{slide}_{段号}`。

备注页默认提取，`--no-notes` 关闭。

## 提取

`extract_v3.py` 对 PPTX 走形状树遍历（含组合形状子级、表格单元格、备注），并记录 `para_splits`
与逐 run 格式签名（粗体/斜体/字号/颜色）供质检比对。

## 写回

`write_v3.py` 对 PPTX 按 key 中的形状路径（含组合形状子级）定位元素，只写 run 文本，排版不碰；
run 数量与 parts 数量不一致即报错退出。

Legacy fallback（仅当 v3 写回器不可用时）：`write_pptx_v2.py`（只支持顶层形状）。

## 质检

PPTX 的结构核对是回抽比对：重新提取输出文件，逐元素比对文本一致、run 数量一致、
分段切分（`para_splits`）一致、格式签名（粗体/斜体/字号/颜色逐 run）一致、key 集合一致。
检查项与阻断约定见 `qa-pack.md`。
