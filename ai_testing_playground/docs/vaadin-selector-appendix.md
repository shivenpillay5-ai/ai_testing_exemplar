# Appendix: Selector learnings for Vaadin-based applications

> **Only relevant if your application under test is built on [Vaadin](https://vaadin.com/).**
> If it isn't, skip this entirely and keep your own equivalent appendix for your UI toolkit.

Vaadin renders heavy web-component markup with shadow DOM, and bundles third-party widgets (like
flatpickr for dates). These are the selector patterns that work reliably in a real Vaadin app,
collected from production automation. Fold the relevant ones into your `.ai/handbook.md` so every
generated test benefits.

---

## General selector preferences

- Prefer stable text selectors: `span:text-is("...")` (exact) and `span:has-text("...")` (contains).
- Use `role`/`name` selectors where the accessibility tree exposes them.
- For toolbar icon buttons with no better attribute, target the icon: e.g.
  `vaadin-button:has(iron-icon[icon="remix:download"])`.
- **Scope to the visible panel.** Vaadin frequently renders hidden duplicate DOM. Scope to the
  visible split-grid (`v-split-layout.gs-searchgrid:not([hidden])`) to avoid ambiguous matches.
- Add an explicit visibility wait (`expect(...).to_be_visible(timeout=...)`) before interacting.

## Tab-content sections render multiple times — always `.first`

Vaadin's nested layout can render the same `div.gs-section[name="..."]` up to three times (once
per nesting level). Calling `expect(section).to_be_visible()` then throws *strict mode violation:
resolved to 3 elements*. Always chain `.first` before any `expect()` or before descending with
`.locator()`. Note: in Playwright Python `.first` is a **property** — never write `.first()`.

## Breadcrumbs — use `.bread-link`

Target breadcrumb segments with `.bread-link`. Do **not** use `.gs-breadcrumb` /
`.gs-vbreadcrumb` / `vaadin-horizontal-layout.gs-breadcrumb` — the breadcrumb container lives in a
`slot="secondary"` web-component slot and is unreachable by Playwright at runtime; `.bread-link`
targets the concrete rendered `div` elements directly.

## Lookup fields & buttons

- **Don't find lookup fields by `[name="..."]`.** `vaadin-custom-field` lookups may have no `name`
  until their owning tab/section is active. Scope to the section and find the button by class:
  `vaadin-button.lookupButton, vaadin-button:has(iron-icon[icon="remix:search"])`.
- **Click lookup buttons with `dispatch_event('click')`** — not `.click()`, not JS `element.click()`.
  Vaadin's `tertiary-inline icon` theme sets `pointer-events: none`, so Playwright's `.click()`
  times out (`<html> intercepts pointer events`). A synthetic JS `element.click()` bypasses CSS
  but Vaadin's server-side listener ignores it. Only `locator.dispatch_event('click')` both
  bypasses the CSS and is received by the server handler.
- **The result is a dialog, not a dropdown.** Clicking a lookup opens a `vaadin-dialog-overlay`
  modal containing a results grid — it does *not* populate combo-box items. Assert
  `vaadin-dialog-overlay[opened]` and the grid inside it; close with `Escape` and wait for the
  overlay to hide before continuing.

## Date pickers use flatpickr, not Vaadin's native picker

- The calendar is flatpickr. To detect it opened, look for `div.flatpickr-calendar.open` — not
  `vaadin-date-picker-overlay[opened]`. A robust combined selector:
  `vaadin-date-picker-overlay[opened], vaadin-overlay[part="overlay"][opened], div.flatpickr-calendar.open`.
- **Actually pick a date and assert the value changed** — opening and closing the calendar is not
  a meaningful assertion.
- **Day cells are appended to `<body>`**, not inside the `v-datepicker` shadow DOM, so scoping a
  click to the field finds zero results. The calendar opens to the field's *current stored date*,
  not today, so computing an absolute label is wrong. Reliable pattern: stamp a stable `id` on the
  calendar container, then query a visible, in-month, non-selected day
  (`span.flatpickr-day:not(.prevMonthDay):not(.nextMonthDay):not(.flatpickr-disabled):not(.disabled)`
  filtered by not `.selected`), read its `aria-label`, and click that.

## Tab-bar overflow chevrons live in shadow DOM

The `vaadin-tabs` overflow chevrons are `<div>` elements with `part="forward-button"` /
`part="back-button"` **inside the shadow root** — not `<button>`/`vaadin-button`. Playwright CSS
chained from a parent locator doesn't reliably pierce into that shadow root, so use
`page.evaluate` with `tabs.shadowRoot.querySelector('div[part="forward-button"]')`. Vaadin's
`ResizeObserver` sets `overflow="end"` asynchronously after render, so `wait_for_function` for it
before asserting. The back-button div is always present regardless of scroll position — don't use
its presence as proof of scrolling; assert `div[part="tabs"].scrollLeft > 0` instead.

## ag-grid column filters commit on blur

ag-grid only applies a column filter value when the input loses focus via a **mouse** click — not
Enter/Tab. After typing (or clearing) the value, click the grid body to blur:

```python
await self._panel.locator(".ag-root").click(position={"x": 10, "y": 200})
```

Without this mouse-blur, the value sits in the input but is never applied, and the test then times
out waiting for a paging change that never comes.

## Detail panel can auto-open and cover the grid

Screens with a `v-split-layout` detail panel auto-open it when only one record is visible, which
covers the grid and breaks subsequent clicks. Detect the panel height with `page.evaluate` +
`querySelector` (never `locator.evaluate`, which hangs waiting for an absent element) and collapse
it by clicking the split-layout handle before continuing pagination tests.
