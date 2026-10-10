# DOCX — key 规则、提取与写回

任务是 DOCX 时读本文件；PPTX 读 `pptx.md`。

## Keys

Element keys are stable across extraction runs:
- `p_body_0`, `p_body_1`, ...
- `t_body_0_r0_c0`, ...
- `p_header_0_0` / `p_headerfirst_0_0` / `p_headereven_0_0`（页脚同理 `p_footer...`；键名中间段是
  story 后缀与 section 序号）
- `fn_0_p0`, `en_0_p0`, ...
- `txbx_0_p0`（文本框）, `p_sdt_0_p0`（SDT）

## 提取范围

`extract_v3.py` 对 DOCX 走全部 story 提取（正文/页眉页脚/脚注尾注/文本框/超链接/域 run 守护）。

## 写回引擎怎么选（环境自适应）

```bash
python scripts/engine_select.py     # 打印 {"recommended": "wir" | "surgical"}
```

| 环境 | 用哪个 | 说明 |
|---|---|---|
| **Linux / WSL2**（CPython 3.12 x86_64） | **WIR**（`docx` skill 自带引擎，`scripts/write_docx_wir.py`） | 只改文字节点、其余一律不碰，保真最省事。**首选。** |
| 原生 Windows / macOS / 引擎缺失 | **surgical**（本 skill 自带 `write_docx_surgical.py`） | 同一思路的纯 Python 实现：全平台可用、出问题可当场改 |

> WIR 说明：那个引擎是第三方写好的**编译产物**（C++，只发布了 Linux 版 `.so`，未附源码），
> 所以**原生 Windows 加载不了**。想在 Windows 上用 WIR：装 WSL2 直接跑现成那份；
> 或者用本 skill 自带的 surgical（已验证可用）。

`write_v3.py` 内部调用 `engine_select.py` 自动分发（Linux/WSL2 + CPython 3.12 x86_64 → WIR，
其余平台 → surgical），日常不需要手动选引擎。

## surgical 引擎说明

只写 `<w:t>` 文本节点（python-docx 定位元素使合并单元格 key 对应、lxml 改写），
保留分页符、`w:ptab`、域（`w:fldChar`/`w:instrText`）、锚定绘图与 `w:pict`；
短高方差分段（封面/标题样式）合并为单 run 避免排版拼凑；多分段单元格经 `para_splits` 保留换行。

## WIR 引擎说明

生成 `TextEdit` 对象按 story 应用，不重建文档。仅 Linux 可加载编译引擎，
接入方式与保真优势详见 `wir-integration.md`。

Legacy fallback（仅当 v3 写回器不可用时）：`write_docx_surgical.py` / `write_docx_wir.py`。

## 质检

DOCX 的结构核对用 `verify_structure.py`（结构节点计数 + 译文覆盖；目标语言含 CJK 时自动改用
`--expect-cjk` 门），检查项与阻断约定见 `qa-pack.md`。
