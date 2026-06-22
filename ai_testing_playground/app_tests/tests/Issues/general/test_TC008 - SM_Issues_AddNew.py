import pytest
from playwright.async_api import Page

from app_tests.pages.navigation import NavigationPage
from app_tests.pages.Issues.IssuePage import IssuePage


@pytest.mark.asyncio
async def test_TC008_SM_Issues_AddNew(logged_in_page: Page):
    nav = NavigationPage(logged_in_page)
    page = IssuePage(logged_in_page)

    await nav.navigate_to_issues()
    await page.verify_page_loaded()
    await page.click_add_new()
    await page.verify_add_new_dialog_open()
    await page.close_dialog()
