#!/usr/bin/env python3
"""
每日10:00/17:00 禅道激活Bug推送脚本
- 从禅道拉取所有激活Bug
- 按指派人分组
- 通过OpenIM发送给对应人员（含每条例的独立跳转链接）
"""
import urllib.request, json, uuid, time, sys
from collections import defaultdict

# ========== 配置 ==========
ZENTAO_URL = "http://192.168.0.28:9980"
OPENIM_URL = "http://192.168.0.27:10002"
ZT_ACCOUNT = "shidawei"
ZT_PASSWORD = "shidawei"
IM_SECRET = "openIM123"
IM_ADMIN = "imAdmin"
PRODUCT_ID = 1  # 数字乡村v1.1

# ========== ZenTao API ==========
def get_zentao_token():
    req = urllib.request.Request(
        f"{ZENTAO_URL}/api.php/v1/tokens",
        data=json.dumps({"account": ZT_ACCOUNT, "password": ZT_PASSWORD}).encode(),
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read()).get("token", "")

def get_active_bugs(token):
    """获取所有激活Bug"""
    all_bugs = []
    page = 1
    while True:
        req = urllib.request.Request(
            f"{ZENTAO_URL}/api.php/v1/products/{PRODUCT_ID}/bugs?page={page}&limit=100",
            headers={"Token": token}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        bugs = data.get("bugs", [])
        if not bugs:
            break
        all_bugs.extend(bugs)
        page += 1
        if len(bugs) < 100:
            break
    # 只保留激活状态
    return [b for b in all_bugs if b.get("status") == "active"]

def get_assignee_name(bug):
    """获取指派人的真实姓名"""
    a = bug.get("assignedTo")
    if isinstance(a, dict):
        return a.get("realname", str(a.get("id", "")))
    return str(a) if a else None

# ========== OpenIM API ==========
def get_openim_token():
    op_id = str(uuid.uuid4())
    req = urllib.request.Request(
        f"{OPENIM_URL}/auth/user_token",
        data=json.dumps({"secret": IM_SECRET, "userID": IM_ADMIN, "platformID": 1}).encode(),
        headers={"Content-Type": "application/json", "operationID": op_id}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read()).get("data", {}).get("token", "")

def get_openim_users(im_token):
    """获取OpenIM所有用户，建立 nickname→userID 映射"""
    op_id = str(uuid.uuid4())
    req = urllib.request.Request(
        f"{OPENIM_URL}/user/get_users",
        data=json.dumps({"pagination": {"pageNumber": 1, "showNumber": 10000}}).encode(),
        headers={"token": im_token, "operationID": op_id, "Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=15)
    users = json.loads(resp.read()).get("data", {}).get("users", [])
    mapping = {}
    for u in users:
        nick = u.get("nickname", "").strip()
        if nick:
            mapping[nick] = u.get("userID", "")
    return mapping

def send_im_message(im_token, recv_id, content, title="禅道Bug提醒"):
    """发送消息到指定用户"""
    op_id = str(uuid.uuid4())
    timestamp = int(time.time() * 1000)
    payload = {
        "sendID": IM_ADMIN,
        "recvID": recv_id,
        "groupID": "",
        "senderNickname": "禅道智能助手",
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
        f"{OPENIM_URL}/msg/send_msg",
        data=json.dumps(payload).encode(),
        headers={"token": im_token, "operationID": op_id, "Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    return result.get("errCode") == 0, result.get("data", {}).get("serverMsgID", "")

def get_severity_label(s):
    return {1: "致命", 2: "严重", 3: "一般", 4: "轻微"}.get(s, "未知")

# ========== 主流程 ==========
def main():
    print(f"[{time.strftime('%Y-%m-%d %H:%M')}] 开始执行Bug推送...")
    
    # 1. 获取Token
    try:
        zt_token = get_zentao_token()
        print(f"  ✅ ZenTao Token获取成功")
    except Exception as e:
        print(f"  ❌ ZenTao认证失败: {e}")
        return False
    
    try:
        im_token = get_openim_token()
        print(f"  ✅ OpenIM Token获取成功")
    except Exception as e:
        print(f"  ❌ OpenIM认证失败: {e}")
        return False
    
    # 2. 获取激活Bug
    try:
        bugs = get_active_bugs(zt_token)
        print(f"  ✅ 获取激活Bug: {len(bugs)}个")
    except Exception as e:
        print(f"  ❌ 获取Bug失败: {e}")
        return False
    
    if not bugs:
        print("  ℹ️ 没有激活Bug，任务完成")
        return True
    
    # 3. 获取用户映射
    try:
        user_map = get_openim_users(im_token)
        print(f"  ✅ OpenIM用户映射: {len(user_map)}人")
    except Exception as e:
        print(f"  ❌ 获取OpenIM用户失败: {e}")
        return False
    
    # 4. 按指派人分组
    grouped = defaultdict(list)
    for b in bugs:
        name = get_assignee_name(b)
        if name and name != "未指派":
            grouped[name].append(b)
        else:
            grouped["(未指派)"].append(b)
    
    print(f"  👥 涉及 {len(grouped)} 人")
    
    # 5. 发送消息
    sent_count = 0
    fail_count = 0
    ignored = 0
    missing_im_users = set()
    
    for person_name, person_bugs in sorted(grouped.items()):
        if person_name == "(未指派)":
            ignored += len(person_bugs)
            print(f"  ⏭️ (未指派) × {len(person_bugs)}个，跳过")
            continue
        
        im_id = user_map.get(person_name)
        if not im_id:
            ignored += len(person_bugs)
            missing_im_users.add(person_name)
            print(f"  ⏭️ {person_name} 未注册OpenIM，跳过{len(person_bugs)}个Bug")
            continue
        
        # 按优先级排序
        person_bugs.sort(key=lambda x: (x.get("pri", 99), x.get("id")))
        
        # 统计
        p1 = sum(1 for b in person_bugs if b.get("pri") == 1)
        p2 = sum(1 for b in person_bugs if b.get("pri") == 2)
        s1 = sum(1 for b in person_bugs if b.get("severity") == 1)
        s2 = sum(1 for b in person_bugs if b.get("severity") == 2)
        
        # 构建消息
        lines = [f"【今日Bug提醒】🔔",
                 f"\n⏰ {time.strftime('%Y-%m-%d %H:%M')}",
                 f"━━━━━━━━━━━━━━━━",
                 f"{person_name}，您有 {len(person_bugs)} 个激活Bug待处理：",
                 f"━━━━━━━━━━━━━━━━"]
        
        if p1: lines.append(f"⚠️ P1紧急: {p1}个")
        if p2: lines.append(f"⚡ P2高优: {p2}个")
        if s1: lines.append(f"🔴 致命: {s1}个")
        if s2: lines.append(f"🟠 严重: {s2}个")
        lines.append("")
        
        for b in person_bugs:
            bid = b["id"]
            bp = b.get("pri", "?")
            sev = get_severity_label(b.get("severity"))
            title = b["title"][:45]
            bug_url = f"{ZENTAO_URL}/bug-view-{bid}.html"
            lines.append(f"  #{bid} P{bp}({sev}) {title}")
            lines.append(f"  🔗 {bug_url}")
        
        if len(person_bugs) > 20:
            more = len(person_bugs) - 20
            lines.append(f"\n  ... 还有 {more} 个Bug，仅显示前20个")
        
        lines.append(f"\n━━━━━━━━━━━━━━━━")
        lines.append(f"📋 全部Bug列表: {ZENTAO_URL}/bug-browse-{PRODUCT_ID}.html")
        
        content = "\n".join(lines)
        
        # 发送
        ok, msg_id = send_im_message(im_token, im_id, content, f"Bug提醒 - {len(person_bugs)}个待处理")
        if ok:
            sent_count += 1
            print(f"  ✅ {person_name}({len(person_bugs)}个Bug) 发送成功")
        else:
            fail_count += 1
            print(f"  ❌ {person_name} 发送失败")
    
    # 6. 汇总
    print(f"\n📊 执行完成:")
    print(f"  推送人数: {sent_count}")
    print(f"  推送失败: {fail_count}")
    print(f"  跳过未注册: {ignored}个Bug")
    if missing_im_users:
        print(f"  未注册OpenIM的人员: {', '.join(sorted(missing_im_users))}")
    print(f"  总处理: {len(bugs)}个Bug")
    
    # 如果有未注册的，额外发一条给管理员
    if missing_im_users:
        try:
            admin_id = user_map.get("石大卫", "7809497014")
            admin_msg = (
                f"【禅道推送 - 人员缺失通知】\n\n"
                f"以下 {len(missing_im_users)} 人在禅道有Bug指派但未在OpenIM注册，\n"
                f"每日Bug提醒无法送达：\n\n"
                + "\n".join(f"  • {name}" for name in sorted(missing_im_users))
                + "\n\n请通知相关人员注册OpenIM。"
            )
            send_im_message(im_token, admin_id, admin_msg, "禅道推送 - 人员缺失")
            print(f"  ✅ 已通知管理员缺失人员")
        except Exception as e:
            print(f"  ⚠️ 通知管理员失败: {e}")
    
    return fail_count == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
