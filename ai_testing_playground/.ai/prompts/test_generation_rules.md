# Compact test-generation rules (digest)

A short digest for generation sub-agents. It **summarises** `.ai/handbook.md` — when in doubt,
the handbook wins. Read this for routine generation instead of re-reading the full handbook.

## Hard rules (never violate)
1. No `assert` in test files. Assertions live in page-class `verify_*` methods.
2. No locators in test files. Selectors live in page classes.
3. Tests read as workflows: create page objects → navigate → act → `verify_*()`.
4. Separate actions from assertions (`click_x()` vs `verify_x_open()`).
5. Close every dialog/overlay/detail panel a test opens.
6. Tests are state-independent; start clean.

## Generation discipline
- Inspect the **live DOM** (Playwright MCP). Never guess field names/selectors from labels.
- Generate a test only for a control that actually exists on the screen.
- Prefer small structured `browser_evaluate` returns over snapshots; no screenshots during generation.
- Filter tests: pick a **non-numeric** column; verify cell contents, not just that paging changed.
- Pagination: anchored-regex wait after each click; directional `verify_*` per direction.

## Skips
- Only `pytest.skip()` with a classified prefix: `NA_FEATURE:`, `NA_DATA:`, `NEEDS_REVIEW:`, `ENV_BLOCKED:`.
- If a behaviour can be asserted honestly, make it pass instead of skipping.
- `HP-*` happy paths must pass — never ship a runnable skipped happy path.

## After generating
- Run the new file (or a canary set). Fix repeated same-cause failures before reporting done.
- Record changed files in `CHANGELOG.md`.
