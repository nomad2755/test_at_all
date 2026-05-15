#!/usr/bin/env python3
"""
upload_to_whhnhy.py - 上传图片到数字资产管理平台获得永久 URL

支持环境:
    --env prod   仅上传到生产区 (8966)
    --env test   仅上传到测试区 (38868)
    --env both   同时上传到测试区+生产区（默认）

使用方法:
    python3 scripts/upload_to_whhnhy.py <图片路径> [--env both]
    python3 scripts/upload_to_whhnhy.py --latest --env both
    python3 scripts/upload_to_whhnhy.py /root/.openclaw/media/inbound/xxx.png --env test

输出:
    生产区 URL: https://www.whhnhy.com:8900/szxc/<hash>.png
    测试区 URL: https://www.whhnhy.com:8901/szxc/<hash>.png  (若 --env both)
"""

import sys
import os
import json
import uuid
import urllib.request
import urllib.error
import argparse

# 数字资产管理平台配置
ENV_CONFIG = {
    "prod": {
        "base_url": "https://www.whhnhy.com:8966",
        "permanent_port": 8900,
    },
    "test": {
        "base_url": "https://www.whhnhy.com:38868",
        "permanent_port": 29000,
    }
}

# 账号（admin 权限可以上传文件）
UPLOAD_ACCOUNT = "admin"
UPLOAD_PASSWORD = "Szxc@2024"


def get_upload_token_and_cookies(base_url):
    """
    使用 Playwright 登录数字资产管理平台，获取 token 和 cookies
    base_url: 平台地址，如 https://www.whhnhy.com:8966 或 https://www.whhnhy.com:38868
    返回: (access_token, cookie_str)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要安装 playwright: pip install playwright && playwright install chromium")
        return None, None

    login_api = f"{base_url}/admin/login"
    file_page = f"{base_url}/admin/infra/file/file"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            # 1. 登录
            page.goto(login_api, timeout=20000, wait_until='domcontentloaded')
            page.wait_for_timeout(1000)

            page.fill('input[placeholder="请输入用户名"]', UPLOAD_ACCOUNT)
            page.fill('input[placeholder="请输入密码"]', UPLOAD_PASSWORD)
            page.click('button')
            page.wait_for_url('**/admin/**', timeout=10000)
            page.wait_for_timeout(2000)

            # 2. 访问文件页获取完整登录态
            page.goto(file_page, timeout=20000, wait_until='domcontentloaded')
            page.wait_for_timeout(2000)

            # 3. 获取 ACCESS_TOKEN
            access_token_json = page.evaluate('localStorage.getItem("ACCESS_TOKEN")')
            access_token_data = json.loads(access_token_json)
            access_token = json.loads(access_token_data['v'])

            # 4. 获取 cookies
            cookies = page.context.cookies()
            cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])

            return access_token, cookie_str

        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return None, None
        finally:
            browser.close()


def upload_to_env(image_path, env="prod"):
    """
    上传图片到指定环境
    env: "prod" 或 "test"
    返回: (permanent_url, env_name) 或 (None, env_name)
    """
    if env not in ENV_CONFIG:
        return None, env

    cfg = ENV_CONFIG[env]
    base_url = cfg["base_url"]
    upload_api = f"{base_url}/admin-api/infra/file/upload"
    env_label = "生产区" if env == "prod" else "测试区"

    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return None, env

    print(f"🔐 正在登录 {env_label}...")
    access_token, cookie_str = get_upload_token_and_cookies(base_url)
    if not access_token or not cookie_str:
        return None, env

    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # 构建 multipart 请求
    filename = os.path.basename(image_path)
    boundary = '----WebKitFormBoundary' + str(uuid.uuid4().int)[:16]

    body = f'''--{boundary}\r
Content-Disposition: form-data; name="file"; filename="{filename}"\r
Content-Type: image/png\r
\r
'''.encode() + image_data + f'''\r
--{boundary}--\r
'''.encode()

    # 发送请求
    req = urllib.request.Request(upload_api, data=body, method='POST')
    req.add_header('Cookie', cookie_str)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('User-Agent', 'Mozilla/5.0')

    try:
        response = urllib.request.urlopen(req, timeout=30)
        result = response.read().decode()

        resp_data = json.loads(result)
        if resp_data.get('code') == 200:
            permanent_url = resp_data.get('data')
            return permanent_url, env
        else:
            print(f"❌ {env_label}上传失败: {result}")
            return None, env

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ {env_label} HTTP错误 {e.code}: {error_body[:200]}")
        return None, env
    except Exception as e:
        print(f"❌ {env_label}上传异常: {e}")
        return None, env


def upload_image(image_path, env="both"):
    """
    上传图片到数字资产管理平台
    env: "prod" / "test" / "both"
    返回:
        env="both": {"prod": url or None, "test": url or None}
        env="prod" 或 "test": url or None
    """
    if env == "both":
        results = {}
        # 先上传生产区
        print(f"\n{'='*60}")
        print(f"📤 开始同时上传到【测试区+生产区】")
        print(f"{'='*60}")

        print(f"\n>>> 1/2 上传生产区 (8966)...")
        prod_url, _ = upload_to_env(image_path, "prod")
        results["prod"] = prod_url
        if prod_url:
            print(f"    ✅ 生产区成功: {prod_url}")
        else:
            print(f"    ❌ 生产区失败")

        print(f"\n>>> 2/2 上传测试区 (38868)...")
        test_url, _ = upload_to_env(image_path, "test")
        results["test"] = test_url
        if test_url:
            print(f"    ✅ 测试区成功: {test_url}")
        else:
            print(f"    ❌ 测试区失败")

        return results

    elif env == "test":
        url, _ = upload_to_env(image_path, "test")
        return url
    else:
        url, _ = upload_to_env(image_path, "prod")
        return url


def get_latest_screenshot():
    """获取最新的截图文件"""
    inbound_dir = '/root/.openclaw/media/inbound'

    if not os.path.exists(inbound_dir):
        return None

    import glob
    files = glob.glob(os.path.join(inbound_dir, '*.png')) + \
            glob.glob(os.path.join(inbound_dir, '*.jpg')) + \
            glob.glob(os.path.join(inbound_dir, '*.jpeg'))

    if not files:
        return None

    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def main():
    parser = argparse.ArgumentParser(description="上传图片到数字资产管理平台")
    parser.add_argument('image_path', nargs='?', help='图片路径')
    parser.add_argument('--latest', action='store_true', help='使用最新截图')
    parser.add_argument('--env', choices=['prod', 'test', 'both'], default='both',
                        help='上传目标环境: prod=生产区(8966), test=测试区(38868), both=两者都上传(默认)')

    args = parser.parse_args()

    if not args.latest and not args.image_path:
        print(__doc__)
        sys.exit(0)

    if args.latest:
        print("📷 获取最新截图...")
        image_path = get_latest_screenshot()
        if not image_path:
            print("❌ 没有找到截图文件")
            sys.exit(1)
        print(f"   使用: {image_path}")
    else:
        image_path = args.image_path

    print(f"📤 上传图片: {image_path}")
    print(f"🌍 目标环境: {args.env}")

    result = upload_image(image_path, args.env)

    if args.env == "both":
        print(f"\n{'='*60}")
        print(f"📋 上传结果汇总")
        print(f"{'='*60}")
        if result.get("prod"):
            print(f"  ✅ 生产区: {result['prod']}")
        else:
            print(f"  ❌ 生产区: 失败")
        if result.get("test"):
            print(f"  ✅ 测试区: {result['test']}")
        else:
            print(f"  ❌ 测试区: 失败")
    else:
        if result:
            print(f"\n✅ 上传成功！")
            print(f"永久 URL: {result}")
        else:
            print(f"\n❌ 上传失败")
            sys.exit(1)


if __name__ == "__main__":
    main()
