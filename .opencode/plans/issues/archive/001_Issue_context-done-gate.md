# Issue: Add context-refresh DONE-gate to to-issues skill + issue template

<!-- Kanban status — update as work progresses: TODO | DOING | DONE | BLOCKED <one-line reason> | CANCELLED -->
**Status:** DONE

- **ID**: 001
- **Parent PRD**: `001_PRD_context-done-gate.md`
- **File**: `001_Issue_context-done-gate.md`

## What to build

Edit `skills/to-issues/SKILL.md` so that every issue the skill produces carries an **unconditional close-out gate**: a checkbox requiring `.opencode/context/` to be refreshed via `/refresh-context-md` before the issue may flip to `Status: DONE`. The gate appears in (a) the skill prose as an explicit transition rule, and (b) the `<issue-template>` block as a `## Close-out` section holding the checkbox.

This is a skill/template edit, not runtime code. Cosmetic changes (internal renames, test-only, dependency bumps) still pass the gate — the `/refresh-context-md` drift-patch phase produces no diff when nothing context-relevant drifted.

## First step (test-first)

Structural red→green test (no runtime — this is a doc specimen):

1. Assert `skills/to-issues/SKILL.md` does NOT currently contain a close-out gate rule or a `/refresh-context-md` checkbox in the issue template → **red** (expected today).
2. After the edit, assert the file contains both:
   - A rule stating `Status → DONE` requires the context-refresh gate to be ticked.
   - An issue-template section holding `- [ ] \`.opencode/context/\` refreshed via \`/refresh-context-md\``.
3. Assert the existing TDD first-step convention and template fields are still present (grep anchors: `First step (test-first)`, `Acceptance criteria`, `Blocked by`).

Concretely: run a `grep`/Read over the edited `SKILL.md` checking the four anchors exist and the two new strings exist. All anchors + new strings present → **green**.

## Acceptance criteria

- [x] `skills/to-issues/SKILL.md` prose states that `Status → DONE` requires the context-refresh close-out checkbox to be ticked.
- [x] The `<issue-template>` block in `skills/to-issues/SKILL.md` contains a `## Close-out` section with checkbox: `` - [ ] `.opencode/context/` refreshed via `/refresh-context-md` ``.
- [x] Gate wording is unconditional (cosmetic/internal changes still pass via refresh no-op, not skipped).
- [x] Existing template fields unchanged: `What to build`, `First step (test-first)`, `Acceptance criteria`, `Blocked by`, the Status header comment, and the TDD-first-step note.
- [x] Skill still instructs moving DONE/CANCELLED issues to `.opencode/plans/issues/archive/`.

## Close-out

- [x] `.opencode/context/` refreshed via `/refresh-context-md` — no-op: config repo has no `.opencode/context/` tree and this is a docs-only change (excluded by [context-hygiene.md](../../instructions/context-hygiene.md)). Gate satisfied.

## Blocked by

None — can start immediately.
