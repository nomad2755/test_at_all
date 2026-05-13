# OpenClaw Workspace - Skills & Memory Guide

> 本工作区为测试工程师 AI 助手（测试小助手 🧪）的完整技能与记忆仓库。通过 GitHub 同步，其他智能体 clone 后可直接使用。

**GitHub**: https://github.com/nomad2755/test_at_all  
**分支**: master

---

## 🗂️ 文件结构

```
workspace/
├── SOUL.md              # AI 身份与核心经验沉淀（必读）
├── MEMORY.md            # 长期记忆（关键系统配置/经验）
├── AGENTS.md            # 工作区规范与工作流
├── IDENTITY.md          # AI 身份定义
├── USER.md              # 用户信息
├── TOOLS.md             # 本地工具配置
├── HEARTBEAT.md         # 心跳任务配置（通常为空）
├── memory/              # 每日工作日志（不推送到 Git）
│   └── YYYY-MM-DD.md
├── skills/              # 技能（Skills）
├── scripts/             # 自动化脚本
└── docs/                # 文档和模块树
```

---

## 🧠 记忆文件说明

### SOUL.md（必读）
AI 的核心身份文档，包含：
- **定位**：测试工程师的专业助手
- **核心信条**：真正有帮助、先想办法再问、有主见
- **经验沉淀**：测试计划排期表、Bug 模板、模块ID映射、API经验
- **定时任务清单**：Jenkins监控、Bug推送等
- **系统账号密码**：ZenTao、Jenkins、OpenIM 等

### MEMORY.md
长期记忆，包含：
- OpenIM 消息推送配置和已知用户
- ZenTao API 使用经验（token、产品ID、用例关联）
- Jenkins 监控配置
- XMind 生成经验
- Bug 截图上传流程
- 踩过的坑（Token过期、f-string格式化、Serveo URL变化等）

### AGENTS.md
工作区行为规范，包括：
- 启动时加载顺序（SOUL.md → USER.md → memory/）
- 心跳任务规范
- 群聊发言规则
- Red Lines（绝对不能做的事）

### memory/YYYY-MM-DD.md
每日工作日志，记录当天完成的任务、发现的问题、重要的调试结果。

---

## 🛠️ Skills 技能清单

### 核心测试技能

| Skill | 文件位置 | 描述 |
|-------|---------|------|
| **zentao-integration** | `skills/zentao-integration/` | ZenTao API 集成，创建需求/Bug/测试用例。**每次任务前必读 SKILL.md** |
| **zentao-bug-report** | `skills/zentao-bug-report/` | ZenTao Bug 创建标准模板，包含 steps 格式、截图处理、module_id 速查 |
| **create-xmind** | `skills/create-xmind/` | 从 XMind 文件生成测试用例并导入 ZenTao |
| **extract-prototype-testcase** | `skills/extract-prototype-testcase/` | 从 Axure 原型页面提取测试用例 |
| **webapp-testing** | `skills/webapp-testing/` | Web 应用测试 |
| **airtest-automation** | `skills/airtest-automation/` | AirTest 自动化测试 |

### 辅助技能

| Skill | 描述 |
|-------|------|
| `axure-html-extractor` | Axure HTML 原型需求提取（curl 下载法） |
| `axure-prototype-generator` | Axure 原型生成器 |
| `create-zen-dao` | ZenTao DAO Client |
| `daily-news-caster` | 每日新闻播报 |
| `tts` | TTS 语音合成 |
| `characteristic-voice` | 声音特征分析 |
| `video-translation` | 视频翻译 |
| `thinking-knowledge-system` | 知识系统 |

---

## 📜 Scripts 自动化脚本

| 脚本 | 功能 |
|------|------|
| `auto_bug_creator.py` | 从 Excel 自动创建 Bug（自动匹配 module_id、指派人） |
| `auto_module_lookup.py` | 禅道 module_id 查询工具 |
| `bug_screenshot_manager.py` | Bug 截图管理 |
| `upload_to_whhnhy.py` | 上传截图到数字资产管理平台获取永久 URL |
| `daily_bug_report.py` | 按指派人分组推送每日 Bug 统计（10:00/17:00） |
| `daily_creator_bug_report.py` | 按创建人分组推送每日 Bug 统计（09:30） |
| `urgent_bug_alerter.py` | P1 紧急 Bug 预警（每30分钟检查，severity=1 & pri=1） |
| `jenkins_alert.py` | Jenkins 构建状态监控 + OpenIM 通知 |
| `jenkins_monitor.py` | Jenkins 状态查询 |
| `jenkins_webhook_server.py` | Jenkins Webhook 中转服务（端口 8099） |
| `create_dataplatform_tc.py` | 数据中台测试用例创建 |

> ⚠️ **执行禅道相关任务前**，必须先读取 `skills/zentao-integration/docs/测试计划排期表.md` 获取当前项目环境、账号、模块信息。

---

## 🔑 关键系统配置

### ZenTao 禅道
- **地址**: http://192.168.0.28:9980
- **账号**: shidawei / shidawei
- **Token**: `edfa8ff0c698a2286131b4f60ffa8811`（会过期，API 返回 401 时重新获取）
- **产品ID 1**: 数字乡村v1.1（需求、Bug、测试用例）
- **产品ID 2**: 个人数字空间

### OpenIM 消息推送
- **地址**: http://192.168.0.27:10002
- **Admin**: imAdmin / openIM123
- **已知用户**: 石大卫(7809497014)、刘偲(1705938371)、张文骏(9175393676)

### Jenkins
- **地址**: http://192.168.0.26:10240
- **账号**: shidw / 178178Shi

### 数字资产管理平台
- **上传API**: https://www.whhnhy.com:8966/admin-api/infra/file/upload
- **永久URL**: https://www.whhnhy.com:8900/szxc/<hash>.png
- **认证**: Bearer Token + Cookies（通过 Playwright 自动获取登录态）

---

## ⚠️ 重要经验（踩坑记录）

### 测试用例关联需求
创建测试用例时，**必须同时传 `parent` + `story` 两个字段**：
```python
data = {
    "title": "用例标题",
    "parent": 需求ID,    # 控制父子用例关系
    "story": 需求ID,     # 控制 UI 需求页面「测试用例」Tab 显示
    "module": module_id,
    "pri": 1,
    "steps": [{"desc": "步骤", "expect": "预期"}]
}
```

### Bug steps 格式
steps 字段必须用 **HTML `<p>` 标签**，不是 JSON 数组：
```html
<p>【环境】</p><p>...</p><p>【操作步骤】</p><p>1. </p><p>【期望结果】</p><p>1. </p>
```

### Token 过期处理
API 返回 401 时，需要重新获取：
```bash
curl -X POST "http://192.168.0.28:9980/api.php/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{"account":"shidawei","password":"shidawei"}'
```

---

## 🔄 同步与更新

### 当前 Git 状态
- **远程仓库**: https://github.com/nomad2755/test_at_all
- **分支**: master
- **最新提交**: `feat: 初始完整备份 2026-05-13` (ebb09da1)

### 手动同步命令
```bash
cd /root/.openclaw/workspace
git add -A
git commit -m "update: 描述本次更新"
git push origin master
```

### 新智能体接入
```bash
git clone https://github.com/nomad2755/test_at_all.git /root/.openclaw/workspace
```

---

## 📌 快速参考

- **测试计划排期表**: `skills/zentao-integration/docs/测试计划排期表.md`
- **数字乡村模块树**: `skills/zentao-integration/docs/数字乡村模块树.md`（404个模块）
- **数据中台模块ID**: SOUL.md 中的 `📊 数据中台模块 ID 映射`
- **Bug 标题格式**: `【模块名称】具体bug内容`，如 `【电商】无法购买商品`

---

*最后更新: 2026-05-13*