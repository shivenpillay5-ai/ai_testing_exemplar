# Workflow blueprint — Issues (EXAMPLE)

One blueprint file per screen. Each entry has a stable id and a one-line behaviour description.
`/generate_workflow_tests` reads this file, confirms each entry against the live DOM, and emits
one atomic pytest case per entry. This is the example the bundled workflow test was written from.

| ID | Workflow |
|---|---|
| WF-01 | Open the detail panel for the first row and verify the header reads the issue's name. |
| HP-02 | Edit the **Description** field, save, reload the detail, and verify the value persisted. |
| UI-03 | The **Code** field is read-only and rejects keyboard edits. |
| SD-04 | The **Status** dropdown opens and lists: Open, In Progress, Resolved, Closed. |
| DT-05 | The **Due Date** picker opens and selecting a day changes the field value. |
| TB-06 | The **History** tab can be selected and its content is visible. |
| NAV-07 | Breadcrumb / back navigation returns to the Issues list grid. |

Conventions:
- `HP-*` entries are happy paths — they must **pass** during validation, not be left as skips.
- Field names (Description, Code, Status, …) must match the **live DOM**, not be guessed.
- After a blueprint is processed it moves to `sub-page-workflows/completed/`.
