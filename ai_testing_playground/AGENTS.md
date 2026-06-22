# Agent Instructions (Codex, Claude Code, and other assistants)

This repository uses a single, assistant-neutral source of truth for all automation
guidance: **`.ai/handbook.md`**.

Before generating, reviewing, or running tests — or editing any skill, command, or
prompt — read `.ai/handbook.md` and follow it.

- Claude Code also reads `CLAUDE.md`, which is a thin bridge pointing here and to the handbook.
- Codex reads this file (`AGENTS.md`).
- Both must converge on `.ai/handbook.md` so behaviour is identical regardless of which assistant runs.

## Skills and commands

- Skill source of truth: `.ai/skills/<skill-name>/SKILL.md`
  - Claude wrapper: `.claude/skills/<skill-name>.md`
  - Codex wrapper: `.codex/skills/<skill-name>/SKILL.md`
- Command source of truth: `.ai/commands/<command-name>.md`
  - Claude wrapper: `.claude/commands/<command-name>.md`
  - Codex wrapper: `.codex/commands/<command-name>.md`

The wrappers must point back to the shared source rather than duplicating logic.
A change that adds or edits a skill/command is incomplete if any wrapper is missing.
