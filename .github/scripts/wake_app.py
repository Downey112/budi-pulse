"""Open the Streamlit app in a real browser so Community Cloud counts it as a visit.

A plain HTTP request only receives a redirect and never starts the app, so it
does not reset the inactivity timer or wake a sleeping app.

After waking, Community Cloud sometimes leaves the page stuck on its loading
screen even once the app is ready, so the page is reloaded if the app has not
appeared after RELOAD_AFTER_SECONDS.
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

APP_URL = os.environ.get("APP_URL", "https://budi-pulse.streamlit.app/")
WAKE_BUTTON = "get this app back up"
TIMEOUT_SECONDS = 780
RELOAD_AFTER_SECONDS = 120


def app_is_running(page) -> bool:
    # The app is served inside an iframe, so check every frame
    for frame in page.frames:
        try:
            if frame.locator('[data-testid="stApp"]').count() > 0:
                return True
        except Exception:
            continue
    return False


def open_app(page) -> None:
    try:
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=60_000)
    except Exception as exc:  # a slow load is retried by the next reload
        print(f"[WARN] Page load failed: {exc}")


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
        )
        page = browser.new_page()
        open_app(page)

        woke = False
        start = time.time()
        last_load = start
        while time.time() - start < TIMEOUT_SECONDS:
            if app_is_running(page):
                # Stay connected briefly so the session registers as traffic
                page.wait_for_timeout(10_000)
                waited = int(time.time() - start)
                print(f"[SUCCESS] App is running after {waited}s{' (woken from sleep)' if woke else ''}.")
                browser.close()
                return 0

            button = page.get_by_role("button", name=WAKE_BUTTON)
            if button.count() > 0:
                print("[INFO] App is asleep. Clicking the wake button...")
                button.first.click()
                woke = True
                last_load = time.time()
            elif time.time() - last_load > RELOAD_AFTER_SECONDS:
                print("[INFO] App still loading. Reloading the page...")
                open_app(page)
                last_load = time.time()

            page.wait_for_timeout(5_000)

        print(f"[ERROR] App did not come up within {TIMEOUT_SECONDS}s. Final URL: {page.url}")
        browser.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
