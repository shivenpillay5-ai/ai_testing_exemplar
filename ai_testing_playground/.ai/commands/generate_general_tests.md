---
name: generate_general_tests
description: Generate a General Screen Functionality test suite for a screen, using live DOM inspection via Playwright MCP.
---

# /generate_general_tests

You are an autonomous test-generation agent. Navigate to the live application via Playwright
MCP, inspect a screen's live DOM, and generate a complete General Screen Functionality (GSF)
suite that obeys `.ai/handbook.md` and the patterns in
`.ai/prompts/general_screen_functionality.md`.

Complete all steps for one screen before moving to the next.

**Before Step 0:** record the current time as `START_TIME` (e.g. `date "+%Y-%m-%d %H:%M:%S"`)
for the final summary.

## Step 0 — Authenticate via Playwright MCP
Read `.env` for `APP_BASE_URL`, `APP_USERNAME`, `APP_PASSWORD`. `browser_navigate` to the URL;
if a login form is present, fill it and submit; wait for the app shell. Do not re-authenticate
between screens — the MCP session persists.

## Step 1 — Identify the screen(s)
If a screen name was provided, use it. Otherwise scan `app_tests/tests/` for screen folders
that lack a `general/` suite, print the candidates, and ask which to generate. Wait for confirmation.

## Step 2 — Locate / create the target folder
Resolve `app_tests/tests/<Domain>/<Screen>/general/` (create it + an `__init__.py` if missing).
Derive the `Domain` from the path and the test `PREFIX` from your project's module table.

## Step 3 — Read the rules
Read `.ai/prompts/general_screen_functionality.md` in full and follow the hard rules from
`.ai/handbook.md` (no asserts/locators in tests; everything in the page class).

## Step 4 — Inspect the live DOM
Navigate to the screen (use `navigation.py` to find the path; browse the menu via snapshots if
the method doesn't exist yet). Confirm it's a standard list/grid screen. Then run **one**
`browser_evaluate` that returns a small structured object: which controls are present
(grid, paging label, pagination, page-size, column filters, clear-filters, refresh, density,
add-new, export, settings, dropdowns) and the column inventory (index, label, isNumeric).
Build the test list from what's present. Pick `COL_IDX`/`FILTER_TERM` (first non-numeric column).

## Step 5 — Create / update the page class
`app_tests/pages/<Domain>/<Screen>Page.py`. If it exists, add only missing methods. If not,
create it from the example `IssuePage.py`, replicating `_panel`, `verify_grid_loaded()`,
the pagination/filter helpers, and the directional `verify_*` methods.

## Step 6 — Update navigation
Add `navigate_to_<screen_snake_case>()` to `navigation.py` if missing.

## Step 7 — Generate the test files
`test_TC001`, `test_TC002`, … with no gaps, in the standard order from the prompt, only for
controls confirmed present. Each file imports only `pytest`, `Page`, and the page/navigation
classes; contains zero asserts and zero locators; calls `verify_page_loaded()` after navigation.

## Step 8 — Validate & report
Run the new suite (or a canary subset). Fix repeated same-cause failures. Then output:
1. Run metrics (start/end/elapsed, files, LOC, LOC/min).
2. Screens processed (screen, domain, test count).
3. Files created; screens skipped (already had tests); screens blocked (with reason).
Record the changed files in `CHANGELOG.md`.
