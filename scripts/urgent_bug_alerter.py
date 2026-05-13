#!/usr/bin/env python3
"""
致命P1 Bug 紧急预警 — 每30分钟执行一次

筛选条件：严重程度=1(致命) AND 优先级=1(最高) AND 状态≠closed/resolved
按指派人分组 → 推送OpenIM
自带去重：已通知过的 (bug_id, assignee) 不再重复提醒

支持 --brief 模式：精简日志、stdout输出JSON、快速退出（供AI任务调用）
"""
import urllib.request, json, uuid, time, sys, os, traceback, copy, argparse
from collections import defaultdict
from datetime import datetime, timezone, timedelta

# ========== 配置 ==========
CONFIG = {
    "zentao_url": "http://192.168.0.28:9980",
    "zentao_account": "shidawei",
    "zentao_password": "shidawei",
    "product_id": 1,
    "openim_url": "http://192.168.0.27:10002",
    "openim_secret": "openIM123",
    "openim_admin": "imAdmin",
    "timezone_offset": 8,
    "bot_nickname": "禅道Bug助手",
    "admin_user_id": "7809497014",
    "admin_user_name": "石大卫",
    "log_file": "/root/.openclaw/workspace/logs/urgent_bug_alerter.log",
    "state_file": "/root/.openclaw/workspace/config/urgent_bug_state.json",
    "retry_times": 2,
    "retry_delay_sec": 3,
    "dedup_window_hours": 2,  # 去重窗口：2小时内不重复发送
}

TZ = timezone(timedelta(hours=CONFIG["timezone_offset"]))
DEDUP_WINDOW_SEC = CONFIG["dedup_window_hours"] * 3600

# ========== 全局开关 ==========
BRIEF_MODE = False  # 静默快速模式

# ========== 日志 ==========
def log(msg, level="INFO"):
    ts = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    if not BRIEF_MODE:
        print(line)
    log_dir = os.path.dirname(CONFIG["log_file"])
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== 去重状态管理 ==========
class NotifyState:
    """
    记录已通知的 (bug_id, assignee) 对。
    结构: { "bug_id|assignee": {"bug_id":..., "assignee":..., "notified_at":..., "notified_ts":...} }
    """
    def __init__(self):
        self.path = CONFIG["state_file"]
        self.data = {}
        self._load()

    def _load(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    log(f"已加载去重状态: {len(self.data)}条记录")
            except Exception as e:
                log(f"加载状态文件失败(将重建): {e}", "WARN")
                self.data = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        log(f"去重状态已保存: {len(self.data)}条记录")

    def is_notified(self, bug_id, assignee):
        """检查是否在去重窗口内已通知过该(bug, 指派人)对"""
        key = f"{bug_id}|{assignee}"
        if key not in self.data:
            return False
        
        # 检查是否在去重窗口内（2小时）
        notified_ts = self.data[key].get("notified_ts", 0)
        now_ts = int(time.time())
        
        if now_ts - notified_ts < DEDUP_WINDOW_SEC:
            # 在窗口期内，已通知过
            return True
        
        # 窗口期已过，视为未通知（并清理过期记录）
        del self.data[key]
        self._save()
        return False

    def mark_notified(self, bug_id, assignee):
        """标记为已通知并持久化"""
        key = f"{bug_id}|{assignee}"
        self.data[key] = {
            "bug_id": bug_id,
            "assignee": assignee,
            "notified_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "notified_ts": int(time.time())
        }
        self._save()

    def cleanup(self, current_bug_assignee_pairs):
        """
        清理无效记录：
        - 当前过滤条件已不匹配的bug（已关闭/已解决/status已变）
        - 指派人已变更的
        - 超出去重窗口期的记录（可选，主要依赖is_notified内自动清理）
        """
        now_ts = int(time.time())
        current_keys = {f"{bid}|{asgn}" for bid, asgn in current_bug_assignee_pairs}
        before = len(self.data)
        self.data = {
            k: v for k, v in self.data.items()
            if k in current_keys and (now_ts - v.get("notified_ts", 0)) < DEDUP_WINDOW_SEC
        }
        after = len(self.data)
        if before != after:
            log(f"去重状态清理: {before}→{after}条（移除{before-after}条过期记录）")
            self._save()


# ========== ZenTao API ==========
class ZenTao:
    def __init__(self):
        self.base = CONFIG["zentao_url"]
        self.token = None

    def get_token(self):
        req = urllib.request.Request(
            f"{self.base}/api.php/v1/tokens",
            data=json.dumps({"account": CONFIG["zentao_account"], "password": CONFIG["zentao_password"]}).encode(),
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        self.token = data.get("token", "")
        if not self.token:
            raise RuntimeError("获取ZenTao Token失败")

    def _get(self, path):
        headers = {"Token": self.token}
        req = urllib.request.Request(f"{self.base}{path}", headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())

    def get_critical_bugs(self):
        """获取严重程度=1 AND 优先级=1 AND 未关闭/未解决 的Bug"""
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

        # 筛选：severity=1, pri=1, status not closed/resolved
        filtered = [
            b for b in all_bugs
            if b.get("severity") == 1
            and b.get("pri") == 1
            and b.get("status") not in ("closed", "resolved")
        ]
        log(f"获取Bug总数: {len(all_bugs)}, 致命P1未关闭: {len(filtered)}")
        return filtered

    @staticmethod
    def get_assignee_name(bug):
        """获取指派人的真实姓名"""
        a = bug.get("assignedTo")
        if isinstance(a, dict):
            return a.get("realname", str(a.get("id", "")))
        return str(a) if a else None

    @staticmethod
    def get_module_name(bug):
        """获取模块名称"""
        m = bug.get("module")
        if isinstance(m, dict):
            return m.get("name", str(m.get("id", "")))
        return str(m) if m else "-"


# ========== OpenIM API ==========
class OpenIM:
    def __init__(self):
        self.base = CONFIG["openim_url"]
        self.token = None
        self.user_map = {}

    def get_token(self):
        op_id = str(uuid.uuid4())
        req = urllib.request.Request(
            f"{self.base}/auth/user_token",
            data=json.dumps({"secret": CONFIG["openim_secret"], "userID": CONFIG["openim_admin"], "platformID": 1}).encode(),
            headers={"Content-Type": "application/json", "operationID": op_id}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        self.token = data.get("data", {}).get("token", "")
        if not self.token:
            raise RuntimeError("获取OpenIM Token失败")

    def load_users(self):
        op_id = str(uuid.uuid4())
        req = urllib.request.Request(
            f"{self.base}/user/get_users",
            data=json.dumps({"pagination": {"pageNumber": 1, "showNumber": 10000}}).encode(),
            headers={"token": self.token, "operationID": op_id, "Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        users = json.loads(resp.read()).get("data", {}).get("users", [])
        self.user_map = {}
        for u in users:
            nick = u.get("nickname", "").strip()
            if nick:
                self.user_map[nick] = u.get("userID", "")

    def send(self, recv_id, content, title="🔴 致命 P1 Bug 紧急预警"):
        """发送文本消息，自动重试"""
        last_err = None
        for attempt in range(1, CONFIG["retry_times"] + 2):
            try:
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
                    headers={"token": self.token, "operationID": op_id, "Content-Type": "application/json"}
                )
                resp = urllib.request.urlopen(req, timeout=15)
                result = json.loads(resp.read())
                ok = result.get("errCode") == 0
                if ok:
                    msg_id = result.get("data", {}).get("serverMsgID", "")
                    return True, msg_id
                log(f"发送API返回异常(errCode={result.get('errCode')}), 重试第{attempt}次", "WARN")
                last_err = f"errCode={result.get('errCode')}"
            except Exception as e:
                last_err = str(e)
                log(f"发送异常: {e}, 重试第{attempt}次", "WARN")
                if attempt <= CONFIG["retry_times"]:
                    time.sleep(CONFIG["retry_delay_sec"])
        return False, last_err


# ========== 消息格式化 ==========
STATUS_LABEL = {"active": "未解决", "resolved": "已解决", "closed": "已关闭"}

def build_alert_message(assignee_name, bugs, zentao_base):
    """构建紧急预警消息"""
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    total = len(bugs)
    sorted_bugs = sorted(bugs, key=lambda x: x.get("id"))

    lines = [
        f"🔴 致命 P1 Bug 紧急预警",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"⏰ {now}",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"{assignee_name}，您当前有 {total} 个致命P1级Bug待处理！",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"📋 详细清单：",
    ]

    for idx, b in enumerate(sorted_bugs, 1):
        bid = b["id"]
        title = (b.get("title") or "").strip()
        if len(title) > 60:
            title = title[:58] + "…"
        module = b.get("moduleName", "-")
        created = b.get("openedDate", "-")[:16] if b.get("openedDate") else "-"
        status = STATUS_LABEL.get(b.get("status"), b.get("status", "?"))

        lines.append(f"  #{idx} #{bid} {title}")
        lines.append(f"     📂 {module}  |  🕐 {created}")
        lines.append(f"     📌 状态: {status}")
        lines.append(f"     🔗 {zentao_base}/bug-view-{bid}.html")

    lines.append("")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 合计: {total} 个致命P1 Bug")
    lines.append(f"📋 全部: {zentao_base}/bug-browse-{CONFIG['product_id']}.html")
    lines.append("")
    lines.append("⚠️ 请优先处理! 如有疑问请及时沟通。")

    return "\n".join(lines)


# ========== 主流程 ==========
def main(args=None):
    global BRIEF_MODE
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", action="store_true", help="精简模式：最小化日志、输出JSON、快速退出")
    parsed, _ = parser.parse_known_args(args or [])
    BRIEF_MODE = parsed.brief

    log("=" * 60)
    log("致命P1 Bug紧急预警任务开始")

    result = {
        "ok": True,
        "total_bugs": 0,
        "total_assignees": 0,
        "sent_ok": 0,
        "sent_skip": 0,
        "sent_fail": 0,
        "missing_users": [],
        "error": None,
    }

    # 1. ZenTao
    try:
        zt = ZenTao()
        zt.get_token()
        log("ZenTao Token获取成功")
    except Exception as e:
        log(f"ZenTao认证失败: {e}", "ERROR")
        result["ok"] = False
        result["error"] = f"ZenTao认证失败: {e}"
        return result

    # 2. 获取致命P1 Bug
    try:
        bugs = zt.get_critical_bugs()
    except Exception as e:
        log(f"获取Bug失败: {e}", "ERROR")
        result["ok"] = False
        result["error"] = f"获取Bug失败: {e}"
        return result

    result["total_bugs"] = len(bugs)
    if not bugs:
        log("当前无致命P1 Bug，任务完成 ✅")
        if BRIEF_MODE:
            print(json.dumps(result, ensure_ascii=False))
        return result

    # 3. 按指派人分组
    grouped = defaultdict(list)
    current_pairs = []
    unassigned = 0
    for b in bugs:
        name = zt.get_assignee_name(b)
        if name:
            assignee = name
        else:
            assignee = "(未指派)"
        grouped[assignee].append(b)
        current_pairs.append((b["id"], assignee))
        if assignee == "(未指派)":
            unassigned += 1

    result["total_assignees"] = sum(1 for n in grouped if n != '(未指派)')
    for name, bug_list in sorted(grouped.items()):
        log(f"  👤 {name}: {len(bug_list)}个Bug")
        if name == "(未指派)":
            log(f"     ↪️ 跳过推送（未指派）")

    # 4. 加载去重状态
    state = NotifyState()

    # 5. OpenIM认证
    try:
        im = OpenIM()
        im.get_token()
        im.load_users()
        log("OpenIM初始化完成")
    except Exception as e:
        log(f"OpenIM初始化失败: {e}", "ERROR")
        result["ok"] = False
        result["error"] = f"OpenIM初始化失败: {e}"
        return result

    # 6. 逐个推送（只推新Bug）
    sent_ok = 0
    sent_skip = 0
    sent_fail = 0
    missing_users = set()
    newly_notified_pairs = set()
    zentao_base = CONFIG["zentao_url"]

    for assignee_name in sorted(grouped.keys()):
        if assignee_name == "(未指派)":
            continue

        assignee_bugs = grouped[assignee_name]
        im_id = im.user_map.get(assignee_name)

        if not im_id:
            missing_users.add(assignee_name)
            log(f"⏭️ {assignee_name} 未注册OpenIM，跳过", "WARN")
            continue

        # 筛选出该人尚未被通知的Bug（去重）
        new_bugs = []
        already_notified = 0
        for b in assignee_bugs:
            if not state.is_notified(b["id"], assignee_name):
                new_bugs.append(b)
            else:
                already_notified += 1

        if not new_bugs:
            sent_skip += 1
            log(f"⏭️ {assignee_name}: {already_notified}个已通知过，无新Bug跳过")
            continue

        if already_notified:
            log(f"🔁 {assignee_name}: {len(assignee_bugs)}个中{len(new_bugs)}个新增, {already_notified}个已通知过")

        # 补充模块名称
        for b in new_bugs:
            b["moduleName"] = zt.get_module_name(b)

        # 构建消息
        try:
            content = build_alert_message(assignee_name, new_bugs, zentao_base)
        except Exception as e:
            log(f"构建消息失败({assignee_name}): {e}", "ERROR")
            sent_fail += 1
            continue

        # 发送
        ok, result_send = im.send(im_id, content, f"🔴 致命P1 Bug紧急预警 - {len(new_bugs)}个")
        if ok:
            sent_ok += 1
            for b in new_bugs:
                state.mark_notified(b["id"], assignee_name)
                newly_notified_pairs.add((b["id"], assignee_name))
            log(f"✅ {assignee_name}(新增{len(new_bugs)}个Bug) → 发送成功")
        else:
            sent_fail += 1
            log(f"❌ {assignee_name} → 发送失败: {result_send}", "ERROR")

    # 7. 清理过期状态
    try:
        state.cleanup(current_pairs)
    except Exception as e:
        log(f"去重状态清理异常: {e}", "WARN")

    # 8. 汇总
    result["sent_ok"] = sent_ok
    result["sent_skip"] = sent_skip
    result["sent_fail"] = sent_fail
    result["missing_users"] = sorted(missing_users)

    log(f"📊 执行汇总: 致命P1 Bug={len(bugs)}, 推送成功={sent_ok}, 跳过={sent_skip}, 失败={sent_fail}")
    if missing_users:
        log(f"⚠️ 未注册OpenIM: {', '.join(sorted(missing_users))}")

    # 通知管理员有人员缺失
    if missing_users:
        try:
            admin_id = im.user_map.get(CONFIG["admin_user_name"], CONFIG["admin_user_id"])
            admin_msg = (
                f"【致命P1预警 - 人员缺失通知】\n\n"
                f"以下 {len(missing_users)} 人被指派了致命P1 Bug但未在OpenIM注册，\n"
                f"紧急预警无法送达：\n\n"
                + "\n".join(f"  • {name}" for name in sorted(missing_users))
                + "\n\n📌 请尽快通知相关人员注册OpenIM。"
            )
            im.send(admin_id, admin_msg, "致命P1预警 - 人员缺失")
            log("✅ 已通知管理员缺失人员")
        except Exception as e:
            log(f"⚠️ 通知管理员失败: {e}", "WARN")

    log(f"任务完成 {'✅' if sent_fail == 0 else '⚠️ 部分失败'}")
    log("=" * 60)

    if BRIEF_MODE:
        print(json.dumps(result, ensure_ascii=False))

    return result


if __name__ == "__main__":
    try:
        result = main()
        ok = result.get("ok", False) if isinstance(result, dict) else result
        sys.exit(0 if ok else 1)
    except Exception as e:
        log(f"未捕获的异常: {e}\n{traceback.format_exc()}", "FATAL")
        sys.exit(1)
