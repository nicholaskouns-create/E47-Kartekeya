---
name: platform-interconnect
description: >-
  Wire and maintain the interactive interconnected platform layer for
  E47-Kartekeya: Copilot skills, agents, instructions, setup steps, MCP-facing
  docs, robots/agent access guidance, and cross-workflow automation. Use when
  asked to install skills, connect agents, configure copilot setup, platform
  interconnect, or multi-agent workflow glue.
argument-hint: 'skills | agents | setup | access | status'
user-invocable: true
---

# platform-interconnect

Keep the repo’s agent/platform surface coherent, discoverable, and durable.

## Platform map

| Layer | Location | Role |
|---|---|---|
| Skills | `.github/skills/**/SKILL.md` | On-demand workflows (`/name`) |
| Agents | `.github/agents/*.agent.md` | Specialized personas |
| Instructions | `.github/copilot-instructions.md` | Always-on repo guidance |
| Setup | `.github/workflows/copilot-setup-steps.yml` | Preinstall tools/deps for cloud agent |
| CI fabric | `.github/workflows/*.yml` | validate, cert, publish |
| Math core | `src/e47/` | Frozen algebraic implementation |
| Docs | `docs/` | provenance, validation scope, maintenance |

## Subcommands

### skills

1. List `.github/skills/*/SKILL.md` with name + description.
2. Add/update skills only under `.github/skills/<name>/SKILL.md`.
3. Keep density low: prefer improve/merge over proliferating overlaps.
4. Required frontmatter: `name` (matches folder), `description` (what + when).

### agents

1. List `.github/agents/`.
2. Create/update `*.agent.md` with clear tools/skills references.
3. Agents should point at skills rather than duplicating long procedures.

### setup

1. Ensure `copilot-setup-steps.yml` exists with job name `copilot-setup-steps`.
2. Install Python 3.12, `pip install -e . -r requirements.txt -r requirements-dev.txt`.
3. Keep permissions minimal (`contents: read` unless writes are required).

### access

1. Distinguish **crawler** access (`robots.txt`) from **GitHub App/repo** access
   (Settings → Integrations — not solvable by code alone).
2. Do not open noop PRs for permission grants; give admin steps when needed.

### status

Emit a compact checklist: skills present, agents present, instructions present,
setup workflow present, CI workflows healthy, cert artifact present.

## Guardrails

- Do not modify frozen E47 invariants while doing platform glue work.
- Do not commit secrets or expand permissions casually.
- Prefer linking existing docs over copying large policy text into skills.

## Related skills

- `/chronicle` — session history tips and instruction improvement
- `/fix-ci` — workflow failure recovery
- `/regenerate-certificate` — cert automation
- `/validate-invariants` — math/CI validation
