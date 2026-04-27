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

## 待跟进
- [ ] 确认 MiniMax API Key 是否已配置
- [ ] 了解工程师当前测试项目
- [ ] 确认是否有待处理的测试任务

---
*最后更新: 2026-04-27*

### ZenTao 集成
- **服务器**: http://192.168.0.28:9980
- **账号**: shidawei / shidawei
- **Token**: 335bfce2adddecff7b3097534e93cf3e
- **产品ID**: 1 (数字乡村v1.1)
- **迭代ID**: 24 (邀请码专项)
- **API 端点**: /api.php/v1
- **已提交 Bug**: ID 9728, 9729

### ZenTao API 使用

#### 基础信息
- **服务器**: http://192.168.0.28:9980
- **API 端点**: /api.php/v1
- **账号**: shidawei / shidawei
- **Token**: 335bfce2adddecff7b3097534e93cf3e

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
*最后更新: 2026-04-24*
