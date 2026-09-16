# Skills and agents

This repository ships Copilot **skills** and **agents** for the interactive
interconnected E47 platform.

## Skills (`.github/skills`)

| Skill | Invoke | Purpose |
|---|---|---|
| `chronicle` | `/chronicle` | Session-history tips, standup, search, cost-tips, improve |
| `fix-ci` | `/fix-ci` | Investigate/fix GitHub Actions failures durably |
| `regenerate-certificate` | `/regenerate-certificate` | Regen validation/spectral certificates |
| `validate-invariants` | `/validate-invariants` | Pytest + frozen invariant checks |
| `platform-interconnect` | `/platform-interconnect` | Skills/agents/setup/access platform glue |

Each skill is a folder with `SKILL.md` (Agent Skills format). Copilot discovers
project skills from `.github/skills/**/SKILL.md`.

### Chronicle note

GitHub Copilot CLI also provides a built-in experimental `/chronicle` command
(`tips`, `standup`, `search`, `cost-tips`, `improve`). When that built-in is
unavailable in a given environment, the repository `chronicle` skill provides the
same workflow using the session store tools.

In Copilot CLI you may need experimental features enabled for the built-in
command. The repo skill works wherever project skills are loaded.

### CLI management (optional)

If using Copilot CLI locally:

```bash
copilot skill list
copilot skill add .github/skills/chronicle --project
```

## Agents (`.github/agents`)

| Agent | Role |
|---|---|
| `e47-validator` | Validation, certificates, CI recovery |
| `platform-orchestrator` | Skills/agents/setup interconnect |

## Always-on instructions

`.github/copilot-instructions.md` loads automatically for Copilot sessions and
encodes install/test commands, frozen invariants, and workflow map.

## Cloud agent bootstrap

`.github/workflows/copilot-setup-steps.yml` preinstalls Python 3.12 and the
editable package before cloud agent work. Merge to the default branch for pickup.
