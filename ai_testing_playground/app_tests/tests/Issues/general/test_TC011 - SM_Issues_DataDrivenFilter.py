"""Data-driven example — one column-filter test case per row in a CSV fixture.

This is the worked example referenced by `app_tests/test_data/README.md`. It shows the pattern
for parametrizing a test from an external data file while still obeying every handbook rule:

  * The CSV lives in `app_tests/test_data/` (screen-specific fixtures go there).
  * Loading/parsing the data is plain setup at module scope — it is NOT assertion or locator
    logic, so it is allowed in a test file.
  * `@pytest.mark.parametrize` turns each row into its own test case, so one bad row of data is
    an isolated failure, not a hidden one.
  * The test body stays a thin workflow: navigate -> act -> verify. Every locator and every
    assertion still lives in `IssuePage` (`filter_column`, `verify_column_filter_results`).

Run just these cases:  pytest -k "DataDrivenFilter"
"""
import csv
from pathlib import Path

import pytest
from playwright.async_api import Page

from app_tests.pages.navigation import NavigationPage
from app_tests.pages.Issues.IssuePage import IssuePage

# Resolve the fixture relative to the repo so the path works from any CWD.
TEST_DATA_DIR = Path(__file__).resolve().parents[3] / "test_data"
FILTER_CASES_CSV = TEST_DATA_DIR / "issue_filters.csv"


def _load_filter_cases():
    """Read the CSV into a list of pytest params, one per data row.

    Pure data loading — no Playwright, no assertions. Keeping this at module scope means the
    cases are expanded at collection time, so each row shows up as its own test id.
    """
    with FILTER_CASES_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [
        pytest.param(int(row["column_index"]), row["filter_term"], id=row["case_id"])
        for row in rows
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("column_index, filter_term", _load_filter_cases())
async def test_TC011_SM_Issues_DataDrivenFilter(
    logged_in_page: Page, column_index: int, filter_term: str
):
    nav = NavigationPage(logged_in_page)
    page = IssuePage(logged_in_page)

    await nav.navigate_to_issues()
    await page.verify_page_loaded()
    await page.click_clear_filters()
    await page.skip_if_no_records()

    original = await page.capture_paging_text()
    await page.filter_column(column_index, filter_term)
    await page.verify_column_filter_results(column_index, original, filter_term)
