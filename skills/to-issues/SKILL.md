---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issue files using tracer-bullet vertical slices. Use when the user wants to decompose a PRD (from .opencode/plans/) into actionable issues. Writes to .opencode/plans/issues/NNN_Issue_<clear_name>.md with a kanban Status header. Each new-feature issue starts with a failing test (TDD).
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets). Each issue becomes a local markdown file, not an external tracker ticket. No triage labels.

## Where issues live

- Issue files live in `.opencode/plans/issues/`
- File name: `NNN_Issue_<clear_name>.md`
- `NNN` is the next zero-padded sequence number. Scan `.opencode/plans/issues/` for existing `NNN_Issue_*.md` files (do not scan `archive/`) and pick the next free number. Start at `000` if none exist.
- Each issue begins with a kanban **Status** line (allowed values: `TODO`, `DOING`, `DONE`, `BLOCKED <one-line reason>`, `CANCELLED`)
- When an issue is DONE or CANCELLED, move its file to `.opencode/plans/issues/archive/`
- **DONE gate (unconditional):** before flipping `Status → DONE`, the issue's `## Close-out` checkbox (see template below) must be ticked. The checkbox requires `.opencode/context/` to be refreshed via `/refresh-context-md`. This is unconditional — every issue runs the refresh before DONE, including cosmetic/internal/test-only/docs-only changes; if nothing drifted, the command's drift-patch phase produces no diff and the gate passes as a no-op. The judgment of whether a context *edit* is needed stays in [context-hygiene.md](../../instructions/context-hygiene.md); the gate only enforces that a refresh was run.
- Reference the parent via its PRD file name, and sibling issues by their file names (e.g. `Blocked by: 002_Issue_export-profile-api.md`)

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a PRD (file name or path) as an argument, read its full body. The PRD is the source of truth for scope and user stories.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change." Prefactoring is its own vertical slice, done first.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer. This is non-negotiable — vertical slices are the whole point.

<vertical-slice-rules>

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Any prefactoring should be done first, as its own slice
- One slice ≈ one issue ≈ one PR. If a slice can't be demo'd alone, it's too thin; if it touches more than one user story, it's too fat
- Resist slicing by layer ("the backend issue", "the UI issue"). That is a horizontal slice and it is wrong

</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source PRD has them)
- **First test**: the one behavior the first failing test asserts (test-first — see the `tdd` skill)

Ask the user:

- Are the dependency relationships correct?
- Should any slices be split further?

Iterate until the user approves the breakdown.

<granularity-default>

**Always split parallelizable slices.** If two slices are independent (neither blocks the other), they belong in separate files — separate PRs, independently demoable, grabbable by parallel agents. Merging forfeits parallelism for no gain. Don't ask; just split.

Merge only when slices are coupled (can't be demoed without the other landing first) or share an indivisible user story. If unsure, split.

</granularity-default>

### 5. Write the issue files

For each approved slice, write a file to `.opencode/plans/issues/NNN_Issue_<clear_name>.md` using the body template below.

Write issues in dependency order (blockers first) so each issue can reference real sibling file names in the "Blocked by" field.

<issue-template>

# Issue: <short title>

<!-- Kanban status — update as work progresses: TODO | DOING | DONE | BLOCKED <one-line reason> | CANCELLED -->
**Status:** TODO

- **ID**: NNN
- **Parent PRD**: `NNN_PRD_<clear_name>.md` (omit if none)
- **File**: `NNN_Issue_<clear_name>.md`

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it here and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## First step (test-first)

For new features, the first concrete step is a **failing test** — see the `tdd` skill. Describe the single behavior the first test asserts, in user-facing terms. This test is a vertical tracer bullet: it must exercise the public path end-to-end and fail until the slice is minimally working.

Do NOT write all tests up front (that is horizontal slicing — an anti-pattern). Name the FIRST test only; the rest evolve during implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- `NNN_Issue_<sibling_clear_name>.md` (if any)

Or "None — can start immediately" if no blockers.

## Close-out

Tick before `Status → DONE` (unconditional gate — see [context-hygiene.md](../../instructions/context-hygiene.md)):

- [ ] `.opencode/context/` refreshed via `/refresh-context-md`

</issue-template>

Do NOT close or modify the parent PRD beyond updating its `Status` line.
