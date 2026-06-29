# PRD: Config reconciliation (AGENTS.md + agents split)

- **ID**: 000
- **Status**: Done
- **File**: `000_PRD_config-reconciliation.md`

## Problem Statement

The `~/.config/opencode/` config tree — git-synced across machines and intended as a reusable reference — has grown inconsistent. Three orthogonal concerns (caveman tone, context-mode routing, context-hygiene) are stitched into one `AGENTS.md` via HTML-comment fences with no clean separation. Awareness sections about planning artifacts and context hygiene are paraphrased separately inside `planner.md`, `build.md`, and `automode.md`, and these copies have already drifted (planner says "MUST NOT edit context"; build/automode say "follow the global rule"). The PRD `Status` enum disagrees between planner Phase 2 (`Draft | Aligned`) and automode's awareness section (`Draft | Aligned | In Progress | Done | Cancelled`). The planner's `bash` allow-list (`mkdir`, `ls` only) is too narrow for its own documented workflow (Phase 0 wants `.gitkeep`, grilling references `git log`/`git diff`/`stat`). The planner description claims "read-only for code" while `external_directory: allow` is wide open. Phase 1b forbids the `question` tool but keeps the permission enabled (intentional — it is used for agent-mode switching tests). All these drifts make the config fragile and untrustworthy as a shared reference.

## Solution

Reconcile the config tree into a strict single-source-of-truth layout, with rules always-on via the `instructions:` array, agents as thin orchestrators that load skills rather than paraphrase them, and a unified PRD lifecycle.

High-level shape:

1. **Split AGENTS.md.** Move the three rule blocks out of `AGENTS.md` into `~/.config/opencode/instructions/{caveman,context-mode,context-hygiene}.md`. `AGENTS.md` becomes a ~20-line index. `opencode.jsonc` declares all four files in `instructions: [...]`. Skill bodies stay on-demand (loaded only when triggered); rules stay always-on.
2. **Make planner a thin orchestrator.** `planner.md` keeps phase list + which skill fires at each phase (`grilling` → `to-prd` → `to-issues` / `tdd`) + permission/role/hygiene reminders. No paraphrasing of skill content.
3. **Strip duplicated awareness.** Remove the "Planning artifacts (awareness, not enforcement)" and "Project context hygiene (awareness)" sections from `build.md` and `automode.md`. Replace with a one-line pointer to `AGENTS.md` and `.opencode/plans/` conventions.
4. **Unify PRD lifecycle.** Status enum: `Draft → Aligned → Done → Cancelled`. Drop `In Progress` everywhere. When the last issue of a PRD moves to `DONE`+archive, the implementing agent flips the PRD `Aligned → Done` and archives the PRD.
5. **Expand planner bash allow-list** to read-only ops: `ls`, `mkdir`, `cat`, `stat`, `git status`, `git log`, `git diff`, `wc`, `head`, `tail`. Patterns ordered broad-first / narrow-last per opencode permission rules. Keep all write/branch ops denied.
6. **Rephrase planner description.** Drop "read-only for code"; accurate form: "writes only planning artifacts under `.opencode/plans/**`". Keep `external_directory: allow`.
7. **Phase 1b behavior.** Keep the "NOT via the `question` tool" sentence. Add: if the user signals "GO" / "proceed" / any clear direct-implementation cue, planner assumes it has been switched to automode (no longer planner) and yields accordingly. (Prompt-level signal — see Further Notes.)
8. **Multimodal subagent unchanged.** Model-level capability enforcement (Kimi vision vs glm-5.2 text) makes the delegation load-bearing.
9. **Build agent parked.** Leave as-is for a future "Chat" reshape. Do not reconcile the build↔automode overlap in this PRD.
10. **Skills own workflow detail.** `grilling`, `to-prd`, `to-issues`, `tdd`, `caveman` skill bodies are the SoT; agent files reference, don't duplicate.

## User Stories

1. As the config owner, I want the three always-on concerns (tone, context-mode routing, context-hygiene) to live in their own files under a dedicated `instructions/` directory, so that each can be edited and version-controlled independently.
2. As the config owner, I want `AGENTS.md` to be a short index pointing at the rule files, so that the global session context stays small and readable.
3. As the config owner, I want `opencode.jsonc` to list every always-on file in `instructions: [...]`, so that the load set is explicit and auditable.
4. As the config owner, I want planner.md to reference skills (`grilling`, `to-prd`, `to-issues`, `tdd`) at each phase rather than paraphrase them, so that there is a single source of truth for the workflow detail.
5. As the config owner, I want planner.md to retain its phase list and permission/role info, so the planner agent is still self-describing.
6. As the config owner, I want the "Planning artifacts (awareness)" and "Project context hygiene (awareness)" sections removed from `build.md` and `automode.md`, so they cannot drift from the canonical rule.
7. As the config owner, I want a single one-line pointer in `build.md` and `automode.md` to `AGENTS.md` and `.opencode/plans/` conventions, so agent files stay short and authoritative.
8. As the config owner, I want the PRD `Status` enum to be exactly `Draft | Aligned | Done | Cancelled` everywhere it appears, so there is no ambiguity about lifecycle states.
9. As the config owner, I want a documented transition rule (`Aligned → Done` when all issues archived), so the PRD's lifecycle end is unambiguous.
10. As the config owner, I want the planner `bash` allow-list expanded to read-only ops (`cat`, `stat`, `git status`, `git log`, `git diff`, `wc`, `head`, `tail`, plus existing `mkdir`/`ls`), so the documented Phase 0 and grilling operations actually succeed.
11. As the config owner, I want planner's write/branch bash ops to remain denied, so planner stays unable to mutate source or git state.
12. As the config owner, I want planner's description to accurately say "writes only planning artifacts under `.opencode/plans/**`" instead of "read-only for code", so the description matches what permissions enforce (read-wide + write-narrow).
13. As the config owner, I want Phase 1b to retain the "NOT via the question tool" sentence, so I can keep using the question tool's options as agent-mode switching cues.
14. As the config owner, I want Phase 1b to instruct the planner that on a clear direct-implementation cue ("GO", "proceed", "just do it") it should treat itself as having been switched to automode and yield, so small tasks can skip the PRD without ceremony.
15. As the config owner, I want the multimodal subagent left untouched, so the existing model-level vision/text enforcement is preserved.
16. As the config owner, I want the build agent left as-is, so future "Chat" reshaping is not blocked by premature reconciliation.
17. As a fresh machine, I want the config to pull cleanly via `git pull` and boot without `ConfigInvalidError`, so the reconciliation preserves a valid opencode config.
18. As a downstream reader (future me or another user), I want a single canonical place for each rule, so I never have to ask "which copy is authoritative".

## Implementation Decisions

- **File layout.** New directory `~/.config/opencode/instructions/` holding `caveman.md`, `context-mode.md`, `context-hygiene.md`. Content extracted verbatim from current `AGENTS.md` HTML-comment blocks; the `<!-- ...-begin -->` / `<!-- ...-end -->` fence lines are removed (clean markdown headers instead).
- **AGENTS.md slim.** Becomes ~20 lines: one-paragraph index + `@`-style pointer lines to the three rule files + a pointer to `.opencode/plans/` and `.opencode/context/` trees. (Note: `@`-ref in `AGENTS.md` does not auto-load; the `instructions:` array does the loading. AGENTS.md's pointers are human-read cross-references, not include directives.)
- **opencode.jsonc.** Add `"instructions": ["AGENTS.md", "instructions/caveman.md", "instructions/context-mode.md", "instructions/context-hygiene.md"]`. Preserve existing `$schema` line. Order is intentional: AGENTS.md first as the index the reader hits first.
- **planner.md rewrite.** Frontmatter (description, mode, model, variant, permission) preserved except: description rephrased to "Planning agent. Drives feature understanding, alignment, PRD creation, and task decomposition before any production code. Writes only planning artifacts under `.opencode/plans/**`." Permission `bash` block rewritten as an ordered object: broad `*: deny` first, then narrow read-only allows last (per opencode permission rule "last matching rule wins").
- **planner.md body.** Phases 0–3 kept as headers, but each phase body is reduced to: (a) which skill to load, (b) the gate condition to exit the phase, (c) any planner-specific permission/hygiene reminder the skill does not own. Phase 1b keeps its two-option (a)/(b) list verbatim, keeps the "NOT via the `question` tool" sentence, and adds the GO/proceed direct-implementation cue behavior.
- **build.md & automode.md.** The two `## Planning artifacts (awareness, not enforcement)` and `## Project context hygiene (awareness)` sections replaced with a single line: `See AGENTS.md (Project context hygiene) and .opencode/plans/ conventions.`. Everything else in those agent files unchanged.
- **PRD Status enum.** Normalized to `Draft | Aligned | Done | Cancelled` in: planner.md Phase 2 (already `Draft|Aligned`, add `Done|Cancelled`), automode.md awareness section (drop `In Progress`), the Hygiene section of planner.md (clarify that `Done` PRDs are archived after all their issues are archived).
- **Transition rule.** When an implementing agent moves the last non-archived issue of a PRD to `DONE` and archives it, that agent then flips the PRD `Status: Aligned` → `Status: Done` and moves the PRD file to `.opencode/plans/archive/`.
- **Skill SoT.** No skill file edits required. The `grilling`, `to-prd`, `to-issues`, `tdd`, `caveman` skills already own their content; planner.md simply stops paraphrasing them.
- **Permission ordering convention.** Document in the planner.md Hygiene or a one-line comment that `bash:` / `edit:` objects use last-match-wins ordering; read-only allows come last.
- **No code change.** No source code touched. Only `~/.config/opencode/{AGENTS.md,opencode.jsonc,agents/*.md}` and a new `instructions/` directory.

## Testing Decisions

This is meta-config (markdown + JSONC), not application code. There is no unit-test seam.

**Seam — opencode config validator + manual smoke.** opencode hard-fails on invalid config at startup (`ConfigInvalidError`). Acceptance is: after the reconciliation, `opencode` restarts cleanly and the documented invariants hold.

Good-test criteria (external behavior, not implementation):

- opencode boots without `ConfigInvalidError`.
- All four `instructions:` files load on session start.
- planner agent (TUI switch) can reach Phase 0 (create `.opencode/plans/` tree) without a `bash` permission block.
- planner can run `git status`/`git log` for grilling (read-only allow-list).
- planner still cannot `edit` outside `.opencode/plans/**`.
- automode can still `edit` code and run `bash` freely.
- multimodal subagent still callable via Task tool from primaries; returns vision findings.
- The duplicated awareness sections are absent from `build.md` and `automode.md` (`grep` for `Planning artifacts (awareness` returns 0 matches in agents/).
- PRD lifecycle test: a throwaway `000_PRD` with `Status: Aligned` + one issue `Status: DONE`+archived → PRD ends up `Status: Done` in `.opencode/plans/archive/`.

Prior art: none — this is the first config-reconciliation pass. Future regen of context docs via `/refresh-context-md` is out of scope here but should still run cleanly after the change.

## Out of Scope

- Reshaping `build.md` into a generic "Chat" agent — parked for later.
- Defining a cross-agent `task_id` / handoff-state propagation convention between planner and automode — deferred.
- Merging `automode` into `build` or vice versa — not happening; both stay, build parked.
- Editing any skill body (`grilling`, `to-prd`, `to-issues`, `tdd`, `caveman`, `caveman-commit`, etc.) — they are already the SoT.
- Rewriting the context-mode routing rules themselves — only their file location changes, not their content.
- Adding a tree-shape invariant script (Seam B) — rejected; manual smoke + `git diff` review suffices for a personal config.
- Touching the `multimodal` agent — unchanged.
- Any production application code outside `~/.config/opencode/`.

## Further Notes

- **Open caveat on Phase 1b GO-cue behavior.** Planner's permission block denies `edit` outside `.opencode/plans/**`. So when the planner "assumes it was switched to automode", it can at most produce a short handoff note and stop; actual code edits still require the user to switch agent in the TUI. The planner prompt instructs it to interpret a GO/proceed cue as "yield to automode", not "start coding while pretending to be planner". If the user wants the agent to actually start coding, they switch via the TUI.
- **Reasoning for keeping `question: allow` on planner.** Owner uses the `question` tool's option labels as mode-switching cues (e.g. option text contains "assume automode"). The actual answer is sometimes ignored; the prompt tree is the test surface. This is why Phase 1b deliberately keeps "NOT via the question tool" — it forbids the *behavior*, not the permission.
- **Context update needed.** Not applicable in the strict sense — `~/.config/opencode/` is the opencode config itself, not a project with a `.opencode/context/` tree. However, if the user later adopts this same reconciliation pattern in a real project repo, the project's `.opencode/context/CONTEXT.md` Architecture section should mention the `instructions/` directory layout.
- **Sequence numbering.** This is `000_PRD_config-reconciliation.md` — the first PRD in this tree. Subsequent PRDs continue at `001`, `002`, … Issues will start at `000_Issue_*` and reference this PRD by filename.
- **Restart reminder.** After the agent files, `instructions/` directory, and `opencode.jsonc` are written, the user must quit and restart opencode for the config changes to take effect (config is loaded once at startup, not hot-reloaded).
