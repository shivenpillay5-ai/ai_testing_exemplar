import pytest
from playwright.async_api import Page

from app_tests.pages.navigation import NavigationPage
from app_tests.pages.Issues.IssuePage import IssuePage


@pytest.mark.asyncio
async def test_TC005_SM_Issues_NextPage(logged_in_page: Page):
    nav = NavigationPage(logged_in_page)
    page = IssuePage(logged_in_page)

    await nav.navigate_to_issues()
    await page.verify_page_loaded()
    await page.click_clear_filters()
    await page.skip_if_no_records()
    await page.change_page_size(20)
    await page.skip_if_single_page()

    initial_text = await page.capture_paging_text()
    await page.go_to_next_page()
    await page.verify_next_page_navigated(initial_text)
