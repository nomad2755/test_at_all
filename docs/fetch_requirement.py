from playwright.sync_api import sync_playwright
import sys

url = sys.argv[1] if len(sys.argv) > 1 else "https://www.whhnhy.com:37777/axure/OnlineHome"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print(f"正在访问: {url}")
    page.goto(url, timeout=30000)
    
    # 等待页面加载
    page.wait_for_load_state("networkidle", timeout=30000)
    
    # 获取页面标题
    title = page.title()
    print(f"\n页面标题: {title}")
    
    # 获取所有文本内容
    content = page.inner_text("body")
    print(f"\n页面内容 (前10000字符):\n{content[:10000]}")
    
    # 保存完整内容到文件
    with open("/root/.openclaw/workspace/docs/requirement_content.txt", "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n")
        f.write(f"标题: {title}\n")
        f.write("="*80 + "\n\n")
        f.write(content)
    
    print("\n\n完整内容已保存到: /root/.openclaw/workspace/docs/requirement_content.txt")
    
    browser.close()
