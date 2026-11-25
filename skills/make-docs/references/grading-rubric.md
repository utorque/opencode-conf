# Documentation Grading Rubric (RALPH)

The verification phase grades **every generated** doc on **5 dimensions** using **A–F** letter
grades. N/A docs are listed with status **N/A** and are not graded. This rubric is the single source
of truth — the verification step, the SKILL.md loop, and any human reviewer all use it.

**Overall grade for a generated document = its lowest dimension grade.** A doc scoring A, A, A, B, A
gets an overall **B**. This is intentionally strict: every dimension must be A to pass.

**PASS** = every generated doc scores A on every dimension, and every non-applicable doc is
justified as N/A. **FAIL** = any generated doc has a dimension below A.

**N/A** = the doc's area does not exist in the project (no datastore, no frontend, no queue, no
tests, no auth surface). N/A must be recorded with a reason in the exploration and verification
reports. A stub file created only to fill a filename is not N/A; it is an accuracy failure.

**Skipped** = the user excluded the doc with `--skip` or a profile. Reported, not graded.

---

## Dimension 1 — Completeness (CMP)

| Grade | Criteria |
|-------|----------|
| **A** | Covers 90%+ of relevant, applicable items found in the codebase. No significant omissions. |
| **B** | Covers 75–89%. Missing a few non-trivial items. |
| **C** | Covers 50–74%. Notable gaps in coverage. |
| **D** | Covers 25–49%. Major sections missing. |
| **F** | Covers <25% or is mostly placeholder content. |

## Dimension 2 — Accuracy (ACC)

| Grade | Criteria |
|-------|----------|
| **A** | All verifiable claims match the codebase. Zero factual errors. |
| **B** | 1–2 minor inaccuracies (e.g. slightly wrong path, outdated field name). |
| **C** | 3–5 inaccuracies or 1 significant error (e.g. wrong architecture description). |
| **D** | Multiple significant errors that would mislead a reader. |
| **F** | Predominantly incorrect or fabricated content. |

## Dimension 3 — Clarity (CLR)

| Grade | Criteria |
|-------|----------|
| **A** | Well-structured, easy to navigate, good use of headings/tables/examples. Has a "Read when" trigger. A new dev could follow it independently. Structured for AI-agent consumption. |
| **B** | Generally clear but some sections are dense or poorly organized. |
| **C** | Readable but requires significant effort. Missing structure or examples. |
| **D** | Confusing organization, jargon-heavy without explanation, hard to follow. |
| **F** | Incoherent or essentially unusable. |

## Dimension 4 — Diagrams (DIA)

| Grade | Criteria |
|-------|----------|
| **A** | Has relevant Mermaid diagrams with correct syntax, accurately represents the system, adds real understanding. |
| **B** | Has diagrams but they're incomplete or slightly inaccurate. |
| **C** | Has diagrams but they're too simplistic or have syntax errors. |
| **D** | Missing diagrams where they should clearly exist, OR diagrams are wrong. |
| **F** | No diagrams at all in a doc that requires them. |

### Diagram requirement matrix (by doc type)

| Doc | Diagram Requirement | Applies when | Grading Rule |
|-----|--------------------|--------------|--------------|
| architecture.md | Required | Always | Must have a system map |
| api-reference.md | Required | API/CLI/library surface exists | Must have a request/CLI flow |
| database-schema.md | Required | Datastore/schema exists | Must have an ER diagram |
| frontend-backend.md | Required | Frontend + backend communicate | Must have a sequence diagram |
| services.md | Required | Multiple boundaries exist | Must have an interaction diagram |
| workflows-and-triggers.md | Required | Jobs/queues/events exist | Must have an event flow |
| devops.md | Required | CI/CD/deploy/IaC exists | Must have a pipeline diagram |
| security.md | Required | Security surface exists | Must have an auth flow |
| README.md | Optional | Always | Auto-A if absent; grade quality if present |
| tech-stack.md | Optional | Always in auto/full | Auto-A if absent; grade quality if present |
| error-catalog.md | Optional | Custom errors exist | Auto-A if absent; grade quality if present |
| testing-strategy.md | Optional | Tests exist | Auto-A if absent; grade quality if present |
| environment-setup.md | Optional | Always | Auto-A if absent; grade quality if present |
| coding-conventions.md | Optional | Always | Auto-A if absent; grade quality if present |
| glossary.md | Not needed | Always | Always A — glossaries don't need diagrams |

A doc whose "Applies when" condition is false is **N/A**, not a D/F for a missing diagram.

## Dimension 5 — Coverage / Cross-References (COV)

| Grade | Criteria |
|-------|----------|
| **A** | Appropriately links to related generated docs. Concepts that span multiple docs are connected. Reader can navigate the full doc set. Has a "Related Docs" section. |
| **B** | Some cross-references but missing obvious connections. |
| **C** | Minimal cross-references. Doc feels isolated. |
| **D** | No cross-references despite clear connections to other docs. |
| **F** | Contradicts other docs or is completely siloed. |

Cross-references to N/A or skipped docs are broken coverage, not valid links.

---

## Deterministic checks

Run these before assigning grades. They are hard failures, not rubric dimensions:

- Every referenced file path exists.
- Every relative `.md` link resolves to a generated doc that exists.
- Endpoint/command/export inventory counts match grep results.
- Every Mermaid fence has a valid diagram header and balanced syntax.
- No high-confidence secrets; `make-docs:allow-secret` only on synthetic examples.
- Every generated doc has `<!-- make-docs:generated -->`.

Run `/build-docs --check` (or the script's `--check`) to validate links without writing HTML.

---

## Writing actionable feedback

For every dimension graded below A, write **specific, actionable feedback** the generator can act
on without re-exploring the codebase:

BAD: "Completeness needs improvement"
GOOD: "Missing 3 API endpoints: `POST /api/webhooks` (src/routes/webhooks.ts:14),
`GET /api/health` (src/routes/health.ts:3), `DELETE /api/sessions/:id` (src/routes/auth.ts:87).
Add these to the endpoint table."

BAD: "Glossary should have more terms"
GOOD: "Missing domain terms: 'Workspace' (used 47× in src/models/ and src/services/, a
tenant-level org unit), 'Pipeline' (src/workers/pipeline.ts, the data-processing chain, not CI/CD).
Add with definitions."
