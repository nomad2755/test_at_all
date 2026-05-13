#!/usr/bin/env python3
"""
create_bug.py - ZenTao Bug 创建工具（支持按模块）

用法:
    python3 create_bug.py <title> <actual_result> [severity] [pri] [module_id]
    python3 create_bug.py "【个人数字空间】分享链接打不开" "点击后无反应" 3 2 295
    python3 create_bug.py "【碳汇】碳汇计算结果错误" "计算值与预期不符" 2 1 163

severity: 1致命 / 2严重 / 3一般 / 4轻微 / 5建议
pri:     1紧急 / 2高 / 3中 / 4低
"""

import json
import sys
import os
import urllib.request

ZENTAO_URL = "http://192.168.0.28:9980"
ACCOUNT = "shidawei"
PASSWORD = "shidawei"
PRODUCT_ID = 1


# ─── 模块名称缓存 ───────────────────────────────────────────
def _load_modules():
    """懒加载 module_id -> 模块名称 映射"""
    path = "/root/.openclaw/workspace/skills/zentao-integration/docs/数字乡村模块树.md"
    if not os.path.exists(path):
        return {}
    m = {}
    with open(path) as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 3 and parts[1].strip().isdigit():
                m[parts[1].strip()] = parts[2].strip()
    return m


# ─── Token ──────────────────────────────────────────────────
def get_token():
    req = urllib.request.Request(
        f"{ZENTAO_URL}/api.php/v1/tokens",
        data=json.dumps({"account": ACCOUNT, "password": PASSWORD}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["token"]


# ─── Bug 创建 ──────────────────────────────────────────────
def create_bug(title, steps_html, severity=3, pri=3, bug_type="codeerror",
               assignedTo=None, module=None):
    """
    创建 Bug

    module: module_id（数字），直接传 API 所需值
            如果传字符串，会自动查找对应 ID
    """
    token = get_token()
    payload = {
        "product": PRODUCT_ID,
        "title": title,
        "steps": steps_html,
        "severity": severity,
        "pri": pri,
        "type": bug_type,
        "openedBuild": "trunk"
    }
    if assignedTo:
        payload["assignedTo"] = assignedTo

    # module 处理：支持数字 ID 或名称字符串
    if module is not None:
        mod_str = str(module)
        # 如果是数字字符串，直接用
        if mod_str.isdigit():
            payload["module"] = int(mod_str)
        else:
            # 尝试按名称查找
            id_map = _load_modules()
            for mid, name in id_map.items():
                if name == module:
                    payload["module"] = int(mid)
                    break

    req = urllib.request.Request(
        f"{ZENTAO_URL}/api.php/v1/bugs",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Token": token,
            "Zentao-Version": "22.4"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


# ─── HTML 模板 ──────────────────────────────────────────────
def build_steps_html(env_url="", browser="", app_version="",
                     username="", password="",
                     precondition="",
                     steps=None, expected=None, actual="",
                     screenshot="暂无"):
    """构建标准模板 HTML"""
    steps = steps or []
    expected = expected or []

    def li(text): return f"<p>{text}</p>"

    html = "<p>【环境】</p>"
    html += f"<p>- 测试地址：{env_url}</p>"
    html += f"<p>- 浏览器：{browser}</p>"
    html += f"<p>- APP版本：{app_version}</p>"

    html += "<p>【账号密码】</p>"
    html += f"<p>- 用户名：{username}</p>"
    html += f"<p>- 密码：{password}</p>"

    html += "<p>【前置条件】</p>"
    html += li(precondition)

    html += "<p>【操作步骤】</p>"
    for i, s in enumerate(steps, 1):
        html += li(f"{i}. {s}")

    html += "<p>【期望结果】</p>"
    for i, e in enumerate(expected, 1):
        html += li(f"{i}. {e}")

    html += "<p>【实际结果】</p>"
    html += li(actual)

    html += "<p>【附截图】</p>"
    html += li(screenshot)

    return html


# ─── CLI 主入口 ─────────────────────────────────────────────
if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv or "--help" in argv or "-h" in argv:
        print(__doc__)
        return

    # 解析参数
    title = argv[0]
    actual = argv[1] if len(argv) > 1 else ""
    severity = int(argv[2]) if len(argv) > 2 else 3
    pri = int(argv[3]) if len(argv) > 3 else 3
    module = argv[4] if len(argv) > 4 else None

    id_map = _load_modules()
    if module:
        mod_name = id_map.get(str(module), module)
    else:
        mod_name = "未指定"

    steps_html = build_steps_html(actual=actual)
    result = create_bug(title, steps_html, severity, pri, module=module)
    bug_id = result.get("id")
    if bug_id:
        print(f"✅ Bug 创建成功！ID: {bug_id} | 模块: [{module}] {mod_name}")
    else:
        print(f"❌ 创建失败: {result}")