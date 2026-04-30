---
name: openim-notification
description: 通过 OpenIM 服务发送消息通知，支持指定用户发送文本消息，用于禅道Bug通知、测试结果推送等场景。
---

# openim-notification

Send notifications via OpenIM service to specified users.

## Triggers

- 发送 OpenIM 消息
- 通过 OpenIM 推送通知
- 发送消息到指定用户
- OpenIM 消息通知
- openIM notification

## Use Cases

- 禅道 Bug 创建/变更时自动通知相关人员
- 测试任务完成后的结果推送
- 系统告警通知到个人或群组
- 定时任务结果汇报

## Inputs

- **必填**：
  - `recvID`：接收者用户 ID（字符串）
  - `content`：消息内容（字符串）
- **可选**：
  - `recvID`：目标用户 ID（默认：张文骏 9175393676）
  - `senderNickname`：发送者昵称（默认：禅道智能助手）
  - `title`：离线推送标题（默认：禅道助手）
  - `sendTime`：发送时间戳（默认：当前时间）

## Outputs

- 成功：返回 `serverMsgID`，消息已投递
- 失败：返回错误码和错误信息，建议重试

## Workflow

1. **获取 Token**（若已有有效 token 可跳过）：
   ```bash
   POST http://192.168.0.27:10002/auth/user_token
   {
     "secret": "openIM123",
     "userID": "imAdmin",
     "platformID": 1
   }
   ```

2. **发送消息**：
   ```bash
   POST http://192.168.0.27:10002/msg/send_msg
   Headers: token: <token>
   Body:
   {
     "sendID": "imAdmin",
     "recvID": "<用户ID>",
     "content": {
       "content": "<消息内容>"
     },
     "contentType": 101,
     "sessionType": 1
   }
   ```

3. **解析结果**：
   - `errCode: 0` → 发送成功
   - `errCode != 0` → 发送失败，检查错误信息

## Known Users

| 姓名 | userID |
|------|--------|
| 石大卫 | 1965695380 |
| 张文骏 | 9175393676 |

## OpenIM API Base

- **地址**：`http://192.168.0.27:10002`
- **Admin账号**：`imAdmin` / `openIM123`

## Limitations

- 仅支持文本消息（contentType: 101）
- token 有效期有限，若返回 401 需重新获取
- 不支持离线推送的复杂定制（iOS Badge 等）

## Examples

**发送测试消息给张文骏：**
- recvID: `9175393676`
- content: `这是一条测试消息`

**发送禅道Bug通知给石大卫：**
- recvID: `1965695380`
- content: `你有一条禅道的Bug需要关注！Bug ID: 9728，标题：xxx`
