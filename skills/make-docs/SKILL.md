---
name: make-docs
description: >-
  Generates a complete, verified documentation suite for a codebase and wires it into AI-agent
  context files, optionally packaging everything into one self-contained single-page HTML dist.
  Runs a multi-phase explore → generate → verify loop: scans the repo, writes ~15 docs in
  docs/ (architecture, API reference, database schema, services, glossary, error catalog, security,
  and more) with Mermaid diagrams, grades every doc A–F on 5 dimensions against the actual source
  code, and regenerates failing docs until all pass. Then updates CLAUDE.md (progressive-disclosure
  section) and creates AGENTS.md for cross-tool compatibility. With --dist, additionally builds
  docs/dist/index.html — one offline, committed HTML page from the Markdown docs. Use when the user
  asks to document a codebase, generate or refresh project documentation, create a docs/ suite,
  bootstrap/update CLAUDE.md or AGENTS.md context files, or build a single-page HTML docs site.
  Harness-agnostic — works with or without subagents.
license: MIT
metadata:
  version: 3.0.0
---

# make-docs

You are the **orchestrator** for a documentation-generation pipeline. Coordinate the phases —
**Bootstrap → Explore → Generate → Verify → Context Update (→ optional Dist Build)** — in an
iterative loop until every document meets grade **A** on every rubric dimension, or the retry
budget is exhausted.

Detailed instructions for each phase live in `references/`. Read the relevant reference file when
you reach that phase (progressive disclosure — don't load them all up front).

| Phase | What it does | Read |
|-------|--------------|------|
| 0 — Bootstrap | Detect/back-up/create CLAUDE.md; note AGENTS.md | `references/context-files.md` |
| 1 — Explore | Scan the codebase across 8 domains → `docs/_exploration_report.md` | `references/exploration.md` |
| 2 — Generate | Write ~15 docs in `docs/` with Mermaid diagrams | `references/generation.md` |
| 3 — Verify | Grade every doc A–F against the source → `docs/_verification_report.md` | `references/verification.md` + `references/grading-rubric.md` |
| 4 — Context Update | Update CLAUDE.md + write AGENTS.md (progressive disclosure) | `references/context-files.md` |
| 5 — Dist Build *(optional)* | Package the docs into one self-contained `docs/dist/index.html` | `references/dist-build.md` |

## Configuration

- **Max retries**: the first argument, if given (e.g. `make-docs 5`). If blank or non-numeric,
  default to **3**.
- **Dist build**: run Phase 5 **only if the user asked for it** (e.g. `make-docs --dist`, or the
  request mentions building a single-page HTML site / dist). Without the flag, stop after Phase 4.
- **Output directory**: `docs/` at the project root.
- **Passing grade**: **A** on every document and every rubric dimension.
- **Completion**: when ALL docs score A across ALL dimensions, or max retries is reached.

## How to run the phases (any harness)

This skill is harness-agnostic. Each phase is a batch of independent work that parallelizes cleanly:

- **If your harness supports subagents / parallel tasks** (e.g. a Task tool, an agent-spawn
  primitive, or a workflow engine): dispatch the phase's work as parallel subagents — 8 explorers in
  Phase 1, up to 15 writers in Phase 2, 1 verifier in Phase 3. Give each subagent the matching
  `references/` file as its instructions, plus its specific brief/doc. Prefer read-only tools for
  explorers and verifiers.
- **If your harness has no subagents**: perform each phase's work yourself, sequentially, following
  the same `references/` files. The output is identical; only the wall-clock time differs.

Whichever mode you use, the phase boundaries, working files, and grading are the same.

## Iteration loop

```
Phase 0: Bootstrap (run once)
build_dist = user asked for the single-page HTML dist

iteration = 0
max_retries = first argument or 3

WHILE iteration < max_retries:
    iteration += 1

    IF iteration == 1:
        Run Phase 1 (Explore)
        Run Phase 2 (Generate ALL docs)
    ELSE:
        Run Phase 2 ONLY for docs that scored below A,
        using the verifier's feedback (revision mode). Preserve passing docs.

    Run Phase 3 (Verify)

    IF verdict == PASS:
        Run Phase 4 (Context Update)
        IF build_dist: Run Phase 5 (Dist Build)
        BREAK → success
    IF iteration == max_retries:
        Run Phase 4 (Context Update, even on partial pass)
        IF build_dist: Run Phase 5 (Dist Build, even on partial pass)
        BREAK → partial success

Print the summary table.
```

Phase 5 always runs **after** Phase 4, on the last iteration only — the dist packages whatever the
final state of `docs/` is, so it must not race with regeneration.

## Final output

When the loop ends, print a summary to the console:

```
📚 Documentation Generation Report
Iteration:  {n} / {max_retries}
Verdict:    {PASS ✅ | FAIL ❌}
CLAUDE.md:  {Created ✨ | Updated 🔄 | Unchanged ─}
AGENTS.md:  {Created ✨ | Updated 🔄 | Unchanged ─}
Dist:       {docs/dist/index.html built ✨ | Skipped ─}

Document                     CMP ACC CLR DIA COV  Overall
README.md                    ...
architecture.md              ...
tech-stack.md                ...
api-reference.md             ...
database-schema.md           ...
frontend-backend.md          ...
services.md                  ...
workflows-and-triggers.md    ...
devops.md                    ...
glossary.md                  ...
error-catalog.md             ...
testing-strategy.md          ...
environment-setup.md         ...
coding-conventions.md        ...
security.md                  ...

Docs generated:  docs/ (15 files)
Context updated: CLAUDE.md, AGENTS.md
Dist built:      docs/dist/index.html (only when requested)
```

On FAIL, also list the specific failing dimensions and the verifier's feedback for each doc.

## Critical rules

1. **Never invent information.** Document only what actually exists in the codebase.
2. **Always include Mermaid diagrams** where the doc table marks them "Required".
3. **Verify against code, not just the exploration report.** The verifier reads actual source files.
4. **On retries, only regenerate failing docs** — never the whole set.
5. **Preserve passing docs** across iterations — do not overwrite docs that already scored A.
6. **The exploration and verification reports are working files** (`docs/_*.md`) — don't delete them;
   they are also excluded from the dist build.
7. **Be honest about gaps.** Flag uncertainties with `⚠️` rather than guessing.
8. **CLAUDE.md stays under ~200 lines total; the auto-generated section under 80.** Use progressive
   disclosure — point to docs, don't duplicate their content.
9. **Never delete human-written CLAUDE.md content.** Only manage the marked auto-generated section.
10. **AGENTS.md is tool-agnostic** — no Claude-specific syntax; keep it under 120 lines.
11. **Structure for AI agents.** Explicit headings, tables, and "Read when" triggers so SpecKit,
    Cursor, Copilot, and other tools can extract context efficiently.
12. **Markdown is the source of truth; generated HTML is never hand-edited.** After any `docs/*.md`
    change, rebuild the dist if one exists (see `references/dist-build.md`).
