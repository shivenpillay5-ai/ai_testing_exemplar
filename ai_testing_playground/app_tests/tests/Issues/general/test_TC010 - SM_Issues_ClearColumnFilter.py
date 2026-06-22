import pytest
from playwright.async_api import Page

from app_tests.pages.navigation import NavigationPage
from app_tests.pages.Issues.IssuePage import IssuePage

COL_IDX = 0
FILTER_TERM = "A"


@pytest.mark.asyncio
async def test_TC010_SM_Issues_ClearColumnFilter(logged_in_page: Page):
    nav = NavigationPage(logged_in_page)
    page = IssuePage(logged_in_page)

    await nav.navigate_to_issues()
    await page.verify_page_loaded()
    await page.click_clear_filters()
    await page.skip_if_no_records()

    original = await page.capture_paging_text()
    await page.filter_column(COL_IDX, FILTER_TERM)
    await page.clear_column_filter(COL_IDX)
    await page.verify_column_filter_cleared(original, COL_IDX)
