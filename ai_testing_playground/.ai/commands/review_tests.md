---
name: review_tests
description: Review generated/changed tests against the handbook rules — no locators/asserts in tests, page-object method coverage, naming, and a live run.
---

# /review_tests

Review a folder (or the current diff) of test files against `.ai/handbook.md`. Report findings;
do not silently rewrite unless asked.

## Checks

1. **No asserts in test files.** Flag any `assert` statement inside a `test_*.py`.
2. **No locators in test files.** Flag `locator(`, `get_by_text(`, `get_by_role(`, `query_selector`,
   `page.click(`, `page.fill(`, or any raw selector in a test file.
3. **No forbidden imports.** Test files should not import `expect` or `re`.
4. **Page-object method coverage.** Every page method a test calls must exist in the page class.
   List any missing methods.
5. **Naming alignment.** File name `test_TC0NN - <PREFIX>_<Screen>_<Feature>.py` matches the inner
   function name `test_TC0NN_<PREFIX>_<Screen>_<Feature>`. Numbering has no gaps.
6. **Cleanup.** A test that opens a dialog/overlay/detail panel closes it before ending.
7. **Skips are classified.** Every `pytest.skip(...)` reason starts with `NA_FEATURE:`,
   `NA_DATA:`, `NEEDS_REVIEW:`, or `ENV_BLOCKED:`.
8. **Live run.** Run the target with `pytest` and report pass/fail/skip counts. For failures,
   give the root cause and whether it's a test bug, a page-object gap, or a real app issue.

## Output
A findings table grouped by severity (blocking / should-fix / nit), then the pytest summary.
