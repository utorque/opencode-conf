# Phase 2 — Generation

Turn the exploration report (`docs/_exploration_report.md`) into polished documentation for the
**applicable** docs only. Each document serves **two audiences at once**: human developers and AI
coding agents. This file is both the operating manual for the generate phase and the prompt to hand
to a per-doc subagent.

## Run modes

- **With parallel subagents**: dispatch **one writer subagent per applicable document**, in
  parallel. Give each subagent this file plus the single row it must write. Each writes exactly one
  file to `docs/`.
- **Without subagents**: write the documents yourself, one at a time, following the same guidance.

On **retry iterations, only regenerate documents that scored below A** — preserve passing docs
untouched. In `--incremental` mode, do the same across runs: keep existing generated docs that
already verified A.

## The document set

Generate only docs whose applicability condition is met. Record every skipped doc as N/A with a
reason in both reports. Never create a stub file to satisfy a filename.

| File | Content | Applies when | Diagrams |
|---|---|---|---|
| `docs/README.md` | Project overview, quick-start, how to run/build/test, tech-stack summary, links to generated docs | Always | Optional |
| `docs/architecture.md` | System architecture: service map, component diagram, deployment view, key design decisions | Always | Required |
| `docs/tech-stack.md` | Complete tech-stack inventory: languages, frameworks, libraries, tools, versions, purpose | Always (`auto`/`full`) | Optional |
| `docs/api-reference.md` | Full API reference: every endpoint/CLI command/public export, method, path, auth, shapes | API/CLI/library surface exists | Required (request/CLI flow) |
| `docs/database-schema.md` | Database schema: tables, fields, types, relationships, indexes, migrations timeline | Datastore/schema exists | Required (ER) |
| `docs/frontend-backend.md` | Frontend–backend communication: data fetching, auth flow, real-time, shared contracts | Frontend + backend communicate | Required (sequence) |
| `docs/services.md` | Service/module inventory: purpose, responsibilities, dependencies | Multiple services/packages/boundaries | Required (interaction) |
| `docs/workflows-and-triggers.md` | Background jobs, cron, event triggers, webhooks, async patterns, queue topology | Jobs/queues/events exist | Required (event flow) |
| `docs/devops.md` | CI/CD pipelines, deployment process, infrastructure, monitoring, environments | CI/CD/deploy/IaC/monitoring exists | Required (pipeline) |
| `docs/glossary.md` | Domain terms, abbreviations, acronyms, business entities with plain-English definitions | Always | Not needed |
| `docs/error-catalog.md` | Error types, codes, HTTP status mappings, where thrown, handling, remediation | Custom errors/error codes exist | Optional |
| `docs/testing-strategy.md` | Test setup, frameworks, patterns, directory structure, commands, coverage, test data | Tests exist | Optional |
| `docs/environment-setup.md` | Local dev setup: prerequisites, install steps, env vars, secrets, gotchas, troubleshooting | Always | Optional |
| `docs/coding-conventions.md` | Code patterns, naming rules, design patterns used, anti-patterns, file organization | Always | Optional |
| `docs/security.md` | Auth model, authorization, validation, secret management, CORS, rate limiting, middleware | Security surface exists | Required (auth flow) |

"Required" diagrams MUST be present and valid **for generated docs**. N/A docs are not graded for
missing diagrams. `small` profile = README, architecture, environment-setup, glossary,
coding-conventions (+ api-reference when an API/CLI/public API exists). `full` profile = every
applicable doc, including optional docs even when thin. `auto` = core plus clearly applicable docs.

## Non-destructive writes

Every generated doc starts with the marker, before the title:

```markdown
<!-- make-docs:generated -->
# Architecture
```

Before writing each file:

1. If the file does not exist → write it.
2. If it exists **with** the marker → overwrite it.
3. If it exists **without** the marker → it is human-written or legacy.
   - Default: skip it, keep the file, and report the conflict in the summary.
   - `--force`: back it up to `docs/_backup/<name>.<UTC timestamp>.md`, then overwrite.
4. If an existing **generated** doc's area is now N/A, move it to
   `docs/_backup/<name>.<UTC timestamp>.md`; do not leave a stale generated doc in the published
   set. Record the N/A reason.
5. `--dry-run`: print the planned writes/conflicts/backups and stop before writing anything.

On retries, only failing generated docs are rewritten; passing docs stay untouched.

## Core principles

1. **Write for a new developer** joining tomorrow: assume they know the tech stack but nothing about
   this specific project.
2. **Structure for AI agents.** These docs are loaded as context by opencode, Cursor, Copilot,
   SpecKit, and others. Use structured tables, explicit headings, and concise summaries. Lead every
   section with a 1–2 sentence summary.
3. **Include Mermaid diagrams** wherever they add clarity or are marked Required.
4. **Never fabricate.** Document only what the exploration data and codebase actually show. If an
   area does not exist, it is N/A; do not invent a database, service, frontend, or API to fill a
   filename. Mark genuinely unclear items with `⚠️ Needs clarification`.
5. **Cross-reference only generated docs** with relative links like
   `[API Reference](api-reference.md)`. Never link a doc that was skipped as N/A.
6. **Be thorough but scannable.** Prefer tables over prose for inventories; short paragraphs; code
   blocks for examples.
7. **Use `.opencode/context/` as a source when present.** Its `CONTEXT.md` and `topics/*.md` capture
   design decisions, architecture rationale, and the project glossary — generated docs must agree
   with them. If the code contradicts the context tree, document the code and flag the drift with
   `⚠️`; Phase 4 reconciles the tree.
8. **No secrets.** Use placeholder values only; never copy real credentials, tokens, or user data.

## Structure every doc should have

- **Marker** — `<!-- make-docs:generated -->` on the first line.
- **Title** — clear, descriptive h1.
- **"Read this doc when" trigger** near the top, e.g.
  `> **Read this doc when:** Adding API endpoints, modifying routes, or changing auth.`
- **Overview** — 2–4 sentences on what it covers.
- **Table of Contents** — for docs longer than 3 sections.
- **Body** — h2/h3 headings, tables, diagrams, short code examples.
- **Related Docs** — links to at least 2 other **generated** docs in the set.
- **Last Updated** — note that it was auto-generated, with the date.

## Agent-friendly patterns

Use tables for inventories, not bullet lists:

```markdown
| Endpoint | Method | Auth | Handler | Description |
|----------|--------|------|---------|-------------|
| /api/users | GET | JWT | src/routes/users.ts:14 | List all users |
```

Include file paths as anchors:

```markdown
## User Service
**Location:** `src/services/user.ts`
**Depends on:** `src/models/user.ts`, `src/utils/hash.ts`
```

Use structured constraint blocks:

```markdown
## Constraints
- All endpoints MUST validate input with Zod schemas.
- Error responses MUST use the `{ success: false, error: { code, message } }` shape.
- New routes MUST be registered in `src/routes/index.ts`.
```

## Mermaid diagrams

Pick the right type: `graph TD`/`graph LR` (architecture, services), `erDiagram` (database),
`sequenceDiagram` (request/auth flows), `flowchart TD` (workflows), `stateDiagram-v2` (lifecycles).

Quality rules:
- Every node labeled with readable text, not just IDs.
- Include directionality with labels where relationships aren't obvious.
- Keep diagrams focused — max ~15 nodes; split if larger.
- Ensure valid Mermaid syntax (proper quoting, no unsupported characters).
- Do not rely on Mermaid click handlers; the dist uses `securityLevel: 'antiscript'`.

## Doc-type-specific guidance

- **glossary.md** — sort terms alphabetically, 1–2 sentence definitions, "Found in" column with file
  paths, group by domain area if distinct. Critical for agents: prevents invented synonyms.
- **error-catalog.md** — group by category (auth, validation, business logic, system); include name/
  class, HTTP status, code, where thrown, recommended handling; document the error response shape.
- **coding-conventions.md** — structure as DO/DON'T pairs with concrete examples; reference the
  linter/formatter configs that enforce each rule. Heavily referenced by AGENTS.md — keep it
  authoritative.
- **environment-setup.md** — a step-by-step guide from zero; prerequisites with versions; every env
  var with an example value (never real secrets); a "Common Issues" section.
- **security.md** — start with the auth flow as a sequence diagram; document the middleware chain in
  order; note what each role/permission can access and any cross-service boundaries.
- **api-reference.md** — for libraries, document public exports and types instead of HTTP endpoints;
  for CLIs, document commands, flags, exit codes, and examples.

## Revision mode (retry iterations)

When re-invoked with verification feedback for a specific doc:
1. Read the **existing** doc file first.
2. Read the **verification feedback** for that document.
3. **Only fix** what the feedback calls out — don't rewrite passing sections.
4. **Preserve** the structure and content graded A.
5. **Add** missing content, **correct** inaccurate content, **improve** unclear sections.
6. Re-check that Mermaid diagrams render (valid syntax).
7. Ensure cross-references still resolve.

## Self-check before finishing any doc

- [ ] Generated marker present on the first line.
- [ ] "Read this doc when" trigger at the top.
- [ ] Every section has substantive content (no empty sections or TODOs).
- [ ] All Mermaid diagrams have valid syntax.
- [ ] All cross-references use correct relative paths and point to generated docs.
- [ ] Tables have header rows and are properly formatted.
- [ ] File paths reference actual files found in exploration.
- [ ] No fabricated information — everything traces to the codebase.
- [ ] No real secrets or user data.
- [ ] `⚠️` markers on genuinely uncertain items.
- [ ] Saved to the correct path in `docs/`.
- [ ] Related Docs section links to at least 2 other generated docs in the set.
