# Axure HTML 原型需求提取工具（curl 法）

通过直接下载 Axure 导出的 HTML 页面文件，解析页面表单字段、业务规则，生成结构化需求文档。

## 背景

当 Axure 原型部署在内网环境时，Playwright 浏览器无法访问（超时）。本工具使用 curl 直接下载 HTML 文件，无需浏览器渲染。

## 快速开始

### 方式一：命令行

```bash
python3 scripts/extract.py <BASE_URL> <PAGE_ID> <PAGE_NAME> [OUTPUT_DIR]

# 示例
python3 scripts/extract.py \
  "https://www.whhnhy.com:37777/axure/digital-asset/sjzcyyfwpt12" \
  "wu2oxn" \
  "数据登记列表（四期）" \
  "/root/.openclaw/workspace/test-team/docs"
```

### 方式二：作为 Skill 使用

当用户提供 Axure 原型链接且 Playwright 访问超时时，优先使用本 skill。

## 工作原理

1. 下载 `BASE_URL/data/document.js` 获取页面索引（ID → 文件名映射）
2. 下载 `PAGE_NAME.html?id=PAGE_ID` 获取页面内容
3. Python 清洗 HTML 标签，提取纯文本
4. 解析字段名、业务规则、交互逻辑
5. 输出结构化需求文档

## 文件结构

```
axure-html-extractor/
├── SKILL.md           # 技能说明
├── README.md          # 本文件
├── package.json       # npm 元数据
├── _meta.json         # 内部元数据
└── scripts/
    └── extract.py    # 提取脚本
```

## 与 Playwright 方法对比

| 方法 | 适用场景 | 速度 | 稳定性 |
|------|----------|------|--------|
| Playwright | 外网可访问 | 慢 | 不稳定（内网易超时） |
| curl | 内网/外网均可 | 快 | 稳定 |

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| document.js 返回 404 | 尝试 `resources/scripts/axure/doc.js` |
| 页面 ID 找不到 | 用中文页面名搜索 document.js |
| 下载的 HTML 很小 | 添加 `?id=PAGE_ID` 参数 |
| 中文乱码 | 确保使用 UTF-8 编码读取 |
