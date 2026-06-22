#!/usr/bin/env python3
"""Validate that every AI skill/command has its Claude and Codex wrappers.

The repo keeps a single source of truth under `.ai/` and thin wrappers under `.claude/` and
`.codex/`. This script enforces that discipline so a half-added skill/command can't slip in.

Run:  python scripts/validate_ai_adapters.py
Exit: 0 when everything is wired up, 1 (with a report) when a wrapper is missing.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_skills() -> list[str]:
    problems = []
    skills_dir = ROOT / ".ai" / "skills"
    if not skills_dir.exists():
        return problems
    for skill_src in sorted(skills_dir.glob("*/SKILL.md")):
        name = skill_src.parent.name
        claude = ROOT / ".claude" / "skills" / f"{name}.md"
        codex = ROOT / ".codex" / "skills" / name / "SKILL.md"
        if not claude.exists():
            problems.append(f"skill '{name}': missing Claude wrapper {claude.relative_to(ROOT)}")
        if not codex.exists():
            problems.append(f"skill '{name}': missing Codex wrapper {codex.relative_to(ROOT)}")
    return problems


def check_commands() -> list[str]:
    problems = []
    commands_dir = ROOT / ".ai" / "commands"
    if not commands_dir.exists():
        return problems
    for command_src in sorted(commands_dir.glob("*.md")):
        name = command_src.stem
        claude = ROOT / ".claude" / "commands" / f"{name}.md"
        codex = ROOT / ".codex" / "commands" / f"{name}.md"
        if not claude.exists():
            problems.append(f"command '{name}': missing Claude wrapper {claude.relative_to(ROOT)}")
        if not codex.exists():
            problems.append(f"command '{name}': missing Codex wrapper {codex.relative_to(ROOT)}")
    return problems


def main() -> int:
    problems = check_skills() + check_commands()
    if problems:
        print("AI adapter validation FAILED:\n")
        for p in problems:
            print(f"  - {p}")
        print(
            "\nEvery .ai/skills/<name>/SKILL.md needs .claude/skills/<name>.md and "
            ".codex/skills/<name>/SKILL.md;\nevery .ai/commands/<name>.md needs "
            ".claude/commands/<name>.md and .codex/commands/<name>.md."
        )
        return 1
    print("AI adapter validation passed — all skills and commands have their wrappers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
