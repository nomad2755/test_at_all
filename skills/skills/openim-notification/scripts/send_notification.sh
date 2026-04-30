#!/bin/bash
# OpenIM 消息发送脚本
# 用法: ./send_notification.sh <recvID> <content> [senderNickname]

OPENIM_HOST="http://192.168.0.27:10002"
ADMIN_USER="imAdmin"
ADMIN_SECRET="openIM123"
PLATFORM_ID=1

# 默认值
SENDER_NICKNAME="${3:-禅道智能助手}"
OFFLINE_TITLE="${4:-禅道助手}"

# 检查参数
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "用法: $0 <recvID> <content> [senderNickname] [offlinePushTitle]"
    echo "示例: $0 9175393676 '这是一条测试消息'"
    exit 1
fi

RECV_ID="$1"
CONTENT="$2"
OPERATION_ID="$(date +%s)$$"
SEND_TIME="$(date +%s)000"

# 1. 获取 Token
TOKEN_RESPONSE=$(curl -s --location --request POST "${OPENIM_HOST}/auth/user_token" \
    --header "operationID: ${OPERATION_ID}" \
    --header "Content-Type: application/json" \
    --data-raw "{
        \"secret\": \"${ADMIN_SECRET}\",
        \"userID\": \"${ADMIN_USER}\",
        \"platformID\": ${PLATFORM_ID}
    }")

TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('token',''))")
if [ -z "$TOKEN" ]; then
    echo "获取 Token 失败: $TOKEN_RESPONSE"
    exit 1
fi

# 2. 发送消息
MSG_RESPONSE=$(curl -s --location --request POST "${OPENIM_HOST}/msg/send_msg" \
    --header "operationID: ${OPERATION_ID}" \
    --header "token: ${TOKEN}" \
    --header "Content-Type: application/json" \
    --data-raw "{
        \"sendID\": \"${ADMIN_USER}\",
        \"recvID\": \"${RECV_ID}\",
        \"groupID\": \"\",
        \"senderNickname\": \"${SENDER_NICKNAME}\",
        \"senderFaceURL\": \"http://www.head.com\",
        \"senderPlatformID\": ${PLATFORM_ID},
        \"content\": {
            \"content\": \"${CONTENT}\"
        },
        \"contentType\": 101,
        \"sessionType\": 1,
        \"isOnlineOnly\": false,
        \"notOfflinePush\": false,
        \"sendTime\": ${SEND_TIME},
        \"offlinePushInfo\": {
            \"title\": \"${OFFLINE_TITLE}\",
            \"desc\": \"\",
            \"ex\": \"\",
            \"iOSPushSound\": \"default\",
            \"iOSBadgeCount\": true
        },
        \"ex\": \"\"
    }")

echo "$MSG_RESPONSE"
