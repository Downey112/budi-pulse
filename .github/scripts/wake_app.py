"""Open the Streamlit app in a real browser so Community Cloud counts it as a visit.

A plain HTTP request only receives a redirect and never starts the app, so it
does not reset the inactivity timer or wake a sleeping app.
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

APP_URL = os.environ.get("APP_URL", "https://budi-pulse.streamlit.app/")
WAKE_BUTTON = "get this app back up"
TIMEOUT_SECONDS = 300


def app_is_running(page) -> bool:
    # The app is served inside an iframe, so check every frame
    for frame in page.frames:
        try:
            if frame.locator('[data-testid="stApp"]').count() > 0:
                return True
        except Exception:
            continue
    return False


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=60_000)

        woke = False
        deadline = time.time() + TIMEOUT_SECONDS
        while time.time() < deadline:
            if app_is_running(page):
                # Stay connected briefly so the session registers as traffic
                page.wait_for_timeout(10_000)
                print(f"[SUCCESS] App is running{' (woken from sleep)' if woke else ''}.")
                browser.close()
                return 0

            button = page.get_by_role("button", name=WAKE_BUTTON)
            if not woke and button.count() > 0:
                print("[INFO] App was asleep. Clicking the wake button...")
                button.first.click()
                woke = True

            page.wait_for_timeout(5_000)

        print(f"[ERROR] App did not come up within {TIMEOUT_SECONDS}s. Final URL: {page.url}")
        browser.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
