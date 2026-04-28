# -*- coding: utf-8 -*-
"""
分析5个Axure原型页面，提取测试功能点
"""
import os
import re
from playwright.sync_api import sync_playwright

# 5个原型页面URL
URLS = [
    ("数据资产对接", "https://www.whhnhy.com:37777/axure/NotaryIntelligentAgent/?id=bpxhu8&p=%E6%95%B0%E6%8D%AE%E8%B5%84%E4%BA%A7%E5%AF%B9%E6%8E%A5&g=1"),
    ("实名认证", "https://www.whhnhy.com:37777/axure/NotaryIntelligentAgent/?id=ohu36s&p=%E5%AE%9E%E5%90%8D%E8%AE%A4%E8%AF%81_1&g=1"),
    ("公证员资质申请", "https://www.whhnhy.com:37777/axure/NotaryIntelligentAgent/?id=kwo3vo&p=%E5%85%AC%E8%AF%81%E5%91%98%E8%B5%84%E8%B4%A8%E7%94%B3%E8%AF%B7&g=1"),
    ("流程优化", "https://www.whhnhy.com:37777/axure/NotaryIntelligentAgent/?id=xhr6il&p=%E6%B5%81%E7%A8%8B%E4%BC%98%E5%8C%96&g=1"),
    ("智能公证", "https://www.whhnhy.com:37777/axure/NotaryIntelligentAgent/?id=egjsmh&p=%E6%99%BA%E8%83%BD%E5%85%AC%E8%AF%81&g=1"),
]

OUTPUT_DIR = r"C:\Users\14031\Desktop\prototype_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_page(page, module_name, url, index):
    """分析单个页面"""
    print(f"\n{'='*60}")
    print(f"[{index+1}/5] 分析: {module_name}")
    print(f"URL: {url}")
    print('='*60)

    try:
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_timeout(2000)  # 等待动态内容加载

        # 截取全屏截图
        screenshot_path = os.path.join(OUTPUT_DIR, f"{index+1:02d}_{module_name}_全屏.png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"[OK] 全屏截图: {screenshot_path}")

        # 获取页面内容分析
        content = page.content()

        # 提取关键信息
        title = page.title()
        print(f"[INFO] 页面标题: {title}")

        # 查找页面上的文本内容
        text_elements = []
        try:
            # 获取所有可见文本
            body_text = page.locator("body").inner_text()
            if body_text:
                text_elements.append(body_text[:2000])  # 限制长度
        except:
            pass

        return {
            "module": module_name,
            "url": url,
            "title": title,
            "content": content,
            "text_elements": text_elements,
            "screenshot": screenshot_path
        }

    except Exception as e:
        print(f"[ERROR] 页面加载失败: {e}")
        return {
            "module": module_name,
            "url": url,
            "error": str(e)
        }

def main():
    print("开始分析5个Axure原型页面...")
    print(f"输出目录: {OUTPUT_DIR}")

    results = []

    with sync_playwright() as p:
        # 启动浏览器（手机视图）
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        page = context.new_page()

        for i, (module_name, url) in enumerate(URLS):
            result = analyze_page(page, module_name, url, i)
            results.append(result)

        browser.close()

    # 输出分析摘要
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)
    for r in results:
        if "error" in r:
            print(f"[{r['module']}] 加载失败: {r['error']}")
        else:
            print(f"[{r['module']}] OK - {r.get('title', 'N/A')}")

    return results

if __name__ == "__main__":
    results = main()
