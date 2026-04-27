from playwright.sync_api import sync_playwright
import json

url = "https://www.kdocs.cn/l/ckbANHtX6tDc"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(url, timeout=30000)
    page.wait_for_load_state('networkidle', timeout=20000)
    page.wait_for_timeout(5000)  # wait for JS rendering

    # Get page title
    title = page.title()
    print(f"Page title: {title}")

    # Try to extract via evaluate (more reliable)
    texts = page.evaluate("""
        () => {
            // Get all visible text from the document content area
            const elements = document.querySelectorAll('[class*="content"], [class*="editor"], [class*="doc"], [id*="content"], [id*="editor"]');
            if (elements.length > 0) {
                return Array.from(elements).map(el => el.innerText).join('\\n');
            }
            // Fallback: get body text
            return document.body.innerText;
        }
    """)
    print(f"Extracted via evaluate: {len(texts)} chars")
    print(texts[:2000])

    # Save with correct encoding
    with open("C:/Users/14031/kdocs_content.txt", "w", encoding="utf-8", errors="replace") as f:
        f.write(f"Title: {title}\n")
        f.write(f"URL: {url}\n")
        f.write("="*50 + "\n")
        f.write(texts)

    print(f"\nSaved to C:/Users/14031/kdocs_content.txt ({len(texts)} chars)")

    browser.close()
