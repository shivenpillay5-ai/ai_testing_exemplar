"""Single place that knows how to authenticate the application under test.

Replace the selectors below with your real login form. This is the ONLY file that should
know how login works — every test reuses the session it establishes (see conftest.py).
"""
import os

from playwright.async_api import Page, expect

BASE_URL = os.getenv("APP_BASE_URL")
USERNAME = os.getenv("APP_USERNAME")
PASSWORD = os.getenv("APP_PASSWORD")


async def login_to_app(page: Page) -> None:
    """Navigate to the app and sign in.

    EXAMPLE implementation — adapt the selectors to your application's login form.
    """
    if not BASE_URL:
        raise EnvironmentError("APP_BASE_URL is missing — copy .env.example to .env and fill it in.")

    await page.goto(BASE_URL, wait_until="domcontentloaded")

    # --- Adapt these three lines to your login form ---
    await page.get_by_label("Username").fill(USERNAME or "")
    await page.get_by_label("Password").fill(PASSWORD or "")
    await page.get_by_role("button", name="Sign In").click()

    # Wait for something that only exists once you're authenticated (the app shell).
    await expect(page.get_by_role("button", name="Menu")).to_be_visible(timeout=30_000)
