# AGENTS.md — index

This file is the entry point. Always-on rules live in sibling files loaded
via `opencode.jsonc`'s `instructions: [...]` array; this file itself is the
first entry. Pointer references below are human cross-references, not
auto-include directives — the `instructions:` array does the loading.

## Rule files (always-on)

- `instructions/caveman.md` — caveman tone/verbosity mode.
- `instructions/context-mode.md` — context-mode MCP routing rules (BLOCKED / REDIRECTED).
- `instructions/context-hygiene.md` — `.opencode/context/` upkeep rules.

## Planning & context trees

- `.opencode/plans/` — PRDs and per-issue task files (see `000_PRD_config-reconciliation.md`).
- `.opencode/context/` — per-project living context tree (lazy-loaded via `@` refs).

## Parallel close-out (cross-agent)

When an agent launches multiple issues as parallel subagents, the launcher owns close-out after the batch returns: scan the PRD's `issues/` (excluding `archive/`) for non-archived siblings; if none remain, flip the PRD `Status: Aligned → Done` and move it to `.opencode/plans/archive/`. Individual subagents only flip their own issue's `Status` and archive their own issue file — no subagent knows whether it is the last one. PRD state machine lives in the `to-prd` skill; issue state machine in `to-issues`.

## Notes

Agent files under `agents/` describe their own role/phase/permission model;
they reference skills rather than paraphrase them. Skill bodies under
`skills/` are the single source of truth for workflow detail.
