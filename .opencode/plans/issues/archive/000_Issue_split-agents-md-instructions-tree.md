# Issue: Split AGENTS.md into instructions/ tree

<!-- Kanban status — update as work progresses: TODO | DOING | DONE | BLOCKED <one-line reason> | CANCELLED -->
**Status:** DONE

- **ID**: 000
- **Parent PRD**: `000_PRD_config-reconciliation.md`
- **File**: `000_Issue_split-agents-md-instructions-tree.md`

## What to build

End-to-end: extracts the three stitched HTML-comment blocks out of `~/.config/opencode/AGENTS.md` into three standalone markdown files under a new `~/.config/opencode/instructions/` directory, and registers all four files in `opencode.jsonc`'s `instructions:` array so they load every session.

Files produced:

- `~/.config/opencode/instructions/caveman.md` — content between `<!-- caveman-begin -->` and `<!-- caveman-end -->`, fences removed, promoted to a top-level `# Caveman mode` header.
- `~/.config/opencode/instructions/context-mode.md` — content between `<!-- context-mode-begin -->` and `<!-- context-mode-end -->`, fences removed, top-level `# context-mode` header retained.
- `~/.config/opencode/instructions/context-hygiene.md` — content between `<!-- context-hygiene-begin -->` and `<!-- context-hygiene-end -->`, fences removed, top-level `# Project context hygiene` header.
- `~/.config/opencode/AGENTS.md` — rewritten as a ~20-line index. One short paragraph: "This file is the entry point. Always-on rules live in sibling files loaded via `opencode.jsonc` `instructions: [...]`." Then pointer lines (human cross-references, not auto-include directives) to `instructions/caveman.md`, `instructions/context-mode.md`, `instructions/context-hygiene.md`, `.opencode/plans/`, `.opencode/context/`.
- `~/.config/opencode/opencode.jsonc` — add `"instructions": ["AGENTS.md", "instructions/caveman.md", "instructions/context-mode.md", "instructions/context-hygiene.md"]` after the existing `"$schema"` line. Preserve `"$schema"`.

Content fidelity: rule text must be byte-identical to current AGENTS.md blocks apart from removing the fence lines and promoting the first header. No rewording.

## First step (test-first)

This is meta-config (markdown + JSONC), not application code — no unit-test seam. The vertical tracer bullet is a **config-boot test**:

1. Save the current state (`cp -r ~/.config/opencode /tmp/opencode-backup-pre-000`).
2. Make the file changes above.
3. Restart opencode: `opencode` in a fresh shell.
4. First failing-behavior assertion: at startup, the model is asked (via fresh session prompt) "what are the caveman-mode switch levels?" — answer must list `lite|full|ultra|wenyan`. If opencode fails to boot (`ConfigInvalidError`) or the answer is wrong, test fails. Red until the split lands correctly.

This test exercises the full public path: config parse → instructions load → rule content present in session context.

## Acceptance criteria

- [ ] Directory `~/.config/opencode/instructions/` exists with `caveman.md`, `context-mode.md`, `context-hygiene.md` files.
- [ ] None of the new files contain `<!-- ...-begin -->` or `<!-- ...-end -->` fence lines.
- [ ] `~/.config/opencode/AGENTS.md` is ≤ 30 lines and contains pointer references to all three `instructions/*.md` files.
- [ ] `~/.config/opencode/opencode.jsonc` declares `"instructions": ["AGENTS.md", "instructions/caveman.md", "instructions/context-mode.md", "instructions/context-hygiene.md"]`.
- [ ] `"instructions"` array entries are written in that exact order (AGENTS.md first).
- [ ] `"$schema"` field preserved unchanged.
- [ ] `opencode` boots without `ConfigInvalidError` after restart.
- [ ] Fresh session confirms caveman switch levels (`lite|full|ultra|wenyan`) are in context — proves `instructions/caveman.md` loaded.
- [ ] Fresh session confirms context-mode BLOCKED rules (`curl`/`wget` blocked, inline HTTP blocked) are in context — proves `instructions/context-mode.md` loaded.
- [ ] Fresh session confirms the context-hygiene "You MUST update context docs" list is in context — proves `instructions/context-hygiene.md` loaded.
- [ ] Old AGENTS.md rule content (caveman, context-mode, context-hygiene) is NOT duplicated anywhere else in the tree.
- [ ] Backup at `/tmp/opencode-backup-pre-000` retained until PRD `000` is fully Done.

## Blocked by

None — can start immediately. Owns `opencode.jsonc`, `AGENTS.md`, and new `instructions/` files; no other issue touches these.
