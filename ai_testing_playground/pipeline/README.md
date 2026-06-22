# Pipelines

Starter Azure DevOps pipelines. Both are templates — adjust the pool, schedule, and test paths.

| File | Purpose |
|---|---|
| `azure-pipelines.yml` | Scheduled headless run of the suite (weekly by default). Publishes JUnit results and failure traces/screenshots. |
| `pr-validation.yml` | Runs only the tests affected by a pull request. Wire it in via a **branch policy** on `main`. |

## One-time setup

1. **Variable group** — Pipelines → Library → add a group named **`ai-testing-playground`** with:
   - `APP_BASE_URL`
   - `APP_USERNAME`
   - `APP_PASSWORD` (mark as **secret**)
2. **Create the pipelines** — Pipelines → New pipeline → Azure Repos Git → select this repo →
   *Existing YAML file* → point at each file above.
3. **PR validation** — Repos → Branches → `main` → Branch policies → Build validation →
   add the `pr-validation` pipeline so it runs on every PR.

## Notes

- `vmImage: ubuntu-latest` is the simplest agent. If your app requires Windows (or is only
  reachable from your network), switch to a self-hosted pool.
- `--with-deps` installs the OS libraries Chromium needs on the hosted agent.
- Failure traces and screenshots are written to `reports/` by `conftest.py` and published as a
  build artifact, so you can download and open a Playwright trace for any failed test.
