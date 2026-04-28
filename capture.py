#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-fonts',
                '--disable-font-subsetting',
                '--disable-web-fonts',
                '--single-process',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--ignore-certificate-errors',
                '--allow-running-insecure-content',
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            ignore_https_errors=True,
        )
        page = await context.new_page()

        # Block all font requests via route.abort()
        async def abort_font(route):
            try:
                await route.abort()
            except Exception:
                pass

        font_patterns = [
            '**/*.woff*', '**/*.ttf', '**/*.otf', '**/*.eot',
            '**/fonts/**', '**/font/**', '**/*font*',
        ]
        for pattern in font_patterns:
            await page.route(pattern, abort_font)

        print("Navigating...")
        await page.goto(
            'https://www.whhnhy.com:37777/axure/userapp/?id=wnmb3j&p=%E9%A6%96%E9%A1%B5&g=1',
            timeout=60000,
            wait_until='commit'
        )
        print("Navigation committed, waiting 5s...")
        await asyncio.sleep(5)

        # Use CDP directly to capture screenshot, bypassing Playwright's font waiting
        print("Creating CDP session...")
        cdp = await context.new_cdp_session(page)
        
        # Inject CSS to disable font-face loading and hide missing font warnings
        await cdp.send("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                CSSFontFaceRule = undefined;
                Object.defineProperty(document.body.style, 'fontFamily', { get: () => 'sans-serif', set: () => {} });
                // Override FontFace API
                if (!window._fontPatch) {
                    window._fontPatch = true;
                    const origAdd = document.fonts ? document.fonts.add : null;
                    // Block all web fonts
                    const link = document.createElement('style');
                    link.textContent = '* { font-family: sans-serif !important; }';
                    document.head.appendChild(link);
                }
            """
        })
        
        # Wait a bit for script injection
        await asyncio.sleep(1)
        
        # Use CDP to capture screenshot
        print("Capturing screenshot via CDP...")
        result = await cdp.send("Page.captureScreenshot", {"format": "png"})
        
        import base64
        screenshot_data = base64.b64decode(result['data'])
        with open('/root/.openclaw/workspace/screenshot.png', 'wb') as f:
            f.write(screenshot_data)
        
        print("Screenshot saved via CDP!")
        await browser.close()

asyncio.run(screenshot())
