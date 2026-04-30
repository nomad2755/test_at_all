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
- **Token 获取**: POST `/auth/user_token` with `{"secret":"openIM123","userID":"imAdmin","platformID":1}`
- **发送消息**: POST `/msg/send_msg` with token
- **contentType**: 101 (文本消息)
- **content 格式**: `{"content": "消息文本"}` (注意是 `"Content"` 大写)
- **sessionType**: 1 (单聊) / 2 (群聊)
- **已知用户**:
  - 石大卫: `1965695380`
  - 张文骏: `9175393676`

### ZenTao 集成
- **服务器**: http://192.168.0.28:9980
- **账号**: shidawei / shidawei
- **Token**: cf2da27b8b734b419352d844bc451a14 (2026-04-27 更新，旧 token 已失效)
- **Token 获取方式**: POST /api.php/v1/tokens with {"account":"shidawei","password":"shidawei"}
- **产品ID**: 1 (数字乡村v1.1)
- **迭代ID**: 24 (邀请码专项)
- **API 端点**: /api.php/v1
- **⚠️ 注意**: Token 会过期，如果 API 返回 401，需重新通过 Token API 获取新 token

### ZenTao API 使用

#### 基础信息
- **服务器**: http://192.168.0.28:9980
- **API 端点**: /api.php/v1
- **账号**: shidawei / shidawei
- **Token**: cf2da27b8b734b419352d844bc451a14

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

## 待跟进
- [ ] 确认 MiniMax API Key 是否已配置
- [ ] 了解工程师当前测试项目
- [ ] 确认是否有待处理的测试任务

---
*最后更新: 2026-04-30*

### ZenTao 集成
- **服务器**: http://192.168.0.28:9980
- **账号**: shidawei / shidawei
- **Token**: d22106bc19b08ebbcecebcbd79dc4338
- **产品ID**: 1 (数字乡村v1.1)
- **迭代ID**: 24 (邀请码专项)
- **API 端点**: /api.php/v1
- **已提交 Bug**: ID 9728, 9729

### ZenTao API 使用

#### 基础信息
- **服务器**: http://192.168.0.28:9980
- **API 端点**: /api.php/v1
- **账号**: shidawei / shidawei
- **Token**: d22106bc19b08ebbcecebcbd79dc4338

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
*最后更新: 2026-04-29*
