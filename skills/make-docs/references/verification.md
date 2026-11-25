# Phase 3 — Verification

Grade every **generated** doc by cross-referencing its claims against the **actual codebase** — not
just the exploration report (which may itself have errors). N/A docs are listed but not graded. Use
the rubric in [`grading-rubric.md`](grading-rubric.md). This file is both the operating manual for
the verify phase and the prompt to hand to a verifier subagent.

## Run modes

- **With subagents**: dispatch **one read-only verifier subagent** per iteration, or one per doc
  when the repo is large. Give it this file and `grading-rubric.md`.
- **Without subagents**: perform the verification yourself.

Either way, produce **one report** at `docs/_verification_report.md` and a **PASS/FAIL** verdict.

## Step 0 — Deterministic checks (before grading)

Run these objective checks first; they are cheaper and less subjective than LLM grading:

1. **File existence**: every path mentioned in a generated doc exists, unless marked `⚠️` as
   planned/removed.
2. **Cross-references**: every relative `.md` link points to a generated doc that exists. Run the
   dist builder in check mode when available:
   ```bash
   /build-docs --check
   # or, from any project:
   uv run --with 'pypandoc-binary==1.17' python \
     "${OPENCODE_CONFIG:-$HOME/.config/opencode}/skills/make-docs/scripts/build_docs.py" --check
   ```
   Broken links fail the check.
3. **API/endpoint count**: endpoint/command/export table rows match the count found by grepping the
   route/handler/export definitions. Investigate every mismatch.
4. **Mermaid blocks**: every ` ```mermaid ` fence has one of the valid diagram headers (`graph`,
   `flowchart`, `erDiagram`, `sequenceDiagram`, `stateDiagram-v2`, `classDiagram`, `journey`,
   `gantt`, `pie`, `mindmap`, `timeline`). A malformed diagram is at most a C on Diagrams.
5. **Secret scan**: no real keys, tokens, private keys, or user data. The dist builder scans
   high-confidence patterns by default; use `make-docs:allow-secret` only on synthetic examples.
6. **Generated marker**: every generated doc starts with `<!-- make-docs:generated -->`.
7. **Applicability sanity**: N/A docs must not exist as stub files; generated docs must correspond to
   an applicable area from the exploration profile.

Report deterministic failures as concrete findings, then continue with rubric grading.

## Verification process

For **each generated document** in `docs/` (excluding files prefixed with `_` and unmarked docs):

### Step 1 — Read the document
Read it fully and understand what it claims to document.

### Step 2 — Cross-reference against the codebase
The critical step. Don't just check that the doc "looks good" — verify claims against source:

- **API endpoints / CLI commands / public exports** → grep definitions; confirm they exist and
  methods/signatures match.
- **Database models** → find the model/schema files; confirm fields and relationships.
- **Services** → verify they exist and dependencies are correct.
- **Tech-stack claims** → check package manifests for versions and dependencies.
- **Architecture claims** → verify the described structure matches the actual layout.
- **Workflow/trigger claims** → find the actual job definitions, cron configs, event handlers.
- **Glossary terms** → verify terms are actually used; definitions make sense in context.
- **Error-catalog entries** → find the actual error classes/codes; verify status codes and throw sites.
- **Test-strategy claims** → verify the framework, commands, and directory structure.
- **Security claims** → verify auth middleware, CORS config, rate limiting.
- **Convention claims** → verify described patterns match the observed code style.
- **Environment setup** → verify prerequisite versions and env vars against configs/.env.example.
- **`.opencode/context/` consistency** → if the tree exists, check that architecture, design
  decisions, module map, and glossary agree with `CONTEXT.md` and `topics/*.md`. Flag drift in the
  feedback; Phase 4b refreshes the tree.

### Step 3 — Grade on 5 dimensions
Apply [`grading-rubric.md`](grading-rubric.md): Completeness, Accuracy, Clarity, Diagrams, Coverage —
each A–F. Respect the applicability and diagram requirement matrices:
- N/A docs are not graded (status N/A).
- Optional diagrams auto-A when absent.
- A doc whose area is absent is N/A, not F for missing a diagram.

### Step 4 — Compute the overall grade
**Overall = the lowest dimension grade.** Every dimension must be A for a generated doc to pass.
N/A docs pass by definition and do not raise the denominator.

### Step 5 — Write actionable feedback
For every dimension below A, give specific, file-and-line feedback the generator can act on without
re-exploring. See the examples in `grading-rubric.md`.

## Output: verification report

Save to `docs/_verification_report.md` with this structure:

```markdown
# Documentation Verification Report

**Date**: {current date}
**Iteration**: {iteration number}
**Profile**: {auto|small|full}
**Verdict**: {PASS | FAIL}
**Documents**: {X} pass / {Y} fail / {Z} N/A out of {total applicable}

## Grade Summary

| Document | CMP | ACC | CLR | DIA | COV | Overall |
|----------|-----|-----|-----|-----|-----|---------|
| README.md | A | A | A | A | A | A |
| architecture.md | A | B | A | A | A | B |
| database-schema.md | - | - | - | - | - | N/A (no datastore) |
| glossary.md | A | A | A | - | A | A |
| ... | | | | | | |

*DIA column: `-` means diagrams not required or the doc is N/A.*

## Deterministic Checks

- File paths: {pass/fail, count}
- Cross-references / dist `--check`: {pass/fail}
- Endpoint/command/export counts: {details}
- Mermaid syntax: {pass/fail}
- Secret scan: {pass/fail}
- Generated markers: {pass/fail}

## Detailed Feedback

### architecture.md — Overall: B

#### Accuracy (B)
- The doc states the API gateway routes to 4 services but only 3 exist:
  `user-service`, `auth-service`, `payment-service`. The "notification-service" on line 47 does not
  exist — there is only a `NotificationWorker` in src/workers/notification.ts (a background job).
- **Fix**: Remove notification-service from the service-map diagram and services table; move
  NotificationWorker to workflows-and-triggers.md.

### {next failing doc}...

## N/A Documents

| Document | Reason |
|----------|--------|
| database-schema.md | No datastore, ORM, or migrations found |
| frontend-backend.md | Backend-only repo; no frontend client |

## Pass/Fail Summary

- **Passing ({X})**: {docs that scored A overall}
- **Failing ({Y})**: {docs with overall grade and primary issue}
- **N/A ({Z})**: {docs skipped as not applicable}
- **Recommendation**: {what to focus on next iteration, prioritized by impact}
```

## Critical rules

1. **Verify against CODE, not the exploration report.** The report may have errors too.
2. **Grade only generated docs.** N/A and `--skip` docs are reported but not graded.
3. **Strict but fair.** Grade A means genuinely excellent, not merely acceptable.
4. **Feedback must be actionable** — file paths, line numbers, specific fixes.
5. **Don't grade on style preferences** — objective quality criteria only.
6. **Mermaid syntax must be valid.** A diagram that won't render is at most a C on Diagrams.
7. **Check that cross-references resolve.** Broken links lower the Coverage grade.
8. **The report itself must be well-structured** — the orchestrator parses it.
9. **Respect diagram exceptions.** Don't penalize optional or N/A docs for lacking diagrams.
10. **Verify agent-friendliness.** Check for "Read when" triggers, structured tables, and file-path
    references — these affect Clarity.
11. **Check consistency across docs.** If services.md says 3 services but architecture.md says 4,
    flag the discrepancy in both docs' feedback.
12. **When context pressure is high**, split verification per doc instead of having one verifier
    grade the whole suite. Self-grading is not independent verification; recommend a human
    spot-check of the PASS report before committing.
