"""IssuePage — EXAMPLE list/grid Page Object.

This is the worked example that the General Screen Functionality (GSF) tests drive. It shows
the reusable patterns every list/grid page object in your suite should follow:

  * a `_panel` property that scopes locators to the visible grid panel
  * all selectors and assertions live HERE, never in the test files
  * actions and assertions are separate methods (`click_export` vs `verify_export_dialog_open`)
  * data guards (`skip_if_no_records`, `skip_if_single_page`) raise classified pytest.skip
  * pagination waits use an anchored regex, not a substring match

The selectors below are illustrative. Repoint them at your real application's DOM.
"""
import re

import pytest
from playwright.async_api import Page, expect

# --- Selectors (centralised so a UI change is a one-line edit) ---
PANEL = "[data-screen='issues']"          # the visible screen/grid container
GRID = "[role='grid']"
PAGING_LABEL = ".paging-label"
ROW = "[role='row']"
CELL = "[role='gridcell']"


class IssuePage:
    def __init__(self, page: Page):
        self.page = page

    @property
    def _panel(self):
        """Scope to the visible screen panel so hidden duplicate DOM never causes ambiguity."""
        return self.page.locator(f"{PANEL}:not([hidden])").first

    # ---------------------------------------------------------------- load checks

    async def verify_page_loaded(self):
        await expect(self._panel).to_be_visible(timeout=15_000)
        title = self._panel.get_by_role("heading", name="Issues")
        await expect(title).to_be_visible(timeout=15_000)

    async def verify_grid_loaded(self):
        """Wait for the paging label to stabilise, then assert a real row range or empty state.

        Do NOT count rows first — wait for the label, then branch on its text.
        """
        label = self._panel.locator(PAGING_LABEL)
        await expect(label).to_have_text(
            re.compile(r"\d+\s+to\s+\d+|No Records Found"), timeout=15_000
        )

    async def verify_paging_label(self):
        label = self._panel.locator(PAGING_LABEL)
        await expect(label).to_be_visible(timeout=10_000)
        text = (await label.inner_text()).strip()
        assert re.search(r"\d+\s+to\s+\d+|No Records Found", text), (
            f"Paging label is malformed: {text!r}"
        )

    # ---------------------------------------------------------------- data guards

    async def skip_if_no_records(self):
        label = self._panel.locator(PAGING_LABEL)
        await expect(label).to_be_visible(timeout=10_000)
        if "No Records Found" in (await label.inner_text()):
            pytest.skip("NA_DATA: grid has no records — data-dependent test not applicable")

    async def skip_if_single_page(self):
        text = await self._panel.locator(PAGING_LABEL).inner_text()
        match = re.search(r"(\d+)\s+to\s+(\d+)\s+of\s+(\d+)", text)
        if match and int(match.group(3)) <= int(match.group(2)):
            pytest.skip("NA_DATA: only one page of results — pagination test not applicable")

    # ---------------------------------------------------------------- toolbar actions

    async def click_clear_filters(self):
        await self._panel.get_by_role("button", name="Clear Filters").click()
        await self.verify_grid_loaded()

    async def click_refresh(self):
        await self._panel.get_by_role("button", name="Refresh").click()

    async def click_export(self):
        await self._panel.get_by_role("button", name="Export").click()

    async def verify_export_dialog_open(self):
        dialog = self.page.get_by_role("dialog")
        await expect(dialog).to_be_visible(timeout=10_000)
        await expect(dialog.get_by_text("Export", exact=True)).to_be_visible()

    async def click_add_new(self):
        await self._panel.get_by_role("button", name="Add").click()

    async def verify_add_new_dialog_open(self):
        dialog = self.page.get_by_role("dialog")
        await expect(dialog).to_be_visible(timeout=10_000)

    async def close_dialog(self):
        await self.page.keyboard.press("Escape")
        await expect(self.page.get_by_role("dialog")).to_be_hidden(timeout=5_000)

    async def toggle_select_all_checkbox(self):
        checkbox = self._panel.locator("thead input[type='checkbox']").first
        await expect(checkbox).to_be_visible(timeout=10_000)
        await checkbox.click()
        await expect(checkbox).to_be_checked()

    # ---------------------------------------------------------------- pagination

    async def change_page_size(self, size: int):
        await self._panel.get_by_label("Page size").select_option(str(size))
        await self.verify_grid_loaded()

    async def _paging_text(self) -> str:
        return (await self._panel.locator(PAGING_LABEL).inner_text()).strip()

    async def wait_for_paging_text_change(self, current_text: str):
        """Wait for the paging label to become genuinely different.

        Uses an anchored regex — a substring check like not_to_have_text("1 to 50 of") would be
        satisfied by "1 to 50 of 100" and return immediately without a real page change.
        """
        label = self._panel.locator(PAGING_LABEL)
        pattern = re.compile(r"^\s*" + re.escape(current_text.strip()) + r"\s*$")
        await expect(label).not_to_have_text(pattern, timeout=15_000)

    async def go_to_first_page(self):
        text = await self._paging_text()
        await self._panel.get_by_role("button", name="First page").click()
        await self.wait_for_paging_text_change(text)

    async def go_to_last_page(self):
        text = await self._paging_text()
        await self._panel.get_by_role("button", name="Last page").click()
        await self.wait_for_paging_text_change(text)

    async def go_to_next_page(self):
        text = await self._paging_text()
        await self._panel.get_by_role("button", name="Next page").click()
        await self.wait_for_paging_text_change(text)

    async def go_to_previous_page(self):
        text = await self._paging_text()
        await self._panel.get_by_role("button", name="Previous page").click()
        await self.wait_for_paging_text_change(text)

    async def capture_paging_text(self) -> str:
        return await self._paging_text()

    # --- directional pagination assertions (specific outcome, not "something changed") ---

    async def verify_on_first_page(self):
        text = await self._paging_text()
        assert text.startswith("1 to"), f"Expected to be on the first page, paging label was {text!r}"

    async def verify_next_page_navigated(self, initial_text: str):
        old = re.search(r"(\d+)\s+to\s+(\d+)", initial_text)
        new = re.search(r"(\d+)\s+to\s+(\d+)", await self._paging_text())
        assert old and new, f"Could not parse paging text (old={initial_text!r})"
        assert int(new.group(1)) == int(old.group(2)) + 1, (
            f"Next page should start one past the previous end: old={initial_text!r}"
        )

    async def verify_previous_page_navigated(self, from_text: str):
        captured = re.search(r"(\d+)\s+to\s+(\d+)", from_text)
        new = re.search(r"(\d+)\s+to\s+(\d+)", await self._paging_text())
        assert captured and new, f"Could not parse paging text (from={from_text!r})"
        assert int(new.group(2)) < int(captured.group(1)), (
            f"Previous page end should be before the captured start: from={from_text!r}"
        )

    async def verify_last_page_navigated(self, initial_text: str):
        initial = re.search(r"(\d+)\s+to\s+(\d+)", initial_text)
        new = re.search(r"(\d+)\s+to\s+(\d+)", await self._paging_text())
        assert initial and new, f"Could not parse paging text (initial={initial_text!r})"
        assert int(new.group(1)) > int(initial.group(1)), (
            f"Last page start should be greater than the initial start: initial={initial_text!r}"
        )

    # ---------------------------------------------------------------- column filtering

    async def filter_column(self, col_idx: int, term: str):
        cell = self._panel.locator(".filter-row .filter-input").nth(col_idx)
        await cell.fill(term)
        # Many grids only commit a filter on blur — click elsewhere to trigger it.
        await self._panel.locator(GRID).click(position={"x": 10, "y": 10})

    async def clear_column_filter(self, col_idx: int):
        cell = self._panel.locator(".filter-row .filter-input").nth(col_idx)
        await cell.fill("")
        await self._panel.locator(GRID).click(position={"x": 10, "y": 10})

    async def get_column_values_by_index(self, col_idx: int) -> list[str]:
        cells = self._panel.locator(f"{ROW} {CELL}:nth-child({col_idx + 1})")
        return [c.strip() for c in await cells.all_inner_texts()]

    async def verify_filter_applied(self, original: str, filtered: str):
        assert filtered != original, (
            f"Filter did not change the grid (still {original!r})"
        )

    async def verify_filter_cleared(self, original: str, restored: str):
        assert restored == original, (
            f"Clearing the filter did not restore the baseline (was {original!r}, now {restored!r})"
        )

    async def verify_no_results(self):
        text = await self._paging_text()
        assert "No Records Found" in text or " 0 " in f" {text} ", (
            f"Expected an empty result set, paging label was {text!r}"
        )

    async def verify_column_filter_results(self, col_idx: int, original: str, term: str):
        filtered = await self._paging_text()
        assert filtered != original, f"Column filter did not change the grid (still {original!r})"
        values = await self.get_column_values_by_index(col_idx)
        assert values, "No visible cells to validate after filtering"
        for value in values:
            assert term.lower() in value.lower(), (
                f"Cell {value!r} does not contain the filter term {term!r}"
            )

    async def verify_column_filter_cleared(self, original: str, col_idx: int):
        restored = await self._paging_text()
        assert restored == original, (
            f"Clearing the column filter did not restore the baseline "
            f"(was {original!r}, now {restored!r})"
        )
