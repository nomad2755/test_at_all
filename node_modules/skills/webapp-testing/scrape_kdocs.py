from playwright.sync_api import sync_playwright

url = "https://www.kdocs.cn/l/ckbANHtX6tDc"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate and wait for full load
    page.goto(url, timeout=30000)
    page.wait_for_load_state('networkidle', timeout=20000)
    page.wait_for_timeout(3000)  # extra wait for JS rendering

    # Get page title
    title = page.title()
    print(f"Page title: {title}")

    # Get all visible text
    content = page.inner_text('body')
    print(f"\n--- Content ({len(content)} chars) ---\n{content[:5000]}")

    # Save to file
    with open("C:/Users/14031/kdocs_content.txt", "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"URL: {url}\n")
        f.write("---\n")
        f.write(content)

    print("\nSaved to C:/Users/14031/kdocs_content.txt")

    browser.close()
