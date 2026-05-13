# 禅道测试工作流 + 钉钉通知 Skill

## 概述
本 skill 整合了 ZenTao API 和钉钉 Webhook，实现：需求分析 → 测试用例设计 → 导入禅道 → 钉钉通知的完整流程。

## 功能
1. **ZenTao API 集成** - 创建测试用例、Bug、任务
2. **钉钉通知** - 发送测试报告到钉钉群
3. **测试工作流** - 一键生成测试用例并推送钉钉

## 配置

### 环境变量
```bash
# 钉钉 Webhook（可选，不配置则只输出到控制台）
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
```

### 钉钉机器人配置
1. 钉钉群 → 群设置 → 智能群助手 → 添加机器人 → 自定义机器人
2. 安全设置选择"加签"或"关键词"
3. 复制 Webhook URL

## 使用方式

### 方式1：Python 脚本（推荐）
```bash
cd /root/.openclaw/workspace/skills/zentao-integration/scripts
python3 zentao_dingtalk_workflow.py --task-id 1234 --case-count 20
```

### 方式2：独立命令
```bash
# 创建测试用例并发送钉钉通知
python3 -c "
from zentao_dingtalk_workflow import ZenTaoDingTalkWorkflow

workflow = ZenTaoDingTalkWorkflow()
result = workflow.run(
    task_title='邀请码功能测试',
    task_id='1234',
    cases=[
        {'title': '正常邀请', 'steps': [{'desc': '输入邀请码', 'expect': '验证通过'}], 'pri': 1}
    ]
)
print(result)
"
```

## 钉钉消息格式

### Markdown 格式
```markdown
# 测试报告 📋

## 任务信息
- **禅道任务**: [ID: 1234](http://192.168.0.28:9980/bug-view-1234.html)
- **执行时间**: 2026-04-28 10:50

## 测试用例统计
| 类型 | 数量 |
|------|------|
| 用例总数 | 20 |
| 已创建 | 20 |

## 创建的测试用例
1. TC-001: 正常邀请
2. TC-002: 邀请码无效

## 报告摘要
（AI 生成的测试分析）

---
🤖 由测试助手自动生成
```

## API 端点

### ZenTao API
- **Base URL**: `http://192.168.0.28:9980/api.php/v1`
- **Token**: `99f5636c120167a9eacc7563e90b7dbf`

### 钉钉 Webhook
- **URL**: `https://oapi.dingtalk.com/robot/send`
- **Method**: POST
- **Auth**: Bearer Token 或关键词

## 文件清单
- `zentao_dingtalk_workflow.py` - 主工作流脚本
- `scripts/send_dingtalk.py` - 钉钉通知模块
