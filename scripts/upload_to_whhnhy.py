#!/usr/bin/env python3
"""
upload_to_whhnhy.py - 上传图片到数字资产管理平台获得永久 URL

使用方法:
    python3 scripts/upload_to_whhnhy.py <图片路径>
    python3 scripts/upload_to_whhnhy.py /root/.openclaw/media/inbound/xxx.png
    python3 scripts/upload_to_whhnhy.py --latest  # 上传最新截图

输出:
    永久 URL 格式: https://www.whhnhy.com:8900/szxc/<hash>.png
"""

import sys
import os
import json
import uuid
import urllib.request
import urllib.error

# 数字资产管理平台配置
WHHNHY_URL = "https://www.whhnhy.com:8966"
UPLOAD_API = f"{WHHNHY_URL}/admin-api/infra/file/upload"
LOGIN_API = f"{WHHNHY_URL}/admin/login"

# 账号（admin 权限可以上传文件）
UPLOAD_ACCOUNT = "admin"
UPLOAD_PASSWORD = "Szxc@2024"


def get_upload_token_and_cookies():
    """
    使用 Playwright 登录数字资产管理平台，获取 token 和 cookies
    返回: (access_token, cookie_str)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要安装 playwright: pip install playwright && playwright install chromium")
        return None, None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        try:
            # 1. 登录
            page.goto(LOGIN_API, timeout=20000, wait_until='domcontentloaded')
            page.wait_for_timeout(1000)
            
            page.fill('input[placeholder="请输入用户名"]', UPLOAD_ACCOUNT)
            page.fill('input[placeholder="请输入密码"]', UPLOAD_PASSWORD)
            page.click('button')
            page.wait_for_url('**/admin/**', timeout=10000)
            page.wait_for_timeout(2000)
            
            # 2. 访问文件页获取完整登录态
            page.goto(f"{WHHNHY_URL}/admin/infra/file/file", timeout=20000, wait_until='domcontentloaded')
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


def upload_image(image_path, access_token=None, cookie_str=None):
    """
    上传图片到数字资产管理平台
    image_path: 图片本地路径
    access_token: 认证 token（可选，如果为空则自动获取）
    cookie_str: Cookie 字符串（可选）
    
    返回: 永久 URL 或 None
    """
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return None
    
    # 如果没有 token 和 cookies，自动获取
    if not access_token or not cookie_str:
        print("🔐 正在获取登录态...")
        access_token, cookie_str = get_upload_token_and_cookies()
        if not access_token or not cookie_str:
            return None
    
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
    req = urllib.request.Request(UPLOAD_API, data=body, method='POST')
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
            return permanent_url
        else:
            print(f"❌ 上传失败: {result}")
            return None
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ HTTP错误 {e.code}: {error_body[:200]}")
        return None
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        return None


def get_latest_screenshot():
    """获取最新的截图文件"""
    inbound_dir = '/root/.openclaw/media/inbound'
    
    if not os.path.exists(inbound_dir):
        return None
    
    # 获取最新的 png/jpg 文件
    import glob
    files = glob.glob(os.path.join(inbound_dir, '*.png')) + \
            glob.glob(os.path.join(inbound_dir, '*.jpg')) + \
            glob.glob(os.path.join(inbound_dir, '*.jpeg'))
    
    if not files:
        return None
    
    # 按修改时间排序，返回最新的
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    # 解析参数
    if sys.argv[1] == '--latest':
        print("📷 获取最新截图...")
        image_path = get_latest_screenshot()
        if not image_path:
            print("❌ 没有找到截图文件")
            sys.exit(1)
        print(f"   使用: {image_path}")
    else:
        image_path = sys.argv[1]
    
    # 上传
    print(f"📤 上传图片: {image_path}")
    url = upload_image(image_path)
    
    if url:
        print(f"\n✅ 上传成功！")
        print(f"永久 URL: {url}")
    else:
        print(f"\n❌ 上传失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
