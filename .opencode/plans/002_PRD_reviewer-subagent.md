# PRD: Reviewer subagent (issue DOING→DONE gate)

**Status:** Draft
**Created:** 2026-06-29
**Grilling:** incomplete — see `## Open questions` before flipping to Aligned

## Problem

Anthropic's "Effective context engineering" & "Building effective agents" emphasize an
**evaluator-optimizer workflow**: a second LLM pass that criticizes output against clear
criteria, halting on invariant violation. Today the config encodes an inline "be-critical"
posture ([instructions/user-preferences.md](../../instructions/user-preferences.md)) and
a context-hygiene done-gate (archived [001_PRD_context-done-gate.md](archive/001_PRD_context-done-gate.md)),
but there is **no isolated second-pass reviewer**:

- Be-critical runs in the *same* context as the implementer → self-review bias.
- Done-gate invariants are checked by the implementer itself → no enforcement.
- No structured artifact recording *what was reviewed* lives next to the issue.

The gap surfaced when comparing the config against the two Anthropic docs (see session
memory, decisions captured 2026-06-29). The config covers
sub-agent isolation (via automode fan-out), right-altitude prompts (thin agents), and
stop conditions (concurrency cap 5) — but the evaluator-optimizer pattern is the one
principle largely absent.

## Solution shape

A hidden subagent `reviewer` (parallels `multimodal`) invoked by `build` and `automode`
**as the last step before flipping an issue `DOING → DONE`**. It runs in its own clean
context, applies a bundled rubric, and returns a structured verdict. The caller appends
the verdict verbatim to the issue file as a `## Review` section.

### Contracts

- **Trigger**: every issue DOING→DONE transition, both `build` and `automode`.
  PRD lifecycle keeps its own human gate (Draft→Aligned→Done) — reviewer does NOT
  gate PRD transitions.
- **Binding model**: hybrid. Taste-level critique is **advisory**; invariant-check
  failures are **halting** (BLOCK).
- **Loops**: 1 iteration. First BLOCK halts and hands back to user (no auto-rework
  loop). Matches "in doubt, ask one focused question" + flag-once-then-execute.
- **Record**: caller appends a `## Review` section to the issue file containing the
  reviewer's returned block verbatim. Lives with the issue, archived together.
- **Rubric home**: `agents/reviewer.md` carries the rubric inline. **No new
  skill / `skills/reviewer/SKILL.md`** — the agent file is the single source of truth
  for the rubric (diverges from the agents-reference-skills pattern; called out below).

### Reviewer output format

Returned to caller, pasted verbatim into `## Review`:

```
## Review

**Reviewer:** reviewer subagent
**Date:** <iso>
**Verdict:** PROCEED | BLOCK

### Invariant checks
- [pass|fail] done-gate 001 — .opencode/context refreshed for any architecture/API/
            data-model/domain-term/module-responsibility shift in the same change.
            Evidence: <git diff summary | "no shift detected">
- [pass|fail] Issue acceptance criteria met. Evidence: <list each criterion, status>.
- [pass|fail] Tests green (tdd). Evidence: <test runner tail or "no product tests apply">.
- [pass|fail] Plans hygiene — issue file path valid, `Status:` header present, no
            writes outside .opencode/plans/** by planner (build/automode may edit
            source — that is allowed).

### Taste notes (advisory)
- <bullet> ...
- <bullet> ...
```

### Halting vs advisory rule

| Check                             | Halts? |
|-----------------------------------|--------|
| Any invariant above = `fail`     | yes — BLOCK |
| Taste notes                       | no — PROCEED, logged |

### Agent file shape (`agents/reviewer.md`)

To be authored in implementation. Must be **thin** (mirrors `multimodal.md` style —
role one-liner + delegation protocol), with the rubric specified inline as the
structured format above. The 4 invariant checks and their evidence requirements live
in the agent file, not a skill — see `## Open questions` Q3.

## Risks & dependencies

- **Diverges from "agents reference skills" convention.** Every other agent file is a
  thin orchestrator pointing at a `skills/*/SKILL.md`. Putting the rubric in
  `agents/reviewer.md` breaks the pattern. Trade-off chosen by user (simpler, one
  file). Re-evaluate if rubric grows.
- **Reviewer must read the same facts as implementer without inheriting dirty context.**
  Pattern: caller passes issue file path + diff + changed-file list as Task-prompt
  inputs; reviewer re-derives truth from disk. Risk: reviewer re-reads large diffs
  inline → context pollution. Mitigation: caller passes *paths*; reviewer reads only
  the specific files/line ranges the rubric names and surfaces only the verdict.
- **1-iteration BLOCK may stall on minor issues.** Accepted — pair with "ask one
  focused question" rule. If friction grows, revisit to 2-iteration cap.
- **Tautological self-check risk:** "no writes outside .opencode/plans/**" only makes
  sense for `planner`; build/automode *should* edit source. Check phrased narrowly
  (only meaningful when reviewer is invoked from a planner-owned transition — not
  the case here, since reviewer only gates issues owned by build/automode). Needs
  rewording — see Q4.
- **Opencode subagent contract unknown.** Whether hidden subagents can be named
  arbitrarily in `subagent_type`, whether they get the tool allow-list — **not
  verified**. See Q1.

## Out of scope

- PRD-lifecycle review (Draft→Aligned) — explicitly excluded.
- Parallelization-voting workflow (run same task N times, pick best).
- Routing workflow.
- Config self-evals harness (the other gap from the comparison) — separate future
  work; this PRD does not depend on it.
- Any prompt-chaining/compaction discipline additions (other gaps from comparison).

## Open questions (resolve before Aligned)

These are what the grilling session did NOT resolve. Each blocks `Status: Aligned`.

### Q1 — Opencode subagent mechanics (research needed)

Unverified assumptions about opencode's hidden-subagent system. Planner is read-only
outside `.opencode/plans/**` and cannot introspect the opencode runtime. Need
answers from user / opencode docs:

- (a) Can a hidden subagent be registered by writing `agents/reviewer.md`
  + adding it to `opencode.jsonc` `agent` block? Or is the registry elsewhere?
- (b) Does `subagent_type: "reviewer"` work in the Task tool, or must it match a
  fixed opencode-builtin enum?
- (c) Permission matrix: does the reviewer need its own `permission` block in
  `opencode.jsonc` (read-only? allow Task? allow grep/glob/read)?
- (d) Does the reviewer get caveman / user-preferences instructions
  auto-loaded, or only `agents/reviewer.md`?

**Recommendation**: delegate to `explore` subagent or read opencode docs off-session.

### Q2 — Evidence-gathering protocol

Reviewer needs ground truth. Open: does it

- (a) Re-run `git diff` / `git status` / test runner itself, or
- (b) Trust evidence the caller passes in the Task prompt?

(a) = independent, more expensive, may hit bash permission rules.
(b) = cheap but trusts the implementer — defeats isolation partially.

**Recommendation**: (a) for invariant 4 (plans hygiene); (b) for the
done-gate shift-detection since it requires judgement the implementer already made.
Resolve with user.

### Q3 — Rubric location confirmation

User said "no skill, only clear description in the reviewer.md file". This breaks the
agents-reference-skills convention (all other agents thin-orchestrate skills). Confirm:

- Is this acceptable long-term, or should we expect to extract
  `skills/reviewer/SKILL.md` once rubric stabilizes?
- If kept inline, the agent file will grow beyond "thin" — does that update
  [CONTEXT.md](../../.opencode/context/CONTEXT.md) glossary entry for "Agent"?

### Q4 — Invariant 4 wording

"no writes outside .opencode/plans/**" is a planner-only constraint. For
build/automode issues, the invariant is meaningless (they SHOULD edit source).
Rephrase to something like:

> Plans hygiene — issue file exists at .opencode/plans/issues/NNN_Issue_*.md,
> `Status:` header present and well-formed, archive discipline followed
> (no archived issue moved to DONE).

Confirm phrasing with user.

### Q5 — Interaction with done-gate 001

Done-gate 001 (archived) says an issue may not flip to DONE until
`.opencode/context/` is refreshed for arch/API/data-model shifts. The reviewer
now also enforces this. Two questions:

- (a) Does the reviewer *replace* the implementer's self-check, or *augment* it?
- (b) If the implementer already checked + refreshed, is reviewer's check a
  no-op (pass with evidence) or independent re-derivation?

**Recommendation**: augment. Implementer self-checks first; reviewer re-derives
independently for high-risk shifts only (to avoid double work). Confirm.

### Q6 — Sequencing vs existing skills

`to-issues` skill writes `## Close-out` template including "flip Status → DONE +
archive". Does reviewer invocation slot BEFORE or AFTER the `## Close-out` step?
i.e., does Close-out become:

```
1. invoke reviewer (Task tool, subagent_type: reviewer)
2. append returned `## Review` block
3. flip Status → DONE
4. archive issue file
```

Confirm with user — affects `to-issues` SKILL.md edit (build agent's job, flagged
here for context-update awareness).

## Further Notes

- **Context update needed**: [.opencode/context/CONTEXT.md](../../.opencode/context/CONTEXT.md)
  — add `reviewer` to Actors list and Domain glossary ("Agent" entry gains a new
  instance; or new term: "Reviewer subagent — hidden subagent gating issue
  DOING→DONE with a bundled rubric, 1-iteration, hybrid halting"). Module map
  gains `agents/reviewer.md`.
- **Context update needed**:
  [.opencode/context/topics/agents-and-skills.md](../../.opencode/context/topics/agents-and-skills.md)
  — `reviewer` is the first agent whose rubric lives in the agent file, not a
  skill. Document the divergence.
- **Context update needed**:
  [.opencode/context/topics/plan-lifecycle.md](../../.opencode/context/topics/plan-lifecycle.md)
  — issue lifecycle gains a pre-DONE review step; update the diagram/prose.
- **Convention divergence flagged**: rubric inline in agent file (Q3). If kept,
  AGENTS.md "agents are thin orchestrators that reference skills rather than
  paraphrase them" needs a carve-out note, or `reviewer` becomes the documented
  exception.
- **Origin**: gap analysis comparing this config against Anthropic's
  "Effective context engineering for AI agents" (Sep 2025) and
  "Building effective agents" (Dec 2024). See session memory `decision` source.

## References

- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Archived PRD 001 — context DONE-gate](archive/001_PRD_context-done-gate.md)
- [instructions/user-preferences.md — be-critical posture](../../instructions/user-preferences.md)
- [agents/multimodal.md — precedent for hidden subagent](../../agents/multimodal.md)
