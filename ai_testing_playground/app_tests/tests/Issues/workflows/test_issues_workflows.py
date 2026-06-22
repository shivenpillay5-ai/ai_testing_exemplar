"""Issues workflow suite (EXAMPLE) — generated from .ai/prompts/sub-page-workflows/Issues.md

Atomic format: one pytest case per blueprint entry, so one data-dependent skip never hides
unrelated coverage. The only helpers permitted in a test file are pure navigation setup (below)
and pytest.skip() data guards — everything else lives in the page objects.
"""
import pytest
from playwright.async_api import Page

from app_tests.pages.navigation import NavigationPage
from app_tests.pages.Issues.IssuePage import IssuePage
from app_tests.pages.Issues.IssueDetailPage import IssueDetailPage


# --- navigation setup helper (permitted: no asserts, no locators) ---
async def open_issue_detail(page: Page) -> IssueDetailPage:
    nav = NavigationPage(page)
    issue_list = IssuePage(page)
    detail = IssueDetailPage(page)

    await nav.navigate_to_issues()
    await issue_list.verify_page_loaded()
    await issue_list.click_clear_filters()
    await issue_list.skip_if_no_records()
    await detail.open_detail_for_first_row()
    return detail


@pytest.mark.asyncio
async def test_TC001_SM_Issues_WF01_open_detail(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)
    await detail.verify_detail_loaded()
    await detail.return_to_list()


@pytest.mark.asyncio
async def test_TC002_SM_Issues_HP02_edit_description_persists(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)
    await detail.edit_field_and_save("Description", "Updated by automation")
    await detail.reload_detail()
    await detail.verify_field_value("Description", "Updated by automation")
    await detail.return_to_list()


@pytest.mark.asyncio
async def test_TC003_SM_Issues_UI03_code_is_readonly(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)
    await detail.verify_field_is_readonly("Code")
    await detail.return_to_list()


@pytest.mark.asyncio
async def test_TC004_SM_Issues_SD04_status_dropdown_options(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)
    await detail.verify_dropdown_opens_with_options(
        "Status", ["Open", "In Progress", "Resolved", "Closed"]
    )
    await detail.return_to_list()


@pytest.mark.asyncio
async def test_TC005_SM_Issues_DT05_due_date_picker(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)
    await detail.verify_datepicker_picks_date("Due Date")
    await detail.return_to_list()


@pytest.mark.asyncio
async def test_TC006_SM_Issues_TB06_history_tab(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)
    await detail.select_tab("History")
    await detail.verify_tab_selected("History")
    await detail.verify_tab_content_visible("History")
    await detail.return_to_list()


@pytest.mark.asyncio
async def test_TC007_SM_Issues_NAV07_back_to_list(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)
    await detail.return_to_list()
