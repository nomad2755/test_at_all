#!/usr/bin/env python3
"""
Jenkins Webhook 中转服务
接收 Jenkins 构建完成回调 → 解析 → 通过 OpenIM 发送给指定用户
用法: python3 jenkins_webhook_server.py
"""

import json
import uuid
import time
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__)

# === 配置 ===
OPENIM_URL = "http://192.168.0.27:10002"
OPENIM_ADMIN = "imAdmin"
OPENIM_SECRET = "openIM123"

# 告警接收人配置
RECEIVERS = {
    "石大卫": "7809497014",
    "刘偲": "1705938371",
    "张文骏": "9175393676",
}

# 构建结果 -> 表情符号映射
RESULT_EMOJI = {
    "SUCCESS": "✅",
    "FAILURE": "❌",
    "UNSTABLE": "⚠️",
    "ABORTED": "⏹",
    "BUILDING": "🔄",
}


def get_openim_token():
    """获取 OpenIM Token"""
    opid = str(uuid.uuid4())
    resp = requests.post(
        f"{OPENIM_URL}/auth/user_token",
        headers={"Content-Type": "application/json", "operationID": opid},
        json={"secret": OPENIM_SECRET, "userID": OPENIM_ADMIN, "platformID": 1},
        timeout=10,
    )
    data = resp.json()
    if data.get("errCode") == 0:
        return data["data"]["token"], opid
    raise Exception(f"OpenIM token failed: {data}")


def send_openim_msg(token, recv_id, content, opid):
    """发送 OpenIM 消息"""
    resp = requests.post(
        f"{OPENIM_URL}/msg/send_msg",
        headers={"token": token, "Content-Type": "application/json", "operationID": opid},
        json={
            "sendID": OPENIM_ADMIN,
            "recvID": recv_id,
            "content": {"content": content},
            "contentType": 101,
            "sessionType": 1,
        },
        timeout=10,
    )
    result = resp.json()
    if result.get("errCode") == 0:
        return True
    raise Exception(f"OpenIM send failed: {result}")


def parse_jenkins_payload(data):
    """解析 Jenkins 回调数据"""
    name = data.get("name", "未知项目")
    build_number = data.get("number", "?")
    result = data.get("result", "UNKNOWN")
    phase = data.get("phase", "UNKNOWN")
    url = data.get("url", "")
    job_url = data.get("job_url", url)
    
    timestamp_ms = data.get("timestamp")
    if timestamp_ms:
        build_time = datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M")
    else:
        build_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return {
        "name": name,
        "build_number": build_number,
        "result": result,
        "phase": phase,
        "url": url or job_url,
        "build_time": build_time,
    }


def build_message(info):
    """构建通知消息"""
    emoji = RESULT_EMOJI.get(info["result"], "❓")
    result_text = {
        "SUCCESS": "构建成功",
        "FAILURE": "构建失败",
        "UNSTABLE": "构建不稳定",
        "ABORTED": "构建已取消",
        "BUILDING": "构建中",
        "UNKNOWN": "状态未知",
    }.get(info["result"], info["result"])

    phase = info["phase"]
    if phase == "COMPLETED":
        msg = (
            f"{emoji} Jenkins 构建通知 | {info['build_time']}\n"
            f"项目: {info['name']}\n"
            f"构建: #{info['build_number']}\n"
            f"结果: {result_text}\n"
            f"链接: {info['url']}"
        )
    elif phase == "STARTED":
        msg = (
            f"🔄 Jenkins 构建开始 | {info['build_time']}\n"
            f"项目: {info['name']}\n"
            f"构建: #{info['build_number']}\n"
            f"正在构建中..."
        )
    else:
        msg = (
            f"📋 Jenkins 构建更新 | {info['build_time']}\n"
            f"项目: {info['name']}\n"
            f"构建: #{info['build_number']}\n"
            f"阶段: {phase}"
        )

    return msg


@app.route("/webhook/jenkins", methods=["POST"])
def jenkins_webhook():
    """Jenkins Webhook 接收端点"""
    try:
        data = request.get_json() or {}
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 收到 Jenkins 回调: {json.dumps(data, ensure_ascii=False)[:200]}")
        
        info = parse_jenkins_payload(data)
        print(f"  -> 项目: {info['name']} #{info['build_number']} {info['result']} ({info['phase']})")
        
        # 只在构建完成时通知（SUCCESS/FAILURE/UNSTABLE/ABORTED）
        if info["phase"] == "COMPLETED" and info["result"] in ("SUCCESS", "FAILURE", "UNSTABLE", "ABORTED"):
            msg = build_message(info)
            print(f"  -> 发送通知: {msg[:100]}...")
            
            try:
                token, opid = get_openim_token()
                sent = 0
                for name, user_id in RECEIVERS.items():
                    try:
                        send_openim_msg(token, user_id, msg, opid)
                        print(f"  -> ✅ 已通知 {name}")
                        sent += 1
                    except Exception as e:
                        print(f"  -> ❌ 通知 {name} 失败: {e}")
                
                print(f"  -> 完成，共发送 {sent}/{len(RECEIVERS)} 人")
                return jsonify({"status": "ok", "notified": sent})
                
            except Exception as e:
                print(f"  -> OpenIM 错误: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        else:
            print(f"  -> 跳过通知 (phase={info['phase']}, result={info['result']})")
            return jsonify({"status": "skipped"})
            
    except Exception as e:
        print(f"  -> 处理错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


@app.route("/", methods=["GET"])
def index():
    """首页"""
    return jsonify({
        "service": "Jenkins Webhook -> OpenIM 中转服务",
        "endpoints": {
            "/webhook/jenkins": "POST - Jenkins 回调接收端点",
            "/health": "GET - 健康检查",
            "/screenshots": "GET - Bug 截图列表",
            "/screenshots/<filename>": "GET - 查看截图",
        },
        "receivers": list(RECEIVERS.keys()),
    })


# === Bug 截图服务 ===
SCREENSHOT_DIR = "/root/.openclaw/workspace/bug_screenshots"
JENKINS_SCREENSHOT_DIR = "/opt/jenkins_home/userContent/bug_screenshots"


@app.route("/screenshots", methods=["GET"])
def list_screenshots():
    """列出所有 Bug 截图"""
    try:
        # 优先从本地目录读取
        files = []
        if os.path.exists(SCREENSHOT_DIR):
            for f in sorted(os.listdir(SCREENSHOT_DIR), reverse=True):
                if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    files.append({
                        "name": f,
                        "url": f"/screenshots/{f}",
                        "size": os.path.getsize(os.path.join(SCREENSHOT_DIR, f))
                    })
        return jsonify({
            "count": len(files),
            "files": files,
            "access_url": "http://公网IP:8099/screenshots/文件名",
            "local_dir": SCREENSHOT_DIR,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/screenshots/<filename>", methods=["GET"])
def serve_screenshot(filename):
    """提供截图访问 - 优先本地目录，fallback 到 Jenkins 目录"""
    # 安全检查：只允许图片文件
    if not any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
        return jsonify({"error": "不允许的文件类型"}), 400
    
    # 先尝试本地目录
    local_path = os.path.join(SCREENSHOT_DIR, filename)
    if os.path.exists(local_path):
        return send_from_directory(SCREENSHOT_DIR, filename)
    
    # fallback 到 Jenkins 目录
    jenkins_path = os.path.join(JENKINS_SCREENSHOT_DIR, filename)
    if os.path.exists(jenkins_path):
        return send_from_directory(JENKINS_SCREENSHOT_DIR, filename)
    
    return jsonify({"error": "文件不存在"}), 404


if __name__ == "__main__":
    import os
    port = int(os.environ.get("JENKINS_WEBHOOK_PORT", 8099))
    print(f"启动 Jenkins Webhook 服务，监听端口 {port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
