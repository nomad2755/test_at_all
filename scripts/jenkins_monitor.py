#!/usr/bin/env python3
"""
Jenkins 构建状态监控脚本
功能：
1. 获取所有 Job 的最新构建状态
2. 识别失败/不稳定的构建
3. 输出简洁的状态报告
4. 支持 --brief 精简模式（供 cron 使用）
"""

import argparse
import json
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

JENKINS_URL = "http://192.168.0.26:10240"
AUTH = ("shidw", "178178Shi")


def get_jenkins_data():
    """通过 Playwright 登录并获取 Jenkins API 数据"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            # Login first
            page.goto(f"{JENKINS_URL}/login", timeout=10000, wait_until="domcontentloaded")
            page.fill("#j_username", "shidw")
            page.fill("#j_password", "178178Shi")
            page.click('button[type="submit"]')
            page.wait_for_timeout(2000)


            # Get API data
            api_url = f"{JENKINS_URL}/api/json?tree=jobs[name,color,lastBuild[result,number,timestamp,url],lastSuccessfulBuild[number],lastFailedBuild[number]]"
            page.goto(api_url, timeout=10000)
            raw = page.inner_text("body")
            return json.loads(raw)
        finally:
            browser.close()


def parse_color(color):
    """解析 Jenkins 颜色"""
    color_map = {
        "blue": "✅",
        "blue_anime": "🔄",
        "red": "❌",
        "red_anime": "🔄",
        "yellow": "⚠️",
        "yellow_anime": "🔄",
        "gray": "⏸",
        "grey": "⏸",
        "aborted": "⏹",
        "aborted_anime": "🔄",
        "nobuilt": "📭",
        "anime": "🔄",
        "disabled": "⏸",
    }
    base = color.replace("_anime", "")
    return color_map.get(color, color_map.get(base, f"❓{color}"))


def build_age(timestamp_ms):
    """计算构建距今时间"""
    if not timestamp_ms:
        return "无记录"
    age_s = time.time() - timestamp_ms / 1000
    days = int(age_s // 86400)
    hours = int((age_s % 86400) // 3600)
    mins = int((age_s % 3600) // 60)
    if days > 0:
        return f"{days}天{hours}时"
    elif hours > 0:
        return f"{hours}时{mins}分"
    elif mins > 0:
        return f"{mins}分"
    return "刚刚"


def main():
    parser = argparse.ArgumentParser(description="Jenkins 构建状态监控")
    parser.add_argument("--brief", action="store_true", help="精简模式，输出 JSON")
    parser.add_argument("--failed-only", action="store_true", help="仅显示失败项目")
    parser.add_argument("--all", action="store_true", help="显示所有项目")
    args = parser.parse_args()

    data = get_jenkins_data()
    jobs = data.get("jobs", [])

    failed = []
    unstable = []
    successful = []
    building = []
    disabled = []
    nobuilt = []

    for j in jobs:
        color = j.get("color", "")
        name = j.get("name")
        lb = j.get("lastBuild")

        result = (lb or {}).get("result") if lb else None
        is_anime = "anime" in color


        if color in ("gray", "grey", "disabled"):
            disabled.append(j)
        elif is_anime:
            building.append(j)
        elif result == "FAILURE":
            failed.append(j)
        elif result == "UNSTABLE":
            unstable.append(j)
        elif not lb:
            if color in ("nobuilt",):
                nobuilt.append(j)
            else:
                successful.append(j)
        else:
            successful.append(j)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if args.brief:
        output = {
            "timestamp": timestamp,
            "summary": {
                "total": len(jobs),
                "failed": len(failed),
                "unstable": len(unstable),
                "building": len(building),
                "disabled": len(disabled),
            },
            "failed_jobs": [
                {"name": j["name"], "number": (j.get("lastBuild") or {}).get("number"), "url": j["url"]}
                for j in failed
            ],
            "unstable_jobs": [
                {"name": j["name"], "number": (j.get("lastBuild") or {}).get("number"), "url": j["url"]}
                for j in unstable
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 正常模式
    print(f"📊 Jenkins 构建状态 | {timestamp}")
    print(f"总计: {len(jobs)} 个 | ❌失败: {len(failed)} | ⚠️不稳定: {len(unstable)} | 🔄构建中: {len(building)} | ⏸禁用: {len(disabled)}")
    print()

    if failed:
        print(f"❌ 失败 ({len(failed)} 个):")
        for j in failed:
            lb = j.get("lastBuild") or {}
            age = build_age(lb.get("timestamp"))
            print(f"   {j['name']} (#{lb.get('number','?')}) {age} {j.get('url','')}")
        print()

    if unstable:
        print(f"⚠️ 不稳定 ({len(unstable)} 个):")
        for j in unstable:
            lb = j.get("lastBuild") or {}
            age = build_age(lb.get("timestamp"))
            print(f"   {j['name']} (#{lb.get('number','?')}) {age} {j.get('url','')}")
        print()

    if building:
        print(f"🔄 正在构建 ({len(building)} 个):")
        for j in building:
            print(f"   {j['name']}")
        print()

    if args.all or not args.failed_only:
        shown = 15 if args.all else 10
        print(f"✅ 正常 ({len(successful)} 个):")
        for j in successful[:shown]:
            lb = j.get("lastBuild") or {}
            color = j.get("color", "")
            status = parse_color(color)
            age = build_age(lb.get("timestamp")) if lb else ""
            num = lb.get("number", "-")
            print(f"   {status} {j['name']} #{num} ({age})")
        if len(successful) > shown:
            print(f"   ... 还有 {len(successful) - shown} 个")
        print()

    if nobuilt:
        print(f"📭 未构建 ({len(nobuilt)} 个):")
        for j in nobuilt[:5]:
            print(f"   {j['name']}")
        if len(nobuilt) > 5:
            print(f"   ... 还有 {len(nobuilt) - 5} 个")

    if disabled:
        print(f"⏸ 禁用 ({len(disabled)} 个):")
        for j in disabled[:5]:
            print(f"   {j['name']}")
        if len(disabled) > 5:
            print(f"   ... 还有 {len(disabled) - 5} 个")


if __name__ == "__main__":
    main()
