# 测试用例综合生成技能

## 技能描述

从 Axure 原型或需求文档中提取测试用例，自动生成：
1. **XMind 脑图** - 测试用例结构化管理
2. **测试数据图片** - 用于 OCR 识别测试

## 核心能力

| 能力 | 说明 | 输出 |
|------|------|------|
| XMind 脑图 | 结构化测试用例，包含前置条件、操作步骤、测试数据 | `.xmind` 文件 |
| 测试图片 | 中文证件票据，PIL 渲染，文字 100% 正确 | `.png` 文件 |

---

## 重要结论（实测经验）

### XMind 生成

| 方案 | 可用？ | 说明 |
|------|--------|------|
| Python xmind 库 (v0.1.0) | ❌ 有 bug | stylesbook 为 None 导致崩溃 |
| 直接生成 XML + ZIP | ✅ **唯一可行** | 手动构建 XML，zipfile 打包 |
| JSON 格式 (XMind 2024) | ❌ 不兼容 | XMind 2021 只能打开 XML 格式 |

**XMind 要点**：
- 根节点用 `<topic>`（不是 `<rootTopic>`）
- 必须包含：`content.xml`, `styles.xml`, `comments.xml`, `meta.xml`, `META-INF/manifest.xml`
- 中文 UTF-8 编码完全支持

### 测试图片生成

| 方案 | 中文文字 | 质感 | 可用？ |
|------|---------|------|-------|
| **纯 PIL 渲染** | ✅ 100%正确 | 无 | ✅ 推荐 |
| 直接 text_to_image + 中文提示词 | ❌ 严重乱码 | — | ❌ |
| PIL + img2img（MiniMax） | ❌ 文字被破坏 | 有 | ❌ |
| PIL + Multiply/Screen 叠加 | ❌ 文字模糊 | 有 | ❌ |
| MiniMax text_to_image（风景/英文） | ✅ 英文可读 | 有 | ✅ 仅限此场景 |

**图片核心结论**：
- 中文证件票据 → **纯 PIL 渲染**（文字 100% 正确）
- 需要质感 → **手动用 PS/Canva 叠加纹理**（不要用 AI）
- 风景/英文素材 → MiniMax MCP `text_to_image` 可用
- PIL 图片 + `图片生成提示词.md` → 可对接通义万相、DALL-E

---

## 触发关键词

- "生成测试用例"
- "生成XMind"
- "生成脑图"
- "生成测试数据图片"
- "导出XMind"
- "创建脑图"
- "测试用例转XMind"
- "生成详细测试用例"
- "分析Axure原型"

---

## 使用流程

### 完整流程（三步走）

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: 分析原型/需求文档                               │
│  • 识别功能模块                                          │
│  • 整理正向/负向测试用例                                  │
│  • 确定需要的测试数据类型                                  │
├─────────────────────────────────────────────────────────┤
│  Step 2: 生成 XMind 脑图（测试用例结构）                   │
│  • 功能描述 → 正向用例 → 负向用例                          │
│  • 每个用例：前置条件、操作步骤、测试数据、预期结果、验证点    │
│  • 输出：模块测试用例.xmind                                │
├─────────────────────────────────────────────────────────┤
│  Step 3: 生成测试数据图片（可选）                          │
│  • 根据用例中的测试数据类型生成图片                          │
│  • PIL 渲染：身份证、户口本、营业执照等证件票据              │
│  • 输出：test_data/01_身份证.png                          │
└─────────────────────────────────────────────────────────┘
```

### 简化流程（只需 XMind）

```
提供需求 → 直接生成 XMind 脑图
```

---

## 数据结构

### XMind 完整测试用例格式

```python
{
    "root_title": "模块名称",
    "sheet_title": "工作表名称",
    "branches": [
        {
            "title": "1. 功能模块",
            "children": [
                {
                    "title": "1.1 功能描述",
                    "children": [
                        "功能点1",
                        "功能点2"
                    ]
                },
                {
                    "title": "1.2 正向测试用例",
                    "children": [
                        {
                            "title": "TC-01：用例名称",
                            "children": [
                                "前置条件：xxx",
                                "操作步骤：1. xxx 2. xxx",
                                "测试数据：xxx",
                                "预期结果：xxx",
                                "验证点：1. xxx 2. xxx"
                            ]
                        }
                    ]
                },
                {
                    "title": "1.3 负向测试用例",
                    "children": [
                        {
                            "title": "TC-02：异常场景",
                            "children": [
                                "前置条件：xxx",
                                "操作步骤：1. xxx",
                                "测试数据：xxx",
                                "预期结果：xxx",
                                "验证点：1. xxx"
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

### XMind 简单格式

```python
{
    "root_title": "模块名称",
    "branches": [
        {"title": "1. 功能A", "children": ["用例1", "用例2"]},
        {"title": "2. 功能B", "children": ["用例3"]}
    ]
}
```

---

## 测试数据图片模板

### 公证/身份类模块

| 文件名 | 说明 | 关键字段 |
|--------|------|----------|
| 01_身份证.png | 个人身份证 | 姓名、身份证号、有效期、地址 |
| 02_户口本.png | 户籍证明 | 姓名、与户主关系、地址 |
| 03_出生医学证明.png | 出生公证 | 新生儿姓名、父母信息、出生地 |
| 04_营业执照.png | 企业认证 | 企业名称、法人、经营范围 |
| 05_公证员执业证.png | 资质认证 | 执业证号、有效期、所属机构 |
| 06_任职证明.png | 资质认证 | 姓名、职位、任职时间 |
| 07_监护关系证明.png | 监护代办 | 监护人、被监护人、关系类型 |

### 出行/交通类模块

| 文件名 | 说明 | 关键字段 |
|--------|------|----------|
| 01_火车票.png | 火车票 | 车次、日期、出发地、目的地 |
| 02_机票.png | 电子客票 | 航班号、日期、行程 |
| 03_打车发票.png | 打车发票 | 金额、日期、地点 |
| 04_驾驶证.png | 驾驶证 | 姓名、准驾车型 |

### 文档模板类

| 文件名 | 说明 | 关键字段 |
|--------|------|----------|
| 01_申办人户口本模板.pdf | 材料模板 | 模板格式说明 |
| 02_监护人信息表模板.pdf | 材料模板 | 填写说明 |
| 03_笔录信息表模板.pdf | 材料模板 | 问答格式 |
| 04_授权委托书模板.pdf | 委托代办 | 委托人、受托人信息 |
| 05_被代理人信息表模板.pdf | 委托代办 | 企业/个人信息 |

---

## 图片生成说明

### 中文证件票据（PIL 渲染）

```python
# 使用 PIL 渲染生成测试图片
from PIL import Image, ImageDraw, ImageFont
import os

def create_id_card():
    img = Image.new('RGB', (600, 380), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 设置字体
    font = ImageFont.truetype("msyh.ttc", 24)

    # 绘制内容
    draw.text((50, 50), "中华人民共和国居民身份证", fill=(0, 0, 0), font=font)
    draw.text((50, 120), "姓名：张三", fill=(0, 0, 0), font=font)
    draw.text((50, 160), "性别：男", fill=(0, 0, 0), font=font)
    draw.text((50, 200), "民族：汉族", fill=(0, 0, 0), font=font)
    draw.text((50, 240), "出生：1990-01-01", fill=(0, 0, 0), font=font)
    draw.text((50, 280), "住址：北京市朝阳区XX路XX号", fill=(0, 0, 0), font=font)
    draw.text((50, 320), "公民身份号码：110101199001011234", fill=(0, 0, 0), font=font)

    img.save("test_data/01_身份证.png")
    print("身份证图片已生成")
```

### 无文字素材（MCP 可用）

```python
# 调用 MiniMax MCP 生成风景素材
mcp__minimax__text_to_image(
    prompt="Beautiful mountain landscape, green mountains, blue sky, natural photography, no text in frame",
    output_directory="test_data/"
)
```

### 图片生成提示词模板

生成 PIL 图片后，目录中会生成 `图片生成提示词.md`，包含：
- 必须保留的文字内容（OCR 所需的关键字段）
- 英文提示词（供 DALL-E、通义万相等模型使用）

如需质感：用 PS/Canva 手动叠加纹理（PIL 图片作为底层）

---

## 代码模板

### 生成 XMind 脑图

```python
from create_xmind import create_xmind

data = {
    "root_title": "公证智能体四期测试功能点",
    "sheet_title": "测试用例",
    "branches": [
        {
            "title": "1. 数据资产对接",
            "children": [
                {
                    "title": "1.2 正向测试用例",
                    "children": [
                        {
                            "title": "DAT-01：正常发起数据资产公证",
                            "children": [
                                "前置条件：企业账号已认证",
                                "操作步骤：1.登录APP 2.进入数据资产页面 3.选择资产 4.发起公证",
                                "测试数据：企业名称-北京数字科技有限公司",
                                "预期结果：材料列表显示完整",
                                "验证点：1.申办人信息自动回显"
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

create_xmind(data, "桌面/测试用例.xmind")
```

### 生成测试数据图片

```python
from PIL import Image, ImageDraw, ImageFont

def create_test_images(output_dir="test_data"):
    os.makedirs(output_dir, exist_ok=True)

    # 身份证
    img = Image.new('RGB', (600, 380), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("msyh.ttc", 22)
    draw.text((50, 50), "中华人民共和国居民身份证", fill=(0, 0, 0), font=font)
    draw.text((50, 100), "姓名：张三", fill=(0, 0, 0), font=font)
    draw.text((50, 140), "公民身份号码：110101199001011234", fill=(0, 0, 0), font=font)
    img.save(f"{output_dir}/01_身份证.png")

    # 更多图片...
```

---

## 工作流程详解

### 流程A：完整生成（原型分析 → XMind → 测试图片）

```
1. 分析 Axure 原型页面
   ├── 识别功能模块（5个模块）
   ├── 整理测试用例（50+用例）
   └── 确定测试数据类型（7种证件）

2. 生成 XMind 脑图
   ├── 功能描述分支
   ├── 正向测试用例分支（前置+步骤+数据+预期+验证）
   └── 负向测试用例分支

3. 生成测试数据图片
   ├── 证件类图片（PIL 渲染）
   └── 模板类文档（PIL 渲染 PDF 预览）
```

### 流程B：仅 XMind

```
提供需求/原型 → 构建数据结构 → 生成 XMind → 输出文件
```

### 流程C：仅测试图片

```
提供数据类型 → PIL 渲染生成 → 输出 test_data/ 目录
```

---

## 依赖

| 依赖 | 说明 |
|------|------|
| Python | 3.8+ |
| zipfile | XMind 打包（内置） |
| uuid | 生成唯一 ID（内置） |
| Pillow | 测试图片生成（pip install Pillow） |
| Playwright | 原型页面截图（可选） |

**XMind 生成无需额外依赖**（纯标准库）。
**测试图片需要**：`pip install Pillow`

---

## 常见问题

### XMind 相关

**Q: 生成的文件打不开？**
A: 确认扩展名是 `.xmind`，用 XMind 2021 打开（不是 XMind 2024）

**Q: 中文显示乱码？**
A: XML 声明指定 `encoding="UTF-8"`，Python 使用 `encode('utf-8')`

**Q: 层级结构不对？**
A: 每个 `<topic>` 内只有一个 `<topics type="attached">`

**Q: 生成的文件打不开或报错？**
A: 检查以下常见问题：

| 问题 | 原因 | 修复 |
|------|------|------|
| 文件损坏 | ZIP结构不完整 | 确保包含所有5个必要文件 |
| 乱码 | 中文编码问题 | 使用UTF-8编码，print输出可能乱码但文件本身正确 |
| 拼写错误 | 文件名写错 | `meatdata.xml` → `metadata.xml` |

**XMind 2021 正确文件结构**：
```
.xmind (ZIP压缩包)
├── content.xml          # 测试用例内容（必须）
├── styles.xml          # 样式定义（必须）
├── comments.xml         # 注释（必须）
├── meta.xml            # 元数据（必须）
└── META-INF/
    └── manifest.xml    # 清单文件（必须）
```

**❌ 错误示例（2026-04-17 修复经验）**：
```python
# 错误1：拼写错误
zf.writestr('META-INF/meatdata.xml', ...)  # ❌ meatdata
zf.writestr('META-INF/metadata.xml', ...)  # ✅ metadata

# 错误2：缺少必要文件
zf.writestr('content.xml', ...)
zf.writestr('styles.xml', ...)
# 缺少 comments.xml, meta.xml, META-INF/manifest.xml ❌

# 错误3：终端输出中文乱码（但文件本身正确）
print("生成成功")  # Windows终端显示乱码，但文件UTF-8编码正确
```

**✅ 正确示例**：
```python
def create_xmind():
    with zipfile.ZipFile(xmind_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('content.xml', make_content_xml())
        zf.writestr('styles.xml', make_styles_xml())
        zf.writestr('comments.xml', make_comments_xml())  # 必须
        zf.writestr('meta.xml', make_meta_xml())          # 必须
        zf.writestr('META-INF/manifest.xml', make_manifest_xml())  # 必须
```

**验证XMind文件**：
```python
import zipfile
with zipfile.ZipFile(xmind_path, 'r') as z:
    # 检查文件结构
    print(z.namelist())
    # 检查中文内容
    content = z.read('content.xml').decode('utf-8')
    print('商标列表展示' in content)  # True = 正确
    # 检查ZIP完整性
    bad = z.testzip()
    print(bad is None)  # True = 正常
```

### 测试图片相关

**Q: 中文显示乱码？**
A: 使用 PIL 渲染，**不要用 AI 生成中文图片**

**Q: 想要有质感的图片？**
A: PIL 图片作为底层，用 PS/Canva 手动叠加纹理（不要用 AI）

**Q: 生成哪些测试数据图片？**
A: 根据 XMind 脑图中的"测试数据清单"模块确定类型

---

## Axure 原型截图规范

### 核心原则：先完整后局部

**❌ 错误做法：边截图边分析**
- 直接分段截图，然后基于不完整的截图分析
- 导致遗漏重要内容，反复重试

**✅ 正确做法：先完整后局部**
1. **第一步**：截图完整页面（full_page=True）
2. **第二步**：查看完整截图，确认页面结构和内容
3. **第三步**：分批截图关键区域（如果需要高分辨率）

### 页面结构识别

Axure 原型页面可能有以下特点：

| 特点 | 说明 | 截图方法 |
|------|------|---------|
| 纵向滚动 | 页面高度 > 视口高度 | 设置 `viewport={'height': 页面高度}` |
| **横向滚动** | 页面宽度 > 视口宽度 | 设置 `viewport={'width': 页面宽度}` |
| iframe 嵌套 | 内容在 iframe 中 | 直接访问 iframe 的 URL 截图 |
| 大面积元素 | 内容在单个大 div/img 中 | 使用 `locator('#元素ID').screenshot()` |

### 截图代码模板

```python
from playwright.sync_api import sync_playwright
import os

url = 'Axure原型URL'
output_dir = r'输出目录'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(3000)

    # Step 1: 获取页面实际尺寸
    page_info = page.evaluate('''
        () => {
            // 检查iframe
            const frames = window.frames;
            let iframe_url = '';
            if (frames.length > 1) {
                iframe_url = frames[1].location.href;  // 通常内容在frames[1]
            }

            return {
                bodyWidth: document.body.scrollWidth,
                bodyHeight: document.body.scrollHeight,
                docWidth: document.documentElement.scrollWidth,
                docHeight: document.documentElement.scrollHeight,
                windowWidth: window.innerWidth,
                windowHeight: window.innerHeight,
                iframeUrl: iframe_url
            };
        }
    ''')
    print(f'页面尺寸: {page_info}')

    # Step 2: 截图完整页面（先完整）
    page.screenshot(path=os.path.join(output_dir, 'complete_full.png'), full_page=True)
    print('完整页面截图完成')

    # Step 3: 如果需要高分辨率，截取各区域
    # 方法A: 横向滚动截图
    for x in [0, 1700, 3400, 5100]:
        page.evaluate(f'window.scrollTo({x}, 0)')
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(output_dir, f'part_x{x}.png'))

    # 方法B: 直接截取大面积元素
    elements = page.evaluate('''
        () => {
            const result = [];
            document.querySelectorAll('*').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 2000 || rect.height > 2000) {
                    result.push({ id: el.id, width: rect.width, height: rect.height });
                }
            });
            return result;
        }
    ''')
    print(f'大面积元素: {elements}')

    # 方法C: iframe内部内容
    if page_info['iframeUrl']:
        frame_page = p.chromium.new_page()
        frame_page.goto(page_info['iframeUrl'], wait_until='networkidle')
        frame_page.screenshot(path='iframe_content.png', full_page=True)

    browser.close()
```

### 存证转公证流程图截图经验

**页面尺寸**: 6901px × 5980px（横向滚动页面）

**截图策略**:
1. ✅ 先用 `full_page=True` 截图完整页面
2. ✅ 查看完整截图，确认内容分布
3. ✅ 发现横向布局后，截取各元素：
   - `left_panel_element.png` (2379×1135) - 左侧App界面
   - `flow_panel_element.png` (3124×2840) - 主流程
   - `right_panel_full.png` (2858×5980) - 右侧完整内容

**教训**:
- ❌ 不要边截边分析，导致遗漏
- ✅ 必须先有完整视图，再分批

---

## ⚠️ 行为规范（必须遵守）

### 需求确认规范

**❌ 禁止行为：自作主张、擅自决定**

对于爬取的需求中任何不明确的地方，**必须主动向用户询问确认**，不得自行假设或推断。

**✅ 正确做法：**
- 需求中没写项目名称 → 询问："这个项目叫什么名字？"
- 需求中没写输出格式 → 询问："需要XMind格式还是HTML格式，还是两者都要？"
- 需求中没写模块数量 → 询问："有几个功能模块？"
- URL参数不明确 → 询问："这些URL对应的是哪几期/哪些模块？"

**❌ 错误做法：**
- 用户没说"三期"还是"四期" → 自己猜一个
- 用户没说XMind还是HTML → 自己两个都做（如果用户只要一个就是浪费）
- 用户没说输出到哪 → 自己随便选个位置

### 命名规范

**❌ 禁止行为：擅自自作主张起名字**

当用户提供需求但没有明确指定项目/文件名称时，**必须主动向用户询问确认**，不得自行决定名称。

**✅ 正确做法：**
- 用户提供了5个Axure URL，但没有说明项目名称
- → 主动询问："这5个原型页面，您希望叫什么名字？"

### 输出前确认

生成任何文件之前，如果用户没有明确指定：
1. **项目/文件夹名称** - 必须询问
2. **文件命名规则** - 遵循用户偏好
3. **输出目录** - 询问或使用默认桌面

---

## 更新日志

- **v4.0** (2026-04-17): XMind文件修复经验
  - 新增XMind文件修复常见问题（文件名拼写、文件结构完整性）
  - 新增XMind 2021正确文件结构表
  - 新增验证XMind文件的Python代码

- **v3.0** (2026-04-03): 综合版本
  - 整合 XMind 脑图生成 + 测试数据图片生成
  - 新增完整工作流程（分析 → 脑图 → 图片）
  - 新增图片生成模板和代码示例
  - 新增测试数据类型对照表

- **v2.0** (2026-04-03): 增强版测试用例
  - 新增详细模式：前置条件、操作步骤、测试数据、预期结果、验证点
  - 481 个节点，22KB XMind 文件

- **v1.0** (2026-04-03): 初始版本
  - XMind XML 格式生成
  - 纯 Python 标准库实现
