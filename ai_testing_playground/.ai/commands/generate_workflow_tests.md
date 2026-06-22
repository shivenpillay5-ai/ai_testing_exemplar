---
name: generate_workflow_tests
description: Generate workflow tests (detail panel, edit/save, tabs, dropdowns, navigation) for a screen from its blueprint, using live DOM inspection via Playwright MCP.
---

# /generate_workflow_tests

You are an autonomous test-generation agent. Generate **workflow** tests for a screen, obeying
`.ai/handbook.md` and the patterns in `.ai/prompts/workflow_tests.md`.

## Step 0 — Authenticate via Playwright MCP
Read `.env` (`APP_BASE_URL`, `APP_USERNAME`, `APP_PASSWORD`); log in if needed; keep the session.

## Step 1 — Find the blueprint
Look for the screen's blueprint at `.ai/prompts/sub-page-workflows/<Screen>.md`. Each entry has
a stable id (`WF-`, `HP-`, `SD-`, `UI-`, `NAV-`, …) and a behaviour description. The authoring
format, id-prefix meanings, and a fill-in template live in
`.ai/prompts/sub-page-workflows/_TEMPLATE.md` (with `Issues.md` as a worked example).
- If a blueprint exists, use it as the workflow source.
- If none exists for a user-named screen, synthesize a **draft** from `_TEMPLATE.md` plus the
  live screen into `sub-page-workflows/_drafts/`, then stop — a draft is not an approved
  blueprint; tell the user to review/promote it (see `docs/adding-a-screen.md`, Step 6) before
  generating tests.

## Step 2 — Confirm against the live DOM
Navigate to the screen and run one targeted `browser_evaluate` guard (field-name/label counts).
Rebuild the full inventory only if the guard diverges from the blueprint.

## Step 3 — Page class
Create/update `app_tests/pages/<Domain>/<Screen>DetailPage.py` with the workflow methods from
the prompt (`open_detail_for_first_row`, `edit_field_and_save`, `verify_field_value`,
`verify_dropdown_opens_with_options`, `verify_datepicker_picks_date`, `verify_tab_selected`,
`section_has_grid_rows`, `return_to_list`, …). Field names come from the **live DOM**.

## Step 4 — Generate the test file (atomic)
`app_tests/tests/<Domain>/<Screen>/workflows/test_<screen_lower>_workflows.py`. One pytest case
per blueprint entry; function/param names carry the workflow id; zero asserts/locators in the
test; only navigation-setup and `pytest.skip()` helpers allowed.

## Step 5 — Validate (gate)
Run the file or a representative canary set (list load, detail open, field checks, one edit/save,
one date-picker save, one dropdown, one navigation). Then audit skips: convert deterministic
states to passing assertions; reserve classified `pytest.skip()` for genuinely unassertable
cases. **`HP-*` happy paths must pass** — if no honest passing path exists, report that entry as
unresolved/needs review instead of emitting a runnable skipped test.

## Step 6 — Report
Summarise generated cases, passes, and any unresolved `HP-*` entries. Move a processed blueprint
to `sub-page-workflows/completed/`. Record changed files in `CHANGELOG.md`.
