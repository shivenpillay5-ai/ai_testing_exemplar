# Prompt: General Screen Functionality (GSF) generation patterns

Authoritative implementation patterns for generating a **General Screen Functionality** suite
for a list/grid screen. The orchestration (which screen, where to write files, how to report)
lives in `.ai/commands/generate_general_tests.md`. The global rules live in `.ai/handbook.md`.

> Generate a test **only** for a control that is actually present on the live screen. Inspect
> the live DOM first — never assume a button/feature exists.

---

## Before you begin

1. Confirm the screen is a standard list/grid screen (it has a data grid + toolbar). If not,
   report it as needing bespoke tests and stop.
2. Inspect the live DOM (via Playwright MCP `browser_evaluate`) and build an inventory of which
   controls exist: grid, paging label, pagination buttons, page-size selector, column filters,
   clear-filters, refresh, density/column-layout, add-new, export, settings, any dropdowns.
3. Build the test list from what is present.

## Step 1 — Page class

Create or update `app_tests/pages/<Domain>/<Screen>Page.py`. All interaction and assertion
methods for the screen live here. Use a `_panel` property to scope to the **visible** grid
panel so hidden duplicate DOM doesn't cause ambiguous matches.

Methods every list/grid page class needs (names are part of the contract):

- `verify_page_loaded()` — the screen's shell/title/toolbar is visible.
- `verify_grid_loaded()` — wait for the paging label to stabilise, then assert it shows a
  real row range (e.g. `\d+\s+to\s+\d+`) **or** an explicit empty state. Don't count rows first.
- `verify_paging_label()` — the paging label is present and well-formed.
- `change_page_size(n)` — set the grid page size.
- `skip_if_no_records()` — `pytest.skip("NA_DATA: ...")` when the grid is empty.
- `skip_if_single_page()` — `pytest.skip("NA_DATA: ...")` when there's only one page.
- `wait_for_paging_text_change(current_text)` — after a pagination click, wait for the label to
  become genuinely different. **Use an anchored regex**, not a substring/`not_to_have_text`
  on a prefix — `"1 to 50 of"` is satisfied by `"1 to 50 of 100"` and would return immediately:
  ```python
  async def wait_for_paging_text_change(self, current_text: str):
      label = self._panel.locator("<paging-label-selector>")
      pattern = re.compile(r"^\s*" + re.escape(current_text.strip()) + r"\s*$")
      await expect(label).not_to_have_text(pattern, timeout=15000)
  ```
- `click_clear_filters()`, `click_refresh()`, `click_export()`, `click_add_new()`,
  `click_search_settings()` + matching `verify_*_dialog_open()` / close methods.
- `filter_column(col_idx, term)` / `clear_column_filter(col_idx)` — apply/clear a column filter.
  If your grid only commits a filter on **blur**, trigger it explicitly (click elsewhere) — do
  not rely on Enter/Tab. (See `docs/vaadin-selector-appendix.md` for the Vaadin specifics.)
- `get_column_values_by_index(col_idx)` — read visible cell values for content validation.

Pagination assertions are directional and live on the page class:

- `verify_on_first_page()` → paging text starts with `"1 to"`.
- `verify_next_page_navigated(initial_text)` → new "from" == old "to" + 1.
- `verify_previous_page_navigated(text)` → new "to" < captured "from".
- `verify_last_page_navigated(initial_text)` → new "from" > initial "from".
- `verify_filter_applied(original, filtered)` → `filtered != original`.
- `verify_filter_cleared(original, restored)` → `restored == original`.
- `verify_no_results()` → empty-state text / "0" in the paging label.
- `verify_column_filter_results(col_idx, original, term)` → every visible cell in that column
  contains `term` (parse the range with `re.search`, never compare raw strings).

## Step 2 — Navigation

Add `navigate_to_<screen_snake_case>()` to `navigation.py` if missing, following the existing
pattern (open menu → hover module → click screen).

## Step 3 — Test files

Path: `app_tests/tests/<Domain>/general/`. Naming:
- File: `test_TC0NN - <PREFIX>_<Screen>_<Feature>.py`
- Function: `test_TC0NN_<PREFIX>_<Screen>_<Feature>`
- Increment with **no gaps**.

Each test:
- Imports only `pytest`, `Page`, and the page/navigation classes — never `expect` or `re`.
- Zero `assert` statements, zero locators.
- Navigates, calls `verify_page_loaded()`, then performs exactly one piece of functionality.

## Standard test order (generate only those whose control is present)

1. **PageLoad** — navigate → `verify_page_loaded()`
2. **GridLoaded** — `click_clear_filters()` → `verify_grid_loaded()`
3. **PagingLabel** — `click_clear_filters()` → `verify_paging_label()`
4. **SelectAllCheckbox** — wait for grid data → `toggle_select_all_checkbox()`
5. **Dropdowns** (entity/template/etc.) — `verify_<name>_dropdown_visible()`
6. **AdvancedFilter** — `open_advanced_filter_popup()`
7. **FirstPage** — page-size → `skip_if_single_page()` → go last → go first → `verify_on_first_page()`
8. **PreviousPage / NextPage / LastPage** — analogous, with `wait_for_paging_text_change` between clicks
9. **RefreshButton** — `click_clear_filters()` → `click_refresh()` → `verify_grid_loaded()`
10. **ColumnLayout** — clear → `verify_grid_loaded()` → change density → `verify_grid_loaded()`
11. **ClearFilters** — clear → `skip_if_no_records()` → filter → `verify_filter_applied()` → clear → `verify_filter_cleared()`
12. **AddNew** — `click_add_new()` → `verify_add_new_dialog_open()`
13. **SettingsButton** — open → verify → close
14. **ExportButton** — `click_export()` → `verify_export_dialog_open()`
15. **FilterByColumn** — clear → skip-if-empty → filter → `verify_column_filter_results()`
16. **FilterNoResults** — clear → skip-if-empty → filter with an impossible term → `verify_no_results()`
17. **ClearColumnFilter** — clear → skip-if-empty → filter → clear column filter → `verify_column_filter_cleared()`
18. **DateFilter** *(only if a date column filter exists)* — select a date via the calendar widget
    (never type a raw date string) → `verify_date_filter_results()`

## Choosing the filter column

Filtering a **numeric** column with a letter returns zero rows and produces a misleading pass.
Before generating filter tests, inspect column headers: pick the first **non-numeric** column
as `COL_IDX` with `FILTER_TERM = "A"`. If all columns are numeric, use `COL_IDX = 0` with a
`FILTER_TERM` value you can see in the live data. Use the same `COL_IDX`/`FILTER_TERM` across
ClearFilters, FilterByColumn, and ClearColumnFilter.
