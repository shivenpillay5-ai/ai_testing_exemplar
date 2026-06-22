# Automation Handbook

This file is the **assistant-neutral source of truth** for how tests are written, generated,
reviewed, and run in this repository. Claude Code (`CLAUDE.md`) and Codex (`AGENTS.md`) both
defer to it. When a rule changes, change it here first.

It is written generically so a team can adopt it for any web application under test. Replace
the bracketed placeholders and the `Issue` example with your own screens.

---

## What this repo is

A UI test-automation suite built with **Playwright + pytest** that drives a real web
application through the browser. Tests are organised by screen. Behaviour for each screen
lives in a **Page Object** class; test files are thin, readable workflows.

## Running tests

```bash
pytest                                         # everything
pytest app_tests/tests/Issues/general          # a folder
pytest -k "PageLoad"                            # by name expression
APP_HEADLESS=false pytest                       # watch the browser (PowerShell: $env:APP_HEADLESS="false")
```

Dependencies are in `requirements.txt`. Credentials/URL come from `.env`
(`APP_BASE_URL`, `APP_USERNAME`, `APP_PASSWORD`).

**Stale bytecode:** if a traceback's line numbers don't match the source you see, Python may
be running an old `.pyc`. Clear it: `find app_tests -name "*.pyc" -delete`.

---

## Architecture

### Session-level login
`conftest.py` logs in **once per test run**. The authenticated browser storage state is saved
to `playwright_state.json` and every test reuses it through the `logged_in_page` fixture. Use
`freshly_logged_in_page` only when a test specifically needs a clean login.

### Page Object Model
Every screen has a page class under `app_tests/pages/<Domain>/`. These classes:
- Accept a Playwright `Page` in `__init__`.
- Expose **only async methods**.
- Follow naming conventions: `verify_page_loaded()`, `verify_grid_loaded()`, `click_*()`, `fill_*()`, `verify_*()`.
- Scope locators to the **visible panel** when the app renders duplicate/hidden DOM
  (expose a `_panel` property returning a scoped locator).

Routing between screens is centralised in `app_tests/pages/navigation.py`. Use the
`NavigationPage` for all menu/hover/click-to-screen flows.

### Test structure
Tests live under `app_tests/tests/<Domain>/...`. Each file holds a single async test:

```python
@pytest.mark.asyncio
async def test_TC001_ISSUE_PageLoad(logged_in_page: Page):
    nav = NavigationPage(logged_in_page)
    page = IssuePage(logged_in_page)

    await nav.navigate_to_issues()
    await page.verify_page_loaded()
```

---

## Test authoring rules (apply to EVERY test file)

These are the non-negotiables. An AI assistant generating tests must obey all of them.

- **Tests must NEVER contain `assert` statements.** All assertions live in the page class as
  `verify_*` methods. The method name tells the reader what is being verified. A test is a
  readable workflow: navigate → act → `verify_*()`.
- **Tests must NEVER contain locators.** No `locator()`, `get_by_text()`, `get_by_role()`, or
  any selector belongs in a test file. Every locator lives in the page class. Need to close a
  dialog or read a value after an action? Add a page-class method and call it.
- **Every locator and assertion belongs in the page class** as a clearly named method.
- **No helper functions with assertion or locator logic in test files.** The only permitted
  test-file helpers are (1) pure navigation setup that creates page objects and navigates, and
  (2) `pytest.skip()` flow-control guards that check data availability. Batch verifications
  (e.g. "verify these 8 fields are read-only") belong in the page class as
  `verify_readonly_fields(fields)` and friends, each looping over a single-field `verify_*`.
- **Separate actions from assertions.** `click_export()` and `verify_export_dialog_open()`
  are two methods, not one.

### Assertion hardening (page-class `verify_*` methods)

- Use `assert <actual> == <expected>, f"descriptive message including the actual value"`.
- Verify the **specific** expected outcome, not just "something changed".
- For dialogs: assert the exact header/title text (`get_by_text("Exact Title", exact=True)`)
  to avoid strict-mode violations — never a generic substring.
- For exports/downloads: assert both that the dialog opened **and** the file has the right extension.
- Guard every regex result: assert the match is not `None` before `.group()`, and include the
  raw text in the failure message.

---

## Documented exception taxonomy

`pytest.skip()` is the mechanism for a test that cannot validly run. Every skip reason must
start with one of these prefixes so a reporting layer can group them:

- `NA_FEATURE:` — the control/feature is not present on this screen or configuration.
- `NA_DATA:` — the live dataset can't support the check (no rows, single page, no alternate value).
- `NEEDS_REVIEW:` — behaviour may be valid but needs product/test-owner review.
- `ENV_BLOCKED:` — couldn't run due to session/access/timeout/environment instability.

Do not use an unclassified skip. If the workflow can be asserted honestly, make it **pass**
instead of skipping.

---

## Test state & runtime conventions

**Timing:**
- Do **not** add `wait_for_timeout` sleeps between ordinary steps. Playwright auto-waits on
  every `expect()`, `click()`, and `fill()`. Explicit sleeps are redundant and slow the suite.
- The usual exception: a short settle (`await page.wait_for_timeout(1000)`) immediately after
  an action that opens a detail panel with **no observable DOM signal** (e.g. a server round-trip).
- Prefer strengthening page-object waits around observable UI states over adding sleeps.

**State independence:**
- Tests run in filename order. A test must not depend on state left by a previous test (open
  filters, dialogs, selected rows). Start from a known clean state.

**Dialog & panel cleanup:**
- Any test that opens a dialog/overlay/detail panel **must close it before the test ends**,
  using the close method on the page class. A leaked overlay blocks later tests.

**No duplicate actions:**
- Before calling a page method, check it doesn't internally do something you've already done
  (e.g. don't call `click_export()` separately if `click_export_and_select_xlsx()` calls it).

**Data-dependent grid tests — skip if empty:**
- A test that interacts with grid rows (column headers, pagination, add-row) must guard against
  an empty grid and `pytest.skip("NA_DATA: ...")` when there are no rows.

---

## Two test types

### 1. General Screen Functionality (GSF)
Screen-level behaviour that most list/grid screens share: page load, grid load, paging label,
select-all, dropdown presence, pagination (first/prev/next/last), refresh, column layout,
clear filters, add new, settings, export, column filtering. Generate **only** the tests for
controls that are actually present on the live screen.

Authoritative patterns: `.ai/prompts/general_screen_functionality.md`.

### 2. Workflow tests
Detail panels, tabs, edit/save behaviour, dropdown/date-picker behaviour, navigation, and
screen-specific business flows. Each numbered workflow entry is **independently runnable** —
one data-dependent skip must never hide unrelated coverage. One file per screen; one pytest
case per workflow entry; function names carry a stable `TC0NN` prefix and a workflow id.

Authoritative patterns: `.ai/prompts/workflow_tests.md`.

A happy-path (`HP-*`) workflow that the app actually supports must **pass** during validation —
not be left as a runnable `pytest.skip()`. If no honest passing path exists, report it as
unresolved rather than hiding it as a skip.

---

## Generation workflow contract

These files must stay aligned. When you change generation behaviour, update all of them:

- **Command files** (`.ai/commands/*.md`) own orchestration: screen discovery, live DOM
  inspection via Playwright MCP, output-folder resolution, and reporting.
- **Prompts** (`.ai/prompts/*.md`) own reusable implementation patterns: page-class methods,
  selector/assertion hardening.
- **This handbook** owns global rules that apply to every generated test.
- `.ai/prompts/test_generation_rules.md` is a **compact digest** for sub-agents. It must
  summarise — not replace — the rules here.

**Live DOM is mandatory.** Generated field names and selectors must come from the live DOM
(inspected via Playwright MCP), not guessed by PascalCase/camelCase converting a label. If a
field can't be resolved on the live screen, log it as unresolved rather than emit a selector
that will fail across many tests.

**Token discipline during generation:** prefer small, structured `browser_evaluate` returns
(booleans/counts/strings) over full snapshots; reserve `browser_snapshot` for login or first
navigation confirmation; do not take screenshots during generation.

---

## Skill & command creation rule

- **Skill source of truth:** `.ai/skills/<skill-name>/SKILL.md`
  - Claude wrapper: `.claude/skills/<skill-name>.md`
  - Codex wrapper: `.codex/skills/<skill-name>/SKILL.md`
- **Command source of truth:** `.ai/commands/<command-name>.md`
  - Claude wrapper: `.claude/commands/<command-name>.md`
  - Codex wrapper: `.codex/commands/<command-name>.md`

Wrappers point back to the shared source; they never duplicate logic. A skill/command change
is incomplete if any wrapper is missing.

---

## Changelog

Every change — by a developer or an AI assistant — must be recorded in `CHANGELOG.md` before
the work is considered complete: date, short description, and every file created/modified/deleted.

---

## Application-specific notes

Replace this section with the quirks of *your* application's UI toolkit: how its grids render,
which selectors are stable, how dialogs/overlays behave, how date pickers work. If your app is
built on **Vaadin**, a ready-made set of these learnings lives in
`docs/vaadin-selector-appendix.md` — fold the relevant parts in here.
