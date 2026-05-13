#!/usr/bin/env python3
"""
Jenkins 每30分钟详细构建状态报告
发送至：石大卫(7809497014)、刘偲(1705938371)、张文骏(9175393676)
"""

import sys
import json
import uuid
import time
import urllib.request
from datetime import datetime

# ========== 配置 ==========
JENKINS_URL = "http://192.168.0.26:10240"
JENKINS_USER = "shidw"
JENKINS_PASS = "178178Shi"
OPENIM_URL = "http://192.168.0.27:10002"
OPENIM_ADMIN = "imAdmin"
OPENIM_SECRET = "openIM123"
BOT_NICKNAME = "Jenkins监控助手"

RECIPIENTS = [
    {"name": "石大卫", "userID": "7809497014"},
    {"name": "刘偲",   "userID": "1705938371"},
    {"name": "张文骏", "userID": "9175393676"},
]

# ========== OpenIM 工具（与 urgent_bug_alerter.py 一致） ==========
class OpenIMClient:
    def __init__(self, base_url, admin, secret):
        self.base = base_url
        self.admin = admin
        self.secret = secret
        self.token = ""
        self._login()

    def _login(self):
        op_id = str(uuid.uuid4())
        payload = json.dumps({"secret": self.secret, "userID": self.admin, "platformID": 1}).encode()
        req = urllib.request.Request(
            f"{self.base}/auth/user_token",
            data=payload,
            headers={"operationID": op_id, "Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        self.token = result["data"]["token"]

    def send(self, recv_id, content, title="📊 Jenkins 构建状态"):
        op_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        payload = {
            "sendID": self.admin,
            "recvID": recv_id,
            "groupID": "",
            "senderNickname": BOT_NICKNAME,
            "senderFaceURL": "",
            "senderPlatformID": 1,
            "content": {"content": content},
            "contentType": 101,
            "sessionType": 1,
            "isOnlineOnly": False,
            "notOfflinePush": False,
            "sendTime": timestamp,
            "offlinePushInfo": {
                "title": title,
                "desc": "",
                "ex": "",
                "iOSPushSound": "default",
                "iOSBadgeCount": True
            },
            "ex": ""
        }
        req = urllib.request.Request(
            f"{self.base}/msg/send_msg",
            data=json.dumps(payload).encode(),
            headers={"token": self.token, "operationID": op_id, "Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        if result.get("errCode") != 0:
            raise Exception(f"发送失败: {result}")
        return result.get("data", {}).get("serverMsgID", "")

# ========== Jenkins 获取数据 ==========
def get_jenkins_data():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        page.goto(f"{JENKINS_URL}/login", timeout=15000, wait_until='domcontentloaded')
        page.wait_for_timeout(2000)
        page.fill('#j_username', JENKINS_USER)
        page.fill('#j_password', JENKINS_PASS)
        page.click('button[type=submit]')
        page.wait_for_timeout(3000)

        # 获取所有 jobs 信息（wait_until=domcontentloaded 避免等待所有资源加载）
        page.goto(
            f"{JENKINS_URL}/api/json?tree=jobs[name,lastBuild[number,timestamp,result,duration,building],lastCompletedBuild[number,timestamp,result,duration]]",
            timeout=30000,
            wait_until='domcontentloaded'
        )
        page.wait_for_timeout(3000)
        jobs_text = page.inner_text('body')
        jobs_data = json.loads(jobs_text)

        page.goto(f"{JENKINS_URL}/queue/api/json", timeout=15000, wait_until='domcontentloaded')
        page.wait_for_timeout(1000)
        queue_text = page.inner_text('body')
        queue_data = json.loads(queue_text) if queue_text.strip().startswith('{') else {'items': []}

        browser.close()
        return jobs_data, queue_data

def build_report(jobs_data, queue_data):
    jobs = jobs_data.get('jobs', [])
    queue_items = queue_data.get('items', [])

    now_ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [f"📊 Jenkins 构建状态报告 | {now_ts}"]
    lines.append(f"总项目数: {len(jobs)}")

    building = []
    unstable = []
    failed = []
    success_recent = []
    queued_names = [q.get('task', {}).get('name', '?') for q in queue_items]

    for job in jobs:
        name = job['name']
        lb = job.get('lastBuild') or {}
        lcb = job.get('lastCompletedBuild') or {}

        if lb.get('building'):
            dur = (lb.get('duration') or 0) // 1000
            building.append({'name': name, 'number': lb.get('number'), 'duration': dur})

        if isinstance(lcb, dict) and lcb.get('timestamp'):
            ts = lcb['timestamp'] / 1000
            age_h = (datetime.now().timestamp() - ts) / 3600
            if age_h < 4:
                result = lcb.get('result')
                dur = (lcb.get('duration') or 0) // 1000
                if result == 'UNSTABLE':
                    unstable.append({'name': name, 'number': lcb.get('number'), 'duration': dur})
                elif result == 'FAILURE':
                    failed.append({'name': name, 'number': lcb.get('number'), 'duration': dur})
                elif result == 'SUCCESS':
                    success_recent.append({'name': name, 'number': lcb.get('number'), 'duration': dur})

    if building:
        lines.append(f"\n🔄 构建中 ({len(building)})")
        for b in building[:20]:
            dur_str = f"{b['duration']}s" if b['duration'] < 3600 else f"{b['duration']//60}m"
            lines.append(f"  • {b['name']} #{b['number']} ({dur_str})")
        if len(building) > 20:
            lines.append(f"  ... 还有 {len(building)-20} 个")
    else:
        lines.append("\n✅ 当前无构建进行")

    if queued_names:
        lines.append(f"\n⏳ 队列中 ({len(queued_names)})")
        for n in queued_names[:10]:
            lines.append(f"  • {n}")
        if len(queued_names) > 10:
            lines.append(f"  ... 还有 {len(queued_names)-10} 个")
    else:
        lines.append("\n📋 队列为空")

    if failed:
        lines.append(f"\n❌ 近期失败 ({len(failed)})")
        for b in failed[:10]:
            dur_str = f"{b['duration']}s" if b['duration'] < 3600 else f"{b['duration']//60}m"
            lines.append(f"  • {b['name']} #{b['number']} ({dur_str})")

    if unstable:
        lines.append(f"\n⚠️ 近期不稳定 ({len(unstable)})")
        for b in unstable[:10]:
            dur_str = f"{b['duration']}s" if b['duration'] < 3600 else f"{b['duration']//60}m"
            lines.append(f"  • {b['name']} #{b['number']} ({dur_str})")

    if success_recent:
        lines.append(f"\n✅ 近期成功 ({len(success_recent)})")
        for b in success_recent[:5]:
            dur_str = f"{b['duration']}s" if b['duration'] < 3600 else f"{b['duration']//60}m"
            lines.append(f"  • {b['name']} #{b['number']} ({dur_str})")
        if len(success_recent) > 5:
            lines.append(f"  ... 还有 {len(success_recent)-5} 个")

    if not building and not failed and not unstable and not queued_names:
        lines.append("\n🟢 所有项目状态正常，无异常")

    return "\n".join(lines)

def main():
    try:
        jobs_data, queue_data = get_jenkins_data()
        report = build_report(jobs_data, queue_data)
    except Exception as e:
        report = f"⚠️ 获取 Jenkins 数据失败: {e}"
        import traceback
        traceback.print_exc()

    print(report)

    try:
        im = OpenIMClient(OPENIM_URL, OPENIM_ADMIN, OPENIM_SECRET)
        for recipient in RECIPIENTS:
            try:
                im.send(recipient['userID'], report)
                print(f"✅ 已发送给 {recipient['name']}({recipient['userID']})")
            except Exception as ex:
                print(f"❌ 发送给 {recipient['name']} 失败: {ex}")
    except Exception as e:
        print(f"❌ OpenIM 认证失败: {e}")

if __name__ == '__main__':
    main()