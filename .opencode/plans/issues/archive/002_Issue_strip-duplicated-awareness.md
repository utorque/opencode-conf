# Issue: Strip duplicated awareness from build.md + automode.md

<!-- Kanban status — update as work progresses: TODO | DOING | DONE | BLOCKED <one-line reason> | CANCELLED -->
**Status:** DONE

- **ID**: 002
- **Parent PRD**: `000_PRD_config-reconciliation.md`
- **File**: `002_Issue_strip-duplicated-awareness.md`

## What to build

End-to-end: removes the two paraphrased awareness sections ("Planning artifacts (awareness, not enforcement)" and "Project context hygiene (awareness)") from `~/.config/opencode/agents/build.md` and `~/.config/opencode/agents/automode.md`, replacing each pair with a single one-line pointer. Also drops the spurious `In Progress` PRD Status value that only appears in `automode.md`'s awareness section.

Files touched:

- `~/.config/opencode/agents/build.md`
- `~/.config/opencode/agents/automode.md`

Specific changes per file:

- **Delete** the `## Planning artifacts (awareness, not enforcement)` section and the `## Project context hygiene (awareness)` section (both headings + their full body).
- **Insert** a single replacement line, placed where the two sections used to start: `See AGENTS.md (Project context hygiene) and .opencode/plans/ conventions.`
- In `automode.md` only: the deleted "Planning artifacts" section mentions PRD Status values `Draft / Aligned / In Progress / Done / Cancelled`. Removing the section eliminates the `In Progress` reference — which is the goal (the canonical enum is `Draft → Aligned → Done → Cancelled`, owned by `planner.md` per `001_Issue_planner-thin-orchestrator.md`).
- Do NOT touch the rest of either file (intro paragraph, permission list, "autonomous engineering agent" framing, etc.).
- Do NOT touch `multimodal.md` or `planner.md`.

## First step (test-first)

Tracer bullet:

1. Back up `~/.config/opencode/agents/build.md` and `~/.config/opencode/agents/automode.md` to `/tmp/opencode-backup-pre-002/`.
2. Apply the section removals.
3. Restart opencode.
4. First failing-behavior assertion: `grep -l "Planning artifacts (awareness" ~/.config/opencode/agents/*.md` returns nothing. On the OLD files this matches `build.md` + `automode.md` → RED. After change → GREEN (zero matches).
5. Second assertion: `grep -l "In Progress" ~/.config/opencode/agents/*.md` returns nothing. Proves the spurious PRD Status value is gone.
6. Third assertion: `opencode` boots without `ConfigInvalidError`. Proves the edits didn't break frontmatter or markdown structure.
7. Fourth assertion: switch to `automode` in TUI, give it a small task — confirm it still announces destructive actions before running them (its intro paragraph + behavior unchanged). Proves only awareness sections were removed, not the agent's operating rules.

These four behaviors form the vertical tracer bullet. No tests written up front beyond them.

## Acceptance criteria

- [ ] `grep -rl "Planning artifacts (awareness" ~/.config/opencode/agents/` returns no matches.
- [ ] `grep -rl "Project context hygiene (awareness)" ~/.config/opencode/agents/` returns no matches.
- [ ] `grep -rl "In Progress" ~/.config/opencode/agents/` returns no matches (the spurious PRD Status value is gone).
- [ ] `~/.config/opencode/agents/build.md` still has its frontmatter intact (`description`, `mode`, `model`, `permission`).
- [ ] `~/.config/opencode/agents/automode.md` still has its frontmatter intact (`description`, `mode`, `model`, `permission`).
- [ ] Both files contain the replacement pointer line `See AGENTS.md (Project context hygiene) and .opencode/plans/ conventions.`
- [ ] Neither file's intro paragraph or operating-rules body (the parts outside the two deleted sections) was modified.
- [ ] `multimodal.md` and `planner.md` untouched by this issue.
- [ ] `opencode` boots without `ConfigInvalidError` after restart.
- [ ] In automode mode, a destructive-action prompt ("delete file X") still triggers the one-line announcement before running. Proves the unchanged operating rules still hold.
- [ ] Backup at `/tmp/opencode-backup-pre-002/` retained until PRD `000` is fully Done.

## Blocked by

None — can start immediately. Owns `agents/build.md` and `agents/automode.md` only; no other issue touches these files. Parallel-safe with `000_Issue_split-agents-md-instructions-tree.md` and `001_Issue_planner-thin-orchestrator.md`.
