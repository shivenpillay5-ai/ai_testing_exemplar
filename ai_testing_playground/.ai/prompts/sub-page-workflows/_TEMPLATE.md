# Workflow blueprint — <ScreenName> (TEMPLATE)

> Copy this file to `<ScreenName>.md` (e.g. `Customers.md`) in this folder, then fill in the
> table. `/generate_workflow_tests <ScreenName>` reads it, confirms each entry against the
> **live DOM**, and emits one atomic pytest case per row. See `docs/adding-a-screen.md` for the
> full walkthrough. The bundled `Issues.md` is a complete, real example to model yours on.

One blueprint file per screen. Each entry is **one independently runnable workflow**, with a
stable id and a one-line, behaviour-focused description (what a user does and what they should
see — not how to click it; the assistant resolves selectors from the live DOM).

| ID | Workflow |
|---|---|
| WF-01 | Open the detail panel for the first row and verify the header reads <what>. |
| HP-02 | Edit the **<Field>** field, save, reload, and verify the value persisted. |
| UI-03 | The **<Field>** field is read-only and rejects keyboard edits. |
| SD-04 | The **<Field>** dropdown opens and lists: <option>, <option>, <option>. |
| DT-05 | The **<Field>** date picker opens and selecting a day changes the field value. |
| TB-06 | The **<Tab>** tab can be selected and its content is visible. |
| NAV-07 | Breadcrumb / back navigation returns to the <ScreenName> list grid. |

## ID prefixes (pick what fits; add your own)

| Prefix | Use it for |
|---|---|
| `WF-` | General workflow / detail-panel behaviour. |
| `HP-` | **Happy path** — must *pass* during validation, never ship as a skip. |
| `SD-` | Single dropdown / select-options behaviour. |
| `DT-` | Date-picker behaviour (must actually select a date and assert the change). |
| `UI-` | Static UI state (read-only fields, disabled controls, labels). |
| `TB-` | Tabs / sub-sections within the detail surface. |
| `NAV-` | Navigation in/out of the detail (breadcrumb, back, deep link). |

## Rules for a good blueprint

- **One behaviour per row.** If a row says "edit, save, *and* check history", split it — a
  data-dependent skip on one half must never hide the other.
- **Describe behaviour, not selectors.** "The Status dropdown lists Open/Closed", not
  "click `#status-ddl`". Field/option names should match the live DOM, but the assistant
  confirms them — don't guess CSS.
- **Name real fields and expected values.** "Edit **Description**, verify it persisted" is
  testable; "edit a field" is not.
- **`HP-*` entries must have an honest passing path.** If the app can't actually support the
  flow with available test data, mark it for review rather than listing it as a happy path.
- **Keep ids stable.** A failing test maps back to its row by id, so don't renumber casually.

After a blueprint is processed it moves to `sub-page-workflows/completed/`.