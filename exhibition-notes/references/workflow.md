# 会议纪要生成工作流程

## 标准流程

### Step 1: 了解任务
- 确认照片文件夹位置
- 确认照片数量和公司数量
- 确认输出格式要求

### Step 2: OCR 提取
使用 PaddleOCR skill（`clawhub install paddleocr-doc-parsing`）

```bash
python scripts/layout_caller.py --file-path "照片路径" --pretty
```

或用 subagent 并行处理多个文件夹。

### Step 3: 会议总结生成（关键）

#### 3.1 Subagent 读完全部内容，识别主题结构
- 派发一个 subagent 读完全部文字内容
- 直接识别主题结构，**不输出摘要**（避免信息损失）
- subagent 输出：识别出的主题结构

#### 3.2 Main agent 向用户确认
- 把主题结构给用户看
- 用户确认后才开始写
- **不确认不写**

#### 3.3 Subagent 并行整理详细内容
- 用户确认主题结构后
- subagent 可以并行处理各家公司的详细内容

#### 3.4 Main agent 汇总撰写
- 按确认的主题结构撰写总结
- 总结在前，各家详细内容在后

### Step 4: 核对信息
读取"大会日程.docx"获取：
- 正确公司名称
- 演讲人信息

### Step 5: 生成 docx
使用 `scripts/make_docx.py`：
- 会议总结在开头，按主题组织
- 公司名加粗 Heading
- 核心亮点加粗 bullet
- 演讲人单独标注
- 图片嵌入前用 PIL normalize

### Step 6: 照片压缩（如需要）
使用 `scripts/compress_images.py`：
- 只压缩 MVIMG/IMG 开头且 > 500KB 的文件
- 最大边 1024px + 质量 60
- 小图（mmexport）不动

## 已知坑

### python-docx JPEG 嵌入 bug
iPhone 拍摄的 JPEG（MVIMG/IMG 开头）直接用 `doc.add_picture()` 会丢失关系。

**解决方案**：先用 PIL 重新保存：
```python
from PIL import Image
img = Image.open(path)
img = img.convert('RGB')
img.save(path, 'JPEG', quality=85)
```

### markdown 格式问题
subagent 输出不要带 `##` 等 markdown 符号，输出纯文本。

### 主题结构必须先确认
不要用预设框架套内容。先读内容，识别结构，向用户确认后再写。
