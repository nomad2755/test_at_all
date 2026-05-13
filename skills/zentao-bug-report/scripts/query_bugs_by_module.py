#!/usr/bin/env python3
"""
query_bugs_by_module.py - 按 module_id 查询 ZenTao Bug

用法:
    python3 query_bugs_by_module.py <module_id> [状态] [页码]
    python3 query_bugs_by_module.py 295                    # 查询个人数字空间的 Bug
    python3 query_bugs_by_module.py 295 active             # 只查激活态 Bug
    python3 query_bugs_by_module.py 295 all 2              # 第二页
    python3 query_bugs_by_module.py 454                    # 查询数据资产综合管理服务平台

状态选项: active(默认) / all / resolved / closed
"""

import json
import sys
import urllib.request
import urllib.parse

ZENTAO_URL = "http://192.168.0.28:9980"
ACCOUNT = "shidawei"
PASSWORD = "shidawei"
PRODUCT_ID = 1
PAGE_SIZE = 100


def get_token():
    req = urllib.request.Request(
        f"{ZENTAO_URL}/api.php/v1/tokens",
        data=json.dumps({"account": ACCOUNT, "password": PASSWORD}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["token"]


def load_modules():
    """从本地模块树加载 id->name 映射"""
    import os
    path = "/root/.openclaw/workspace/skills/zentao-integration/docs/数字乡村模块树.md"
    if not os.path.exists(path):
        return {}
    id_to_name = {}
    with open(path) as f:
        for line in f:
            m = line.strip().split("|")
            if len(m) >= 3 and m[1].strip().isdigit():
                id_to_name[m[1].strip()] = m[2].strip()
    return id_to_name


def query_bugs(module_id, status="active", page=1, page_size=PAGE_SIZE):
    """
    按 module_id 查询 Bug
    
    status:
      active   - 激活态Bug (默认, type=codeerror+interface+function+performance)
      all     - 所有Bug
      resolved - 已解决
      closed  - 已关闭
    """
    token = get_token()
    offset = (page - 1) * page_size
    
    # 构建过滤条件
    if status == "active":
        params = f"product={PRODUCT_ID}&module={module_id}&limit={page_size}&offset={offset}&type=codeerror,interface,function,performance&orderBy=id_desc"
    elif status == "all":
        params = f"product={PRODUCT_ID}&module={module_id}&limit={page_size}&offset={offset}&orderBy=id_desc"
    elif status == "resolved":
        params = f"product={PRODUCT_ID}&module={module_id}&limit={page_size}&offset={offset}&orderBy=id_desc&status=resolved"
    elif status == "closed":
        params = f"product={PRODUCT_ID}&module={module_id}&limit={page_size}&offset={offset}&orderBy=id_desc&status=closed"
    else:
        params = f"product={PRODUCT_ID}&module={module_id}&limit={page_size}&offset={offset}&orderBy=id_desc"
    
    url = f"{ZENTAO_URL}/api.php/v1/bugs?{params}"
    req = urllib.request.Request(
        url,
        headers={"Token": token, "Zentao-Version": "22.4"},
        method="GET"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        return data


def format_bug(bug, id_to_name):
    """格式化单个 Bug 输出"""
    bid = bug.get("id", "?")
    title = bug.get("title", "?")
    status = bug.get("status", "?")
    severity = bug.get("severity", "?")
    pri = bug.get("pri", "?")
    assigned = bug.get("assignedTo", "?")
    openedby = bug.get("openedBy", "?")
    openeddate = (bug.get("openedDate") or "")[:10]
    resolveddate = (bug.get("resolvedDate") or "")[:10]
    return (f"  [{bid}] 【{severity}/{pri}】{title}\n"
            f"       状态:{status} | 指派:{assigned} | "
            f"创建:{openedby} {openeddate} | 解决:{resolveddate}")


def main():
    argv = sys.argv[1:]
    if not argv or "--help" in argv or "-h" in argv:
        print(__doc__)
        return

    module_id = argv[0] if argv else "0"
    status = argv[1] if len(argv) > 1 else "active"
    page = int(argv[2]) if len(argv) > 2 else 1
    page_size = PAGE_SIZE

    id_to_name = load_modules()
    mod_name = id_to_name.get(module_id, f"未知模块({module_id})")

    print(f"\n🔍 查询模块: [{module_id}] {mod_name}  |  状态: {status}  |  页码: {page}\n")
    print("=" * 70)

    try:
        data = query_bugs(module_id, status, page, page_size)
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return

    bugs = data.get("bugs", [])
    total = data.get("total", len(bugs))
    pages = (total // page_size) + (1 if total % page_size else 0)

    if not bugs:
        print("📭 无 Bug（或模块 ID 不存在）")
        return

    print(f"📊 共 {total} 个 Bug  |  第 {page}/{max(pages,1)} 页\n")
    print("-" * 70)
    for bug in bugs:
        print(format_bug(bug, id_to_name))
        print()

    # 统计摘要
    sev_count = {}
    status_count = {}
    for b in bugs:
        sev_count[b.get("severity","?")] = sev_count.get(b.get("severity","?"), 0) + 1
        status_count[b.get("status","?")] = status_count.get(b.get("status","?"), 0) + 1

    print("-" * 70)
    print("📈 本页统计:")
    print(f"   严重性: " + "  ".join(f"S{k}={v}" for k, v in sorted(sev_count.items())))
    print(f"   状态:   " + "  ".join(f"{k}={v}" for k, v in sorted(status_count.items())))


if __name__ == "__main__":
    main()