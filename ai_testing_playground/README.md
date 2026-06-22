# AI-Driven Test Automation — Playground & Starter Pack

A reusable, **generic** starting point for teams that want to build UI test automation with
the help of AI coding assistants (Claude Code, Codex, and similar). It is deliberately small
and readable: clone it, point it at your own application, and grow it into a real suite.

It bundles three things teams usually have to invent from scratch:

1. **A working test framework skeleton** — Playwright + pytest, session login, a Page Object
   Model, and a navigation layer, demonstrated on a generic "Issue" screen.
2. **AI assets that travel with the repo** — an assistant-neutral handbook, reusable prompts,
   and skills/commands wired for both Claude Code and Codex so an assistant can *generate*,
   *review*, and *run* tests consistently.
3. **Enablement docs** — a Confluence-ready guide (`docs/`) explaining setup, the patterns,
   and the hard-won learnings so a new team can adopt AI-assisted testing quickly.

> This is a **learning/starter** repo. The example tests describe patterns; they will only
> run end-to-end once you wire them to a real application. Treat the `Issue` screen as a
> worked example to copy, not a live test target.

## Links

- **Repository (Azure DevOps):** https://dev.azure.com/is-cfm/The%20Golden%20Source/_git/ai_testing_playground
- **Enablement guide (Confluence):** https://cfm-confluence.atlassian.net/wiki/spaces/QA/pages/2096529410
- **New here?** Start with [docs/adding-a-screen.md](docs/adding-a-screen.md).

---

## Why this exists

Writing UI automation by hand is slow and inconsistent. An AI assistant can write most of it
**if** you give it three things: clear rules, good examples, and reusable prompts. This repo
packages exactly that. The core idea:

- **Tests read like workflows** — `navigate → act → verify`. No assertions or selectors in test files.
- **All locators and assertions live in page objects** (`verify_*`, `click_*`, `fill_*` methods).
- **The AI follows a written handbook**, so generated tests match your conventions every time.

---

## Tech choices (and why)

| Choice | What | Why |
|---|---|---|
| **Language** | Python 3.11+ | Readable, batteries-included, huge testing ecosystem. |
| **Browser driver** | [Playwright](https://playwright.dev/python/) | Fast, reliable auto-waiting, shadow-DOM friendly, one API for Chromium/Firefox/WebKit. |
| **Test runner** | [pytest](https://docs.pytest.org/) + `pytest-asyncio` | Fixtures, parametrization, rich plugin ecosystem; async support for Playwright's async API. |
| **Design pattern** | Page Object Model (POM) | Keeps selectors/assertions in one place so tests stay short and resilient to UI change. |
| **AI assistants** | Claude Code & Codex via shared `.ai/` source of truth | Same rules and prompts regardless of which assistant a teammate uses. |
| **Live inspection** | [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Lets the assistant inspect the *live* DOM while generating tests, instead of guessing selectors. |

You can swap any layer (e.g. Selenium, Jest/Playwright-test, a different assistant) — the
*structure* and the *handbook discipline* are the reusable parts.

---

## Quick start

### 1. Create a virtual environment and install

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows PowerShell
# source venv/bin/activate            # macOS / Linux
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Configure your environment

```powershell
copy .env.example .env                # cp .env.example .env on macOS/Linux
```

Edit `.env` with your app URL and credentials:

```ini
APP_BASE_URL=https://your-app-under-test.example.com
APP_USERNAME=your_username
APP_PASSWORD=your_password
```

### 3. Run the example tests

```powershell
pytest                                              # everything pytest.ini collects
pytest app_tests/tests/Issues/general               # one folder
pytest -k "PageLoad"                                 # by name expression
$env:APP_HEADLESS="false"; pytest                    # watch the browser locally
```

> The bundled `Issue` example points at placeholder selectors. Repoint `app_tests/pages/`
> and `login.py`/`navigation.py` at your own application to make them pass.

---

## Project layout

| Path | Purpose |
|---|---|
| `app_tests/conftest.py` | Playwright lifecycle, one-time session login, storage-state reuse, custom flags. |
| `app_tests/pages/login.py` | Single place that knows how to authenticate. |
| `app_tests/pages/navigation.py` | Central menu/navigation helpers — all routing lives here. |
| `app_tests/pages/Issues/IssuePage.py` | **Example** list/grid page object (the reusable GSF patterns). |
| `app_tests/pages/Issues/IssueDetailPage.py` | **Example** detail page object (workflow patterns). |
| `app_tests/tests/Issues/general/` | **Example** General Screen Functionality suite. |
| `app_tests/tests/Issues/workflows/` | **Example** workflow suite (detail panel, edit/save, tabs). |
| `.ai/handbook.md` | **The source of truth.** Assistant-neutral rules every generated test must follow. |
| `.ai/prompts/` | Reusable generation prompts + a compact rules digest. |
| `.ai/skills/`, `.ai/commands/` | Skill/command sources, wrapped for Claude (`.claude/`) and Codex (`.codex/`). |
| `docs/` | Enablement guide, the "add a screen" tutorial, and the Vaadin selector appendix. |
| `pipeline/` | Starter Azure DevOps pipelines (scheduled run + PR validation). |
| `scripts/` | `validate_ai_adapters.py` (wrapper check) and `check_test_rules.py` (no asserts/locators in tests). |
| `.pre-commit-config.yaml` | Runs the two checks above on every commit (`pre-commit install`). |
| `tools/md_to_docx.py` | Generate a throwaway Word `.docx` from a Markdown doc on demand (output is git-ignored; Markdown stays the source of truth). |
| `CLAUDE.md`, `AGENTS.md` | Bridges that point assistants at `.ai/handbook.md`. |
| `CHANGELOG.md` | Log of every change. |

---

## How the AI assets fit together

```
.ai/handbook.md          ← rules every generated test must obey (the contract)
   │
   ├── .ai/prompts/       ← reusable "how to generate X" instructions
   │
   └── .ai/skills/  +  .ai/commands/      ← entry points an assistant can invoke
            │                    │
   .claude/skills/  .codex/skills/    .claude/commands/  .codex/commands/
            └──────── thin wrappers that read the shared source ────────┘
```

When you change a rule, change it in `.ai/handbook.md` **first**; the wrappers never duplicate logic.

Available skills/commands (generic):

| Command | What it does |
|---|---|
| `/generate_general_tests` | Generate a General Screen Functionality suite for a screen, using live DOM inspection. |
| `/generate_workflow_tests` | Generate workflow tests (detail panel, edit/save, tabs) from a screen blueprint. |
| `/review_tests` | Review tests for the handbook rules (no locators/asserts in tests, POM coverage). |
| `/run_tests` | Run a selected pytest target and summarize results. |

---

## The golden rules (full version in `.ai/handbook.md`)

1. **No `assert` statements in test files.** Assertions live in `verify_*` page-object methods.
2. **No Playwright locators in test files.** Selectors live in page objects.
3. **Tests read top-to-bottom as a workflow:** create page objects → navigate → act → `verify_*()`.
4. **Clean up after yourself** — close any dialog/overlay/detail panel a test opened.
5. **Tests are independent** — never depend on state left by a previous test.
6. **Document legitimate skips** with a classified reason prefix (`NA_FEATURE:`, `NA_DATA:`, `NEEDS_REVIEW:`, `ENV_BLOCKED:`).
7. **Log every change** in `CHANGELOG.md`.

---

## Enablement docs

- `docs/ai-testing-enablement.md` — the Confluence-ready guide: setup, framework choices,
  learnings, key pointers, and a rollout checklist for a new team. **This Markdown is the single
  source of truth.** Need a Word copy (e.g. to attach somewhere)? Generate a throwaway one with
  `python tools/md_to_docx.py docs/ai-testing-enablement.md guide.docx` — `.docx` files are
  git-ignored so the two formats can never drift.
- `docs/adding-a-screen.md` — step-by-step tutorial for covering your first real screen.
- `docs/demo-walkthrough.md` — a 30-minute lunch-and-learn outline for introducing the approach to a team.
- `docs/vaadin-selector-appendix.md` — hard-won selector learnings for **Vaadin-based** apps
  (shadow DOM, flatpickr date pickers, lookup buttons). Skip it if your app isn't Vaadin.

---

## Making it your own — checklist

1. Rename the package (`app_tests/`) and the `Issue` example to one real screen in your app.
2. Implement `login.py` against your real login form.
3. Fill in `navigation.py` for how your app routes between screens.
4. Get **one** small test passing end-to-end before generating more.
5. Edit `.ai/handbook.md` so its rules match *your* app's conventions and selector quirks.
6. Then let the assistant generate the rest with `/generate_general_tests`.
