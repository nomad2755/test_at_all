#!/usr/bin/env python3
"""
Jenkins 每日详细报告（含失败/不稳定原因分析）
每天早上9点发送给：汪洋、朱飞、王明
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
    {"name": "汪洋", "userID": "1218039171"},
    {"name": "朱飞", "userID": "9513791516"},
    {"name": "王明", "userID": "4659926734"},
    {"name": "王紫辛", "userID": "4051590407"},
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
        self.token = json.loads(resp.read())["data"]["token"]

    def send(self, recv_id, content, title="📊 Jenkins 每日构建报告"):
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

        # 获取概览（wait_until=domcontentloaded 避免加载所有资源）
        page.goto(
            f"{JENKINS_URL}/api/json?tree=jobs[name,lastBuild[number,timestamp,result,duration,estimatedDuration,building],lastCompletedBuild[number,timestamp,result,duration]]",
            timeout=30000,
            wait_until='domcontentloaded'
        )
        page.wait_for_timeout(3000)
        jobs_text = page.inner_text('body')
        jobs_data = json.loads(jobs_text)

        browser.close()
        return jobs_data

def analyze_failure_reason(name, build_number):
    """通过查看job的控制台输出分析失败原因"""
    from playwright.sync_api import sync_playwright
    try:
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

            # 获取控制台输出最后100行
            console_url = f"{JENKINS_URL}/job/{name}/{build_number}/consoleText"
            page.goto(console_url, timeout=20000, wait_until='domcontentloaded')
            page.wait_for_timeout(2000)
            text = page.inner_text('body')
            lines = text.strip().split('\n')
            last_lines = lines[-80:] if len(lines) > 80 else lines

            browser.close()

            # 分析失败原因
            text_block = '\n'.join(last_lines).lower()

            # SSH相关
            if any(k in text_block for k in ['ssh', 'connection refused', 'connection timeout', 'exec timed out', 'exit status', 'publish over ssh', 'ssh_exchange_identification']):
                if 'exec timed out' in text_block or 'timeout' in text_block:
                    return "⏱️ SSH执行超时（Exec timed out）— 远程服务器响应慢或脚本执行超时"
                elif 'connection refused' in text_block or 'connection timed out' in text_block:
                    return "🔌 SSH连接失败（connection refused/timeout）— 目标服务器不可达或端口不通"
                elif 'exit status' in text_block:
                    for line in reversed(last_lines):
                        if 'exit status' in line.lower():
                            return f"⚠️ 命令执行异常（{line.strip()}）— 发布脚本执行失败"
                    return "⚠️ SSH发布失败（Exit Status）— 部署脚本执行异常"
                elif 'publish over ssh' in text_block:
                    return "📡 SSH发布插件异常 — SSH发布配置或连接问题"
                elif 'ssh_exchange' in text_block:
                    return "🔐 SSH认证失败 — SSH密钥或认证信息错误"

            # Maven/编译相关
            if any(k in text_block for k in ['maven', 'compile', 'build failed', 'test failure', 'failure']):
                if 'maven' in text_block and 'test' in text_block:
                    return "🧪 Maven测试失败（Test Failure）— 单元测试未通过"
                elif 'compilation' in text_block or 'compile error' in text_block:
                    return "💥 编译失败（Compilation Error）— 代码编译不通过"
                elif 'build failed' in text_block:
                    return "🏗️ 构建失败（Build Failed）— Maven/Gradle构建失败"
                elif 'test failure' in text_block:
                    return "🧪 测试失败（Test Failure）"
                return "🔨 构建异常 — Maven或构建工具执行失败"

            # Git/Docker相关
            if any(k in text_block for k in ['git', 'docker', 'dockerfile']):
                if 'git' in text_block and ('checkout' in text_block or 'clone' in text_block or 'merge' in text_block):
                    return "📦 Git操作失败 — 代码检出或合并失败"
                elif 'docker' in text_block and ('build' in text_block or 'pull' in text_block):
                    return "🐳 Docker镜像构建/拉取失败"
                return "📦 版本控制或容器化异常"

            # 网络/权限相关
            if any(k in text_block for k in ['permission denied', 'access denied', 'unauthorized', 'forbidden', 'no such host']):
                return "🔒 权限不足（Permission Denied / Access Denied）"
            if 'out of memory' in text_block or 'heap space' in text_block:
                return "💾 内存不足（Out of Memory / Heap Space）"
            if 'disk' in text_block and ('full' in text_block or 'no space' in text_block):
                return "💽 磁盘空间不足"
            if 'no such host' in text_block or 'network' in text_block:
                return "🌐 网络异常（No such host / Network unreachable）"

            # 找不到明确原因，返回最后几行
            for line in reversed(last_lines):
                line = line.strip()
                if line and len(line) > 10 and not line.startswith('[') and 'error' in line.lower():
                    return f"⚠️ {line[:80]}"
            return "❓ 未知原因（请查看控制台日志）"

    except Exception as e:
        return f"❓ 无法获取控制台日志: {str(e)[:50]}"

# ========== 报告生成 ==========
def build_report(jobs_data):
    jobs = jobs_data.get('jobs', [])
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []

    lines.append(f"📊 Jenkins 每日构建详细报告")
    lines.append(f"生成时间: {now_str}")
    lines.append(f"总项目数: {len(jobs)}")
    lines.append("")

    # ---- 1. 统计汇总 ----
    total_completed = 0
    total_success = 0
    total_unstable = 0
    total_failed = 0

    for job in jobs:
        lcb = job.get('lastCompletedBuild') or {}
        if isinstance(lcb, dict) and lcb.get('timestamp'):
            total_completed += 1
            r = lcb.get('result')
            if r == 'SUCCESS': total_success += 1
            elif r == 'UNSTABLE': total_unstable += 1
            elif r == 'FAILURE': total_failed += 1

    success_rate = int(total_success / total_completed * 100) if total_completed > 0 else 0
    lines.append("【📈 整体统计】")
    lines.append(f"  总构建次数: {total_completed}")
    lines.append(f"  ✅ 成功: {total_success} ({success_rate}%)")
    lines.append(f"  ⚠️ 不稳定: {total_unstable}")
    lines.append(f"  ❌ 失败: {total_failed}")
    lines.append("")

    # ---- 2. 近期失败项目（含原因分析，30天内） ----
    lines.append("【❌ 失败项目分析】（30天内失败）")
    HOUR_LIMIT = 720  # 30天
    failed_list = []
    for job in jobs:
        lcb = job.get('lastCompletedBuild') or {}
        if isinstance(lcb, dict) and lcb.get('result') == 'FAILURE':
            ts = lcb.get('timestamp', 0) / 1000
            age_h = (datetime.now().timestamp() - ts) / 3600
            if age_h < HOUR_LIMIT:
                failed_list.append({
                    'name': job['name'],
                    'number': lcb.get('number'),
                    'ts': ts,
                    'duration': (lcb.get('duration') or 0) // 1000,
                })

    if failed_list:
        # 按时间倒序
        failed_list.sort(key=lambda x: -x['ts'])
        for f in failed_list[:15]:
            ts_str = datetime.fromtimestamp(f['ts']).strftime('%m-%d %H:%M')
            dur_str = f"{f['duration']}s" if f['duration'] < 3600 else f"{f['duration']//60}m"
            lines.append(f"  ❌ {f['name']} #{f['number']} | {ts_str} | 耗时:{dur_str}")
            reason = analyze_failure_reason(f['name'], f['number'])
            lines.append(f"     🔍 原因: {reason}")
    else:
        lines.append("  无失败记录")
    lines.append("")

    # ---- 3. 近期不稳定项目（全部显示，历史遗留也追踪） ----
    lines.append("【⚠️ 不稳定项目分析】（全部不稳定项目）")
    unstable_list = []
    for job in jobs:
        lcb = job.get('lastCompletedBuild') or {}
        if isinstance(lcb, dict) and lcb.get('result') == 'UNSTABLE':
            ts = lcb.get('timestamp', 0) / 1000
            age_h = (datetime.now().timestamp() - ts) / 3600
            if age_h < 8760 * 2:  # 显示所有不稳定项目，最多2年内
                unstable_list.append({
                    'name': job['name'],
                    'number': lcb.get('number'),
                    'ts': ts,
                    'duration': (lcb.get('duration') or 0) // 1000,
                })

    if unstable_list:
        unstable_list.sort(key=lambda x: -x['ts'])
        for u in unstable_list[:15]:
            ts_str = datetime.fromtimestamp(u['ts']).strftime('%m-%d %H:%M')
            dur_str = f"{u['duration']}s" if u['duration'] < 3600 else f"{u['duration']//60}m"
            age_days = int((datetime.now().timestamp() - u['ts']) / 86400)
            age_str = f"({age_days}天前)" if age_days > 0 else ""
            lines.append(f"  ⚠️ {u['name']} #{u['number']} | {ts_str} | 耗时:{dur_str} {age_str}")
            reason = analyze_failure_reason(u['name'], u['number'])
            lines.append(f"     🔍 原因: {reason}")
    else:
        lines.append("  无不稳定记录")
    lines.append("")

    # ---- 4. 近期成功项目（48小时内） ----
    lines.append("【✅ 近期成功项目】（48小时内成功）")
    success_list = []
    for job in jobs:
        lcb = job.get('lastCompletedBuild') or {}
        if isinstance(lcb, dict) and lcb.get('result') == 'SUCCESS':
            ts = lcb.get('timestamp', 0) / 1000
            age_h = (datetime.now().timestamp() - ts) / 3600
            if age_h < 48:
                success_list.append({
                    'name': job['name'],
                    'number': lcb.get('number'),
                    'ts': ts,
                    'duration': (lcb.get('duration') or 0) // 1000,
                })

    if success_list:
        success_list.sort(key=lambda x: -x['ts'])
        for s in success_list[:20]:
            ts_str = datetime.fromtimestamp(s['ts']).strftime('%m-%d %H:%M')
            dur = s['duration']
            dur_str = f"{dur}s" if dur < 3600 else f"{dur//60}m"
            lines.append(f"  ✅ {s['name']} #{s['number']} | {ts_str} | {dur_str}")
        if len(success_list) > 20:
            lines.append(f"  ... 还有 {len(success_list)-20} 个成功项目")
    else:
        lines.append("  无成功记录")
    lines.append("")

    # ---- 5. 总结 ----
    if total_failed == 0 and total_unstable == 0:
        lines.append("🟢 全网所有项目今日构建状态正常，无失败/不稳定记录。")
    elif total_failed > 0:
        lines.append(f"⚠️ 今日有 {total_failed} 个失败项目，建议优先排查。")
    elif total_unstable > 0:
        lines.append(f"⚠️ 今日有 {total_unstable} 个不稳定项目，建议关注。")

    return "\n".join(lines)

# ========== 主程序 ==========
def main():
    report = ""
    try:
        jobs_data = get_jenkins_data()
        report = build_report(jobs_data)
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