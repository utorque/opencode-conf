# Plan lifecycle

> PRD and issue state machines, parallel close-out, and the context DONE-gate.

## Flow: align → plan → decompose → build

Inspired by [mattpocock/skills](https://github.com/mattpocock/skills).

1. **Align** — `/grilling` interviews the user (auto-launched by `planner` agent) until the "why" is shared. Phase refuses to design/build if rationale unclear.
2. **Plan** — `to-prd` synthesizes the conversation + codebase understanding into a PRD at `.opencode/plans/NNN_PRD_<slug>.md`.
3. **Decompose** — `to-issues` breaks the PRD into tracer-bullet vertical-slice issues at `.opencode/plans/issues/NNN_Issue_<slug>.md`. Each new-feature issue starts with a failing test (TDD red→green→refactor).
4. **Build** — pick an issue in `automode`, implement against acceptance criteria; `Status` advances `TODO → DOING → DONE` (`BLOCKED`/`CANCELLED` if off-rail).

## PRD state machine (`to-prd`)

`Draft → Aligned → Done`

- `Draft` — being written.
- `Aligned` — alignment (grilling) complete; ready to decompose into issues.
- `Done` — non-archived issue siblings exhausted; PRD files move to `.opencode/plans/archive/`.

## Issue state machine (`to-issues`)

`TODO → DOING → DONE` (off-rails: `BLOCKED <reason>` | `CANCELLED`)

- `**Status:** TODO` — grabbable.
- `DOING` — picked up by an agent.
- `DONE` — gated by PRD 001's **Done-gate** (below).
- `BLOCKED` — needs user input, carries one-line reason.
- `CANCELLED` — abandoned superseded.

## Done-gate (PRD 001)

An issue may **not** move to `DONE` until `.opencode/context/` has been refreshed for any architecture/API/data-model shift introduced by the issue's work. User declined automation/hooks; gate is explicit + close-out-enforced at issue level.

## Parallel close-out

When a launcher fans out multiple issues as concurrent subagents, the launcher (not the individual subagents) owns close-out:

1. After the batch returns, scan the PRD's `issues/` (excluding `archive/`) for non-archived siblings.
2. If none remain, flip PRD `Status: Aligned → Done` and move PRD file into `.opencode/plans/archive/`.
3. Individual subagents only flip their **own** issue's `Status` and archive their **own** issue file — no subagent knows whether it is the last one.

## NNN counter

PRDs and issues share an incrementing `NNN` zero-padded counter. Next NNN derivable from highest existing number across active + archive trees.
