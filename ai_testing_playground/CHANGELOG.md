# Changelog

Every change to this repository — by a developer or an AI assistant — should be recorded
here before the work is considered complete. Append a new dated block per session.

Format:

```
## YYYY-MM-DD ~HH:MM

| Description | Files Affected | Reason |
|---|---|---|
| What changed | path/to/file | Why it was needed |
```

---

## 2026-06-12 ~ (team-review feedback)

| Description | Files Affected | Reason |
|---|---|---|
| Remove the duplicated Word guide; make Markdown the single source of truth and git-ignore generated `.docx` | docs/AI-Driven-Test-Automation-Enablement-Guide.docx (deleted), .gitignore, README.md | Two formats of the same guide would drift and users could follow the wrong one; `.docx` is now regenerated on demand from the `.md` via tools/md_to_docx.py |
| Add a worked data-driven test example so the test_data folder is no longer empty | app_tests/test_data/issue_filters.csv, app_tests/test_data/README.md, app_tests/tests/Issues/general/test_TC011 - SM_Issues_DataDrivenFilter.py | A cloning user had no example of how a CSV/JSON-driven, parametrized test should be wired |
| Add a blueprint template and document how to author one for a new screen | .ai/prompts/sub-page-workflows/_TEMPLATE.md, .ai/commands/generate_workflow_tests.md, .ai/prompts/workflow_tests.md, docs/adding-a-screen.md | /generate_workflow_tests assumed a blueprint exists with only Issues.md as an example and no template or how-to — new users hit a wall adapting it to their own app |

## 2026-06-03 ~10:18

| Description | Files Affected | Reason |
|---|---|---|
| Add 30-minute demo / lunch-and-learn outline (repo copy of the Confluence page) | docs/demo-walkthrough.md, README.md | Let the demo outline travel with the code alongside the other enablement docs |

## 2026-06-03 ~10:05

| Description | Files Affected | Reason |
|---|---|---|
| Starter Azure DevOps pipelines (scheduled run + PR validation) | pipeline/azure-pipelines.yml, pipeline/pr-validation.yml, pipeline/README.md | Make the suite run itself in CI |
| Capture Playwright trace + screenshot on test failure | app_tests/conftest.py | Make failures debuggable locally and in CI |
| Wrapper validator + test-rule checker + pre-commit hooks | scripts/validate_ai_adapters.py, scripts/check_test_rules.py, .pre-commit-config.yaml | Enforce the .ai→.claude/.codex wrapper discipline and the no-asserts/no-locators rule |
| "Add a screen" tutorial with diagrams | docs/adding-a-screen.md | Give new contributors a concrete onboarding path |
| Cross-links (ADO repo + Confluence) and new components documented | README.md, docs/ai-testing-enablement.md, docs/AI-Driven-Test-Automation-Enablement-Guide.docx | Connect the repo, Confluence, and Word doc |

## 2026-06-03 ~Initial

| Description | Files Affected | Reason |
|---|---|---|
| Initial playground scaffold: AI-driven UI test automation starter | (all) | Seed a reusable, generic starting point for teams adopting AI-assisted testing |
