# Prompt: Workflow test generation patterns

Authoritative implementation patterns for generating **workflow** tests — detail panels, tabs,
edit/save, dropdown/date behaviour, navigation, and screen-specific business flows. Orchestration
lives in `.ai/commands/generate_workflow_tests.md`; global rules in `.ai/handbook.md`.

---

## Inputs

A **screen blueprint** describes the workflows to cover. Keep one blueprint file per screen
(e.g. `.ai/prompts/sub-page-workflows/<Screen>.md`). Start from
`.ai/prompts/sub-page-workflows/_TEMPLATE.md` (fill-in template + id-prefix reference);
`Issues.md` is a complete worked example. Each entry has a stable id and a short behaviour
description, for example:

- `WF-01` Open detail panel for the first row and verify the header.
- `HP-02` Edit the Description field, save, reload, verify the value persisted.
- `SD-03` Open the Status dropdown and verify it lists the expected options.
- `UI-05` The Code field is read-only and rejects keyboard edits.
- `NAV-01` Breadcrumb / back navigation returns to the list grid.

Confirm the blueprint against the **live DOM** with one targeted check (field-name or label
counts). Rebuild the full inventory only if the guard diverges.

## Output format — atomic, one case per entry

- **One file per screen:** `test_<screen_lower>_workflows.py` in the screen's `workflows/` folder.
- **One pytest case per blueprint entry.** `WF-01`, `HP-02`, etc. each get their own
  `test_TC0NN_` function (or one `pytest.param(..., id="WORKFLOWID_description")`).
- **No broad category bundles** — a skip for one data-dependent entry must not hide later entries.
- Function/param names include the workflow id so a failure maps back to the blueprint.
- Zero `assert` statements and zero locators in the test file (same as every test).

```python
@pytest.mark.asyncio
async def test_TC002_ISSUE_HP02_edit_description_persists(logged_in_page: Page):
    detail = await open_issue_detail(logged_in_page)        # navigation helper only
    await detail.edit_field_and_save("Description", "Updated by automation")
    await detail.reload_detail()
    await detail.verify_field_value("Description", "Updated by automation")
    await detail.return_to_list()                            # cleanup
```

Permitted test-file helpers: pure navigation setup (`open_<screen>_detail()`,
`return_to_<screen>_list()`) and `pytest.skip()` data guards. Everything else is a page method.

## Page-class methods workflows rely on

- `open_detail_for_first_row()` / `double_click_first_row()` — open the detail panel. If the
  panel opens with no observable DOM signal, add a short settle inside the method, not the test.
- `verify_detail_loaded()` / `verify_header(text)` — the detail surface is up.
- `verify_field_is_editable(name)` / `verify_field_is_readonly(name)` and the batch wrappers
  `verify_editable_fields(fields)` / `verify_readonly_fields(fields)` (each loops over the single).
- `edit_field_and_save(name, value)`, `reload_detail()`, `verify_field_value(name, value)`.
- `verify_dropdown_opens_with_options(name, expected_options)`.
- `verify_datepicker_picks_date(name)` — actually **select a date and assert the value changed**;
  never just assert the calendar opened and closed.
- `verify_tab_selected(tab)` / `verify_tab_content_visible(tab)`.
- `section_has_grid_rows(section)` → bool — for data guards before grid-tab interactions.
- `return_to_list()` — close the detail panel and confirm the list grid is back (cleanup).

## Validation gate (before reporting complete)

Run the generated file, or at minimum a representative canary set: list load, detail open,
visible-field checks, one edit/save, one date-picker save, one dropdown, one navigation. If the
same root cause fails repeatedly, fix the page class (or document an unsupported app behaviour)
before continuing.

**Happy-path (`HP-*`) entries are strict:** a generated happy-path test must *pass*. Do not
emit a runnable `pytest.skip()`/`xfail()` for an `HP-*`. If the app rejects the save, the value
doesn't persist, or a dropdown has no alternate value, look for a different live-supported
field/value; if none exists, report that entry as **unresolved / needs review** rather than
shipping a skipped happy path.

**Skip audit:** after the run, classify every skip. If the live screen exposes a deterministic
state (read-only rejects edits, reload preserves values, a control is genuinely absent,
pagination is validly single-page), assert that state and make the test **pass**. Reserve
`pytest.skip()` for cases with no deterministic behaviour to assert (no rows after cleanup,
missing data setup, environment blocker) — always with a classified prefix.
