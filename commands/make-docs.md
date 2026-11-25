---
description: Generate a complete, verified documentation suite for this codebase (explore → generate → verify loop) and wire it into CLAUDE.md/AGENTS.md. Add --dist to also build the single-page offline HTML at docs/dist/index.html.
---

Run the `make-docs` skill (single source of truth at `skills/make-docs/SKILL.md` — read it first,
then the `references/` file for each phase as you reach it). Do not paraphrase or re-invent the
workflow.

Pass through the command arguments:

- First numeric argument = max verification retries (default 3), e.g. `/make-docs 5`.
- `--dist` (or an explicit "build the dist / single-page HTML" request) = also run Phase 5
  (Dist Build) after verification finishes, per `skills/make-docs/references/dist-build.md`.
  Without it, stop after Phase 4 (Context Update).

Work in the current project root. When the harness supports subagents, parallelize the phases as
the skill describes (read-only explorers in Phase 1, per-doc writers in Phase 2, one verifier in
Phase 3); otherwise run them sequentially. Finish by printing the skill's Documentation Generation
Report, and never commit unless the user asked.
