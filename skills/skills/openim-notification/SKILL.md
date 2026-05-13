# openim-notification

Send notifications via OpenIM service to specified users. Integrate with ZenTao, Jenkins, and other internal systems for automated alerting.

## Triggers

- 发送 OpenIM 消息
- 通过 OpenIM 推送通知
- 发送消息到指定用户
- OpenIM 消息通知
- Jenkins 构建结果通知
- 系统告警通知

## Known Users

| 姓名 | userID |
|------|--------|
| 石大卫 | 7809497014 ⚠️ 注意：1965695380 是王新 |
| 张文骏 | 9175393676 |
| 刘偲 | 1705938371 |

## OpenIM API Base

- **地址**：`http://192.168.0.27:10002`
- **Admin账号**：`imAdmin` / `openIM123`
- **Token获取**：`POST /auth/user_token`，headers 必须带 `operationID`（uuid格式）
- **contentType**：101（文本消息）
- **sessionType**：1（单聊）/ 2（群聊）
- **接收人**:
  - 石大卫: `7809497014`
  - 刘偲: `1705938371`
  - 张文骏: `9175393676`

## 集成系统账号

| 系统 | 地址 | 账号 | 密码 |
|------|------|------|------|
| Jenkins | http://192.168.0.26:10240 | shidw | 178178Shi |
| ZenTao | http://192.168.0.28:9980 | shidawei | shidawei |

## Workflow

### 1. 获取 Token
```python
import requests, uuid
opid = str(uuid.uuid4())
resp = requests.post(
    f"http://192.168.0.27:10002/auth/user_token",
    headers={"Content-Type": "application/json", "operationID": opid},
    json={"secret": "openIM123", "userID": "imAdmin", "platformID": 1},
    timeout=10
)
token = resp.json()["data"]["token"]
```

### 2. 发送消息
```python
resp = requests.post(
    f"http://192.168.0.27:10002/msg/send_msg",
    headers={"token": token, "Content-Type": "application/json", "operationID": opid},
    json={
        "sendID": "imAdmin",
        "recvID": "<userID>",
        "content": {"content": "<消息内容>"},
        "contentType": 101,
        "sessionType": 1,
    },
    timeout=10
)
# errCode: 0 = 成功
```

## 集成场景

### ZenTao Bug 通知
- 从 ZenTao API 拉取 Bug 数据
- 整理统计信息后通过 OpenIM 发送

### Jenkins 构建状态通知
- 轮询 Jenkins API 获取构建状态
- 发现失败/不稳定时通过 OpenIM 告警

### 系统监控告警
- 定时任务检测异常
- 自动通知相关人员

## Jenkins 集成

**Jenkins 地址**：`http://192.168.0.26:10240`（账号：shidw / 178178Shi）

**脚本位置**：`/root/.openclaw/workspace/scripts/`

| 脚本 | 功能 |
|------|------|
| `jenkins_alert.py` | 轮询 Jenkins，失败/不稳定时通过 OpenIM 告警，支持 `--brief` 输出 JSON |
| `jenkins_monitor.py` | 获取 Jenkins 所有项目状态，支持 `--brief` / `--all` |
| `jenkins_webhook_server.py` | Webhook 中转服务（端口 8099），接收 Jenkins 回调后通过 OpenIM 发通知 |

**已知不稳定项目（2026-05-09）：**
| 项目 | 构建# | 原因 |
|------|-------|------|
| dam_cloud25 | #429 | SSH发布超时 |
| dam_screenv3 | #85 | SSH发布失败（Exit Status 1）|
| hp-hospital-web51 | #3 | SSH发布失败（Exit Status 1）|
| 测试 | #6 | SSH发布失败（Exit Status 8）|
| 测试环境镜像 | #1 | SSH发布失败（Exit Status 17）|

## Limitations

- 仅支持文本消息（contentType: 101）
- token 有效期约 90 天，需重新获取
- 不支持离线推送的复杂定制

## Examples

**发送测试消息：**
```python
send_openim_msg(token, "9175393676", "这是一条测试消息", opid)
```

**Jenkins 告警示例输出：**
```
🚨 Jenkins 构建状态告警 | 2026-05-09 14:45
共 0 个失败 + 5 个不稳定

⚠️ 不稳定 (5 个):
  [dam_cloud25] #429 410天4时前
  原因: ERROR: Exception when publishing... [Exec timed out after 120,000 ms]
  链接: http://192.168.0.26:10240/job/dam_cloud25/429/
```
