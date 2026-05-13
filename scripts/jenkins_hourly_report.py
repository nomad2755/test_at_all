#!/usr/bin/env python3
"""
Jenkins 每小时详细构建状态报告
- 正在构建的进度
- 队列情况
- 近期不稳定项目

发送至：石大卫(7809497014)、刘偲(1705938371)、张文骏(9175393676)
"""

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

# ========== OpenIM 客户端 ==========
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

    def send(self, recv_id, content, title="📊 Jenkins 构建状态报告"):
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

# ========== Jenkins 数据获取 ==========
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

        # 获取 jobs 概览（wait_until=domcontentloaded 避免加载所有资源）
        page.goto(
            f"{JENKINS_URL}/api/json?tree=jobs[name,lastBuild[number,timestamp,result,duration,estimatedDuration,building],lastCompletedBuild[number,timestamp,result,duration],lastFailedBuild[number,timestamp],lastSuccessfulBuild[number,timestamp]]",
            timeout=30000,
            wait_until='domcontentloaded'
        )
        page.wait_for_timeout(3000)
        jobs_text = page.inner_text('body')
        jobs_data = json.loads(jobs_text)

        # 获取队列
        page.goto(f"{JENKINS_URL}/queue/api/json", timeout=15000, wait_until='domcontentloaded')
        page.wait_for_timeout(1000)
        queue_text = page.inner_text('body')
        queue_data = json.loads(queue_text) if queue_text.strip().startswith('{') else {'items': []}

        browser.close()
        return jobs_data, queue_data

# ========== 报告生成 ==========
def build_report(jobs_data, queue_data):
    jobs = jobs_data.get('jobs', [])
    queue_items = queue_data.get('items', [])

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []

    # ---------- 标题 ----------
    lines.append(f"📊 Jenkins 构建状态报告 | {now_str}")
    lines.append(f"总项目数: {len(jobs)}")
    lines.append("")

    # ---------- 正在构建（进度） ----------
    building = []
    for job in jobs:
        lb = job.get('lastBuild') or {}
        if lb.get('building'):
            dur = (lb.get('duration') or 0) // 1000
            est = lb.get('estimatedDuration', 0) // 1000
            remain = max(0, est - dur)
            prog = int(dur / est * 100) if est > 0 else 0
            start_ts = datetime.fromtimestamp(lb.get('timestamp', 0) / 1000).strftime('%H:%M:%S') if lb.get('timestamp') else '?'
            building.append({
                'name': job['name'],
                'number': lb.get('number'),
                'dur': dur,
                'est': est,
                'remain': remain,
                'prog': prog,
                'start': start_ts,
            })

    if building:
        lines.append(f"🔄 正在构建 ({len(building)}个)")
        for b in sorted(building, key=lambda x: -x['prog'])[:20]:
            dur_s = f"{b['dur']}s" if b['dur'] < 3600 else f"{b['dur']//60}m"
            remain_s = f"{b['remain']}s" if b['remain'] < 3600 else f"{b['remain']//60}m"
            lines.append(f"  ▶ {b['name']} #{b['number']}")
            lines.append(f"    进度:{b['prog']:3d}% | 已:{dur_s} | 预计剩余:{remain_s} | 开始:{b['start']}")
        if len(building) > 20:
            lines.append(f"  ... 还有 {len(building)-20} 个")
    else:
        lines.append("✅ 当前无构建进行")

    lines.append("")

    # ---------- 队列情况 ----------
    queue_names = [q.get('task', {}).get('name', '?') for q in queue_items]
    if queue_items:
        lines.append(f"⏳ 队列中 ({len(queue_items)}个)")
        for i, q in enumerate(queue_items[:15]):
            task = q.get('task', {})
            why = q.get('why', '等待资源')
            wait_ms = q.get('inQueueSince', 0)
            wait_s = int((datetime.now().timestamp() * 1000 - wait_ms) / 1000) if wait_ms else 0
            wait_str = f"{wait_s}s" if wait_s < 3600 else f"{wait_s//60}m"
            lines.append(f"  {i+1}. {task.get('name', '?')} | 等待:{wait_str} | 原因:{why[:40]}")
        if len(queue_items) > 15:
            lines.append(f"  ... 还有 {len(queue_items)-15} 个")
    else:
        lines.append("📋 队列为空")

    lines.append("")

    # ---------- 近期不稳定项目 ----------
    lines.append("⚠️ 近期不稳定项目")
    unstable_count = 0
    for job in jobs:
        lcb = job.get('lastCompletedBuild') or {}
        if isinstance(lcb, dict) and lcb.get('result') == 'UNSTABLE':
            ts = lcb.get('timestamp', 0) / 1000
            age_h = (datetime.now().timestamp() - ts) / 3600
            dur_s = (lcb.get('duration', 0) or 0) // 1000
            dur_str = f"{dur_s}s" if dur_s < 3600 else f"{dur_s//60}m"
            lines.append(f"  ⚠️ {job['name']} #{lcb.get('number')} | {datetime.fromtimestamp(ts).strftime('%m-%d %H:%M')} | 耗时:{dur_str} | age:{int(age_h*10)/10}h")
            unstable_count += 1
    if unstable_count == 0:
        lines.append("  无")

    lines.append("")

    # ---------- 近期失败项目 ----------
    lines.append("❌ 近期失败项目")
    failed_count = 0
    for job in jobs:
        lcb = job.get('lastCompletedBuild') or {}
        if isinstance(lcb, dict) and lcb.get('result') == 'FAILURE':
            ts = lcb.get('timestamp', 0) / 1000
            age_h = (datetime.now().timestamp() - ts) / 3600
            dur_s = (lcb.get('duration', 0) or 0) // 1000
            dur_str = f"{dur_s}s" if dur_s < 3600 else f"{dur_s//60}m"
            lines.append(f"  ❌ {job['name']} #{lcb.get('number')} | {datetime.fromtimestamp(ts).strftime('%m-%d %H:%M')} | 耗时:{dur_str} | age:{int(age_h*10)/10}h")
            failed_count += 1
    if failed_count == 0:
        lines.append("  无")

    lines.append("")

    # ---------- 近期成功项目 ----------
    lines.append("✅ 近期成功项目")
    success_count = 0
    shown = []
    for job in jobs:
        lcb = job.get('lastCompletedBuild') or {}
        if isinstance(lcb, dict) and lcb.get('result') == 'SUCCESS':
            ts = lcb.get('timestamp', 0) / 1000
            age_h = (datetime.now().timestamp() - ts) / 3600
            if age_h < 8:  # 8小时内成功的
                dur_s = (lcb.get('duration', 0) or 0) // 1000
                dur_str = f"{dur_s}s" if dur_s < 3600 else f"{dur_s//60}m"
                lines.append(f"  ✅ {job['name']} #{lcb.get('number')} | {datetime.fromtimestamp(ts).strftime('%m-%d %H:%M')} | 耗时:{dur_str}")
                success_count += 1
    if success_count == 0:
        lines.append("  无")

    lines.append("")

    # ---------- 总结 ----------
    if not building and not queue_items and unstable_count == 0 and failed_count == 0:
        lines.append("🟢 所有项目状态正常，无异常")

    return "\n".join(lines)

# ========== 主程序 ==========
def main():
    report = ""
    try:
        jobs_data, queue_data = get_jenkins_data()
        report = build_report(jobs_data, queue_data)
    except Exception as e:
        import traceback
        report = f"⚠️ 获取 Jenkins 数据失败: {e}\n{traceback.format_exc()}"

    print(report)

    try:
        im = OpenIMClient(OPENIM_URL, OPENIM_ADMIN, OPENIM_SECRET)
        for r in RECIPIENTS:
            try:
                im.send(r['userID'], report)
                print(f"✅ 已发送给 {r['name']}({r['userID']})")
            except Exception as ex:
                print(f"❌ 发送给 {r['name']} 失败: {ex}")
    except Exception as e:
        print(f"❌ OpenIM 认证失败: {e}")

if __name__ == '__main__':
    main()