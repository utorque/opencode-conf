# Agents & skills

> How opencode's agent/phase/permission profiles relate to skill bodies.

## Agents (`agents/*.md`)

Four agents, each a YAML-frontmatter + body definition loaded by opencode:

| Agent | Mode | Model | Role |
|-------|------|-------|------|
| `planner` | `primary` | `neuralwatt/glm-5.2` (`variant: max`) | Read-only outside `.opencode/plans/**`. Drives alignment (`/grilling`), PRD authoring, issue decomposition. Writes only to `.opencode/plans/**`. The opencode-builtin `plan` agent is disabled (`agent.plan.disable: true` in `opencode.jsonc`) — this is its replacement. |
| `build` | `primary` | `neuralwatt/glm-5.2-short` | Main engineering/coding agent. Text-only. Implements one issue. May spawn `multimodal` subagent (only `task` it can launch). |
| `automode` | `primary` | `neuralwatt/glm-5.2-short` (`variant: high`) | Autonomous multi-step. All permissions `allow`. Unattended risk. |
| `multimodal` | `subagent` (`hidden: true`) | `neuralwatt/moonshotai/Kimi-K2.7-Code` | Visual inspection: screenshots, UI, diagrams. Read-only (read/glob/grep/list). |

Permission matrix lives per-agent in the file frontmatter. Permissions policy at top level in `opencode.jsonc` (`permission.skill.*: allow`).

## Skills (`skills/*/SKILL.md`)

Workflow single source of truth. Agents **reference** skill bodies; they do NOT paraphrase them. Loaded via `permission.skill.*: allow` + `/skill` tool (or implicit instruction body). Skill families:

- **caveman family** — terse-mode compression skills. `caveman` (mode), `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`. Most have a brief `README.md` alongside `SKILL.md`.
- **planning family** — `grilling` (alignment interview), `to-prd` (synthesize PRD), `to-issues` (decompose PRD into tracer-bullet issues).
- **tdd** — red-green-refactor; default approach for new-feature issues.
- **pdf** — PDF read/write/merge/split/OCR; under `skills/pdf/` carries `forms.md`, `reference.md`, `scripts/`.

## Relationship

Agents define the *who/where* (role, phase, permission scope). Skills define the *how* (workflow body). An agent file's prose must point at skills rather than restate their steps — paraphrasing drifts (the failure mode PRD 000 reconciled out).

## Commands (`commands/*.md`)

Slash commands, frontmatter-prefixed:
- `refresh-context-md` (agent: `build`) — regenerates `.opencode/context/`.
- `project-status` — renders PRD completion + kanban board.
