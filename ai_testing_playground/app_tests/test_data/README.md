# Test data fixtures

Screen-specific, data-driven test inputs live here as **CSV** or **JSON** files. Keeping data
out of the test code lets you add coverage by adding a row, not by writing a new test, and keeps
the example values in one reviewable place.

## Worked example (already in this folder)

[`issue_filters.csv`](issue_filters.csv) drives the parametrized test
[`test_TC011 - SM_Issues_DataDrivenFilter.py`](../tests/Issues/general/test_TC011%20-%20SM_Issues_DataDrivenFilter.py).
Each row becomes its own pytest case:

```csv
case_id,column_index,filter_term
DD01,0,A
DD02,0,E
DD03,0,S
```

Run just those cases:

```powershell
pytest -k "DataDrivenFilter"
```

## The pattern

1. **Put the data here.** One file per screen/scenario (`<screen>_<thing>.csv` or `.json`).
2. **Load it at module scope** in the test file and feed it to `@pytest.mark.parametrize` —
   give each case a stable `id` (e.g. the `case_id` column) so a failure names the offending row.
3. **Keep the handbook rules.** Loading/parsing data is plain setup and is fine in a test file,
   but every **locator and assertion still lives in the page object**. The test body stays a thin
   `navigate -> act -> verify` workflow; only the *inputs* come from the file.

```python
def _load_cases():
    with (Path(__file__).resolve().parents[3] / "test_data" / "issue_filters.csv").open() as f:
        return [pytest.param(int(r["column_index"]), r["filter_term"], id=r["case_id"])
                for r in csv.DictReader(f)]

@pytest.mark.parametrize("column_index, filter_term", _load_cases())
async def test_...(logged_in_page, column_index, filter_term):
    ...
```

JSON works the same way — `json.loads(path.read_text())` then build the param list. Prefer CSV
for flat tabular cases and JSON when a case needs nested/structured input.