# PRD: Context-refresh DONE-gate for to-issues

**Status:** Done

- **ID**: 001
- **File**: `001_PRD_context-done-gate.md`

## Problem

[Context freshness analysis](../../skills/to-issues/SKILL.md) showed the `.opencode/context/` keep-updated rule is **advisory only**: nothing blocks an issue from flipping `Status → DONE` while skipping the context-doc update. Compliance is 100% model discretion. Over a session the context tree drifts silently; only the manual `/refresh-context-md` backstop recovers it, and it is rarely run on time.

User declined automation (no hooks, no CI gate). Instead: make the gate **explicit and close-out-enforced** at the issue level — an issue may not move to `DONE` until `.opencode/context/` has been refreshed.

## Goal

Every issue produced by the `to-issues` workflow carries an unconditional close-out gate: `[ ] .opencode/context/ refreshed via /refresh-context-md`. The gate is stated **twice** — in the `to-issues` skill (so the authoring agent writes it into every issue) and inside each issue's close-out checklist (so the implementing agent must tick it before `Status → DONE`).

## Non-goals / out of scope

- No git hooks, no pre-commit, no CI verification.
- No restating the gate in `agents/build.md` / `agents/automode.md` (user scoped to skill + issue only).
- No changes to `context-hygiene.md`, `to-prd`, or `/refresh-context-md` itself.
- No retrofitting already-archived or in-flight issues.
- Gate does **not** decide whether a context edit is needed — that judgment stays in `context-hygiene.md`. The gate only enforces that a refresh was run (its drift-patch phase no-ops if nothing drifted).

## Requirements

1. **Unconditional gate.** Every issue, regardless of whether the change touches architecture/API/data model, must run `/refresh-context-md` (or equivalent drift check) before `Status → DONE`. Cosmetic/internal changes still pass the gate — the command's drift-patch phase simply produces no diff.
2. **In the skill.** `skills/to-issues/SKILL.md` states: an issue's `Status → DONE` transition requires the context-refresh close-out checkbox to be ticked; the checkbox is part of the issue template.
3. **In the issue template.** The `<issue-template>` block in `skills/to-issues/SKILL.md` gains a `## Close-out` (or equivalent) section containing the checkbox: `- [ ] \`.opencode/context/\` refreshed via \`/refresh-context-md\``.
4. **Preserve existing structure.** No other template fields removed. TDD-first-step rule for new features stays intact.

## Acceptance criteria

- [x] `skills/to-issues/SKILL.md` contains an explicit rule that `Status → DONE` requires the context-refresh gate to be ticked.
- [x] The issue template inside `skills/to-issues/SKILL.md` contains a close-out checkbox referencing `/refresh-context-md`.
- [x] Gate is unconditional (not gated on "touches architecture" judgment) — wording makes cosmetic/internal changes still pass via the refresh no-op path.
- [x] Existing template fields and the TDD-first-step convention are unchanged.

## Further notes

- **No context update needed** — this config repo (`~/.config/opencode`) has no `.opencode/context/` tree; it is the config itself, not a project consuming the config. The change edits rule docs, which `context-hygiene.md` explicitly excludes from mandatory context updates ("docs-only changes — no context edit needed").
- If a consuming project later wants to audit gate compliance retroactively, that belongs to a future PRD (hook/CI) — explicitly declined here.
