# Agents & skills

> Why four agents exist, and the reference-don't-paraphrase boundary.

## Why these agents

- `planner` — read-only outside `.opencode/plans/**`; owns alignment + decomposition. Replaces opencode's builtin `plan` agent (disabled: `agent.plan.disable: true`) so read-only scope is enforced per-phase, not by willpower.
- `build` — one-issue implementer, text-only. Spawns `multimodal` for visual inspection (its only subagent).
- `automode` — autonomous multi-step, all permissions `allow`. Unattended risk.
- `multimodal` — hidden subagent; visual inspection only (read/glob/grep/list).

Per-agent model/mode/permissions live in each `agents/*.md` frontmatter — read the file for specifics.

## Skills

Workflow single source of truth under `skills/*/SKILL.md`. Families: planning (`grilling`, `to-prd`, `to-issues`), `tdd`, `pdf`.

## Boundary

Agents define *who/where* (role, phase, scope). Skills define *how* (workflow body). Agent prose must **reference** skill bodies, not paraphrase them — paraphrasing drifts (the failure mode PRD 000 reconciled out).
