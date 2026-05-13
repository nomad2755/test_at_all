#!/usr/bin/env python3
"""
每日09:30 禅道Bug按创建人分组推送脚本
- 查询所有未关闭/未解决Bug（status != closed/resolved）
- 按Bug创建人（openedBy）分组
- 通过OpenIM一对一推送个人Bug清单
- 含日志、异常捕获、配置项预留
"""
import urllib.request
import json
import uuid
import time
import sys
import os
import traceback
from collections import defaultdict
from datetime import datetime, timezone, timedelta

# ========== 配置区（按需调整） ==========
CONFIG = {
    # ZenTao 配置
    "zentao_url": "http://192.168.0.28:9980",
    "zentao_account": "shidawei",
    "zentao_password": "shidawei",
    "product_id": 1,                     # 数字乡村v1.1

    # OpenIM 配置
    "openim_url": "http://192.168.0.27:10002",
    "openim_secret": "openIM123",
    "openim_admin": "imAdmin",

    # 推送配置
    "timezone_offset": 8,                # 北京时间 +8
    "bot_nickname": "禅道Bug助手",
    "max_bugs_per_msg": 20,              # 单条消息最多显示多少个Bug
    "admin_user_id": "7809497014",       # 管理员（石大卫）
    "admin_user_name": "石大卫",

    # 日志
    "log_file": "/root/.openclaw/workspace/logs/creator_bug_report.log",
}

# 时区
TZ = timezone(timedelta(hours=CONFIG["timezone_offset"]))


# ========== 日志 ==========
def log(msg, level="INFO"):
    ts = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_dir = os.path.dirname(CONFIG["log_file"])
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ========== ZenTao API ==========
class ZenTao:
    def __init__(self):
        self.base = CONFIG["zentao_url"]
        self.token = None

    def get_token(self):
        """获取/刷新ZenTao Token"""
        req = urllib.request.Request(
            f"{self.base}/api.php/v1/tokens",
            data=json.dumps({
                "account": CONFIG["zentao_account"],
                "password": CONFIG["zentao_password"]
            }).encode(),
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        self.token = data.get("token", "")
        if not self.token:
            raise RuntimeError("获取ZenTao Token失败")
        return self.token

    def _get(self, path):
        """GET请求，自动刷新Token"""
        headers = {"Token": self.token}
        req = urllib.request.Request(f"{self.base}{path}", headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())

    def get_active_bugs(self):
        """获取所有未关闭/未解决的Bug（status != closed/resolved）"""
        all_bugs = []
        page = 1
        while True:
            data = self._get(
                f"/api.php/v1/products/{CONFIG['product_id']}/bugs"
                f"?page={page}&limit=100"
            )
            bugs = data.get("bugs", [])
            if not bugs:
                break
            all_bugs.extend(bugs)
            page += 1
            if len(bugs) < 100:
                break

        # 筛选：未关闭 且 未解决
        filtered = [
            b for b in all_bugs
            if b.get("status") not in ("closed", "resolved")
        ]
        log(f"获取Bug总数: {len(all_bugs)}, 未关闭/未解决: {len(filtered)}")
        return filtered

    @staticmethod
    def get_creator_name(bug):
        """获取Bug创建人的真实姓名"""
        opened = bug.get("openedBy")
        if isinstance(opened, dict):
            return opened.get("realname", str(opened.get("id", "")))
        return str(opened) if opened else None


# ========== OpenIM API ==========
class OpenIM:
    def __init__(self):
        self.base = CONFIG["openim_url"]
        self.token = None
        self.user_map = {}  # nickname → userID

    def get_token(self):
        """获取OpenIM Token"""
        op_id = str(uuid.uuid4())
        req = urllib.request.Request(
            f"{self.base}/auth/user_token",
            data=json.dumps({
                "secret": CONFIG["openim_secret"],
                "userID": CONFIG["openim_admin"],
                "platformID": 1
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "operationID": op_id
            }
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        self.token = data.get("data", {}).get("token", "")
        if not self.token:
            raise RuntimeError("获取OpenIM Token失败")
        return self.token

    def load_users(self):
        """加载OpenIM所有用户，建立 nickname → userID 映射"""
        op_id = str(uuid.uuid4())
        req = urllib.request.Request(
            f"{self.base}/user/get_users",
            data=json.dumps({
                "pagination": {"pageNumber": 1, "showNumber": 10000}
            }).encode(),
            headers={
                "token": self.token,
                "operationID": op_id,
                "Content-Type": "application/json"
            }
        )
        resp = urllib.request.urlopen(req, timeout=15)
        users = json.loads(resp.read()).get("data", {}).get("users", [])
        self.user_map = {}
        for u in users:
            nick = u.get("nickname", "").strip()
            if nick:
                self.user_map[nick] = u.get("userID", "")
        log(f"OpenIM用户映射加载: {len(self.user_map)}人")
        return self.user_map

    def send(self, recv_id, content, title="Bug待处理提醒"):
        """发送文本消息到指定用户"""
        op_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        payload = {
            "sendID": CONFIG["openim_admin"],
            "recvID": recv_id,
            "groupID": "",
            "senderNickname": CONFIG["bot_nickname"],
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
            headers={
                "token": self.token,
                "operationID": op_id,
                "Content-Type": "application/json"
            }
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        ok = result.get("errCode") == 0
        msg_id = result.get("data", {}).get("serverMsgID", "")
        return ok, msg_id


# ========== 消息格式化 ==========
STATUS_LABEL = {
    "active": "未解决",
    "resolved": "已解决",
    "closed": "已关闭",
    "delayed": "延期",
    "postponed": "搁置",
}

SEVERITY_LABEL = {
    1: "致命",
    2: "严重",
    3: "一般",
    4: "轻微",
}

PRI_LABEL = {
    1: "P1-紧急",
    2: "P2-高优",
    3: "P3-普通",
}


def format_bug_message(creator_name, bugs, zentao_base):
    """
    构建发送给单个创建人的消息文本。
    bugs: 该创建人名下的所有未关闭/未解决Bug列表
    """
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    total = len(bugs)
    max_show = CONFIG["max_bugs_per_msg"]

    # 统计
    severity_count = defaultdict(int)
    pri_count = defaultdict(int)
    for b in bugs:
        severity_count[b.get("severity", 0)] += 1
        pri_count[b.get("pri", 99)] += 1

    # 按优先级排序
    sorted_bugs = sorted(bugs, key=lambda x: (x.get("pri", 99), x.get("id")))

    lines = [
        f"【Bug处理提醒】🎯",
        f"⏰ {now}",
        f"━━━━━━━━━━━━━━━━━━━",
        f"{creator_name}，您创建了 {total} 个Bug待处理：",
        f"━━━━━━━━━━━━━━━━━━━",
    ]

    # 统计摘要
    summary_parts = []
    for sev in [1, 2]:
        if severity_count[sev]:
            summary_parts.append(f"🔴{SEVERITY_LABEL[sev]}:{severity_count[sev]}")
    if severity_count[3]:
        summary_parts.append(f"🟡一般:{severity_count[3]}")
    if summary_parts:
        lines.append(f"  严重程度: {' '.join(summary_parts)}")

    sum2_parts = []
    for p in [1, 2]:
        if pri_count[p]:
            sum2_parts.append(f"⚡{PRI_LABEL[p]}:{pri_count[p]}")
    if sum2_parts:
        lines.append(f"  优先级: {' '.join(sum2_parts)}")
    lines.append("")

    # Bug清单
    for idx, b in enumerate(sorted_bugs[:max_show], 1):
        bid = b["id"]
        status = STATUS_LABEL.get(b.get("status"), b.get("status", "未知"))
        sev = SEVERITY_LABEL.get(b.get("severity"), "?")
        pri = b.get("pri", "?")
        title = b.get("title", "").strip()
        if len(title) > 50:
            title = title[:48] + "…"

        lines.append(f"  #{idx} #{bid} [{status}]")
        lines.append(f"     {title}")
        lines.append(f"     P{pri} | {sev}级")
        lines.append(f"     🔗 {zentao_base}/bug-view-{bid}.html")
        lines.append("")

    if total > max_show:
        lines.append(f"  … 还有 {total - max_show} 个Bug未显示")

    lines.append(f"━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📋 全部Bug列表: {zentao_base}/bug-browse-{CONFIG['product_id']}.html")
    lines.append(f"\n💡 请尽快处理，谢谢。")

    return "\n".join(lines)


# ========== 主流程 ==========
def main():
    log("=" * 60)
    log("每日按创建人分组Bug推送任务开始")

    # 1. ZenTao认证
    try:
        zt = ZenTao()
        zt.get_token()
        log("ZenTao Token获取成功")
    except Exception as e:
        log(f"ZenTao认证失败: {e}\n{traceback.format_exc()}", "ERROR")
        return False

    # 2. 获取Bug数据
    try:
        bugs = zt.get_active_bugs()
    except Exception as e:
        log(f"获取Bug失败: {e}\n{traceback.format_exc()}", "ERROR")
        return False

    if not bugs:
        log("没有未关闭/未解决的Bug，任务完成 ✅")
        return True

    # 3. 按创建人分组
    grouped = defaultdict(list)
    no_creator = []
    for b in bugs:
        name = zt.get_creator_name(b)
        if name:
            grouped[name].append(b)
        else:
            no_creator.append(b)

    if no_creator:
        log(f"无创建人信息的Bug: {len(no_creator)}个，跳过")

    log(f"涉及创建人数: {len(grouped)}人")
    for name, bug_list in sorted(grouped.items()):
        log(f"  👤 {name}: {len(bug_list)}个Bug")

    # 4. OpenIM认证 & 加载用户
    try:
        im = OpenIM()
        im.get_token()
        log("OpenIM Token获取成功")
        im.load_users()
    except Exception as e:
        log(f"OpenIM初始化失败: {e}\n{traceback.format_exc()}", "ERROR")
        return False

    # 5. 逐个推送
    sent_ok = 0
    sent_fail = 0
    skipped_bugs = 0
    missing_users = set()

    zentao_base = CONFIG["zentao_url"]

    for creator_name in sorted(grouped.keys()):
        creator_bugs = grouped[creator_name]
        im_id = im.user_map.get(creator_name)

        if not im_id:
            skipped_bugs += len(creator_bugs)
            missing_users.add(creator_name)
            log(f"⏭️ {creator_name} 未注册OpenIM，跳过{len(creator_bugs)}个Bug", "WARN")
            continue

        # 构建消息
        try:
            content = format_bug_message(creator_name, creator_bugs, zentao_base)
        except Exception as e:
            log(f"构建消息失败({creator_name}): {e}", "ERROR")
            sent_fail += 1
            continue

        # 发送
        try:
            ok, msg_id = im.send(im_id, content, f"Bug待处理 - {len(creator_bugs)}个")
            if ok:
                sent_ok += 1
                log(f"✅ {creator_name}({len(creator_bugs)}个Bug) → 发送成功 msgId={msg_id[:16]}…")
            else:
                sent_fail += 1
                log(f"❌ {creator_name} → 发送失败（API返回错误）", "ERROR")
        except Exception as e:
            sent_fail += 1
            log(f"❌ {creator_name} → 发送异常: {e}", "ERROR")

    # 6. 汇总
    log("─" * 40)
    log(f"📊 执行汇总:")
    log(f"   未关闭/未解决Bug总数: {len(bugs)}个")
    log(f"   涉及创建人数: {len(grouped)}人")
    log(f"   推送成功: {sent_ok}人")
    log(f"   推送失败: {sent_fail}人")
    log(f"   跳过(未注册IM): {skipped_bugs}个Bug / {len(missing_users)}人")

    if missing_users:
        log(f"   未注册OpenIM的人员: {', '.join(sorted(missing_users))}")

    # 通知管理员有人员缺失
    if missing_users:
        try:
            admin_id = im.user_map.get(CONFIG["admin_user_name"], CONFIG["admin_user_id"])
            admin_msg = (
                f"【禅道推送 - 人员缺失通知】\n\n"
                f"以下 {len(missing_users)} 人有创建Bug但未在OpenIM注册，\n"
                f"每日Bug提醒无法送达：\n\n"
                + "\n".join(f"  • {name}" for name in sorted(missing_users))
                + "\n\n📌 请通知相关人员注册OpenIM。"
            )
            im.send(admin_id, admin_msg, "禅道推送 - 人员缺失")
            log("✅ 已通知管理员缺失人员")
        except Exception as e:
            log(f"⚠️ 通知管理员失败: {e}", "WARN")

    log(f"任务完成 {'✅' if sent_fail == 0 else '⚠️ 部分失败'}")
    log("=" * 60)
    return sent_fail == 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        log(f"未捕获的异常: {e}\n{traceback.format_exc()}", "FATAL")
        sys.exit(1)
