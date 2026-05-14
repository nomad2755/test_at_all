# MEMORY.md - 长期记忆

## 身份
- **名称：** 测试小助手 🧪
- **角色：** 测试工程师的专业助手
- **风格：** 专业、细致、乐于助人

## 用户信息
- **称呼：** 工程师
- **职业：** 测试工程师
- **时区：** Asia/Shanghai (GMT+8)
- **偏好：** 系统化测试方法、数据驱动策略、可维护的测试用例

## 技术笔记

### XMind 生成技能
- **技能位置**: `/root/.openclaw/workspace/test_cases/skills/create-xmind/`
- **核心文件**: `scripts/xmind_to_zentao.py`
- **关键结论**: XMind 文件必须包含 5 个 XML 文件 (content.xml, styles.xml, comments.xml, meta.xml, META-INF/manifest.xml)

### XMind→ZenTao 测试用例导入经验 (重要)
**问题描述**: 通过 API 提交的测试用例，步骤和预期在 ZenTao UI 中显示为空。

**根本原因**: ZenTo API 对 `steps` 字段格式有严格要求：
- ❌ 错误格式: `[["步骤", "预期"], ...]` (嵌套数组)
- ✅ 正确格式: `[{"desc": "步骤", "expect": "预期"}, ...]` (对象数组)

**API 行为**:
- POST 创建时 API 返回 201 成功，但查询返回 steps=[]（API 内部 bug）
- UI 显示为空是因为 steps 被以错误格式存储

**修复方法**:
1. `format_steps_for_zentao()` 返回类型必须是 `List[Dict]`，不是 `List[List[str]]`
2. 每个步骤格式: `{"desc": "描述", "expect": "预期结果"}`
3. `merge_steps_and_expected()` 也需相应调整

**XMind 结构注意**:
- "测试步骤" 主题的标题可能包含所有步骤的合并文本（如 "1. xxx 2. xxx"）
- 子主题才是真正的独立步骤
- 如果 desc 为空但 notes 有内容，用 notes 作为 desc 的备选

### OpenIM 消息推送
- **服务地址**: `http://192.168.0.27:10002`
- **Admin账号**: `imAdmin` / `openIM123`
- **Token 获取**: POST `/auth/user_token` with `{"secret":"openIM123","userID":"imAdmin","platformID":1}` + `operationID` header (uuid)
- **发送消息**: POST `/msg/send_msg` with token + `operationID` header (uuid)
- **contentType**: 101 (文本消息)
- **content 格式**: `{"content": "消息文本"}` (注意是 `"Content"` 大写)
- **sessionType**: 1 (单聊) / 2 (群聊)
- **已知用户**:
  - 石大卫: `7809497014` ⚠️ 注意：不要用 1965695380（那是王新）
  - 张文骏: `9175393676`
  - 刘偲: `1705938371`
  - 张海棠: `HTang` (id=27)，通过 `GET /users` API 发现

### Jenkins 构建状态监控（2026-05-09 新增）
- **服务器**: `http://192.168.0.26:10240`（内网）
- **账号**: `shidw` / `178178Shi`
- **OpenClaw 服务器**: `192.168.0.68`（与 Jenkins 同 subnet，可直接互通）
- **公网 IP**: `120.202.35.151`（云防火墙 blocking 大多数端口）
- **Jenkins Webhook 中转**: `jenkins_webhook_server.py` Flask 服务，监听端口 8099
- **监控脚本**: `jenkins_alert.py` 每 10 分钟轮询，失败/不稳定时通过 OpenIM 通知
- **已知不稳定项目**（均 SSH 发布失败）:
  - dam_cloud25 #429: Exec timed out 120s
  - dam_screenv3 #85: Exit Status [1]
  - hp-hospital-web51 #3: Exit Status [1]
  - 测试 #6: Exit Status [8]
  - 测试环境镜像 #1: Exit Status [17]
- **定时任务**: cron ID `03134f26-e3f3-4cf8-aee8-6090731059af`，每 10 分钟执行一次
- **去重机制**: 同小时内相同项目不重复通知

### ZenTao 集成
- **服务器**: http://192.168.0.28:9980
- **账号**: shidawei / shidawei
- **Token**: fe0023e6b32f6c8af7eb8495d0366cbf (2026-05-14 更新，会过期)
- **Token 获取方式**: POST /api.php/v1/tokens with {"account":"shidawei","password":"shidawei"}
- **⚠️ 注意**: Token 会过期，如果 API 返回 401，需重新通过 Token API 获取新 token
- **产品ID**: 1 (数字乡村v1.1)
- **迭代ID**: 24 (邀请码专项)
- **API 端点**: /api.php/v1
- **module_id**：Bug 创建时必须填写模块 ID（数字），不是模块名称。通过已有 Bug 反查或询问用户确认。已知映射：个人数字空间=102，iOS=295，物理资产=121，资产管理/数字文化=430，数据资产运营服务平台=161，多轮对话=162，碳足迹核算模型=198。
- **module**：`module_id` 字段在 Bug 创建时通过 `module` 字段传递

### 数据中台前端进度统计表（2026-05-12 新增）
**来源文件：** `/root/Downloads/数据中台前端进度统计表.xlsx`
**用途：** 创建数据中台 Bug 时参考指派人

**责任人速查：**
| 责任人 | 负责模块 |
|--------|---------|
| 张海棠 | 首页、公共（消息/系统设置/申请试用/个人中心）、数据资产 |
| 朱艳 | API管理、数据质量 |
| 金毅 | 数据治理-元数据/主数据、数据安全-数据隐私/数据权限 |
| 曹勇 | 数据安全-敏感数据 |
| 张耀文 | 数据开发、用户管理 |
| 徐记平 | 数据集成、数据挖掘 |
| 王新 | 数据建模 |
| 柴胜杰 | AI智能体 |

**module_id：** 待从已有数据中台 Bug 反查（当前未知）

---

### ZenTao Bug 截图永久 URL 上传（2026-05-12 实测成功）

**上传脚本**：`python3 /root/.openclaw/workspace/scripts/upload_to_whhnhy.py <图片路径>`

**流程**：
1. 截图文件保存在 `/root/.openclaw/media/inbound/` 下，按时间戳 UUID 命名
2. 用 `ls -lt` 查看最新文件，取第一个
3. 执行 upload_to_whhnhy.py，自动获取登录态 + 上传 + 返回永久 URL
4. 永久 URL 格式：`https://www.whhnhy.com:8900/szxc/<hash>.png`

**已验证可用**，2026-05-12 上传 3216604a...png 成功。


**推荐使用 `auto_bug_creator.py` 自动创建 Bug：**
```bash
python3 scripts/auto_bug_creator.py <Bug描述> [severity] [pri]
python3 scripts/auto_bug_creator.py "登录失败" --dry-run  # 试运行
```
- 自动从 `测试计划排期表.xlsx` 读取模块的 URL、账号、负责人
- 关键词同义词匹配（数字家园→个人数字空间→module_id=102）
- 自动填充 `module_id`（对应 ZenTao「所属模块」）
- 表格数据不完整的模块（个人APP、个人数字空间）有硬编码补充

**已知 module_id 映射（从已有 Bug 反查）：**
| 模块名 | module_id |
|--------|---------|
| 个人数字空间 | 102 |
| iOS相关 | 295 |
| 物理资产 | 121 |
| 资产管理/数字文化 | 430 |
| 数据资产运营服务平台 | 161 |
| 多轮对话 | 162 |
| 碳足迹核算模型 | 198 |

**Bug 标题格式：** `【模块名称】具体bug内容`
- 示例：`【电商】无法购买商品`、`【登录】验证码无法刷新`
- 注意：不要在标题中加入优先级标识，优先级通过 severity/pri 字段控制

**steps 字段必须使用 HTML 格式（`<p>` 标签）：**
```html
<p>【环境】</p><p>- 测试地址：</p><p>- 浏览器：</p><p>【账号密码】</p><p>- 用户名：</p><p>- 密码：</p><p>【前置条件】</p><p>1. </p><p>【操作步骤】</p><p>1. </p><p>【期望结果】</p><p>1. </p><p>【实际结果】</p><p>1. </p><p>【附截图】</p><p>暂无</p>
```

**openedBuild 字段传 `"trunk"`**
**严重程度对照：** severity=1（致命）/2（严重）/3（一般）/4（轻微）/5（建议）
**优先级对照：** pri=1（紧急）/2（高）/3（中）/4（低）
**Bug 类型：** codeerror / interface / function / performance / others
**module 字段：** 传 module_id（数字），不是模块名称！

**技能已保存：** `/root/.openclaw/workspace/skills/zentao-bug-report/`

**Bug 截图永久 URL（2026-05-12 新增，严格优先）**：
- `upload_to_whhnhy.py` 脚本上传截图到数字资产管理平台，获得**永久 URL**
- 上传 API: `POST https://www.whhnhy.com:8966/admin-api/infra/file/upload`
- 认证: `Authorization: Bearer <token>` + cookies（Playwright 自动获取登录态）
- 永久 URL 格式: `https://www.whhnhy.com:8900/szxc/<hash>.png`
- **严禁使用 Serveo URL**（非静态，每次变化）

**Bug 截图公网访问（备选方案，仅平台不可用时使用）**：
- 用户截图在 `/root/.openclaw/media/inbound/` 下，**每次都要用最新文件**
- 通过端口 8099 的 Flask 服务对外提供访问
- 如防火墙阻断 8099，用 `ssh -R 80:localhost:8099 serveo.net` 临时穿透
- ⚠️ **Serveo URL 每次都变化**，旧的立即失效

### 测试计划排期表（2026-05-11 新增，2026-05-12 强化）

**来源文件：** `/root/.openclaw/workspace/skills/zentao-integration/docs/测试计划排期表.md`


**每次创建 Bug 和执行任务前必须读取此文件，获取：**
1. 当前项目的测试环境、URL、账号密码
2. 提测时间线、项目状态、负责人
3. 对应业务的模块名称（用于 Bug 标题【模块名称】）
4. 测试阶段规范、发包时间、Bug 优先级定义

**已在以下位置联动同步：**
- ✅ SOUL.md → 新增"测试计划排期表（每次必读）"章节
- ✅ zentao-bug-report Skill → 创建 Bug 前必读步骤
- ✅ zentao-integration Skill → 新增"指派人查询 & APP模块对照"章节（2026-05-12）

**指派人和模块速查已内置到 zentao-integration Skill：**
- 按模块/项目查找测试负责人 → 确定 Bug 指派人
- APP/业务模块完整清单 → 确认 Bug 标题【模块名称】
- ZenTao 用户 account + OpenIM userID 对照表

包含内容：
- 测试环境总览（数字乡村 / 测试环境/生产环境 / 各平台URL+账号）
- 95个测试项目时间安排（2025年10月至今）
- 测试流程标准规范（6大阶段+发包/Bug规范+优先级定义）
- AI提效落地版块（技术栈/模块进展/AI使用情况统计）
- 测试项目跟踪表（各平台角色/账号/负责人）
- 测试组问题跟踪（7大类问题与解决方案）

### ZenTao API 使用

#### 基础信息
- **服务器**: http://192.168.0.28:9980
- **API 端点**: /api.php/v1
- **账号**: shidawei / shidawei
- **Token**: fe0023e6b32f6c8af7eb8495d0366cbf (2026-05-14 更新，会过期)

#### 产品与项目
- **产品ID 1**: 数字乡村v1.1
- **产品ID 2**: 个人数字空间
- **项目ID 1**: 数字乡村
- **项目ID 2**: 个人数字空间
- **重要**: 产品和项目是不同概念，产品属于项目

#### 测试用例 API (重要发现)

**创建测试用例到迭代（推荐方式）：**
```bash
POST /api.php/v1/executions/{迭代ID}/testcases
```
- 请求体：
```json
{
  "title": "用例标题",
  "pri": 1-3,
  "type": "feature|performance|config|security|others",
  "steps": "[{\"desc\": \"步骤\", \"expect\": \"预期\"}]"
}
```
- ✅ 可以创建成功
- ⚠️ 但查询 execuions/{id}/testcases 返回空列表（API bug）
- ⚠️ UI 中看不到创建的用例

**创建测试用例到产品（存在问题）：**
```bash
POST /api.php/v1/products/{产品ID}/testcases
```
- ⚠️ 无论指定哪个产品ID，都会创建到产品 2（个人数字空间）
- ⚠️ 这是一个 API bug

**更新测试用例：**
```bash
PUT /api.php/v1/testcases/{id}
```
- 可以更新用例的各种字段

**创建迭代：**
```bash
POST /api.php/v1/projects/{项目ID}/executions
```
- 请求体：`{"name": "迭代名", "begin": "2026-04-27", "end": "2026-05-31", "type": "sprint"}`

#### ZenTao Bug 状态统计
- 总 Bug: 8,128
- 激活: 221
- 已解决: 8,128
- 解决率: 97.4%

### 邀请码专项迭代 (#24)
- 总 Bug: 12
- 激活: 7
- 已解决: 1
- 已关闭: 4

### 测试用例生成
- **内测邀请页面测试用例**: 15 个用例 (P0/P1/P2)
- **测试流程规范文档**: `docs/测试工作流程标准规范_AI辅助版.md`

### ZenTao API 已知问题（测试用例）
1. **API 不存储 steps 字段** - POST 创建成功但 GET 返回 steps=[]（API bug）
2. 通过 API 创建测试用例到迭代后，UI 中不显示（数据丢失）
3. 通过 products/{id}/testcases 创建的用例会错误归属到产品 2
4. 更新用例 steps 不生效
5. 关联用例到迭代后 execution 始终为 0
6. **steps 字段格式** `[{"desc": "...", "expect": "..."}]`（对象数组），不是嵌套数组

### ZenTao Bug 状态统计
- 总 Bug: 8,128
- 激活: 221
- 已解决: 8,128
- 解决率: 97.4%

### 邀请码专项迭代 (#24)
- 总 Bug: 12
- 激活: 7
- 已解决: 1
- 已关闭: 4

### 测试用例生成
- **内测邀请页面测试用例**: 15 个用例 (P0/P1/P2)
- **测试流程规范文档**: `docs/测试工作流程标准规范_AI辅助版.md`

### 2026-04-29 工作记录

#### Jenkins 部署（成功）
- **部署方式**: Docker (`jenkins/jenkins:lts`)
- **公网访问**: https://a4bf8dd5965ce7b5-120-202-35-151.serveousercontent.com
- **本地端口**: 8080 (Jenkins) / 50000 (Agent)
- **初始管理员密码**: `225a9d7b69e44369ba1f5161a648731c`
- **数据卷**: `/opt/jenkins_home`
- **已安装插件**: 95 个
- **特点**: 已安装中文本地化插件（localization-zh-cn）和暗色主题（dark-theme）

#### whhnhy.com 后台系统
- **地址**: https://whhnhy.com:8910
- **子系统**: /knowledge/login (知识库登录)
- **状态**: 仅内网访问，Linux 服务器无法直接访问
- **后续**: 需通过 ngrok 或内网穿透方式解决

#### JMeter 压测
- **测试记录**: 50 请求，0 失败，P95=26ms，吞吐量 32.3 req/s
- **结论**: 响应性能良好

---

## 已安装 Skills 清单

### 测试相关技能 (工作区)
| 技能名 | 描述 |
|--------|------|
| zentao-integration | 禅道 API 集成 |
| create-xmind | XMind 生成 |
| extract-prototype-testcase | 原型提取测试用例 |
| airtest-automation | AirTest 自动化测试 |
| webapp-testing | Web 应用测试 |
| openim-notification | OpenIM 消息推送 |

### 工具类技能 (工作区)
| 技能名 | 描述 |
|--------|------|
| create-zen-dao | 创建禅道文档 |
| flybirds | 飞鸟测试框架 |
| video-translation | 视频翻译 |
| tts | TTS 语音合成 |
| characteristic-voice | 声音特征 |
| daily-news-caster | 每日新闻 |
| thinking-knowledge-system | 知识系统 |

### 系统内置技能 (54个)
| 分类 | 技能 |
|------|------|
| AI/编码 | coding-agent, gemini |
| 天气/时间 | weather |
| 提醒/日历 | apple-reminders, things-mac |
| 笔记/文档 | apple-notes, bear-notes, notion, obsidian |
| 消息/社交 | imsg, slack, discord, wacli |
| 音乐/媒体 | spotify-player, songsee, openai-whisper |
| 智能家居 | openhue, eightctl |
| 开发工具 | github, gh-issues, trello |
| 其他 | clawhub, skill-creator, tmux, healthcheck, summarize |

---


### 📚 2026-05-14 每日错误学习
**扫描范围**: 今天和昨天的会话，共发现 5 条值得关注的问题

**1. 【Assistant 响应失败】（共 717 次）**
   示例: [assistant turn failed before producing content]
   上下文: [cron:4908cdcd-c171-4b78-9264-312d3aba4249 致命P1 Bug紧急预警(每30分钟)] 执行致命P1 Bug紧急预警脚本（--brief精简模式）：cd /root/.openclaw/workspace && python3 scripts/urgent_bug_alerter.py --brief
Current time: Wednesday, May

**2. 【认证失效】（共 3 次）**
   示例: Unauthorized
   上下文: [Wed 2026-05-13 09:11 GMT+8] 查看目前禅道已经有的模块，保存到skills文件和soul文件中方便下次调用

**3. 【工具执行错误】（共 7 次）**
   示例: not found
   上下文: [Wed 2026-05-13 09:11 GMT+8] 查看目前禅道已经有的模块，保存到skills文件和soul文件中方便下次调用

**4. 【文件路径不存在】（共 3 次）**
   示例: ENOENT: no such file or directory, access '/root/.openclaw/workspace/memory/2026-05-13.md'
   触发工具: read
   上下文: Continue the OpenClaw runtime event.

**5. 【路径安全限制】（共 2 次）**
   示例: Local media path is not under an allowed directory: /tmp/mindmap_final.png
   触发工具: image
   上下文: [Wed 2026-05-13 10:48 GMT+8] 你提取到思维导图的图片了吗


## 待跟进
- [ ] 确认 MiniMax API Key 是否已配置
- [ ] 了解工程师当前测试项目
- [ ] 确认是否有待处理的测试任务

---
*最后更新: 2026-04-30*

### ZenTao 集成
- **服务器**: http://192.168.0.28:9980
- **账号**: shidawei / shidawei
- **Token**: fe0023e6b32f6c8af7eb8495d0366cbf (2026-05-14 更新)
- **产品ID**: 1 (数字乡村v1.1)
- **迭代ID**: 24 (邀请码专项)
- **API 端点**: /api.php/v1
- **已提交 Bug**: ID 9728, 9729, 9844, 9846-9852

### ZenTao API 使用

#### 基础信息
- **服务器**: http://192.168.0.28:9980
- **API 端点**: /api.php/v1
- **账号**: shidawei / shidawei
- **Token**: fe0023e6b32f6c8af7eb8495d0366cbf (2026-05-14 更新)

#### 产品与项目
- **产品ID 1**: 数字乡村v1.1
- **产品ID 2**: 个人数字空间
- **项目ID 1**: 数字乡村
- **项目ID 2**: 个人数字空间
- **重要**: 产品和项目是不同概念，产品属于项目

#### 数据中台模块树（2026-05-12 创建完成，共59个模块，ID 506~564）

| module_id | 模块名称 | 父级 | 责任人 |
|-----------|---------|------|--------|
| 506 | 数据中台 | - | - |
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
| 517-522 | API管理子模块（数据分析/API管理/API调用/资产地图/资产目录/查看详情） | 507/508 | - |
| 523-525 | 数据开发子模块（数据分析/任务管理/任务流设计器） | 509 | - |
| 526-528 | 数据治理子模块（元数据管理/主数据管理/数据质量） | 510 | 金毅/朱艳 |
| 529-531 | 数据安全子模块（敏感数据/数据隐私/数据权限） | 511 | 曹勇/金毅 |
| 532-535 | 数据集成子模块（数据分析/数据源/任务管理/任务日志） | 512 | - |
| 536-564 | 三级子模块（质量监控/敏感数据子模块/数据隐私子模块/数据权限子模块/元数据子模块/主数据子模块/数仓分层/数据指标等） | 528-531 | - |

#### 测试用例 API (重要发现)

**创建测试用例到迭代（推荐方式）：**
```bash
POST /api.php/v1/executions/{迭代ID}/testcases
```
- 请求体：
```json
{
  "title": "用例标题",
  "pri": 1-3,
  "type": "feature|performance|config|security|others",
  "steps": "[{\"desc\": \"步骤\", \"expect\": \"预期\"}]"
}
```
- ✅ 可以创建成功
- ⚠️ 但查询 execuions/{id}/testcases 返回空列表（API bug）
- ⚠️ UI 中看不到创建的用例

**创建测试用例到产品（存在问题）：**
```bash
POST /api.php/v1/products/{产品ID}/testcases
```
- ⚠️ 无论指定哪个产品ID，都会创建到产品 2（个人数字空间）
- ⚠️ 这是一个 API bug

**更新测试用例：**
```bash
PUT /api.php/v1/testcases/{id}
```
- 可以更新用例的各种字段

**创建迭代：**
```bash
POST /api.php/v1/projects/{项目ID}/executions
```
- 请求体：`{"name": "迭代名", "begin": "2026-04-27", "end": "2026-05-31", "type": "sprint"}`

#### ZenTao Bug 状态统计
- 总 Bug: 8,128
- 激活: 221
- 已解决: 8,128
- 解决率: 97.4%

### 邀请码专项迭代 (#24)
- 总 Bug: 12
- 激活: 7
- 已解决: 1
- 已关闭: 4

### 测试用例生成
- **内测邀请页面测试用例**: 15 个用例 (P0/P1/P2)
- **测试流程规范文档**: `docs/测试工作流程标准规范_AI辅助版.md`

### ZenTao API 关键发现（重要）
1. **测试用例关联需求**：使用 `parent` 字段，不是 `story` 字段
2. **steps 格式**：必须传 JSON 数组 `[{desc, expect}]`，不是字符串
3. 创建测试用例时使用产品2可以避免显示问题
4. 批量导入时偶发 HTTP 502，需要重试机制

### ZenTao API 已知问题
1. 通过 API 创建测试用例到迭代后，UI 中不显示
2. 通过 products/{id}/testcases 创建的用例会错误归属到产品 2
3. 测试任务的创建需要特定格式，project 需要是对象 `{"id": 1}`

### ZenTao Bug 状态统计
- 总 Bug: 8,128
- 激活: 221
- 已解决: 8,128
- 解决率: 97.4%

### 邀请码专项迭代 (#24)
- 总 Bug: 12
- 激活: 7
- 已解决: 1
- 已关闭: 4

### 测试用例生成
- **内测邀请页面测试用例**: 15 个用例 (P0/P1/P2)
- **测试流程规范文档**: `docs/测试工作流程标准规范_AI辅助版.md`

## 待跟进
- [ ] 确认 MiniMax API Key 是否已配置
- [ ] 了解工程师当前测试项目
- [ ] 确认是否有待处理的测试任务

---
*最后更新: 2026-05-14**

## 🔐 系统账号与访问凭证（重要）

| 系统 | 地址 | 账号 | 密码 | 备注 |
|------|------|------|------|------|
| ZenTao | http://192.168.0.28:9980 | shidawei | shidawei | API Token: cf2da27b8b734b419352d844bc451a14 |
| Jenkins | http://192.168.0.26:10240 | shidw | 178178Shi | 本服务器: 192.168.0.68 |
| OpenIM | http://192.168.0.27:10002 | imAdmin | openIM123 | 消息推送服务 |
| Axure 原型 | https://www.whhnhy.com:37777 | - | - | 账号同 ZenTao |

## 🌐 网页访问方法

内网网页访问用 Playwright 自动登录后操作。常用登录字段：
- Jenkins: `#j_username` / `#j_password`
- ZenTao: `input[name="account"]` / `input[name="password"]`

## 2026-05-09 经验更新

### 定时任务稳定性优化
- **P1预警超时问题**：timeout=120s 时偶发超时（AI回复慢），最终稳定在 timeout=300s
- **根因**：Python脚本只执行~1秒，但 isolated session 初始化+AI回复需要30~100秒
- **优化**：增加 `--brief` 模式给脚本，减少 stdout 输出，降低 AI input tokens（~19000→~1200）
- **配置**：P1预警任务 timeout 设为 300s，其他任务 120s

### 脚本新增 --brief 模式
`urgent_bug_alerter.py --brief`：精简日志、stdout输出JSON、快速退出

### ZenTao Story 创建经验（2026-05-13 实战成功）

**创建内容：** AI数据中台完整需求理解（主需求#14 + 8个子需求#15~#22）
**创建结果：** ✅ 全部成功，父子关系正确

**关键发现（重要）：**
1. **Story 描述字段**：用 `spec` 而不是 `desc`（desc 不生效）
2. **顶级需求 parent**：传 `-1`（不是 0，也不是空）
3. **子需求 parent**：传主需求 ID 数字（如 14），返回数据中显示 -1 是正常行为，UI 关系正确
4. **验证方法**：查询主需求 story/14，检查 `childStories` 字段（值为 "15,16,17,18,19,20,21,22"）
5. **module_id**：数据中台主需求用 506，子需求按模块分配（512=数据集成，514=数据建模，509=数据开发等）

**经验已同步到：**
- `skills/zentao-integration/SKILL.md` → 附录「Story 创建经验总结（2026-05-13 实战记录）」
- `MEMORY.md` → 本条记录
