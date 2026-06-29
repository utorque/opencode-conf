# Issue: Rewrite planner.md as thin orchestrator

<!-- Kanban status — update as work progresses: TODO | DOING | DONE | BLOCKED <one-line reason> | CANCELLED -->
**Status:** DONE

- **ID**: 001
- **Parent PRD**: `000_PRD_config-reconciliation.md`
- **File**: `001_Issue_planner-thin-orchestrator.md`

## What to build

End-to-end: rewrites `~/.config/opencode/agents/planner.md` so the agent body stops paraphrasing the `grilling`, `to-prd`, `to-issues`, and `tdd` skills and instead references them at each phase. Unifies the PRD `Status` enum. Expands the bash allow-list to read-only ops. Rephrases the description. Adds the Phase 1b GO-cue yield behavior.

Single file touched: `~/.config/opencode/agents/planner.md`.

Specific changes:

- **Frontmatter `description`** — replace "Read-only for code; writes only planning artifacts under .opencode/plans/." with "Writes only planning artifacts under .opencode/plans/**." Drop the "Read-only for code" claim (false: `external_directory: allow` and `read: allow` permit wide reads).
- **Frontmatter `permission.bash`** — rewrite as an ordered object. Broad rule first (`"*": "deny"`), narrow read-only allows last (opencode permission rule: last matching rule wins). Allow list, in this order: `"*": "deny"`, then `"git status": "allow"`, `"git log *": "allow"`, `"git diff *": "allow"`, `"cat *": "allow"`, `"stat *": "allow"`, `"wc *": "allow"`, `"head *": "allow"`, `"tail *": "allow"`, `"mkdir *": "allow"`, `"ls *": "allow"`. All write/branch ops stay denied via the leading `*: deny`.
- **Phase 0 body** — kept; ensure it still mentions `mkdir` (allowed). `.gitkeep` line stays.
- **Phase 1 body** — reduce to: "Follow the `grilling` skill. Exit gate: user confirms alignment." Plus the existing "explore code" + "delegate to `explore` subagent" notes kept since they're planner-local.
- **Phase 1b body** — KEEP the two-option (a)/(b) list verbatim. KEEP the sentence "Do not call `question`, do not assume (a)" (the `question` tool stays banned for Phase 1b's behavior — the permission stays `allow` for other uses, see Further Notes in the PRD). ADD a paragraph: "If the user signals direct implementation (e.g. 'GO', 'proceed', 'just do it', 'skip the artifacts'), treat the session as having switched to automode. Yield: produce a one-line handoff note pointing at the alignment summary, then stop. The user must switch agent in the TUI to start coding — planner's edit permissions still deny source code."
- **Phase 2 body** — reduce to: "Follow the `to-prd` skill. Exit gate: PRD file written with `Status: Draft`, then user signs off → `Status: Aligned`." Add a one-line reminder of the full PRD Status enum: `Draft → Aligned → Done → Cancelled` (no `In Progress`).
- **Phase 3 body** — reduce to: "Follow the `to-issues` and `tdd` skills. Each new-feature issue's first concrete step is a failing test. Write issues in dependency order. Issue `Status: TODO` at top of file."
- **Hygiene section** — keep the rule that planner is read-only outside `.opencode/plans/**`. Add the PRD lifecycle rule: "When the last non-archived issue of a PRD moves to DONE+archive, the implementing agent flips the PRD `Status: Aligned` → `Status: Done` and moves the PRD file to `.opencode/plans/archive/`. Cancelled supersedes any state."
- **Remove** any paraphrased PRD-template details, "vertical tracer-bullet slices" elaboration, or skill-content duplication currently in the body — those belong to the skills.

## First step (test-first)

Config-boot + behavior tracer bullet:

1. Back up `~/.config/opencode/agents/planner.md` to `/tmp/opencode-backup-pre-001/planner.md`.
2. Apply the rewrite.
3. Restart opencode, switch to planner agent in TUI.
4. First failing-behavior assertion: in planner mode, attempt `git status` from a planner turn → succeeds (allow-list expanded). On the OLD planner.md this would be denied → that's RED. After rewrite → GREEN.
5. Second assertion (after GREEN above): attempt `edit` on a file outside `.opencode/plans/**` → still denied (write/branch ops not in allow-list). Proves the allow-list expanded read-only, not opened writes.
6. Third assertion: prompt planner with "GO, just build it" → planner yields with a one-line handoff note, does not attempt to edit source. Proves Phase 1b GO-cue behavior landed.

Tests 1–3 are the vertical tracer bullet; run them in sequence. No tests written up front beyond these behaviors.

## Acceptance criteria

- [ ] `agents/planner.md` frontmatter `description` no longer contains the string "Read-only for code".
- [ ] `permission.bash` is an object with `"*": "deny"` as the FIRST entry, followed by read-only allows for `git status`, `git log *`, `git diff *`, `cat *`, `stat *`, `wc *`, `head *`, `tail *`, `mkdir *`, `ls *`.
- [ ] No write/branch bash patterns (`git push`, `git commit`, `rm`, `mv`, `npm install`, etc.) appear in the bash allow-list.
- [ ] `permission.edit` block unchanged: `"*": "deny"` first, `".opencode/plans/**": "allow"` last.
- [ ] Phase 0 still references `.opencode/plans/`, `.opencode/plans/archive/`, `.opencode/plans/issues/`, `.opencode/plans/issues/archive/`.
- [ ] Phase 1 body names the `grilling` skill and does not redefine what grilling is.
- [ ] Phase 1b body still contains the two-option (a)/(b) list.
- [ ] Phase 1b body still contains "Do not call `question`".
- [ ] Phase 1b body contains a GO-cue yield paragraph mentioning at least one of: "GO", "proceed", "just do it".
- [ ] Phase 1b GO-cue paragraph explicitly notes that planner cannot edit source — must yield.
- [ ] Phase 2 body names the `to-prd` skill. PRD Status enum documented as `Draft → Aligned → Done → Cancelled` (no `In Progress`).
- [ ] Phase 3 body names the `to-issues` and `tdd` skills. No PRD template details inlined.
- [ ] Hygiene section documents the PRD `Aligned → Done` transition rule.
- [ ] `opencode` boots without `ConfigInvalidError` after restart.
- [ ] In planner mode, `git status` runs (was previously denied by `bash: * deny`).
- [ ] In planner mode, `edit` outside `.opencode/plans/**` is still denied.
- [ ] In planner mode, prompting "GO, just build it" causes planner to yield (one-line handoff note, no edit attempt) rather than start coding.
- [ ] Backup at `/tmp/opencode-backup-pre-001/planner.md` retained until PRD `000` is fully Done.

## Blocked by

None — can start immediately. Owns `agents/planner.md` only; no other issue touches this file. Parallel-safe with `000_Issue_split-agents-md-instructions-tree.md` and `002_Issue_strip-duplicated-awareness.md`.
