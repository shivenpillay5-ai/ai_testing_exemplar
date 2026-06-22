# Issues — worked example

This screen is the bundled **example**. Use it as the template to copy when you add a real screen.

- `general/` — General Screen Functionality (GSF) suite. The bundled subset (TC001–TC010) shows
  the core patterns: page load, grid load, paging label, select-all, pagination, refresh, export,
  add-new, column filter, clear column filter. A full GSF suite typically continues with
  previous/first/last page, advanced filter, settings, column-layout/density, clear-filters, and a
  date filter — generate the rest for your screen with `/generate_general_tests`.
- `workflows/` — atomic workflow suite generated from
  `.ai/prompts/sub-page-workflows/Issues.md`: one pytest case per blueprint entry.

> The selectors in `app_tests/pages/Issues/*.py` are placeholders. These tests will not pass
> against a real app until you repoint the page objects, `login.py`, and `navigation.py`.

How the layers relate:

```
test file (workflow)  →  IssuePage / IssueDetailPage  →  the browser
   navigate, act, verify        all selectors + assertions live here
```
