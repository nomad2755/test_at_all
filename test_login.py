#!/usr/bin/env python3
"""
登录自动化测试脚本
运行方式: python test_login.py
依赖: pip install playwright && playwright install chromium
"""
from playwright.sync_api import sync_playwright

# 请填写你们的账号密码
USERNAME = "your_username"  # TODO: 填入账号
PASSWORD = "your_password"  # TODO: 填入密码
LOGIN_URL = "https://whhnhy.com:8910/knowledge/login?redirect=/accountHomepage"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        print(f"1. 访问登录页: {LOGIN_URL}")
        page.goto(LOGIN_URL, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # 保存登录页截图
        page.screenshot(path="login_page.png")
        print("   截图已保存: login_page.png")
        
        # 分析登录页元素
        print("\n2. 分析登录页元素...")
        inputs = page.query_selector_all("input")
        print(f"   找到 {len(inputs)} 个输入框:")
        for i, inp in enumerate(inputs):
            print(f"   [{i}] type={inp.get_attribute('type')} placeholder={inp.get_attribute('placeholder')} name={inp.get_attribute('name')}")
        
        buttons = page.query_selector_all("button")
        print(f"\n   找到 {len(buttons)} 个按钮:")
        for i, btn in enumerate(buttons):
            txt = btn.inner_text().strip()
            print(f"   [{i}] {txt[:50]}")
        
        # 尝试找登录表单
        print("\n3. 填写登录信息...")
        try:
            # 通用查找用户名/密码输入框
            page.fill('input[type="text"], input[name*="user"], input[name*="account"], input[placeholder*="账号"], input[placeholder*="用户名"]', USERNAME, timeout=3000)
            print(f"   已填写用户名: {USERNAME}")
        except Exception as e:
            print(f"   填写用户名失败: {e}")
        
        try:
            page.fill('input[type="password"]', PASSWORD, timeout=3000)
            print(f"   已填写密码: {PASSWORD}")
        except Exception as e:
            print(f"   填写密码失败: {e}")
        
        # 保存填写后截图
        page.screenshot(path="login_filled.png")
        print("\n   截图已保存: login_filled.png")
        
        # 提交登录
        print("\n4. 点击登录按钮...")
        try:
            page.click('button[type="submit"], button:has-text("登录"), button:has-text("登入"), button:has-text("登录")')
            print("   已点击登录")
        except Exception as e:
            print(f"   点击登录失败: {e}")
        
        # 等待登录结果
        page.wait_for_timeout(3000)
        
        # 保存登录后截图
        page.screenshot(path="after_login.png")
        print("\n5. 登录后截图已保存: after_login.png")
        print(f"   当前URL: {page.url}")
        
        # 判断是否登录成功
        if "login" not in page.url.lower():
            print("\n✅ 登录成功!")
        else:
            print("\n❌ 还在登录页，登录可能失败")
            # 获取页面提示信息
            try:
                errors = page.query_selector_all(".el-message--error, .ant-message-error, [class*='error']")
                for err in errors:
                    print(f"   错误提示: {err.inner_text()}")
            except:
                pass
        
        browser.close()
        print("\n测试完成!")

if __name__ == "__main__":
    main()
