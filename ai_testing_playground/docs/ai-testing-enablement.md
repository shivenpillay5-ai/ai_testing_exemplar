# Setting up AI-Driven Test Automation — Team Enablement Guide

> **Audience:** QA engineers, SDETs, and developers who want to stand up UI test automation
> for their project with the help of AI coding assistants (Claude Code, Codex, and similar).
>
> **What you'll get out of it:** a working framework skeleton, a repeatable way to *generate*
> tests with an AI assistant, and the conventions that keep those tests maintainable.
>
> This page accompanies the **AI Testing Playground** starter repo. Clone the repo, then read
> this top to bottom.

---

## 1. Why AI-driven testing (and what it is *not*)

Writing UI automation by hand is slow, repetitive, and drifts in style across a team. A capable
AI assistant can write the bulk of it — **if** you give it three things:

1. **Clear, written rules** (a handbook) so every generated test looks the same.
2. **Good examples** to pattern-match against.
3. **Live access to the application** so it inspects the real DOM instead of guessing selectors.

This is *assisted* automation, not magic. The assistant accelerates the formulaic 80% (page
loads, grids, pagination, filters, field checks). Humans still own: the test strategy, what's
worth covering, reviewing generated code, and the genuinely tricky flows.

**Rule of thumb:** if you can describe a test in one sentence and it follows a pattern the suite
already has, the assistant should write it. If it needs judgement about product behaviour, you
write it (or pair with the assistant).

---

## 2. The stack — and why each piece

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.11+** | Readable, low-ceremony, enormous testing ecosystem; easy for non-specialists to review. |
| Browser automation | **Playwright** | Auto-waiting (far fewer flaky sleeps), first-class shadow-DOM support, one API across Chromium/Firefox/WebKit, built-in tracing. |
| Test runner | **pytest** + `pytest-asyncio` | Fixtures, parametrization, plugins, great reporting; async support for Playwright's async API. |
| Design pattern | **Page Object Model (POM)** | Selectors and assertions live in one class per screen, so tests stay short and a UI change is a one-file fix. |
| AI assistants | **Claude Code** and/or **Codex** | Drive generation, review, and runs. Both read the same `.ai/` source of truth so behaviour is identical. |
| Live inspection | **Playwright MCP** | Lets the assistant open the real app and read the live DOM while it writes tests. This is the single biggest quality lever. |

You can substitute layers (Selenium, Playwright's own test runner, a different assistant). The
*reusable* parts are the **handbook discipline** and the **POM + thin-test** structure.

---

## 3. Prerequisites

- Python 3.11+ and `pip`.
- Node.js (for the Playwright MCP server, which runs via `npx`).
- An AI coding assistant: **Claude Code** and/or **Codex**.
- Access to your application under test (a non-production / UAT environment) and a test account.
- Git.

---

## 4. First-time setup (≈15 minutes)

```powershell
# 1. Get the starter repo and create an isolated environment
git clone <your-fork-of-the-playground>
cd ai-testing-playground
python -m venv venv
.\venv\Scripts\Activate.ps1            # macOS/Linux: source venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium

# 2. Configure secrets locally (never commit these)
copy .env.example .env                  # then edit APP_BASE_URL / APP_USERNAME / APP_PASSWORD

# 3. Confirm the assistant can drive a browser
#    .mcp.json already registers the Playwright MCP server. In your assistant, confirm the
#    "playwright" MCP tools are available (browser_navigate, browser_snapshot, …).
```

Then **make it yours**:

1. Implement `app_tests/pages/login.py` against your real login form.
2. Fill in `app_tests/pages/navigation.py` for how your app routes between screens.
3. Get **one** small test passing end-to-end (`pytest -k PageLoad`) before generating more.
4. Edit `.ai/handbook.md` so its rules and selector notes match *your* app.

> **Don't skip step 3.** A green "page loads" test proves login, navigation, session reuse, and
> selectors all work. Everything else builds on it.

---

## 5. How the repo is organised

```
.ai/handbook.md        ← THE source of truth: rules every test must follow
.ai/prompts/           ← reusable "how to generate X" instructions + a compact digest
.ai/skills/  .ai/commands/   ← entry points the assistant invokes
.claude/  .codex/       ← thin wrappers so Claude & Codex both use the .ai sources
app_tests/conftest.py   ← logs in once per run, reuses the session for every test
app_tests/pages/        ← Page Objects: ALL selectors and assertions live here
app_tests/tests/        ← thin test files: navigate → act → verify
docs/                   ← this guide + the Vaadin selector appendix
```

**The contract, in one breath:** test files contain *no selectors and no asserts*. They read as
a workflow. Everything mechanical lives in a page object method whose name says what it does.

```python
# A test file — readable as plain English, nothing clever in it
async def test_TC002_SM_Issues_GridLoaded(logged_in_page):
    nav = NavigationPage(logged_in_page)
    page = IssuePage(logged_in_page)
    await nav.navigate_to_issues()
    await page.verify_page_loaded()
    await page.click_clear_filters()
    await page.verify_grid_loaded()      # the assertion lives inside this method
```

---

## 6. The AI-driven workflow

1. **Point the assistant at the handbook.** `CLAUDE.md`/`AGENTS.md` already tell it to read
   `.ai/handbook.md` first. The handbook is the contract it generates against.
2. **Generate a suite.** Invoke a command/skill and name a screen:
   - `/generate_general_tests Issues` — page load, grid, paging, filters, export, etc.
   - `/generate_workflow_tests Issues` — detail panel, edit/save, dropdowns, tabs, navigation.
   The assistant logs into the live app via Playwright MCP, **inspects the real DOM**, and writes
   the page object + test files.
3. **Review.** `/review_tests <folder>` checks the rules (no asserts/locators in tests, page-object
   coverage, naming, classified skips) and runs the suite.
4. **Run.** `/run_tests <target>` runs a selection and summarises pass/fail/skip.
5. **Log it.** Every change is recorded in `CHANGELOG.md`.

**Why live DOM inspection matters:** the most common cause of bad generated tests is the
assistant *guessing* a selector or field name from a label. Forcing it to read the live DOM
(via MCP) before writing eliminates most of that class of failure.

---

## 7. Key conventions (the golden rules)

1. **No `assert` in test files.** Assertions live in `verify_*` page-object methods.
2. **No locators in test files.** Selectors live in page objects.
3. **Separate actions from assertions** — `click_export()` and `verify_export_dialog_open()`.
4. **Assert the *specific* outcome**, not "something changed" (exact dialog title, exact row range).
5. **Clean up** — close any dialog/overlay/detail panel a test opened.
6. **Tests are independent** — start from a known clean state; never depend on a prior test.
7. **Classify every skip** — `NA_FEATURE:`, `NA_DATA:`, `NEEDS_REVIEW:`, `ENV_BLOCKED:`. A skip is a
   *documented exception*, not a silent pass. If you can assert the behaviour honestly, do that.
8. **Happy paths must pass** — never ship a runnable test that just skips a flow the app supports.

---

## 8. Learnings & pitfalls (hard-won)

These are the things that bite teams in the first month:

- **Don't sleep; wait for state.** Playwright auto-waits on every `expect`/`click`/`fill`. Adding
  `wait_for_timeout` between steps hides races and slows the suite. The one fair exception is a
  server round-trip that produces *no* observable DOM change — and even then, put the short wait
  *inside the page method*, not the test.
- **Anchored waits, not substring waits.** When waiting for a paged grid to change, an anchored
  regex is essential: waiting for the label to stop being `"1 to 50 of"` is satisfied by
  `"1 to 50 of 100"` and returns instantly. (See `IssuePage.wait_for_paging_text_change`.)
- **Filter a *text* column, not a numeric one.** Filtering a numeric column with a letter returns
  zero rows — the test then "passes" vacuously. Pick the first non-numeric column.
- **Scope to the visible panel.** Many enterprise UIs render hidden duplicate DOM (detail panels,
  off-screen tabs). Scope locators to the visible container (`:not([hidden])`, `.first`) or you'll
  hit ambiguous-match errors.
- **Session reuse pays off.** Logging in once per run (storage state) instead of per test cuts
  minutes off a suite and removes a whole class of login flakiness.
- **One green test before a hundred red ones.** Generating 40 tests before login works just gives
  you 40 failures. Prove the spine first.
- **Generated ≠ trusted.** Always review. The assistant is fast and consistent, not infallible —
  it can assert the wrong thing confidently. `/review_tests` plus a human read is the safety net.
- **Keep the handbook current.** When you discover a new selector quirk, add it to
  `.ai/handbook.md`. Every future generation benefits. The handbook is a living asset, not a
  one-time doc.

---

## 9. Security & secrets

- Credentials and URLs live in `.env`, which is **git-ignored**. Never commit them.
- Use a **non-production** environment and a dedicated test account with least privilege.
- Keep generated tests **non-destructive** against shared environments — verify that a control
  exists/opens rather than saving/deleting live data, unless you have isolated test data.
- In CI, inject secrets from your secret store (pipeline variables / a vault), not from a file.
- Be mindful that screenshots, traces, and DOM dumps can capture sensitive data — treat report
  artifacts accordingly and keep them out of source control.

---

## 10. CI/CD (where this goes next)

The starter runs locally; productionising it usually means:

- A scheduled pipeline (nightly/weekly) that installs deps + Chromium, injects secrets, runs a
  chosen path headless, and publishes a report.
- A PR-validation pipeline that detects changed test files and runs only the affected ones.
- A reporting layer that classifies the documented-exception skip prefixes into a dashboard so
  "intentionally skipped" is visually distinct from "failed".

Headless is the default in CI; `APP_HEADLESS=false` (or `--headed`) is for local debugging.

---

## 11. Rollout checklist for a new team

- [ ] Clone the playground; create venv; install deps + Chromium.
- [ ] Implement `login.py` and `navigation.py` for your app; get one PageLoad test green.
- [ ] Tailor `.ai/handbook.md`: your module list, naming prefixes, and selector quirks.
- [ ] Generate the GSF suite for one real screen; review it; get it green.
- [ ] Generate a workflow suite for the same screen from a small blueprint.
- [ ] Stand up a CI job (start with a scheduled headless run on a few screens).
- [ ] Agree team norms: every change logged in `CHANGELOG.md`; skips must be classified.
- [ ] Schedule a 30-min demo so the team sees the generate → review → run loop.

---

## 12. FAQ

**Do the example tests run as-is?** No — they point at placeholder selectors. They're a worked
example to copy. Repoint the page objects at your app to make them pass.

**Claude or Codex?** Either. Both read the same `.ai/` sources, so the rules and prompts are
identical. Use whichever your team has access to (or both).

**My app isn't Vaadin — is the Vaadin appendix useful?** Skip it. It captures selector learnings
specific to Vaadin's shadow DOM and flatpickr date pickers. Keep your own equivalent appendix for
your UI toolkit instead.

**How do I stop the assistant inventing selectors?** Make sure the Playwright MCP server is wired
up and insist (in the handbook) that field names/selectors come from the live DOM. The included
commands already do this.

**How much does it really save?** The formulaic suites (page load, grid, pagination, filters) are
where the leverage is — minutes of generation versus hours of hand-writing. The win compounds as
your handbook captures more conventions.

---

## 13. Related resources

- **Repository (Azure DevOps):** https://dev.azure.com/is-cfm/The%20Golden%20Source/_git/ai_testing_playground
- **Add your first screen** — the step-by-step tutorial: `docs/adding-a-screen.md` (mirrored as a child page here in Confluence).
- **Vaadin selector appendix** — `docs/vaadin-selector-appendix.md` (only if your app is Vaadin-based).
- **Starter CI pipelines** — `pipeline/azure-pipelines.yml` (scheduled run) and `pipeline/pr-validation.yml`.
- **Guardrails** — `scripts/validate_ai_adapters.py` and `scripts/check_test_rules.py`, run automatically via `.pre-commit-config.yaml`.
