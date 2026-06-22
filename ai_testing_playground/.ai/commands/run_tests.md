---
name: run_tests
description: Run a selected pytest target and summarize results (pass/fail/skip, with classified documented exceptions).
---

# /run_tests

Run a chosen pytest target and report results clearly.

## Steps
1. Determine the target. If the user named a screen/folder/expression, use it; otherwise ask.
   Examples: `pytest app_tests/tests/Issues/general`, `pytest -k "PageLoad"`.
2. Clear stale bytecode if a previous run showed mismatched tracebacks:
   `find app_tests -name "*.pyc" -delete`.
3. Run with `pytest` (add `APP_HEADLESS=false` only when a visible run is requested).
4. Summarise: total / passed / failed / skipped. Group skips by their classified prefix
   (`NA_FEATURE:`, `NA_DATA:`, `NEEDS_REVIEW:`, `ENV_BLOCKED:`) and report them as documented
   exceptions rather than failures.
5. For each failure, give a one-line root cause and whether it's a test issue, a page-object
   gap, or a real application problem.

Do not modify test files in this command — that's `/review_tests` or a generation command.
