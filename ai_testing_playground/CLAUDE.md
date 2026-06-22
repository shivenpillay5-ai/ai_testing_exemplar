# Claude Instructions

This repository's shared automation handbook lives in `.ai/handbook.md`.

Before making code, test, prompt, skill, or workflow-generation changes in this repo, read `.ai/handbook.md` and follow its repository-specific guidance unless it conflicts with a direct user instruction or higher-priority system/developer instruction.

Do not duplicate the full `.ai/handbook.md` contents here. Keep this file as a bridge so Claude and other assistants draw from the same source of truth.

When updating repository-wide automation rules, update `.ai/handbook.md` first, then adjust this file only if the bridge itself needs to change.

## Skill Creation Rule

Any new repository skill must be created in `.ai/skills/<skill-name>/SKILL.md` as the source of truth, with both required wrappers added in the same change:

- `.claude/skills/<skill-name>.md`
- `.codex/skills/<skill-name>/SKILL.md`

A skill change is incomplete if either wrapper is missing. When prompting an AI assistant to create or update a skill, explicitly include this wrapper requirement in the prompt.

Every repository skill should also be invokable as a command. Add a same-name (or name-normalized) command source and both command wrappers:

- `.ai/commands/<skill-name>.md`
- `.claude/commands/<skill-name>.md`
- `.codex/commands/<skill-name>.md`

## Command Creation Rule

Any new repository command must be created in `.ai/commands/<command-name>.md` as the source of truth, with both required wrappers added in the same change:

- `.claude/commands/<command-name>.md`
- `.codex/commands/<command-name>.md`

A command change is incomplete if either wrapper is missing. When prompting an AI assistant to create or update a command, explicitly include this wrapper requirement in the prompt.
