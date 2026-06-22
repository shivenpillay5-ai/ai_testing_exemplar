"""IssueDetailPage — EXAMPLE detail/workflow Page Object.

Drives the detail panel that opens when you open a row from IssuePage. Demonstrates the
workflow patterns: open detail, edit/save, reload-and-verify-persistence, read-only checks,
dropdown options, date-picker selection, tab content, grid-tab data guards, and cleanup.

Selectors are illustrative — repoint them at your real application's DOM.
"""
import pytest
from playwright.async_api import Page, expect

DETAIL = "[data-panel='issue-detail']"


class IssueDetailPage:
    def __init__(self, page: Page):
        self.page = page

    @property
    def _detail(self):
        return self.page.locator(f"{DETAIL}:not([hidden])").first

    def _field(self, name: str):
        return self._detail.get_by_label(name)

    # ---------------------------------------------------------------- open / load

    async def open_detail_for_first_row(self):
        """Open the detail panel for the first grid row.

        Some apps open the panel via a server round-trip with no observable DOM signal; if so,
        a short settle belongs HERE (inside the page method), not in the test.
        """
        await self.page.locator("[role='row'][data-rowindex='0']").dblclick()
        await self.page.wait_for_timeout(1000)  # detail panel server round-trip has no DOM signal
        await self.verify_detail_loaded()

    async def verify_detail_loaded(self):
        await expect(self._detail).to_be_visible(timeout=15_000)

    async def verify_header(self, expected: str):
        header = self._detail.get_by_role("heading")
        await expect(header.first).to_have_text(expected, timeout=10_000)

    # ---------------------------------------------------------------- field checks

    async def verify_field_is_editable(self, name: str):
        field = self._field(name)
        await expect(field).to_be_editable(timeout=10_000)

    async def verify_field_is_readonly(self, name: str):
        field = self._field(name)
        await expect(field).not_to_be_editable(timeout=10_000)
        # A read-only field should also reject keyboard edits.
        before = await field.input_value()
        await field.press_sequentially("X", timeout=2_000)
        after = await field.input_value()
        assert before == after, f"Read-only field {name!r} accepted an edit ({before!r} -> {after!r})"

    async def verify_editable_fields(self, fields: list[str]):
        for name in fields:
            await self.verify_field_is_editable(name)

    async def verify_readonly_fields(self, fields: list[str]):
        for name in fields:
            await self.verify_field_is_readonly(name)

    async def verify_field_value(self, name: str, expected: str):
        field = self._field(name)
        actual = await field.input_value()
        assert actual == expected, f"Field {name!r}: expected {expected!r}, got {actual!r}"

    # ---------------------------------------------------------------- edit / save / reload

    async def edit_field_and_save(self, name: str, value: str):
        field = self._field(name)
        await field.fill(value)
        await self._detail.get_by_role("button", name="Save").click()
        await self._verify_save_confirmed()

    async def _verify_save_confirmed(self):
        toast = self.page.get_by_text("Saved", exact=False)
        await expect(toast.first).to_be_visible(timeout=10_000)

    async def reload_detail(self):
        await self._detail.get_by_role("button", name="Reload").click()
        await self.verify_detail_loaded()

    # ---------------------------------------------------------------- dropdowns / dates

    async def verify_dropdown_opens_with_options(self, name: str, expected_options: list[str]):
        dropdown = self._field(name)
        await dropdown.click()
        listbox = self.page.get_by_role("listbox")
        await expect(listbox).to_be_visible(timeout=10_000)
        for option in expected_options:
            await expect(listbox.get_by_text(option, exact=True)).to_be_visible()
        await self.page.keyboard.press("Escape")

    async def verify_datepicker_picks_date(self, name: str):
        """Actually select a date and assert the field value CHANGED.

        Never merely assert the calendar opened and closed — that is not a meaningful check.
        """
        field = self._field(name)
        before = await field.input_value()
        await field.click()
        calendar = self.page.locator(".calendar[role='dialog'], [role='dialog'].calendar").first
        await expect(calendar).to_be_visible(timeout=10_000)
        # Pick a selectable day that is not the currently-selected one.
        await calendar.locator("[role='gridcell']:not([aria-disabled='true'])").first.click()
        after = await field.input_value()
        assert after and after != before, (
            f"Date picker for {name!r} did not change the value (still {before!r})"
        )

    # ---------------------------------------------------------------- tabs / grid tabs

    async def select_tab(self, tab: str):
        await self._detail.get_by_role("tab", name=tab).click()

    async def verify_tab_selected(self, tab: str):
        await expect(self._detail.get_by_role("tab", name=tab)).to_have_attribute(
            "aria-selected", "true", timeout=10_000
        )

    async def verify_tab_content_visible(self, tab: str):
        await expect(self._detail.get_by_role("tabpanel")).to_be_visible(timeout=10_000)

    async def section_has_grid_rows(self, section: str) -> bool:
        rows = self._detail.locator(f"[data-section='{section}'] [role='row']")
        return await rows.count() > 0

    # ---------------------------------------------------------------- cleanup / nav

    async def return_to_list(self):
        """Close the detail panel and confirm the list grid is back (required cleanup)."""
        await self._detail.get_by_role("link", name="Issues").click()
        await expect(self._detail).to_be_hidden(timeout=10_000)
