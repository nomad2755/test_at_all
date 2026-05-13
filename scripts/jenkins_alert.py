#!/usr/bin/env python3
"""
Jenkins 构建状态监控 + OpenIM 告警
每小时检查一次，发现失败/不稳定项目时通知石大卫、刘偲、张文骏
包含具体的失败原因和影响分析
"""

import json
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests

# === 配置 ===
JENKINS_URL = "http://192.168.0.26:10240"
OPENIM_URL = "http://192.168.0.27:10002"
OPENIM_ADMIN = "imAdmin"
OPENIM_SECRET = "openIM123"

# 告警接收人: 姓名 -> userID
RECEIVERS = {
    "石大卫": "7809497014",
    "刘偲": "1705938371",
    "张文骏": "9175393676",
}

# 状态文件（用于去重）
STATE_FILE = "/root/.openclaw/workspace/config/jenkins_monitor_state.json"


def get_jenkins_data():
    """通过 Playwright 登录并获取 Jenkins API 数据"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        try:
            page.goto(f"{JENKINS_URL}/login", timeout=10000, wait_until="domcontentloaded")
            page.fill("#j_username", "shidw")
            page.fill("#j_password", "178178Shi")
            page.click('button[type="submit"]')
            page.wait_for_timeout(2000)

            api_url = f"{JENKINS_URL}/api/json?tree=jobs[name,color,lastBuild[result,number,timestamp,url]]"
            page.goto(api_url, timeout=10000)
            return json.loads(page.inner_text("body"))
        finally:
            browser.close()


def get_failure_reasons(problem_jobs):
    """批量获取每个问题项目的失败原因"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # 先登录
        page.goto(f"{JENKINS_URL}/login", timeout=10000, wait_until="domcontentloaded")
        page.fill("#j_username", "shidw")
        page.fill("#j_password", "178178Shi")
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)

        results = {}
        for j in problem_jobs:
            name = j["name"]
            build_url = (j.get("lastBuild") or {}).get("url", "")
            if not build_url:
                results[name] = "无构建URL"
                continue

            try:
                console_url = build_url.rstrip('/') + '/consoleText'
                page.goto(console_url, timeout=8000)
                text = page.inner_text("body")
                lines = [l.strip() for l in text.split('\n') if l.strip()]

                reason = None
                for line in reversed(lines[-30:]):
                    if any(kw in line for kw in ['ERROR', 'Exception', 'Status', 'FAILED', 'FAILURE']):
                        # 清理ANSI颜色码
                        clean = ''.join(c for c in line if ord(c) > 31 and ord(c) != 27)
                        reason = clean[:200]
                        break

                if not reason:
                    reason = lines[-1][:200] if lines else "无详细信息"

                results[name] = reason

            except Exception as e:
                results[name] = f"获取失败原因超时"

        browser.close()
        return results


def get_openim_token():
    """获取 OpenIM Token"""
    import uuid
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


def build_age(timestamp_ms):
    """计算构建距今时间"""
    if not timestamp_ms:
        return "未知"
    age_s = time.time() - timestamp_ms / 1000
    days = int(age_s // 86400)
    hours = int((age_s % 86400) // 3600)
    if days > 0:
        return f"{days}天{hours}时前"
    elif hours > 0:
        return f"{hours}时前"
    else:
        mins = int((age_s % 3600) // 60)
        return f"{mins}分前"


def load_state():
    """加载状态文件"""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"last_notified": {}}


def save_state(state):
    """保存状态文件"""
    import os
    os.makedirs("/root/.openclaw/workspace/config", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False)


def should_notify(state, problem_jobs):
    """判断是否需要发送通知（去重）"""
    now_key = datetime.now().strftime("%Y-%m-%d %H")
    last_notify_time = state.get("last_notify_time", "")

    if last_notify_time != now_key:
        state["last_notify_time"] = now_key
        state["last_notified"] = {}
        return True, state

    last_notified = state.get("last_notified", {})
    problem_keys = set()
    for j in problem_jobs:
        lb = j.get("lastBuild") or {}
        key = f"{j['name']}#{lb.get('number')}"
        problem_keys.add(key)

    new_problems = problem_keys - set(last_notified.keys())
    return bool(new_problems), state


def main():
    brief = "--brief" in sys.argv

    try:
        data = get_jenkins_data()
    except Exception as e:
        print(f"获取 Jenkins 数据失败: {e}")
        sys.exit(1)

    jobs = data.get("jobs", [])

    failed = []
    unstable = []

    for j in jobs:
        lb = j.get("lastBuild")
        if not lb:
            continue
        result = lb.get("result")
        if result == "FAILURE":
            failed.append(j)
        elif result == "UNSTABLE":
            unstable.append(j)

    all_problems = failed + unstable

    if brief:
        reasons = {}
        if all_problems:
            reasons = get_failure_reasons(all_problems)

        output = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total": len(jobs),
                "failed": len(failed),
                "unstable": len(unstable),
            },
            "failed_jobs": [
                {
                    "name": j["name"],
                    "number": (j.get("lastBuild") or {}).get("number"),
                    "age": build_age((j.get("lastBuild") or {}).get("timestamp")),
                    "url": (j.get("lastBuild") or {}).get("url", ""),
                    "reason": reasons.get(j["name"], ""),
                }
                for j in failed
            ],
            "unstable_jobs": [
                {
                    "name": j["name"],
                    "number": (j.get("lastBuild") or {}).get("number"),
                    "age": build_age((j.get("lastBuild") or {}).get("timestamp")),
                    "url": (j.get("lastBuild") or {}).get("url", ""),
                    "reason": reasons.get(j["name"], ""),
                }
                for j in unstable
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 正常模式
    state = load_state()
    need_notify, state = should_notify(state, all_problems)

    if not need_notify:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 无新增问题，跳过通知")
        return

    # 获取失败原因
    reasons = {}
    if all_problems:
        print("正在获取失败原因...")
        reasons = get_failure_reasons(all_problems)

    # 准备告警消息
    msg_lines = [f"🚨 Jenkins 构建状态告警 | {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    msg_lines.append(f"共 {len(failed)} 个失败 + {len(unstable)} 个不稳定")

    if failed:
        msg_lines.append(f"\n❌ 失败 ({len(failed)} 个):")
        for j in failed:
            lb = j.get("lastBuild") or {}
            reason = reasons.get(j["name"], "")
            msg_lines.append(f"  [{j['name']}] #{lb.get('number')} {build_age(lb.get('timestamp'))}")
            msg_lines.append(f"  原因: {reason}")
            msg_lines.append(f"  链接: {lb.get('url', '')}")

    if unstable:
        msg_lines.append(f"\n⚠️ 不稳定 ({len(unstable)} 个):")
        for j in unstable:
            lb = j.get("lastBuild") or {}
            reason = reasons.get(j["name"], "")
            msg_lines.append(f"  [{j['name']}] #{lb.get('number')} {build_age(lb.get('timestamp'))}")
            msg_lines.append(f"  原因: {reason}")
            msg_lines.append(f"  链接: {lb.get('url', '')}")

    msg_text = "\n".join(msg_lines)
    print(msg_text)
    print()

    # 发送 OpenIM 通知
    try:
        token, opid = get_openim_token()
        success_count = 0
        for name, user_id in RECEIVERS.items():
            try:
                send_openim_msg(token, user_id, msg_text, opid)
                print(f"✅ 已通知 {name} ({user_id})")
                success_count += 1
            except Exception as e:
                print(f"❌ 通知 {name} 失败: {e}")

        print(f"\n共通知 {success_count}/{len(RECEIVERS)} 人")

        # 更新去重状态
        problem_keys = {}
        for j in all_problems:
            lb = j.get("lastBuild") or {}
            key = f"{j['name']}#{lb.get('number')}"
            problem_keys[key] = True
        state["last_notified"] = problem_keys
        save_state(state)

    except Exception as e:
        print(f"发送通知失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
