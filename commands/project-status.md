---
description: Render project status — PRD completion, kanban board, archived-done count, next NNN, and issue dependency graph.
---
Render the current status of the `.opencode/plans/` tree. Read the files directly; no plugin, no tools. If `.opencode/plans/` does not exist, say "No plan tree — run /new-prd to start." and stop.

## Conventions (source of truth)

- PRDs: `.opencode/plans/NNN_PRD_<slug>.md` (exclude `archive/`). Status from the `- **Status**: Draft|Aligned` metadata bullet.
- Active issues: `.opencode/plans/issues/NNN_Issue_<slug>.md`. Archived issues: `.opencode/plans/issues/archive/NNN_Issue_<slug>.md`.
- Issue status line: `**Status:** TODO|DOING|DONE|BLOCKED <one-line reason>|CANCELLED`.
- Parent PRD link: an issue body line `- **Parent PRD**: \`NNN_PRD_<slug>.md\``.
- `## Blocked by` section lists `NNN_Issue_<slug>.md` file refs (siblings the issue waits on).
- NNN ids are zero-padded to 3 digits; next free id = max(existing across active+archive)+1, padded. Gaps from archives are NOT backfilled.

## Steps

1. **Gather.** List every PRD file (exclude `archive/`), every active issue, and every archived issue. Read each one to parse its status, Parent PRD, Blocked-by refs, and slug. Skip `.gitkeep`.

2. **PRD completion.** For each PRD, find every issue (active OR archived) whose `Parent PRD` line references that PRD's filename. Compute `done = count(status === DONE)`, `total = count(all referencing issues)`. Render as a list:
   ```
   - #NNN <slug> — Status: <Draft|Aligned> — <done>/<total> issues done (<pct>%)
   ```
   When a PRD has zero referencing issues, show `0/0 issues done (—)`. When `done === total === 0`, it just means no issues decomposed yet.

3. **Kanban board.** Render active issues (exclude `archive/`) as a 5-column markdown table — `| TODO | DOING | BLOCKED | DONE | CANCELLED |`. One entry per line joined with `<br>`. Empty cell = `_(none)_`. Each entry: `[#NNN_<slug>](<relative path from .opencode/plans/>)`. BLOCKED entries append their reason inline (truncate to ~40 chars + `…` if longer).

4. **Archived DONE count.** One line: `_N issues archived as DONE._` (count files under `issues/archive/` whose status is DONE). If 0, say `_(no archived issues yet)_`.

5. **Next NNN hint.** Two lines:
   ```
   Next PRD id:  NNN
   Next issue id: NNN
   ```
   Compute each as the max existing NNN (scan active+archive for that kind) +1, zero-padded to 3 digits.

6. **Dependency graph.** Render a Mermaid `flowchart LR` of active issues only. One node per active issue, labelled `NNN<br/><slug>` (slug truncated to ~20 chars). Draw an edge `BLOCKER --> BLOCKED` for every `## Blocked by` entry that resolves to another active issue (skip refs to archived issues — those are done). Style nodes by status:
   - TODO: `:::todo` (or default)
   - DOING: fill `#ffd166` via classDef
   - BLOCKED: fill `#ef476f` (white text)
   - DONE: fill `#06d6a0`
   - CANCELLED: fill `#cccccc` (strikethrough label)

   Define `classDef` entries once. If there are no edges (everyone is unblocked), emit the graph with just nodes and a one-line caption: `_(no active blockers — all issues parallelisable)_`.

## Output order

Render the six sections in order: PRD completion → kanban → archived DONE count → next NNN → dependency graph. Section headers are `## ` markdown headings. Do not add commentary beyond the sections.
