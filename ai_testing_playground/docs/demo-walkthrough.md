# 30-Minute Demo: AI-Driven Testing Walkthrough

> **Purpose:** a 30-minute lunch-and-learn to show a team the AI-driven testing approach end to
> end and get them to try it. Companion to [ai-testing-enablement.md](ai-testing-enablement.md)
> and [adding-a-screen.md](adding-a-screen.md).
>
> **Audience:** QA engineers and developers. No prior Playwright/pytest knowledge assumed.
>
> **Goal of the session:** everyone leaves understanding the *generate → review → run* loop and
> the two golden rules, and at least one person volunteers to pilot it on a real screen.

This page mirrors the Confluence page **"30-Minute Demo: AI-Driven Testing Walkthrough"**. Keep
the two in sync if you edit either.

---

## Before the session (presenter prep)

- [ ] Clone the playground repo and get it opening in your IDE (Claude Code or Codex ready).
- [ ] Have a real, non-production app screen you can demo against, with a test login in `.env`.
- [ ] Confirm the Playwright MCP server connects (the assistant can open a browser).
- [ ] Do one dry run of the live demo so the generate step doesn't surprise you.
- [ ] Have this page, the enablement guide, and the repo open in tabs.
- [ ] Pre-open a failing test + its saved trace, in case the live generate has hiccups (a safe fallback).

---

## Agenda (30 minutes)

| Time | Segment | What to cover |
|---|---|---|
| 0:00–0:03 | **The problem** | Hand-writing UI tests is slow, repetitive, and drifts in style. Show a screen with ~15 obvious checks nobody has time to automate. |
| 0:03–0:08 | **The approach & stack** | Playwright + pytest + Page Object Model, driven by an AI assistant that reads a shared handbook and inspects the live DOM. Why each piece (1 line each). |
| 0:08–0:13 | **The two golden rules + repo tour** | No asserts and no locators in test files — everything lives in page objects. Show a test file (reads like English) next to its page object. Quick tour of `.ai/`, `app_tests/`, `docs/`. |
| 0:13–0:23 | **Live demo: generate → review → run** | The main event — see the script below. |
| 0:23–0:27 | **Pitfalls & guardrails** | Generated ≠ trusted (always review). Live-DOM inspection stops invented selectors. Pre-commit + trace-on-failure. Classified skips. |
| 0:27–0:30 | **Call to action + Q&A** | "Who has a screen we can pilot this week?" Point to the enablement guide and the [Adding your first screen](adding-a-screen.md) tutorial. |

---

## Live demo script (the 10-minute core)

> Narrate what you're doing and *why* at each step. The point isn't the output — it's that the
> assistant follows the handbook and inspects the real app.

1. **Show the spine.** Run the existing PageLoad test for a screen so the room sees a green test
   first. "This proves login, navigation, and selectors work — everything builds on this."
2. **Generate.** In the assistant: `/generate_general_tests <Screen>`. Call out that it opens the
   live app via Playwright MCP and reads the real DOM before writing anything. Show the page
   object + test files it produces.
3. **Read a generated test aloud.** Point out: no `assert`, no `locator()` — it reads as
   navigate → act → verify. The assertions live in the page object's `verify_*` methods.
4. **Review.** `/review_tests <folder>`. Show it checking the rules and running the suite. "This
   is the safety net — generated code still gets reviewed."
5. **Run + show a failure.** `/run_tests <folder>`. If something fails, open the auto-saved trace
   (`playwright show-trace`) and step through it. This usually gets the biggest reaction.
6. **Commit.** Mention the pre-commit hooks block a commit that breaks the wrapper rule or sneaks
   an assert into a test.

---

## Key messages (say these explicitly)

- The assistant accelerates the formulaic 80%; humans own strategy, review, and the tricky flows.
- The handbook is the contract — consistent output comes from written rules, not luck.
- Live-DOM inspection is the single biggest quality lever; it stops invented selectors.
- This is reusable across projects — the structure and handbook discipline travel; the example
  screen is just a pattern to copy.

---

## Likely questions (have answers ready)

- *"Can it test our app?"* — Yes; you implement `login.py` + `navigation.py` once, then generate per screen.
- *"Claude or Codex?"* — Either; both read the same `.ai/` sources.
- *"How do we trust generated tests?"* — Review step + the no-asserts/no-locators guardrails + a human read.
- *"What about flaky tests?"* — Playwright auto-waits; the handbook bans sleeps; session reuse removes login flakiness.
- *"How much time does it save?"* — Minutes vs hours on the formulaic suites; compounds as the handbook grows.

---

## Follow-up after the session

- [ ] Share the repo link and the enablement guide in the team channel.
- [ ] Book a 1-hour pairing slot with whoever volunteered a pilot screen.
- [ ] Capture any new selector quirks from the demo into `.ai/handbook.md`.

---

> Adjust timings to your audience. If you only have 15 minutes, keep the live demo and the two
> golden rules; drop the stack rationale and trim Q&A.
