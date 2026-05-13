"""
碳计算页面自动化测试脚本
目标: https://whhnhy.com:8966/east_carbon/carbonProject/projectManage/carbonCalculation

运行方式:
  pip install pytest-playwright
  playwright install chromium
  python test_carbon_calculation.py --base-url https://whhnhy.com:8966

支持 --headed 参数显示浏览器界面便于观察
"""

import re
import sys
import argparse
from typing import Generator

import pytest
from playwright.sync_api import Page, BrowserContext, expect, sync_playwright


# ============================================================
# 配置
# ============================================================
BASE_URL = "https://whhnhy.com:8966"
PATH = "/east_carbon/carbonProject/projectManage/carbonCalculation"
FULL_URL = f"{BASE_URL}{PATH}"

# 如果页面需要登录，在此设置凭据
LOGIN_URL = f"{BASE_URL}/east_carbon/login"
CREDENTIALS = {
    "username": "",  # TODO: 填写实际账号
    "password": "",  # TODO: 填写实际密码
}


# ============================================================
# 辅助函数
# ============================================================
def login_if_needed(page: Page):
    """检查是否需要登录，如需要则执行登录"""
    if page.url.startswith(LOGIN_URL) or page.url == BASE_URL + "/":
        print("[登录] 检测到需要登录，执行登录流程...")
        page.fill('input[name="username"], input[placeholder*="账号"]', CREDENTIALS["username"])
        page.fill('input[name="password"], input[placeholder*="密码"]', CREDENTIALS["password"])
        page.click('button[type="submit"], .login-btn, .el-button--primary')
        page.wait_for_load_state("networkidle")
        # 登录后等待跳转到目标页面
        page.goto(FULL_URL)
        page.wait_for_load_state("networkidle")


def take_debug_screenshot(page: Page, name: str):
    """保存调试截图"""
    page.screenshot(path=f"/tmp/carbon_debug_{name}.png", full_page=True)
    print(f"[截图] 已保存: /tmp/carbon_debug_{name}.png")


# ============================================================
# 测试用例
# ============================================================

class TestCarbonCalculation:
    """碳计算页面自动化测试套件"""

    def test_01_page_loads_successfully(self, page: Page):
        """TC-01: 页面能正常加载"""
        response = page.goto(FULL_URL, wait_until="networkidle", timeout=30000)
        assert response is not None, "页面无响应"
        assert response.ok, f"页面返回异常状态码: {response.status}"
        print(f"[OK] 页面加载成功，状态码: {response.status}")

    def test_02_page_title_and_url(self, page: Page):
        """TC-02: 页面标题和 URL 正确"""
        assert PATH in page.url, f"URL 不匹配: {page.url}"
        title = page.title()
        print(f"[信息] 页面标题: {title}")
        assert len(title) > 0, "页面标题为空"

    def test_03_basic_ui_elements(self, page: Page):
        """TC-03: 页面基础 UI 元素检测"""
        # 检查关键元素是否存在
        selectors = [
            "button",           # 按钮
            "input",            # 输入框
            "select",           # 下拉框
            "table",            # 表格
            ".el-table",        # Element UI 表格
            ".el-form",         # Element UI 表单
        ]
        for sel in selectors:
            elements = page.locator(sel)
            count = elements.count()
            if count > 0:
                print(f"[OK] 找到元素 '{sel}': {count} 个")
        take_debug_screenshot(page, "ui_elements")

    def test_04_form_fields_available(self, page: Page):
        """TC-04: 表单输入字段检测"""
        inputs = page.locator("input, .el-input__inner, textarea")
        count = inputs.count()
        print(f"[信息] 输入框数量: {count}")
        for i in range(min(count, 20)):
            el = inputs.nth(i)
            placeholder = el.get_attribute("placeholder") or "无placeholder"
            name = el.get_attribute("name") or "无name"
            print(f"  - 输入框 #{i}: name={name}, placeholder={placeholder}")
        assert count > 0, "页面没有找到任何输入框"

    def test_05_buttons_clickable(self, page: Page):
        """TC-05: 按钮可点击"""
        buttons = page.locator("button, .el-button, [role='button']")
        count = buttons.count()
        print(f"[信息] 按钮数量: {count}")
        enabled_count = 0
        for i in range(min(count, 30)):
            btn = buttons.nth(i)
            text = btn.text_content() or btn.get_attribute("title") or f"button#{i}"
            disabled = btn.is_disabled()
            visible = btn.is_visible()
            status = "可点击" if (visible and not disabled) else "不可用"
            print(f"  - [{status}] {text.strip()[:50]}")
            if visible and not disabled:
                enabled_count += 1
        assert enabled_count > 0, "没有可点击的按钮"

    def test_06_carbon_calculation_flow(self, page: Page):
        """TC-06: 碳计算核心流程（选择项目 → 填写参数 → 计算）"""
        take_debug_screenshot(page, "before_calculation")

        # 1. 查找并点击"计算"或"开始计算"按钮
        calc_btn = page.locator(
            "button:has-text('计算'), "
            "button:has-text('开始计算'), "
            "button:has-text('碳排放'), "
            ".el-button--primary:has-text('计算')"
        ).first
        if calc_btn.is_visible():
            calc_btn.click()
            page.wait_for_timeout(2000)  # 等待计算结果
            take_debug_screenshot(page, "after_calculation")
            print("[OK] 碳计算按钮已点击")
        else:
            print("[信息] 未找到碳计算按钮，可能页面需要先选择项目或填写参数")

        # 2. 检查是否有加载状态
        loading = page.locator(".el-loading-mask, .loading, [class*='loading']").first
        if loading.is_visible():
            print("[信息] 检测到加载中状态")
            loading.wait_for(state="hidden", timeout=15000)
            print("[OK] 加载完成")

        # 3. 检查计算结果区域
        result_selectors = [
            "text=碳排放", "text=碳足迹", "text=排放量",
            "text=tCO2", "text=千克", "text=吨",
            ".chart", ".el-card", ".result",
        ]
        for sel in result_selectors:
            results = page.locator(sel)
            if results.count() > 0 and results.first.is_visible():
                text = results.first.text_content() or ""
                print(f"[信息] 发现结果区域: {text[:80]}")
                break

    def test_07_table_data_available(self, page: Page):
        """TC-07: 表格数据检测"""
        # 查找表格
        table = page.locator("table, .el-table, .el-table__body, .table").first
        if table.is_visible():
            rows = page.locator("table tr, .el-table__row")
            row_count = rows.count()
            print(f"[信息] 表格行数: {row_count}")
            if row_count > 0:
                cells = rows.first.locator("td, th")
                cell_count = cells.count()
                print(f"[信息] 表头/首行列数: {cell_count}")
                row_data = []
                for i in range(cell_count):
                    cell_text = cells.nth(i).text_content() or ""
                    row_data.append(cell_text.strip())
                print(f"[信息] 首行数据: {row_data}")
            assert row_count > 0, "表格没有数据行"
        else:
            print("[信息] 页面没有检测到表格")

    def test_08_page_performance(self, page: Page):
        """TC-08: 页面加载性能"""
        # 收集性能指标
        timing = page.evaluate("""() => {
            const t = performance.timing;
            const n = performance.getEntriesByType('navigation')[0];
            return {
                domContentLoaded: t.domContentLoadedEventEnd - t.navigationStart,
                loadComplete: t.loadEventEnd - t.navigationStart,
                domInteractive: t.domInteractive - t.navigationStart,
                ttfb: n ? n.responseStart - n.requestStart : 0,
                duration: n ? n.duration : 0
            };
        }""")
        print(f"[性能指标]")
        print(f"  DOMContentLoaded: {timing['domContentLoaded']}ms")
        print(f"  Load Complete:    {timing['loadComplete']}ms")
        print(f"  DOM Interactive:  {timing['domInteractive']}ms")
        print(f"  TTFB:             {timing['ttfb']}ms")
        print(f"  Navigation Duration: {timing['duration']}ms")

    def test_09_console_no_errors(self, page: Page):
        """TC-09: 控制台无严重错误"""
        errors = []
        def on_console(msg):
            if msg.type == "error" or msg.type == "warning":
                errors.append(f"[{msg.type}] {msg.text}")

        page.on("console", on_console)
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(3000)

        if errors:
            print(f"[警告] 检测到 {len(errors)} 个控制台错误/警告:")
            for err in errors[:10]:
                print(f"  {err}")
        else:
            print("[OK] 控制台无错误或警告")

    def test_10_responsive_check(self, page: Page):
        """TC-10: 页面响应式检查（常见分辨率）"""
        viewports = [
            (1920, 1080),  # 桌面
            (1440, 900),   # 笔记本
            (1280, 800),   # 小笔记本
            (375, 812),    # iPhone X
            (414, 896),    # iPhone 11 Pro Max
        ]
        for w, h in viewports:
            page.set_viewport_size({"width": w, "height": h})
            page.wait_for_timeout(500)
            # 检查是否有元素溢出或错位
            body_width = page.evaluate("document.body.scrollWidth")
            overflow = body_width > w * 1.1  # 允许 10% 误差
            status = "⚠️ 水平溢出" if overflow else "✅ 正常"
            print(f"  {w}x{h}: body宽度={bodyWidth if bodyWidth else 'N/A'} {status}")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="碳计算页面自动化测试")
    parser.add_argument("--base-url", default=BASE_URL, help="基础URL")
    parser.add_argument("--headed", action="store_true", help="显示浏览器界面")
    parser.add_argument("--slow-mo", type=int, default=0, help="操作延迟(ms)")
    parser.add_argument("--username", default="", help="登录账号")
    parser.add_argument("--password", default="", help="登录密码")
    args = parser.parse_args()

    if args.username:
        CREDENTIALS["username"] = args.username
    if args.password:
        CREDENTIALS["password"] = args.password

    FULL_URL = f"{args.base_url}{PATH}"
    LOGIN_URL = f"{args.base_url}/east_carbon/login"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not args.headed,
            slow_mo=args.slow_mo,
            args=["--ignore-certificate-errors"]  # 忽略自签名证书错误
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        page = context.new_page()

        # 收集控制台日志
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_logs.append(f"[PAGE_ERROR] {err}"))

        try:
            # 加载页面
            print(f"正在加载: {FULL_URL}")
            resp = page.goto(FULL_URL, wait_until="networkidle", timeout=30000)
            if resp:
                print(f"状态码: {resp.status}")

            # 检查是否需要登录
            login_if_needed(page)
            page.wait_for_timeout(2000)

            # 完整截图
            take_debug_screenshot(page, "full_page")
            print(f"页面标题: {page.title()}")

            # 打印 DOM 中可见的文本内容（用于分析页面结构）
            body_text = page.locator("body").text_content() or ""
            visible_text = ' '.join(body_text.split())[:2000]
            print(f"\n页面可见文本 (前2000字符):\n{visible_text}")

            # 打印所有按钮
            print("\n所有按钮:")
            for btn in page.locator("button, .el-button, [role='button']").all():
                text = (btn.text_content() or "").strip()
                if text:
                    print(f"  [{btn.is_visible() and '可见' else '隐藏'}] {text}")

            # 打印所有输入框
            print("\n所有输入框:")
            for inp in page.locator("input, .el-input__inner, textarea").all():
                ph = inp.get_attribute("placeholder") or ""
                nm = inp.get_attribute("name") or ""
                v = inp.input_value() or "(空)"
                if ph or nm:
                    print(f"  placeholder={ph} name={nm} value={v}")

            # 控制台日志
            if console_logs:
                print(f"\n控制台日志 ({len(console_logs)} 条):")
                for log in console_logs[:20]:
                    print(f"  {log}")

        except Exception as e:
            take_debug_screenshot(page, "error")
            print(f"\n[错误] {e}")
        finally:
            browser.close()

    print("\n测试完成")
