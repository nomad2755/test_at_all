---
name: zentao-bug-report
description: ZenTao Bug creation via API with standard template. Use when user asks to create, submit, or report a bug in ZenTao, or wants to use the standard bug report template (【环境】【账号密码】【前置条件】【操作步骤】【期望结果】【实际结果】【附截图】).
---

# ZenTao Bug Report Skill

Create bugs in ZenTao via API using the standard template.

## ⚠️ 创建 Bug 前必读

**每次创建 Bug 前，必须先读取测试计划排期表获取上下文：**
```bash
cat /root/.openclaw/workspace/skills/zentao-integration/docs/测试计划排期表.md
```

**从中确认：**
1. **模块名称** → Bug 标题格式【模块名称】的具体模块是什么
2. **测试环境 URL 和账号** → 对应业务的正确地址和登录凭证
3. **负责人** → 确定指派人（assignedTo），见下表：

| Bug 模块 | 测试负责人 | 指派账号 |
|---------|-----------|---------|
| APP/物理资产/ PAD | 石大卫 | shidawei |
| 数字资产运营服务平台/后台 | 刘偲 | liusi |
| 数字版权 | 张文骏 | zhangwenjun |
| 个人APP | 方美玲/杨旭 | - |

**完整指派人和模块对照表**：见 `zentao-integration/SKILL.md` →「指派人查询 & APP模块对照」章节

## 附：模块抓取方法（从禅道页面获取真实 module_id）

**重要经验（2026-05-13）**：从已有 Bug 标题提取 module_id 名称的方式不准确，**必须从禅道模块维护页面直接抓取**。

**抓取步骤：**
1. Playwright 登录 ZenTao Web → 访问 `http://192.168.0.28:9980/tree-browse-1-bug-0-0-qa.html`
2. 在 `name="app-qa"` iframe 中提取 JS 变量 `data`：`re.search(r"var\\s+data\\s*=\\s*\\$.parseJSON\\(\\s*['\"](.*?)['\"]\\s*\\)", html, re.DOTALL)`
3. `data` 是**嵌套 JSON**（含 `children` 子数组），必须递归展开每个 `children` 字段，将所有节点合并到同一列表
4. 返回结果含 404 个节点（42 个一级 + 子模块），每个节点含 `id/name/parent/grade/order`
5. 验证：一级模块数=42，总模块数=404
6. 保存到 `docs/数字乡村模块树.md`

---

## 🚨 数据中台 Bug 指派参考（2026-05-12 新增）

**来源文件：** `/root/Downloads/数据中台前端进度统计表.xlsx`

创建数据中台相关 Bug 时，根据以下对照表确定指派人：

### 数据中台责任人速查

| 责任人 | OpenIM ID | 禅道账号 | 负责模块 |
|--------|----------|---------|---------|
| **张海棠** (HTang) | `27` | 待确认 | 首页、公共（消息/系统设置/申请试用/个人中心）、数据资产（资产地图/资产目录/查看详情） |
| **朱艳** | 待确认 | 待确认 | API管理（全部）、数据质量（全部6个子模块） |
| **金毅** | 待确认 | 待确认 | 数据治理-元数据管理/主数据管理、数据安全-数据隐私/数据权限 |
| **曹勇** | 待确认 | 待确认 | 数据安全-敏感数据（数据密级/识别规则/数据发现/识别任务） |
| **张耀文** | 待确认 | 待确认 | 数据开发（数据分析/任务管理/任务流设计器）、用户管理（组织结构/角色管理/用户管理） |
| **徐记平** | 待确认 | 待确认 | 数据集成（数据分析/数据源/任务管理/任务日志）、数据挖掘（全部8个） |
| **王新** | `1965695380` | 待确认 | 数据建模（全部12个子模块） |
| **柴胜杰** | 待确认 | 待确认 | AI智能体 |

### 数据中台 module_id 映射（2026-05-12 实测确认，共59个模块）

> 创建数据中台 Bug 时直接使用以下 module_id（product=1, type=bug）：

| module_id | 模块名称 | 父级 | 责任人 |
|-----------|---------|------|--------|
| 506 | 数据中台 | - (根) | - |
| 507 | API管理 | 506 | 朱艳 |
| 508 | 数据资产 | 506 | 张海棠 |
| 509 | 数据开发 | 506 | 张耀文 |
| 510 | 数据治理 | 506 | 金毅 |
| 511 | 数据安全 | 506 | 金毅/曹勇 |
| 512 | 数据集成 | 506 | 徐记平 |
| 513 | 数据挖掘 | 506 | 徐记平 |
| 514 | 数据建模 | 506 | 王新 |
| 515 | 用户管理 | 506 | 张耀文 |
| 516 | AI智能体 | 506 | 柴胜杰 |
| 517 | 数据分析 | 507 | 朱艳 |
| 518 | API管理 | 507 | - |
| 519 | API调用 | 507 | - |
| 520 | 资产地图 | 508 | - |
| 521 | 资产目录 | 508 | - |
| 522 | 查看详情 | 508 | - |
| 523 | 数据分析 | 509 | - |
| 524 | 任务管理 | 509 | - |
| 525 | 任务流设计器 | 509 | - |
| 526 | 元数据管理 | 510 | 金毅 |
| 527 | 主数据管理 | 510 | 金毅 |
| 528 | 数据质量 | 510 | 朱艳 |
| 529 | 敏感数据 | 511 | 曹勇 |
| 530 | 数据隐私 | 511 | 金毅 |
| 531 | 数据权限 | 511 | 金毅 |
| 532 | 数据分析 | 512 | - |
| 533 | 数据源 | 512 | - |
| 534 | 任务管理 | 512 | - |
| 535 | 任务日志 | 512 | - |
| 536 | 质量监控 | 528 | - |
| 537 | 质量对象 | 528 | - |
| 538 | 质量规则 | 528 | - |
| 539 | 质量任务 | 528 | - |
| 540 | 校验结果 | 528 | - |
| 541 | 质量报告 | 528 | - |
| 542 | 数据密级 | 529 | - |
| 543 | 识别规则 | 529 | - |
| 544 | 数据发现 | 529 | - |
| 545 | 识别任务 | 529 | - |
| 546 | 脱敏规则 | 530 | - |
| 547 | 白名单 | 530 | - |
| 548 | 集成脱敏规则 | 530 | - |
| 549 | 用户组 | 530 | - |
| 550 | 我的权限 | 531 | - |
| 551 | 权限审批 | 531 | - |
| 552 | 权限审计 | 531 | - |
| 553 | 数据检索 | 526 | - |
| 554 | 元数据分析 | 526 | - |
| 555 | 元数据采集 | 526 | - |
| 556 | 数据模型 | 527 | - |
| 557 | 编码规则 | 527 | - |
| 558 | 主数据维护 | 527 | - |
| 559 | 主数据分发 | 527 | - |
| 560 | 建模看板 | 514 | - |
| 561 | 数仓分层 | 514 | - |
| 562 | 原子指标 | 513 | - |
| 563 | 派生指标 | 513 | - |
| 564 | 复合指标 | 513 | - |

> 共 59 个模块（ID 506~564），由 Playwright 批量创建，父子关系已确认。可直接用于 Bug 创建。

### 数据中台 Bug 标题格式

```
【数据中台-模块名】具体bug内容
```

示例：
- `【数据中台-API管理】API市场搜索结果为空时无提示`
- `【数据中台-数据质量】质量监控页面无法加载`
- `【数据中台-数据建模】数仓分层保存失败`

---

## 🚀 智能创建 Bug（推荐）

**使用 `auto_bug_creator.py` 自动识别模块 + 填充信息：**

```bash
# 提交一个 Bug（severity=3, pri=3 默认）
python3 /root/.openclaw/workspace/scripts/auto_bug_creator.py "我的数字家园里面的照片按钮点击没有反应"

# 指定严重程度和优先级
python3 /root/.openclaw/workspace/scripts/auto_bug_creator.py "登录失败" 2 1

# 试运行（不实际提交）
python3 /root/.openclaw/workspace/scripts/auto_bug_creator.py "登录失败" --dry-run

# ⭐ 自动上传最新截图并添加到 Bug（推荐）
python3 /root/.openclaw/workspace/scripts/auto_bug_creator.py "登录失败" --screenshot
```

**自动完成：**
- ✅ 从 `测试计划排期表.xlsx` 读取模块的 URL、账号、负责人
- ✅ 根据 Bug 描述关键词（个人app/数字家园/电商/版权/碳汇/后台等）自动匹配模块
- ✅ 自动填充 `module_id`（对应 ZenTao 所属模块）
- ✅ 自动映射指派人（石大卫→shidawei，张文骏→zhangwenjun，刘偲→liusi）
- ✅ 自动生成 Bug 标题前缀【模块名称】
- ✅ 智能构建 steps HTML 模板
- ⚠️ 表格中数据不完整的模块（个人APP/个人数字空间）有硬编码补充

**已知 module_id 映射（2026-05-13 禅道页面实测，共 404 个）：**

> 完整列表已保存到 `skills/zentao-integration/docs/数字乡村模块树.md`
> 一级模块（42个）：

| module_id | 模块名称 |
|-----------|---------|
| 454 | 数据资产综合管理服务平台 |
| 146 | 数据资产运营服务管理平台 |
| 237 | 数字版权 |
| 322 | 数字版权优化 |
| 489 | CRM系统 |
| 484 | 华骏官网 |
| 196 | 新版AI小优 |
| 430 | 文化资产 |
| 156 | 个人APP |
| 157 | 人工智能多轮对话 |
| 158 | 生态农场 |
| 159 | 物理资产 |
| 160 | 生态价值资产 |
| 161 | 活立木 |
| 162 | 生态积分 |
| 163 | 碳汇 |
| 164 | 数字商城 |
| 165 | 数据资产入表 |
| 129 | OA系统 |
| 398 | 价值评估智能体 |
| 345 | 智能客服 |
| 295 | 个人数字空间 |
| 124 | 碳足迹 |
| 125 | 生态价值 |
| 274 | 数字钱包 |
| 254 | 二维码溯源 |
| 150 | 人工智能 |
| 154 | 数字资产管理平台（后台） |
| 181 | 黄陂人民医院多媒体信息发布系统 |
| 189 | 黄陂人民医院官网 |
| 201 | 专利项目管理平台 |
| 210 | 统一身份认证平台 |
| 228 | 个人和公司知识库 |
| 103 | 资产管理平台（Web） |
| 102 | 资产汇聚平台（APP） |
| 384 | 法律智能体 |
| 101 | 后台管理系统 |
| 121 | PAD终端 |
| 385 | 公证智能体 |
| 444 | 短视频电商 |
| 472 | 邀请码专项 |
| 506 | 数据中台 |

> ⚠️ 如需更细粒度的子模块 ID，请查阅 `数字乡村模块树.md`

**如果模块 ID 未知**，工具会自动设为 0，需要人工确认后手动更新。

## Quick Start（手动方式）

```bash
# 1. Get token (if expired)
TOKEN=$(curl -s -X POST "http://192.168.0.28:9980/api.php/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{"account":"shidawei","password":"shidawei"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# 2. Create bug
curl -s -X POST "http://192.168.0.28:9980/api.php/v1/bugs" \
  -H "Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Zentao-Version: 22.4" \
  -d '{
    "product": 1,
    "title": "【模块名】具体bug内容",
    "module": <module_id>,
    "steps": "<p>【环境】</p><p>...</p>",
    "severity": 3,
    "pri": 3,
    "type": "function",
    "openedBuild": "trunk",
    "assignedTo": "shidawei"
  }'
```

## Screenshot Handling (Bug 截图处理) - ⭐ 优先方案

当用户提交 Bug 时提供截图，**严格优先使用数字资产管理平台上传播图**，获得永久 URL。

### ⭐ 方案一：数字资产管理平台上传（推荐，永久 URL）

**上传脚本：** `python3 scripts/upload_to_whhnhy.py <图片路径>`

**步骤 1：上传截图**

```bash
# 上传指定文件
python3 /root/.openclaw/workspace/scripts/upload_to_whhnhy.py /root/.openclaw/media/inbound/xxx.png

# 或者自动使用最新截图
python3 /root/.openclaw/workspace/scripts/upload_to_whhnhy.py --latest
```

**步骤 2：在 steps 的【附截图】处填入返回的永久 URL**

```html
<p>【附截图】</p><p>https://www.whhnhy.com:8900/szxc/<hash>.png</p>
```

**优点：**
- ✅ URL 永久有效，不受服务器重启影响
- ✅ 不需要穿透服务
- ✅ 直接可用，无需额外操作

---

### ⚠️ 备选方案：Serveo 临时穿透（仅紧急情况使用）

如果数字资产管理平台不可用，再用此方案：

**步骤 1：确定正确的截图文件**

⚠️ 用户每次发来的新截图会保存在 `/root/.openclaw/media/inbound/` 下，文件名为时间戳 UUID。**每次都要用最新上传的文件**，不要用之前缓存或复制过的旧文件。

```bash
# 查看最新上传的文件（按时间排序，最新的在最前面）
ls -lt /root/.openclaw/media/inbound/

# 取最新的 .png 文件（第一行）
NEWEST=$(ls -t /root/.openclaw/media/inbound/*.png 2>/dev/null | head -1)

# 复制到 bug_screenshots/，用描述性文件名
cp "$NEWEST" /root/.openclaw/workspace/bug_screenshots/<描述性文件名>.png
```

**步骤 2：启动 Serveo 穿透**

```bash
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8099 serveo.net
```

输出示例：`Forwarding HTTP traffic from https://xxxx.serveousercontent.com`

**步骤 3：在 steps 的【附截图】处填入公网 URL**

```html
<p>【附截图】</p><p>https://<公网URL>/screenshots/<文件名>.png</p>
```

⚠️ **Serveo URL 每次都变化（非静态）**，截图文件名建议用纯 ASCII 避免 URL 编码问题。

## Bug Template (Standard)

```
【环境】
- 测试地址：
- 浏览器：
- APP版本：

【账号密码】
- 用户名：
- 密码：

【前置条件】
1. 

【操作步骤】
1. 

【期望结果】
1. 

【实际结果】
1. 

【附截图】
暂无
```

## Field Reference

| Field | Required | Notes |
|-------|----------|-------|
| `product` | ✅ | Product ID (数字乡村v1.1 = 1) |
| `title` | ✅ | Format: 【模块名称】具体bug内容，e.g. 【电商】无法购买商品 |
| `module` | ✅ | **Module ID（数字）**，不是模块名称！从已有 Bug 反查或询问用户 |
| `steps` | ✅ | HTML `<p>` 格式 |
| `severity` | ✅ | 1-5 (1=最严重) |
| `pri` | ✅ | 1-4 (1=最高) |
| `type` | ✅ | codeerror / interface / function / performance / others |
| `openedBuild` | ✅ | Always `"trunk"` |
| `assignedTo` | ○ | shidawei / zhangwenjun / liusi |

See `references/fields.md` for complete field list and severity/pri reference.