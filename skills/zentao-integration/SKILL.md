# ZenTao Integration Skill

ZenTao 禅道集成技能 - 用于管理需求、测试用例、Bug等。

## ⚠️ 每次任务前必读

**文件位置**: `docs/测试计划排期表.md`

**执行任何 ZenTao 相关任务前（创建 Bug/用例/需求/查询数据），必须先读取此文件：**
- 了解当前项目的**测试环境、URL、账号密码**
- 确认**项目时间线、负责人、提测状态**
- 获取**业务版块和模块名称**（用于 Bug 标题和用例归属）
- 参考**测试流程规范**，确保操作符合团队标准

```bash
cat /root/.openclaw/workspace/skills/zentao-integration/docs/测试计划排期表.md
```

## 功能

- ✅ 创建需求文档（Story）及子需求
- ✅ 创建测试用例并关联到需求
- ✅ 批量导入测试用例
- ✅ 创建测试用例模块
- ✅ 查询和验证数据

## 重要发现（经验总结）

### 1. 测试用例关联需求（⚠️ 重要纠正 2026-05-13）

**关键发现**: 必须同时使用 `parent` 和 `story` 两个字段，缺一不可！

```python
# ❌ 错误方式 - 只用 parent（ZenTao UI 需求的「测试用例」Tab看不到）
data = {"title": "用例标题", "parent": 需求ID}
# → API 返回 id 但 story=0，需求页面看不到

# ❌ 错误方式 - 只用 story
data = {"title": "用例标题", "story": 需求ID}
# → 可能不生效

# ✅ 正确方式 - 同时使用 parent + story
data = {
    "title": "用例标题",
    "parent": 需求ID,   # 控制父子用例关系
    "story": 需求ID,    # 控制显示在需求的「测试用例」Tab
    "module": module_id,
    "pri": 1,
    "type": "feature",
    "steps": [{"desc": "步骤", "expect": "预期"}]
}
```

**验证方法**: 创建后查 API `GET /testcases/{id}`，确认 `story` 字段等于需求ID。
在 ZenTao UI 打开 `story-view-{需求ID}.html`，切换到「测试用例」Tab 应能看到关联的用例。

### 2. Steps 字段格式

**关键发现**: `steps` 必须传 JSON 数组，不能是字符串！

```python
# ❌ 错误方式 - 字符串格式
data = {"steps": "[{\"desc\":\"步骤\",\"expect\":\"预期\"}]"}

# ✅ 正确方式 - 数组格式
data = {"steps": [{"desc": "步骤", "expect": "预期"}]}
```

### 3. 创建时的产品ID问题

- 产品1创建的需求/测试用例可能在UI上显示不正常
- 建议使用产品2创建测试用例
- 创建后验证 `product` 字段

### 4. HTTP 502 处理

批量导入时偶发502错误，需要重试机制。

## API 端点


**自动创建 Bug（推荐）**：使用 `auto_bug_creator.py` 自动识别模块 + 填充信息，参考 `zentao-bug-report` Skill。

**Bug 创建标准模板**（手动方式）：
- 标题：`【模块名称】具体bug内容`
- steps：HTML `<p>` 格式
- `module`：传 **module_id（数字）**，不是模块名称！
- openedBuild：`"trunk"`
- 已知 module_id：个人数字空间=102，iOS=295，物理资产=121，资产管理/数字文化=430，数据资产运营服务平台=161，多轮对话=162，碳足迹核算模型=198

**关键点（快速参考）：**
- `steps` 字段用 **HTML `<p>` 标签**，不是 JSON 数组
- `openedBuild` 传 `"trunk"`，不是数字 ID
- 模板：
```html
<p>【环境】</p><p>- 测试地址：</p><p>【账号密码】</p><p>- 用户名：</p><p>【前置条件】</p><p>1. </p><p>【操作步骤】</p><p>1. </p><p>【期望结果】</p><p>1. </p><p>【实际结果】</p><p>1. </p><p>【附截图】</p><p>暂无</p>
```
- severity: 1致命/2严重/3一般/4轻微/5建议
- pri: 1紧急/2高/3中/4低

### 指派人查询 & APP模块对照

⚠️ **创建 Bug 时，如果不确定指派给谁或属于哪个模块，必须先查这个表！**

完整数据在：`docs/测试计划排期表.md` → Sheet 2（测试项目跟踪表）

#### 指派人快速查询（按模块/项目）

| Bug 涉及模块 | 平台 | 测试负责人 | 产品负责人 | 指派账号（ZenTao account） |
|------------|------|----------|-----------|------------------------|
| 数字资产汇聚中心App（农民角色） | APP | 石大卫 | - | shidawei |
| 数字资产汇聚中心App（政府角色） | APP | 石大卫 | - | shidawei |
| PAD-物理资产版块（农民） | PAD | 石大卫 | - | shidawei |
| PAD-物理资产版块（政府） | PAD | 石大卫 | - | shidawei |
| 资产管控汇聚平台（后台） | 后台 | 刘偲 | - | liusi |
| 数字资产运营服务平台 | PC | 刘偲 | - | liusi |
| 数字版权（发行方） | PC | 张文骏 | - | zhangwenjun |
| 个人APP | APP | 方美玲/杨旭 | 方美玲/杨旭 | - |
| 数字版权（用户） | PC | - | 王紫珊 | - |
| 碳汇服务平台 | Web | - | 陈斯 | - |
| 碳足迹综合管理平台 | Web | - | 陈斯 | - |
| 活立木交易平台 | Web | - | 陈斯 | - |
| 数字资产管理平台（红色PC） | PC | - | - | - |
| 知识库 | Web | - | - | - |
| 短视频电商（商户） | PC | - | - | - |
| 短视频电商（发行方） | PC | - | - | - |
| 价值评估智能体平台 | Web | - | - | - |
| 东方数碳 | Web | - | - | - |
| 公证智能体 | Web | - | - | - |
| 法律智能体 | Web | - | - | - |
| 智能客服 | Web | - | - | - |
| 黄陂人民医院官网 | Web | - | - | - |
| 专利项目管理平台 | Web | - | - | - |
| 星河全球数字资产管理平台（大屏） | 大屏 | - | 骆炳森 | - |

**查指派人的标准操作：**
1. 先确定 Bug 属于哪个业务模块
2. 在上表中找到对应的测试负责人
3. 在 ZenTao 中搜索该负责人的账号（通常是姓名拼音）
4. 如果找不到，通过 `GET /users` API 确认账号

#### 数据中台 Bug 指派参考（2026-05-12 新增）

> **来源：** `/root/Downloads/数据中台前端进度统计表.xlsx`
> 创建数据中台相关 Bug 时使用，参考指派人和 module_id

| 责任人 | 负责模块 | 禅道账号 | OpenIM ID |
|--------|---------|---------|----------|
| 张海棠 | 首页、公共（消息/系统设置/申请试用/个人中心）、数据资产 | 待确认 | HTang/27 |
| 朱艳 | API管理、数据质量（6个子模块均0%进度） | 待确认 | 待确认 |
| 金毅 | 数据治理-元数据/主数据、数据安全-数据隐私/数据权限 | 待确认 | 待确认 |
| 曹勇 | 数据安全-敏感数据（4个子模块） | 待确认 | 待确认 |
| 张耀文 | 数据开发、用户管理 | 待确认 | 待确认 |
| 徐记平 | 数据集成、数据挖掘 | 待确认 | 待确认 |
| 王新 | 数据建模（全部12个模块） | 待确认 | 1965695380 |
| 柴胜杰 | AI智能体 | 待确认 | 待确认 |

### module_id（2026-05-12 确认，全部实测）

创建数据中台 Bug 时使用以下 module_id（product=1, type=bug）：

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

> 共 59 个模块（506~564），由 Playwright 批量创建，父子关系已确认。可直接用于 Bug 创建。

---

---
## 附录：模块抓取方法（从禅道页面获取真实 module_id）

⚠️ **重要经验（2026-05-13）**：从已有 Bug 标题提取 module_id 名称的方式不准确（会提取父模块的误名称），**必须从禅道模块维护页面直接抓取**。

**抓取步骤：**

1. Playwright 登录 ZenTao Web（`input[name="account"]` / `input[name="password"]`）
2. 访问模块树页面：`http://192.168.0.28:9980/tree-browse-1-bug-0-0-qa.html`
3. 等待页面加载完成（8秒）
4. 在 `name="app-qa"` 的 iframe 中提取 JS 变量：
   ```python
   frame1 = frames[1]
   html = frame1.content()
   match = re.search(r"var\s+data\s*=\s*\$\.parseJSON\(\s*['\"](.*?)['\"]\s*\)", html, re.DOTALL)
   raw_str = match.group(1).replace('\\"', '"')
   ```
5. 由于 data 包含嵌套的 `children` 字段（子节点 JSON 数组），需要**递归解析**每个对象，将所有节点展开到同一层级：
   ```python
   def extract_nested(raw_str):
       all_nodes = []
       def parse_array(arr_str):
           nodes = []
           i = 0
           while i < len(arr_str):
               if arr_str[i] == '{':
                   depth = 1
                   j = i + 1
                   while j < len(arr_str) and depth > 0:
                       c = arr_str[j]
                       pc = arr_str[j-1] if j > 0 else ''
                       if c == '{' and pc != '\\': depth += 1
                       elif c == '}' and pc != '\\': depth -= 1
                       j += 1
                   obj_str = arr_str[i:j]
                   try:
                       obj = json.loads(obj_str)
                       if 'id' in obj and 'name' in obj:
                           nodes.append(obj)
                           if 'children' in obj and obj['children']:
                               children_str = json.dumps(obj['children'])
                               nodes.extend(parse_array(children_str))
                   except: pass
                   i = j
               else: i += 1
           return nodes
       return parse_array(raw_str)
   ```
6. 返回的 `all_nodes` 包含所有模块节点，每个节点含 `id`、`name`、`parent`、`grade`、`order` 字段
7. 构建 parent→children 树后输出树结构，确认数据正确

**关键点：**
- ⚠️ `data` 是**嵌套 JSON**，不是扁平数组，每个节点可能有 `children` 子数组
- ⚠️ 不能用 `json.loads()` 直接解析整个字符串，必须递归展开 `children`
- ⚠️ 必须等页面加载 8 秒，否则 iframe 内容不完整
- **结果用途**：所有 module_id 对应禅道页面的**真实模块名称**，可直接用于 Bug 创建
- **保存位置**：`docs/数字乡村模块树.md`

**验证数据正确性的方法：**
- 一级模块（parent=0）数量 = 42
- 总模块数 = 404
- 检查 grade=2,3,4 的节点是否有正确的 parent 关系

## 附录：模块创建方法（Playwright）

⚠️ 仅在需要创建新模块时使用；数据中台模块树已创建完毕，一般不需要再创建。

**创建路径：** `/tree-browse-{productID}-bug-{parentID}-0-qa.html`
- productID=1（数字乡村v1.1）
- parentID=模块ID（根为 0，数据中台为 506）

**操作步骤：**
1. Playwright 登录 ZenTao Web（`input[name="account"]` / `input[name="password"]`）
2. 访问 `http://192.168.0.28:9980/tree-browse-1-bug-{parentID}-0-qa.html`
3. 在 iframe `name="app-qa"` 中操作：
   - 点击 `.btn-add` 添加模块输入行（初始只有几个，需追加到足够数量）
   - 用 `frame.evaluate()` 赋值：`inputs[i].value = name` + `dispatchEvent(new Event('input',{bubbles:true}))`
   - JS 点击 `button[type="submit"]` 提交表单
4. reload 页面，用正则 `data-id="(\d+)"><a[^>]*title="([^"]*)"` 验证 module_id

**注意事项：**
- 不能用 Playwright 的 `fill()` 直接填充（元素初始不可见）
- API POST `/tree-manageChild-{productID}-bug.html` 在有权限控制的页面返回登录重定向
- 模块创建完成后将 ID 同步到 SOUL.md 和本文件

**Bug 标题格式：** `【数据中台-模块名】具体bug内容`，如 `【数据中台-API管理】API市场搜索无结果提示`

---

#### APP / 业务模块清单（用于确认 Bug 标题【模块名称】）

完整列表在：`docs/测试计划排期表.md` → 1.1 节「业务版块对照」

**测试环境（端口 38868）全部模块：**
- 通用 / 内测邀请码 / 物理资产 / 生态价值资产 / 碳汇 / 活立木
- 文化资产 / 生态农场 / 生态积分 / 个人APP / 数字商城
- 碳足迹 / 数字版权 / 公证智能体 / 知识库 / 短视频电商
- 新版AI小优 / 数据资产综合管理服务平台 / 数字资产运营服务平台
- 数字资产管理平台（红色PC）/ 星河全球数字资产管理平台
- 法律智能体 / 碳足迹综合管理平台 / 东方数碳 / 智能客服
- 价值评估智能体平台 / 黄陂人民医院官网 / 专利项目管理平台 / OA系统

**生产环境（端口 8966/9100/8900）全部模块：**
- 数字资产运营服务平台 / 数字版权（商户/发行方/评估机构）
- 东方数碳 / 法律智能体 / 碳足迹 / 数字资产管理大后台
- 数字资产客服 / 黄陂人民医院 / 专利项目管理平台 / 公证智能体 / 知识库 / 大管理后台

#### ZenTao 用户 ID 速查

| 姓名 | ZenTao account | userID（OpenIM用） |
|------|---------------|-------------------|
| 石大卫 | shidawei | 7809497014 |
| 张文骏 | zhangwenjun | 9175393676 |
| 刘偲 | liusi | 1705938371 |
| 张海棠 | HTang | 27 |
| 方美玲 | - | - |
| 杨旭 | - | - |
| 王紫珊 | - | - |
| 陈斯 | - | - |

**查询 ZenTao 用户列表（API）：**
```bash
curl -s -H "Token: edfa8ff0c698a2286131b4f60ffa8811" \
  "http://192.168.0.28:9980/api.php/v1/users" | python3 -c "
import sys,json
users = json.load(sys.stdin).get('users', [])
for u in users:
    print(f\"{u.get('dept','')} | {u.get('account','')} | {u.get('id','')} | {u.get('realname','')}\")"
```

### 基础配置
- **Base URL**: `http://192.168.0.28:9980/api.php/v1`
- **Token**: `edfa8ff0c698a2286131b4f60ffa8811`（2026-05-12 更新，会过期，API 返回 401 时重新获取）
- **认证方式**: `POST /tokens` with `{"account":"shidawei","password":"shidawei"}`

### 需求(Stories)
```
GET    /products/{productID}/stories          # 获取需求列表
POST   /products/{productID}/stories           # 创建需求
PUT    /stories/{storyID}                     # 更新需求
```

### 测试用例
```
GET    /products/{productID}/testcases        # 获取测试用例（可能有分页问题）
POST   /products/{productID}/testcases         # 创建测试用例
GET    /testcases/{id}                         # 获取单个测试用例
PUT    /testcases/{id}                         # 更新测试用例
```

### 测试用例模块
```
GET    /products/{productID}/testcase-modules  # 获取模块列表
POST   /products/{productID}/testcase-modules  # 创建模块
```

### 迭代/执行
```
GET    /projects/{projectID}/executions        # 获取迭代列表
POST   /projects/{projectID}/executions        # 创建迭代
```

## 使用示例

### 1. 创建需求

```python
# 创建主需求
data = {
    "title": "【内测邀请码管理系统】用户端邀请码申请与管理功能",
    "type": "story",
    "pri": 1,
    "product": 1,
    "status": "draft"
}
story = api_post("products/1/stories", data)
# 返回: {"id": 4, ...}

# 创建子需求
data = {
    "title": "【邀请码登录】邀请码登录功能",
    "type": "story",
    "parent": 4,  # 关联主需求
    "product": 1
}
sub_story = api_post("products/1/stories", data)
# 返回: {"id": 5, ...}
```

### 2. 创建测试用例（关联需求）

```python
data = {
    "title": "【TC-LOGIN-001】正常邀请码登录流程",
    "pri": 1,
    "type": "feature",
    "module": 102,           # module_id（数字），如个人数字空间=102
    "parent": 5,             # 控制父子用例关系
    "story": 5,              # ✅ 关键：关联到需求ID，UI需求页面「测试用例」Tab可见
    "steps": [
        {"desc": "用户打开登录页面", "expect": "显示登录表单"},
        {"desc": "输入有效的邀请码", "expect": "邀请码被接受"},
        {"desc": "点击登录按钮", "expect": "登录成功"}
    ]
}
tc = api_post("products/1/testcases", data)  # ✅ 用 product=1
```

### 3. 批量导入测试用例

```bash
python3 scripts/batch_import_cases.py
```

## 已知问题

1. **测试用例 steps 字段 bug**: 通过某些endpoint创建的用例，steps可能为空
2. **产品ID混淆**: API有时会将用例创建到错误的产品
3. **HTTP 502**: 批量操作时偶发，需要重试
4. **异步事件循环错误 (async event loop)**: 实时对话功能常见的 `Cannot create async connection: no running event loop` 错误，原因和解决方案：
   - **原因**: 后端代码在非异步环境下执行异步连接（Python asyncio），事件循环未启动
   - **解决方案**: 确保异步调用在正确的 async 上下文中执行，或使用 `asyncio.run()` / `await` 包装异步代码

## 文件结构

```
zentao-integration/
├── SKILL.md                      # 本文件
├── docs/
│   └── 测试计划排期表.md          # 完整测试计划排期表（含环境/账号/项目时间/流程规范/AI提效）
├── scripts/
│   ├── create_stories.py         # 创建需求脚本
│   ├── create_testcases.py      # 创建测试用例脚本
│   ├── batch_import_cases.py    # 批量导入测试用例
│   └── zentao_api.py            # API基础类
└── README.md
```

### OpenIM 消息通知集成

ZenTao Bug/测试用例变更时，可通过 OpenIM 自动通知相关人员。

#### OpenIM 配置
- **地址**: `http://192.168.0.27:10002`
- **Admin**: `imAdmin` / `openIM123`
- **Token**: `POST /auth/user_token` with `{"secret":"openIM123","userID":"imAdmin","platformID":1}`

#### 发送消息
```python
# 发送 Bug 通知
data = {
    "sendID": "imAdmin",
    "recvID": "<用户ID>",
    "content": {"content": "Bug内容"},
    "contentType": 101,
    "sessionType": 1
}
```

#### 已知用户
| 姓名 | userID |
|------|--------|
| 石大卫 | 7809497014 ⚠️ 注意：1965695380 是王新 |
| 张文骏 | 9175393676 |

### 典型工作流：Bug通知

```python
# 1. 获取 ZenTao Bug 列表
bugs = api_get("/products/1/bugs?page=1&limit=200")

# 2. 整理统计信息
msg = f"📊 禅道Bug统计报告\n总Bug: {total}\n激活: {active}"

# 3. 通过 OpenIM 发送
openim_send("9175393676", msg)
```

## 安全注意

- Token 包含敏感信息，不要在日志中输出完整Token
- 定期检查Token是否过期

---

## 附录：Story 创建经验总结（2026-05-13 实战记录）

### 背景
从 Axure 思维导图提取 AI 数据中台完整需求理解（8大功能域、214个原型页面），成功创建到禅道：
- 主需求 ID:14（【数据中台】AI数据中台系统完整需求理解）
- 子需求 ID:15~22（8个子模块）

### 关键发现

#### 1. 需求描述字段用 `spec` 而不是 `desc`
ZenTao API 用 `spec` 字段存储 Story 的详细说明，`desc` 字段不生效。
```python
# ✅ 正确
data = {"title": "...", "spec": "详细需求描述..."}
# ❌ 错误（不生效）
data = {"title": "...", "desc": "详细需求描述..."}
```

#### 2. 顶级需求的 parent 值传 `-1`（不是 0）
```python
# ✅ 顶级需求
data = {"parent": -1, ...}  # 在 API 返回中显示 parent:-1
# ❌ 错误尝试
data = {"parent": 0, ...}    # 或留空
```

#### 3. 子需求 parent 传主需求 ID 数字
```python
# ✅ 子需求
data = {"parent": 14, ...}  # 关联到主需求 ID 14
# 返回数据中 parent 显示为 -1（这是 ZenTao 内部行为，UI 父子关系正确）
```

#### 4. 创建后检查 `childStories` 字段验证成功
主需求创建后，其 `childStories` 字段会自动填充子需求 ID 列表（逗号分隔）。
```bash
curl -s -H "Token: $TOKEN" "http://192.168.0.28:9980/api.php/v1/stories/14" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('childStories','?'))"
# 期望输出: "15,16,17,18,19,20,21,22"
```

#### 5. 数据中台 module_id 速查（Story 创建用）
| module_id | 模块名称 | 备注 |
|-----------|---------|------|
| 506 | 数据中台 | 主需求模块 |
| 507 | API管理 | 数据服务 |
| 508 | 数据资产 | 资产地图/目录 |
| 509 | 数据开发 | ETL/任务管理 |
| 510 | 数据治理 | 元数据/主数据/安全/质量 |
| 512 | 数据集成 | 数据源/采集任务 |
| 513 | 数据挖掘 | 指标体系 |
| 514 | 数据建模 | 数仓分层/模型设计 |
| 515 | 用户管理 | 组织/角色/权限 |
| 516 | AI智能体 | AI数据助手 |

#### 6. 批量创建子需求模板
```bash
PARENT_ID=14
for MODULE in 512 514 509 510 513 508 507 516; do
  curl -s -X POST "http://192.168.0.28:9980/api.php/v1/products/1/stories" \
    -H "Token: $TOKEN" -H "Content-Type: application/json" \
    -d "{\"product\":1,\"module\":$MODULE,\"parent\":$PARENT_ID,\"title\":\"标题\",\"type\":\"story\",\"category\":\"feature\",\"pri\":1,\"status\":\"draft\",\"spec\":\"描述\"}" \
    | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'ID:{d[\"id\"]} {d[\"title\"]}')"
done
```

### 验证方法
1. 在禅道 UI 中打开主需求页面，确认"细分需求"标签页中显示8个子需求
2. 通过 API 查询主需求 story/14，确认 `childStories` 字段值
3. 通过 API 查询子需求 story/15~22，确认各自的 `module` 字段正确

---

## 附录：测试用例关联需求实战（2026-05-13）

### 问题背景
通过 API 创建测试用例后，在 ZenTao UI 的需求详情页「测试用例」Tab 看不到关联的用例。

### 根因分析

通过 API 逐步调试发现：

| 尝试方式 | API 返回 | UI 是否可见 |
|---------|---------|-----------|
| `parent=ID` only | `story=0` | ❌ 不可见 |
| `story=ID` only | 可能无效 | ❌ 不可见 |
| `parent=ID` + `story=ID` | `story=ID` | ✅ 可见 |

**结论**: `parent` 控制父子用例关系，`story` 控制显示在需求的「测试用例」Tab。两者必须同时传！

### 调试过程（经验）

```python
# 验证用例 #360 - 传 parent=14 story=14 → 成功
data = {
    "title": "验证测试",
    "parent": 14,
    "story": 14,      # ✅ 关键！
    "module": 512,
    "pri": 2,
    "type": "feature",
    "steps": [{"desc": "步骤", "expect": "预期"}]
}
# API: POST /products/1/testcases
# 返回: {"id": 360, "product": 1, "story": 14, ...} ✅
```

### 完整创建模板

```python
def create_testcase(token, title, module_id, story_id, pri, steps):
    """创建测试用例并关联到需求"""
    data = {
        "title": title,          # 【模块名】功能点
        "module": module_id,       # module_id（数字），不是模块名称
        "parent": story_id,        # 关联到需求ID
        "story": story_id,        # ✅ 关键：UI需求页面「测试用例」Tab显示
        "pri": pri,               # 1=P0 / 2=P1 / 3=P2
        "type": "feature",
        "steps": [{"desc": s[0], "expect": s[1]} for s in steps]
    }
    payload = json.dumps(data, ensure_ascii=False)
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"{ZENDAO}/products/1/testcases",  # ✅ 用 product=1
        "-H", f"Token: {token}",
        "-H", "Content-Type: application/json",
        "-H", "Zentao-Version: 22.4",
        "-d", payload
    ], capture_output=True, text=True, timeout=15)
    resp = json.loads(r.stdout)
    if "error" in resp:
        return None, resp.get("error")
    return resp.get("id"), None
```

### 产品选择

- ✅ **用 product=1**（数字乡村v1.1），关联需求正常
- ⚠️ product=2 的 testcases 查询 API 有问题（返回 `{"error":"error"}` 400）

### module_id 与 story 关系

| 功能域 | story_id | module_id |
|--------|---------|-----------|
| 数据集成 | #15 | 512 |
| 数据建模 | #16 | 514 |
| 数据开发 | #17 | 509 |
| 数据治理 | #18 | 510 |
| 数据挖掘分析 | #19 | 513 |
| 数据资产 | #20 | 508 |
| 数据服务 | #21 | 507 |
| AI智能体 | #22 | 516 |

### 验证步骤

1. **API 验证**（创建后立即检查）：
```bash
curl -s -H "Token: $TOKEN" \
  "http://192.168.0.28:9980/api.php/v1/testcases/{返回的ID}" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'story={d[\"story\"]} product={d[\"product\"]}')"
# 期望输出: story={需求ID} product=1
```

2. **UI 验证**：
   - 打开 `http://192.168.0.28:9980/story-view-{需求ID}.html`
   - 切换到「测试用例」Tab
   - 应能看到关联的全部测试用例

### 批量创建脚本位置

已验证可用的脚本：`/tmp/tc_create*.py`（分4个文件，共156个用例，全部成功关联）

**脚本结构**：
```
/tc_create.py   → 数据集成 #361-375
/tc_create2.py  → 数据建模 #376-396, 数据开发 #397-427
/tc_create3.py → 数据治理 #428-458, 数据挖掘分析 #459-470
/tc_create4.py → 数据资产 #471-482, 数据服务 #483-511, AI智能体 #512-516
```
