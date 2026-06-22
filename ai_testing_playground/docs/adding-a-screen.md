# Tutorial: Adding your first screen

This walks you through covering a real screen in your application, using the bundled **Issue
exemplar** as the pattern to copy. By the end you'll have a page object and a passing
"page loads" test — the spine everything else builds on.

> Time: ~30 minutes for the first screen, far less once the pattern is familiar.

---

## The mental model

Three layers, and the rule that keeps them clean:

```
   ┌─────────────────────────────────────────────────────────────┐
   │  TEST FILE          navigate → act → verify                   │
   │  (no selectors,     "what should happen", in plain steps      │
   │   no asserts)                                                 │
   └───────────────┬───────────────────────────────────────────────┘
                   │ calls methods on
                   ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  PAGE OBJECT        click_export(), verify_grid_loaded(), …    │
   │  (ALL selectors     "how to do it" + "how to check it"        │
   │   and assertions)                                             │
   └───────────────┬───────────────────────────────────────────────┘
                   │ drives
                   ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  THE BROWSER        your application under test (Playwright)   │
   └─────────────────────────────────────────────────────────────┘
```

If you ever feel the urge to write `assert` or `page.locator(...)` in a test file — stop, and
put it in the page object instead. That single habit is what keeps the suite maintainable.

---

## Step 1 — Get the spine working first

Before adding any new screen, make sure the framework can log in and reach the app:

```powershell
copy .env.example .env          # fill in APP_BASE_URL / APP_USERNAME / APP_PASSWORD
pytest -k PageLoad
```

If that's red, fix `app_tests/pages/login.py` and `navigation.py` before going further. A green
PageLoad proves login, session reuse, navigation, and selectors all work end to end.

---

## Step 2 — Copy the exemplar for your screen

Say your screen is **Customers**. Copy the Issue files and rename:

```
app_tests/pages/Issues/IssuePage.py        →  app_tests/pages/Customers/CustomerPage.py
app_tests/pages/Issues/IssueDetailPage.py  →  app_tests/pages/Customers/CustomerDetailPage.py
app_tests/tests/Issues/                     →  app_tests/tests/Customers/
```

Rename the classes (`IssuePage` → `CustomerPage`) and add `__init__.py` to the new folders.

---

## Step 3 — Point the selectors at your real DOM

Open `CustomerPage.py` and replace the placeholder selectors at the top with your app's real
ones. This is where the **Playwright MCP** earns its keep — let the assistant inspect the live
screen instead of guessing:

> "Navigate to the Customers screen and tell me the selector for the grid container, the paging
> label, the toolbar Export button, and the column filter inputs."

Update the constants (`PANEL`, `GRID`, `PAGING_LABEL`, …) and the toolbar button names.

---

## Step 4 — Add navigation

In `navigation.py`, add one method for the screen:

```python
async def navigate_to_customers(self):
    await self.open_menu()
    await self.hover_over_module("Sales")        # your module label
    await self.click_screen("Customers")         # your screen label
    await expect(self.page.locator("[role='grid']").first).to_be_visible(timeout=30_000)
```

---

## Step 5 — Get one test green, then let the assistant do the rest

Run the page-load test for the new screen and fix anything that's off:

```powershell
pytest -k "Customers_PageLoad"
```

Once it's green, generate the full suite from the live DOM:

```
/generate_general_tests Customers
```

Then review and run:

```
/review_tests app_tests/tests/Customers/general
/run_tests app_tests/tests/Customers/general
```

---

## Step 6 — Workflows (detail panel, edit/save, tabs)

Workflow tests are generated from a **blueprint**: a one-file-per-screen list of the behaviours
you want covered. `/generate_workflow_tests` reads it, confirms each entry against the live DOM,
and writes one pytest case per row. This is the step a new user hits first, so do it in order:

1. **Copy the template.** `.ai/prompts/sub-page-workflows/_TEMPLATE.md` is a fill-in-the-blanks
   starting point; `Issues.md` in the same folder is a complete worked example. Copy one to
   `.ai/prompts/sub-page-workflows/Customers.md`.
2. **Write one row per behaviour**, each with a stable id and a one-line description:

   ```markdown
   | ID    | Workflow                                                              |
   |-------|-----------------------------------------------------------------------|
   | WF-01 | Open the detail panel for the first row and verify the header.        |
   | HP-02 | Edit the **Name** field, save, reload, and verify the value persisted.|
   | SD-03 | The **Region** dropdown opens and lists the expected options.         |
   | NAV-04| Back navigation returns to the Customers list grid.                   |
   ```

   Describe **behaviour, not selectors** — name real fields and expected values, keep one
   behaviour per row, and remember `HP-*` rows must have an honest passing path (never ship a
   happy path as a skip). The full authoring rules and id-prefix meanings are in `_TEMPLATE.md`.
3. **Generate.** If no blueprint exists for the screen, the command synthesizes a *draft* into
   `sub-page-workflows/_drafts/` and stops — promote it to an approved blueprint before generating.

```
/generate_workflow_tests Customers
```

The generate → review → run loop, end to end:

```
   blueprint / screen name
            │
            ▼
   /generate_*   ──>  inspects live DOM (MCP), writes page object + tests
            │
            ▼
   /review_tests ──>  checks rules (no asserts/locators), runs the suite
            │
            ▼
   /run_tests    ──>  pass / fail / classified skips
            │
            ▼
   commit  ──>  pre-commit validates wrappers + test rules  ──>  push  ──>  CI
```

---

## When a test fails

`conftest.py` automatically saves a **screenshot** and a **Playwright trace** for any failing
test into `reports/`. Open the trace to step through exactly what the browser did:

```powershell
playwright show-trace reports\<test-name>-trace.zip
```

In CI these are published as a build artifact, so you can download and replay a failure from a
pipeline run.

---

## Checklist

- [ ] PageLoad green before anything else.
- [ ] Page object copied from the exemplar; selectors point at the real DOM.
- [ ] `navigate_to_<screen>()` added.
- [ ] GSF suite generated, reviewed, and green (or skips are classified).
- [ ] Workflow blueprint written; workflow suite generated and reviewed.
- [ ] `CHANGELOG.md` updated; `pre-commit run --all-files` clean.
