from playwright.sync_api import sync_playwright
import time
from markdownify import markdownify as md


with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="/Users/mac/Library/Application Support/Google/Chrome/Default",
        channel="chrome",
        headless=False,
        # args=["--disable-blink-features=AutomationControlled"]
    )

    page = browser.new_page()
    page.goto("https://www.jobsearch.com.au/jobs?q=Software+Developer")

    # Wait for challenge iframe to appear
    frame = None
    for _ in range(10):
        for f in page.frames:
            if "challenge" in f.url or "turnstile" in f.url:
                frame = f
                break
        if frame:
            break
        time.sleep(1)

    if not frame:
        print("No challenge iframe found – page likely already verified.")
    else:
        print("Challenge iframe detected.")

        try:
            checkbox = frame.locator("input[type='checkbox']")
            checkbox.click(force=True)
            print("Checkbox clicked.")
        except Exception as e:
            print("Failed to click checkbox:", e)

        # Wait for verification to finish
        page.wait_for_load_state("networkidle")

    # Extract HTML
    html_content = page.content()

    with open("page_content.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML extracted and saved to page_content.html")

    with open("page_content.html", "r", encoding="utf-8") as f:
        html = f.read()

    markdown_output = md(html, heading_style="ATX")

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print("Markdown saved to output.md")


browser.close()
