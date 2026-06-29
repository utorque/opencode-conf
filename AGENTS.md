# AGENTS.md — index

This file is the entry point. Always-on rules live in sibling files loaded
via `opencode.jsonc`'s `instructions: [...]` array; this file itself is the
first entry. Pointer references below are human cross-references, not
auto-include directives — the `instructions:` array does the loading.

## Project Overview and objectives

This config tunes [opencode](https://opencode.ai) for **token-efficient, plan-first agentic coding**. Priorities, in order:

1. **Protect the context window** — large outputs routed through a sandbox and indexed (context-mode), model responses compressed (caveman). Raw bytes never enter conversation unless needed for an edit.
2. **Plan before build** — every non-trivial feature goes through align → plan → decompose → build. `/grilling` stress-tests understanding before a PRD exists.
3. **Parallel by default** — issues are independently-grabbable vertical slices; the launcher fans them out as concurrent subagents and owns close-out.
4. **Living context** — `.opencode/context/` mirrors the codebase and is updated in the same change as code when architecture/API/data model shifts.

If a task's **rationale or objective is missing or unclear** — why it matters, what success looks like, who/what it serves — you MUST invoke [`/grilling`](./skills/grilling/SKILL.md) to interview the user until the "why" is shared before designing or building. Do not guess the why.

## Rule files (always-on)

- [instructions/caveman.md](./instructions/caveman.md) — caveman tone/verbosity mode.
- [instructions/user-preferences.md](./instructions/user-preferences.md) — code-style defaults + standing "be critical" push-back posture.
- [instructions/context-mode.md](./instructions/context-mode.md) — context-mode MCP routing rules (BLOCKED / REDIRECTED).
- [instructions/context-hygiene.md](./instructions/context-hygiene.md) — `.opencode/context/` upkeep rules.

## Planning & context trees

- [`.opencode/plans/`](./.opencode/plans/) — PRDs and per-issue task files (see [000_PRD_config-reconciliation.md](./.opencode/plans/archive/000_PRD_config-reconciliation.md)).
- `.opencode/context/` — per-project living context tree (lazy-loaded via `@` refs).

## Parallel close-out (cross-agent)

When an agent launches multiple issues as parallel subagents, the launcher owns close-out after the batch returns: scan the PRD's `issues/` (excluding `archive/`) for non-archived siblings; if none remain, flip the PRD `Status: Aligned → Done` and move it to `.opencode/plans/archive/`. Individual subagents only flip their own issue's `Status` and archive their own issue file — no subagent knows whether it is the last one. PRD state machine lives in the `to-prd` skill; issue state machine in `to-issues`.

## Notes

Agent files under `agents/` describe their own role/phase/permission model;
they reference skills rather than paraphrase them. Skill bodies under
`skills/` are the single source of truth for workflow detail.
