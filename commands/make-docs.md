---
description: Generate or refresh a verified docs/ suite for this codebase, adapting the doc set to the project type (auto/small/full), then wire it into AGENTS.md and .opencode/context/ when present. Add --dist for the single-page offline HTML at docs/dist/index.html.
---

Run the `make-docs` skill (single source of truth at `skills/make-docs/SKILL.md` — read it first,
then the `references/` file for each phase as you reach it). Do not paraphrase or re-invent the
workflow.

Pass through the command arguments:

- First numeric argument = max verification retries (default 3), e.g. `/make-docs 5`.
- `--profile auto|small|full` — how much of the doc set to generate (default `auto`; see
  `skills/make-docs/references/exploration.md` for the applicability matrix).
- `--only a,b` / `--skip c,d` — scope individual doc stems.
- `--incremental` — verify existing generated docs first and regenerate only missing/failing docs.
- `--force` — overwrite a `docs/<name>.md` that lacks `<!-- make-docs:generated -->` (backup first).
- `--dry-run` — print planned docs/conflicts/backups; write nothing.
- `--dist` (or an explicit "build the dist / single-page HTML" request) = also run Phase 5
  (Dist Build) after verification finishes, per `skills/make-docs/references/dist-build.md`.
  Without it, stop after Phase 4 (Context Update).

Work in the current project root. When the harness supports subagents, parallelize the phases as
the skill describes (read-only explorers in Phase 1, per-doc writers in Phase 2, verifier in
Phase 3); otherwise run them sequentially. Detect applicability before generating: skip N/A docs,
record the reasons, and never fabricate an area to fill a filename. Finish by printing the skill's
Documentation Generation Report, and never commit unless the user asked.
