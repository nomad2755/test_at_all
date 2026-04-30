#!/usr/bin/env python3
"""
Open-IM 通知发送工具 v3
集成认证 + 发送消息

认证: POST http://192.168.0.27:10002/auth/user_token
发送: POST https://easydoc-test.rentsoft.cn/rpc/2/im/message/send
"""

import argparse
import requests
from datetime import datetime


def authenticate(api_host: str, secret: str = "openIM123", 
               user_id: str = "imAdmin") -> str:
    """
    获取 Open-IM Token
    Returns: token string or None
    """
    url = f"{api_host}/auth/user_token"
    headers = {
        "Content-Type": "application/json",
        "operationID": str(int(datetime.now().timestamp() * 1000))
    }
    payload = {
        "secret": secret,
        "userID": user_id,
        "platformID": 1
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("errCode") == 0:
            token = result.get("data", {}).get("token")
            print(f"✅ 认证成功")
            return token
        else:
            print(f"❌ 认证失败: {result.get('errMsg')}")
            return None
    except Exception as e:
        print(f"❌ 认证异常: {e}")
        return None


def send_message(api_url: str, token: str, recv_id: str, 
               recv_id_type: str, content: str, content_type: int = 1) -> dict:
    """
    发送消息到 Open-IM
    """
    params = {"token": token}
    payload = {
        "recvID": recv_id,
        "recvIDType": recv_id_type,
        "content": content,
        "contentType": content_type
    }
    
    try:
        response = requests.post(api_url, json=payload, params=params, timeout=15)
        result = response.json()
        
        if result.get("errCode") == 0:
            print(f"✅ 消息发送成功")
            return {"success": True, "msg_id": result.get("data", {}).get("serverMsgID")}
        else:
            print(f"❌ 发送失败: {result.get('errMsg')}")
            return {"success": False, "error": result.get("errMsg")}
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return {"success": False, "error": str(e)}


def send_text(api_url: str, token: str, user_id: str, text: str) -> dict:
    """发送给用户"""
    return send_message(api_url, token, user_id, "singleChat", text, 1)


def send_to_group(api_url: str, token: str, group_id: str, text: str) -> dict:
    """发送到群"""
    return send_message(api_url, token, group_id, "groupChat", text, 1)


def send_test_report(api_url: str, token: str, user_id: str,
                    task_title: str, task_id: str,
                    total: int, created: int,
                    zentao_url: str = "http://192.168.0.28:9980") -> dict:
    """发送测试报告"""
    content = f"""【测试报告】

📌 任务: {task_title}
🔗 禅道: {zentao_url}/task-view-{task_id}.html

📊 用例统计:
• 总数: {total}
• 已创建: {created}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    return send_text(api_url, token, user_id, content)


def send_bug_notification(api_url: str, token: str, user_id: str,
                         bug_id: int, bug_title: str,
                         severity: str, desc: str,
                         zentao_url: str = "http://192.168.0.28:9980") -> dict:
    """发送 Bug 通知"""
    severity_map = {"1": "🔴 致命", "2": "🟠 严重", "3": "🟡 一般", "4": "🔵 优化"}
    
    content = f"""🐛 【新建Bug】

🔖 ID: {bug_id}
📛 标题: {bug_title}
⚠️ 严重程度: {severity_map.get(severity, severity)}
🔗 禅道: {zentao_url}/bug-view-{bug_id}.html

📄 描述: {desc}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    return send_text(api_url, token, user_id, content)


def main():
    parser = argparse.ArgumentParser(description="Open-IM 通知发送工具")
    parser.add_argument("--host", type=str, default="http://192.168.0.27:10002", 
                       help="Open-IM 主机地址")
    parser.add_argument("--secret", type=str, default="openIM123", help="认证密钥")
    parser.add_argument("--user-id", type=str, default="imAdmin", help="认证用户ID")
    parser.add_argument("--api-url", type=str, default="https://easydoc-test.rentsoft.cn/rpc/2/im/message/send",
                       help="发送消息 API 地址")
    
    # 接收者
    parser.add_argument("--recv-user", help="接收用户 ID")
    parser.add_argument("--recv-group", help="接收群 ID")
    
    # 消息类型
    parser.add_argument("--type", choices=["text", "report", "bug"], default="text", help="消息类型")
    parser.add_argument("--content", default="", help="文本内容")
    parser.add_argument("--title", default="", help="标题")
    parser.add_argument("--task-id", help="禅道任务 ID")
    parser.add_argument("--bug-id", type=int, help="Bug ID")
    parser.add_argument("--severity", default="3", help="严重程度")
    
    args = parser.parse_args()
    
    # 1. 认证
    print("🔐 正在认证...")
    token = authenticate(args.host, args.secret, args.user_id)
    if not token:
        print("❌ 认证失败，退出")
        return
    
    # 2. 确定接收者
    recv_id = args.recv_user or args.recv_group
    recv_type = "singleChat" if args.recv_user else "groupChat"
    
    if not recv_id:
        print("❌ 请指定 --recv-user 或 --recv-group")
        return
    
    # 3. 发送消息
    if args.type == "text":
        send_text(args.api_url, token, recv_id, args.content)
    elif args.type == "report":
        send_test_report(args.api_url, token, recv_id,
                        args.title or "测试任务",
                        args.task_id or "0",
                        total=10, created=10)
    elif args.type == "bug":
        send_bug_notification(args.api_url, token, recv_id,
                            args.bug_id or 0,
                            args.title or "Bug 标题",
                            args.severity,
                            args.content or "无描述")
    
    print("✅ 完成")


if __name__ == "__main__":
    main()
