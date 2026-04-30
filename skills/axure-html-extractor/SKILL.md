---
name: axure-html-extractor
description: "通过 curl 直接下载 Axure 导出的 HTML 文件，解析页面表单字段、业务规则、交互逻辑，生成结构化需求文档。适用于内网环境或 Playwright 无法访问的场景。输入 Axure 原型链接，输出需求文档。"
version: 1.0.0
author: Commander Agent
metadata:
  trigger_keywords:
    - "axure"
    - "原型链接"
    - "从原型提取需求"
    - "提取原型需求"
    - "内网axure"
    - "axure html"
    - "curl提取"
---

# Axure HTML 原型需求提取（curl 直接下载法）

## 背景

当 Axure 原型部署在内网环境时，Playwright 浏览器无法访问（超时）。本工具使用 curl 直接下载 HTML 文件，无需浏览器渲染，速度快且稳定。

## 核心原理

Axure 导出的 HTML 是**纯静态文件**，直接下载即可获取完整内容，不需要渲染 JS。

- **Playwright**：启动浏览器 → 访问 URL → 等 JS 加载 → 读 DOM（内网容易超时）
- **curl**：直接下载 HTML 文件 → 清洗标签 → 读纯文本（快稳，但丢失 CSS 样式信息）

## 技术流程

### 步骤 1：探测 document.js 获取页面文件名

```bash
BASE_URL="https://www.example.com/axure/项目名"
curl -s "$BASE_URL/data/document.js" > /tmp/document.js
```

document.js 包含页面 ID → HTML 文件名映射，格式：
```
"pageId",bq="页面名",br="页面名.html"
```

```python
import re

with open('/tmp/document.js', 'r', encoding='utf-8', errors='ignore') as f:
    doc = f.read()

# 查找页面 ID 对应的文件名
# 格式: "wu2oxn",bq="数据登记列表（四期）",br="数据登记列表（四期）.html"
pattern = rf'"{page_id}"[^,]*bq="([^"]+)"[^,]*br="([^"]+\.html)"'
match = re.search(pattern, doc)
if match:
    page_name = match.group(1)
    page_file = match.group(2)
```

### 步骤 2：下载页面 HTML

```bash
PAGE_FILE="数据登记列表（四期）.html"
PAGE_ID="wu2oxn"
curl -s "$BASE_URL/$PAGE_FILE?id=$PAGE_ID" -o /tmp/page_$PAGE_ID.html
```

注意：页面名包含中文时，URL 访问时需要保持中文编码（curl 会自动处理）。

### 步骤 3：Python 清洗 HTML，提取纯文本

```python
import re

with open(f'/tmp/page_{page_id}.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# 清洗 HTML
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '', text)
text = re.sub(r'&nbsp;', ' ', text)
text = re.sub(r'&amp;', '&', text)
text = re.sub(r'\s+', ' ', text).strip()
```

### 步骤 4：从纯文本中解析内容

```python
# 提取必填字段（* 字段名：）
required_fields = re.findall(r'\* ([^：]+)：', text)

# 提取字段规则段落
field_rules = re.search(r'字段规则\s*([\s\S]+?)(?=交互规则|页面交互)', text)
if field_rules:
    rules_text = field_rules.group(1)

# 提取交互规则段落
interaction_rules = re.search(r'交互规则\s*([\s\S]+?)(?=取消|提交)', text)
if interaction_rules:
    interaction_text = interaction_rules.group(1)

# 提取按钮
buttons = re.findall(r'(取消|提交|存草稿|重置|删除|编辑|查看)[^取消提交存草稿]*', text)
```

### 步骤 5：识别字段类型和约束

| 标识 | 含义 |
|------|------|
| `* 字段名：` | 必填字段 |
| `字段名：xxx` | 普通字段 |
| `请输入xxx` | placeholder 提示 |
| `0-500字内` | 长度约束 |
| `单选` / `可多选` | 选择约束 |
| `如果...则...` | 条件显示 |
| `必填` | 必填标识 |
| `{KB,MB,GB}` | 枚举值 |

### 步骤 6：生成需求文档

```markdown
# 【页面名称】 - 需求文档

## 一、页面概述
- 页面名称：
- 页面 ID：
- 所属模块：
- 功能说明：

## 二、表单字段说明
| 字段名 | 类型 | 约束 | 必填 | 说明 |

## 三、业务规则
### 3.1 字段联动规则
### 3.2 条件显示规则

## 四、交互规则

## 五、页面操作
```

## 完整执行脚本

见 `scripts/extract.py`

```bash
# 使用方法
python3 scripts/extract.py <BASE_URL> <PAGE_ID> <PAGE_NAME> [OUTPUT_DIR]

# 示例
python3 scripts/extract.py \
  "https://www.whhnhy.com:37777/axure/digital-asset/sjzcyyfwpt12" \
  "wu2oxn" \
  "数据登记列表（四期）" \
  "/root/.openclaw/workspace/test-team/docs"
```

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| document.js 返回 404 | 可能是 Axure RP8 格式 | 尝试 `resources/scripts/axure/doc.js` |
| 页面 ID 在 document.js 中找不到 | 格式不同 | 用页面中文名搜索 |
| 下载的 HTML 内容很少 | 需要加 `?id=PAGE_ID` 参数 | 确认 URL 包含 query string |
| HTML 全是框架代码 | 找错了文件 | 确认是 `.html` 页面文件 |
| 中文乱码 | 编码问题 | 使用 `encoding='utf-8', errors='ignore'` |

## 依赖

```bash
# 仅需 curl 和 Python3（标准库）
pip install playwright  # 可选，仅用于对比测试
```

## 注意事项

1. **URL 编码**：BASE_URL 不要编码，文件名用原始中文（curl 自动处理）
2. **Query String**：`?id=PAGE_ID` 参数必须加
3. **编码处理**：使用 `encoding='utf-8', errors='ignore'`
4. **字段定位**：重点关注 `*` 必填标识、`字段名：`格式、`字段规则`段落
5. **联动逻辑**：同一字段在不同条件下有不同选项时，从"字段规则"中提取联动关系
6. **列表页面**：如果是列表页（如数据登记列表），重点提取 Tab 状态、查询条件、列表字段、操作按钮
