"""Shared Playwright + pytest lifecycle.

The suite logs in ONCE per run, saves the authenticated storage state, and reuses it for every
test via the `logged_in_page` fixture. This keeps tests fast and independent of the login flow.
"""
import os
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, async_playwright

from .pages.login import login_to_app

load_dotenv()

REPORTS_DIR = Path("reports")

HOME_URL = os.getenv("APP_BASE_URL")
if not HOME_URL:
    raise EnvironmentError("APP_BASE_URL is missing — copy .env.example to .env and fill it in.")

STORAGE_STATE_FILE = "playwright_state.json"
POST_TEST_SETTLE_MS = int(os.getenv("POST_TEST_SETTLE_MS", "500"))
HOME_NAVIGATION_ATTEMPTS = int(os.getenv("HOME_NAVIGATION_ATTEMPTS", "3"))
HOME_NAVIGATION_TIMEOUT_MS = int(os.getenv("HOME_NAVIGATION_TIMEOUT_MS", "45000"))


def pytest_addoption(parser):
    parser.addoption(
        "--debug-ui",
        action="store_true",
        default=False,
        help="Run with a visible browser and a pause after each test for debugging.",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Force a visible (non-headless) browser run.",
    )


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Stash each phase's report on the item so fixtures can see if the test failed."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _test_failed(request: pytest.FixtureRequest) -> bool:
    report = getattr(request.node, "rep_call", None)
    return bool(report and report.failed)


async def _start_trace(context):
    """Begin capturing a Playwright trace (screenshots + DOM snapshots) for this test."""
    await context.tracing.start(screenshots=True, snapshots=True, sources=True)


async def _finish_trace(context, page, request: pytest.FixtureRequest):
    """On failure, save a screenshot and a trace.zip into reports/ named after the test."""
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in request.node.name)
    if _test_failed(request):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        try:
            if not page.is_closed():
                await page.screenshot(path=str(REPORTS_DIR / f"{safe_name}.png"), full_page=True)
        except Exception as exc:  # never mask the real test failure
            print(f"Could not capture screenshot: {exc}")
        try:
            await context.tracing.stop(path=str(REPORTS_DIR / f"{safe_name}-trace.zip"))
        except Exception as exc:
            print(f"Could not save trace: {exc}")
    else:
        try:
            await context.tracing.stop()
        except Exception:
            pass


def browser_launch_options(request: pytest.FixtureRequest) -> dict:
    """Headless by default; visible when APP_HEADLESS=false or --headed/--debug-ui is passed."""
    headless = env_flag("APP_HEADLESS", default=True)
    if request.config.getoption("headed") or request.config.getoption("debug_ui"):
        headless = False
    default_slow_mo = 0 if headless else 100
    slow_mo = int(os.getenv("PLAYWRIGHT_SLOW_MO_MS", str(default_slow_mo)))
    return {"headless": headless, "slow_mo": slow_mo}


async def goto_home_with_retries(page):
    """Navigate to the app shell with bounded retries for transient stalls."""
    last_error = None
    for attempt in range(1, HOME_NAVIGATION_ATTEMPTS + 1):
        try:
            await page.goto(HOME_URL, wait_until="domcontentloaded", timeout=HOME_NAVIGATION_TIMEOUT_MS)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
            if attempt == HOME_NAVIGATION_ATTEMPTS:
                raise
            await page.wait_for_timeout(2000 * attempt)
    raise last_error


async def settle_after_test(page, request: pytest.FixtureRequest):
    settle_ms = 3000 if request.config.getoption("debug_ui") else POST_TEST_SETTLE_MS
    if settle_ms > 0 and not page.is_closed():
        await page.wait_for_timeout(settle_ms)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def playwright_instance():
    async with async_playwright() as p:
        yield p


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def browser(playwright_instance, request: pytest.FixtureRequest):
    browser = await playwright_instance.chromium.launch(**browser_launch_options(request))
    yield browser
    await browser.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def auth_storage_state(browser):
    """Log in once and persist the authenticated storage state for the whole run."""
    context = await browser.new_context(ignore_https_errors=True)
    page = await context.new_page()

    print("Logging in once for the test session...")
    await login_to_app(page)
    await context.storage_state(path=STORAGE_STATE_FILE)

    await context.close()
    return STORAGE_STATE_FILE


@pytest_asyncio.fixture
async def logged_in_page(request: pytest.FixtureRequest, browser, auth_storage_state):
    """Default fixture for most tests — starts authenticated at the app shell."""
    context = await browser.new_context(ignore_https_errors=True, storage_state=auth_storage_state)
    await _start_trace(context)
    page = await context.new_page()
    await goto_home_with_retries(page)

    yield page

    await settle_after_test(page, request)
    await _finish_trace(context, page, request)
    await context.close()


@pytest_asyncio.fixture
async def freshly_logged_in_page(request: pytest.FixtureRequest, browser):
    """Use only when a test specifically needs a clean login flow (not the cached session)."""
    context = await browser.new_context(ignore_https_errors=True)
    await _start_trace(context)
    page = await context.new_page()
    await login_to_app(page)

    yield page

    await settle_after_test(page, request)
    await _finish_trace(context, page, request)
    await context.close()
