---
name: exhibition-notes
description: 从展会/会议照片生成结构化会议纪要 docx。当用户说"帮我处理展会记录照片"、"整理会议纪要"、"从照片生成 docx" 时触发。完整流程：OCR 提取 → AI 归纳总结 → 信息核对 → 写入 docx（含格式要求）→ 嵌入压缩图片 → 发送。
---

# Exhibition Notes - 展会/会议记录 Skill

从会议照片文件夹生成结构化会议纪要 docx。

## 核心工作流程

### Step 1: 需求确认
用户说目标 → 直接确认方案，不多余提问。

### Step 2: OCR 提取
- 使用 PaddleOCR（已安装）
- subagent 并行处理各文件夹
- 输出 **Markdown 格式**（保持结构：标题、列表、加粗）

### Step 3: 会议总结生成（关键步骤）

**⚠️ 常见错误：先用预设框架套内容。正确做法是：先读内容，再识别结构，最后确认。**

#### 3.1 Subagent 读完全部内容，识别主题结构
- 派发一个 subagent 读完全部文字内容
- **直接识别主题结构**，不需要先输出摘要（避免信息损失）
- subagent 输出识别出的主题结构

#### 3.2 Main agent 向用户确认主题结构
- 把 subagent 识别的主题结构给用户看
- 用户确认后，才开始写总结
- **不确认不写**

#### 3.3 Subagent 并行整理详细内容
- 用户确认主题结构后
- subagent 可以并行处理各家公司的详细内容

#### 3.4 Main agent 汇总撰写
- **Main agent 负责汇总**，不是派给新的 subagent
- 按确认的主题结构撰写总结
- 总结在前，各家详细内容在后
- **Subagent 只整理各家内容，Main agent 决定如何组装**

### Step 4: 信息核对
- 读"大会日程.docx"获取正确公司名、演讲人
- **自己核对，不问用户**

### Step 5: 整理各家详细内容（Subagent 并行）

**⚠️ 常见错误：Subagent 自己决定内容组织结构。正确做法：Main agent 给出整理框架，Subagent 按框架整理。**

**Main agent 给出整理框架：**
```
公司名
演讲人
核心亮点（2-4条，加粗）
详细正文（关键数据+关键文字保留，有结构）
```

Subagent 按框架整理各家内容，Main agent 决定如何归入各主题。

### Step 6: Docx 输出标准（必须严格遵守）

**最终文档结构：**
```
会议总结（按5个确认的主题结构输出）
├── 主题1
│   ├── 主题总结要点
│   └── 各家公司详细内容（嵌入照片）
├── 主题2
│   └── ...
...
```

**总结部分：**
- 放在文档最开头
- 按确认的5个主题分类
- 每个主题下用编号列表
- 语言平实，不浮夸

**详细内容部分：**
- 各家内容归入对应主题
- 公司名加粗 Heading
- 演讲人斜体
- 核心亮点加粗
- 每家公司下嵌入该文件夹的照片（最多6张）

**照片嵌入：**
- PIL normalize 后再嵌入（避免 iPhone JPEG bug）
- 每家最多6张

**语言风格：**
- 平实，不浮夸
- 不写"颠覆"、"战略物资"、"竞争壁垒"、"重磅"等词
- 是"在做某方向"，不是"某公司领先/突破/重担"
- 层次清晰，主题下用编号列表，每点一意

### Step 7: 照片处理
**必须先压缩照片，再嵌入 docx**

```
压缩参数：最大边 1024px + 质量 60
只压缩 MVIMG/IMG 开头的大文件（> 500KB）
小图（mmexport）不动
```

### Step 8: 发送 + 迭代优化

---

## 已知坑

### python-docx 图片嵌入 bug
直接用 `doc.add_picture()` 嵌入 iPhone 照片会丢失关系。
**必须**先用 PIL 重新保存：
```python
from PIL import Image
img = Image.open(path)
img = img.convert('RGB')  # 关键！避免 RGBA JPEG 问题
img.save(path, 'JPEG', quality=85)
```

### markdown 格式问题
subagent 输出不要带 `##` 等 markdown 符号，输出纯文本。

### 公司名核对
必须读大会日程确认正确名称，不能用文件夹名代替公司名。

---

## 相关脚本

- `scripts/make_docx.py` - 生成 docx（已包含 PIL normalize 逻辑）
- `scripts/compress_images.py` - 压缩大图脚本（最大边 1024px + 质量 60）
- `references/workflow.md` - 详细工作流程文档
