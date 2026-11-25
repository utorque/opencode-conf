---
name: make-docs
description: >-
  Generates or refreshes a verified docs/ suite for a codebase, adapting the doc set to the
  project type, writing Mermaid docs, grading them against source, and wiring results into
  AGENTS.md (plus .opencode/context/ when present). Optional --dist builds one offline HTML page.
  Use when asked to document a codebase, refresh docs/, bootstrap AGENTS.md docs links, or build
  a single-page docs site.
license: MIT
metadata:
  version: 3.2.0
---

# make-docs

You are the **orchestrator** for a documentation-generation pipeline. Coordinate the phases —
**Bootstrap → Explore → Generate → Verify → Context Update (→ optional Dist Build)** — in an
iterative loop until every **applicable** document meets grade **A** on every rubric dimension, or
the retry budget is exhausted. Documents that do not apply to the project are recorded as **N/A**
and are not generated or graded.

Detailed instructions for each phase live in `references/`. Read the relevant reference file when
you reach that phase (progressive disclosure — don't load them all up front).

| Phase | What it does | Read |
|-------|--------------|------|
| 0 — Bootstrap | Detect/back-up AGENTS.md, ensure `docs/`, inspect existing doc ownership | `references/context-files.md` |
| 1 — Explore | Scan the codebase across 8 domains, detect the project profile and doc applicability, reading `.opencode/context/` when present → `docs/_exploration_report.md` | `references/exploration.md` |
| 2 — Generate | Write only applicable docs in `docs/` with Mermaid diagrams | `references/generation.md` |
| 3 — Verify | Run deterministic checks, then grade every generated doc A–F against the source → `docs/_verification_report.md` | `references/verification.md` + `references/grading-rubric.md` |
| 4 — Context Update | Update AGENTS.md + refresh `.opencode/context/` if present (progressive disclosure) | `references/context-files.md` |
| 5 — Dist Build *(optional)* | Package the generated docs into one self-contained `docs/dist/index.html` | `references/dist-build.md` |

## Configuration

- **Profile**: `--profile auto|small|full` (default `auto`).
  - `auto` — core docs plus every doc whose applicability condition is met.
  - `small` — core docs only: README, architecture, environment-setup, glossary, coding-conventions
    (+ api-reference when an API/CLI/public API surface exists).
  - `full` — every applicable doc, including optional docs (error catalog, testing, tech stack).
  - N/A areas are always skipped, in every profile. Never write a stub doc to satisfy a filename.
- **Scope overrides**: `--only a,b` / `--skip c,d` using doc stems (e.g. `architecture,api-reference`).
- **Incremental**: `--incremental` verifies existing generated docs first and regenerates only
  missing or failing docs. Without it, applicable generated docs are refreshed normally.
- **Safety**: `--force` allows overwriting an existing `docs/<name>.md` that lacks the
  `<!-- make-docs:generated -->` marker (the old file is backed up first). `--dry-run` prints the
  planned doc set, conflicts, and backups without writing anything.
- **Max retries**: the first numeric argument, if given (e.g. `make-docs 5`). If blank or
  non-numeric, default to **3**.
- **Dist build**: run Phase 5 **only if the user asked for it** (e.g. `make-docs --dist`, or the
  request mentions building a single-page HTML site / dist). Without the flag, stop after Phase 4.
- **Output directory**: `docs/` at the project root.
- **Passing grade**: **A** on every generated document and every rubric dimension; **N/A** docs are
  not graded and do not block PASS.
- **Completion**: all applicable docs are A or N/A, or max retries is reached.
- **Generated marker**: every generated doc starts with `<!-- make-docs:generated -->`. The dist
  builder publishes only marked docs by default.

## How to run the phases (any harness)

This skill is harness-agnostic. Each phase is a batch of independent work that parallelizes cleanly:

- **If your harness supports subagents / parallel tasks** (e.g. a Task tool, an agent-spawn
  primitive, or a workflow engine): dispatch the phase's work as parallel subagents — 8 explorers in
  Phase 1, one writer per generated doc in Phase 2, 1 verifier in Phase 3 (or one per doc when the
  repo is large). Give each subagent the matching `references/` file as its instructions, plus its
  specific brief/doc. Prefer read-only tools for explorers and verifiers.
- **If your harness has no subagents**: perform each phase's work yourself, sequentially, following
  the same `references/` files. The output is identical; only the wall-clock time differs.

Whichever mode you use, the phase boundaries, working files, applicability decisions, and grading
are the same.

## Iteration loop

```
Phase 0: Bootstrap (run once; honour --dry-run)
build_dist = user asked for the single-page HTML dist
incremental = --incremental
profile = auto | small | full
docs = applicable docs from Phase 1 (minus --skip, plus --only)

iteration = 0
max_retries = first numeric argument or 3

WHILE iteration < max_retries:
    iteration += 1

    IF iteration == 1:
        Run Phase 1 (Explore + Project Profile)
        IF --dry-run: print planned docs/conflicts and STOP
        IF incremental AND existing generated docs exist:
            Verify existing generated docs first
            Generate only missing or failing docs
        ELSE:
            Generate ALL applicable docs
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
Documentation Generation Report
Iteration:  {n} / {max_retries}
Profile:    {auto|small|full}
Verdict:    {PASS | FAIL}
AGENTS.md:         {Created | Updated | Unchanged}
.opencode/context: {Updated | Not present}
Dist:              {docs/dist/index.html built | Skipped}
Generated: {X}   N/A: {Y}   Skipped by user: {Z}

Document                     CMP ACC CLR DIA COV  Overall
{one row per generated doc}
{one row per N/A doc: "N/A (reason)"}
```

On FAIL, also list the specific failing dimensions and the verifier's feedback for each doc.

## Critical rules

1. **Applicability before generation.** Detect the project profile first; generate only docs whose
   area exists. Record N/A docs and reasons in the reports. Never fabricate a database, frontend,
   service boundary, queue, or API to satisfy the fixed doc list. If an existing **generated** doc's
   area no longer exists, move that marked file to `docs/_backup/<name>.<UTC timestamp>.md` and
   record it as N/A — never leave a stale generated doc in the published set.
2. **Never invent information.** Document only what actually exists in the codebase.
3. **Always include Mermaid diagrams** where the doc table marks them "Required" **and the doc is
   applicable**. If the area does not exist, the doc is N/A instead of diagram-less.
4. **Mark every generated doc** with `<!-- make-docs:generated -->` before the title.
5. **Never overwrite an unmarked doc** unless `--force` is set; back it up to
   `docs/_backup/<name>.<UTC timestamp>.md` first. `--dry-run` must not write.
6. **Verify against code, not just the exploration report.** The verifier reads actual source files
   and runs the deterministic checks in `references/verification.md`.
7. **On retries, only regenerate failing docs** — never the whole set.
8. **Preserve passing docs** across iterations — do not overwrite docs that already scored A.
9. **The exploration and verification reports are working files** (`docs/_*.md`) — don't delete them;
   they are also excluded from the dist build. `docs/_backup/` is likewise internal.
10. **Be honest about gaps.** Flag uncertainties with `⚠️` rather than guessing.
11. **AGENTS.md stays under ~120 lines.** Use progressive disclosure — point to generated docs,
    don't duplicate their content. Only link docs that were actually generated.
12. **Never delete human-written AGENTS.md content.** Only manage the marked auto-generated section.
13. **AGENTS.md is tool-agnostic** — plain relative Markdown links, no `@`-import syntax.
14. **When `.opencode/context/` exists, treat it as a primary source.** Read `CONTEXT.md` and its
    `topics/` during exploration and generation; keep generated docs consistent with it. Phase 4
    refreshes the context tree for architecture/API/data-model shifts the docs surfaced.
15. **Structure for AI agents.** Explicit headings, tables, and "Read when" triggers so opencode,
    SpecKit, Cursor, Copilot, and other tools can extract context efficiently.
16. **No secrets in docs.** Never commit real credentials, tokens, or user data. The dist builder's
    secret scan must pass; use `make-docs:allow-secret` only for clearly synthetic examples.
17. **Markdown is the source of truth; generated HTML is never hand-edited.** After any `docs/*.md`
    change, rebuild the dist if one exists (see `references/dist-build.md`).
18. **Do not commit unless the user asked.** Leave the doc set, AGENTS.md, and dist changes for
    review.
