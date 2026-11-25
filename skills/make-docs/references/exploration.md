# Phase 1 — Exploration

Scan the codebase and produce structured, factual inventories of what exists. This file is both the
**operating manual** for the explore phase and the **prompt** to hand to a subagent when you run it
as one.

## Run modes

- **With parallel subagents** (harness has a Task/agent/parallel primitive): dispatch **8 read-only
  subagents**, one per brief below, in parallel. Give each subagent *this file's "Core principles"
  and "Search strategy" sections plus its single brief*. Restrict each to read-only tools.
- **Without subagents**: work through the 8 briefs yourself, sequentially, using read/grep/glob.

Either way, the phase ends by **merging all findings into one report** saved to
`docs/_exploration_report.md` (the `_` prefix marks it an internal working file).

## Core principles

1. **Read only.** Never create, modify, or delete files during exploration.
2. **Be exhaustive.** Search broadly — check every directory, not just the obvious ones.
3. **Be precise.** Report exact file paths, line numbers, and snippets where relevant.
4. **Be structured.** Output well-organized markdown with clear headings and tables.
5. **Never fabricate.** If you can't find something, say so. Don't guess.
6. **Determine applicability first.** A doc is generated only when its area actually exists. Absence
   is a finding, not a gap to fill.
7. **Use `.opencode/context/` when present.** If it exists, read `CONTEXT.md` and its `topics/*.md`
   before scanning: it holds the project's stated intent, design decisions, and glossary. Treat it
   as a strong prior, but confirm against the code — the tree can drift.
8. **Respect existing doc ownership.** Check `docs/*.md` for `<!-- make-docs:generated -->`. Unmarked
   files are human-written; report them as conflicts, do not assume they are yours to rewrite.
9. **Think like an AI agent.** Structure output so other agents can parse it as context.

## Search strategy

1. Start with `tree -L 3` or `find . -maxdepth 3 -type f` to understand the directory structure.
2. Check package manifests first: `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`,
   `pom.xml`, `build.gradle`, `Gemfile`, `composer.json`, `pyproject.toml`, etc.
3. Check for existing context files: `AGENTS.md`, `.opencode/context/` (read `CONTEXT.md` and
   `topics/*.md`), `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`, `docs/`,
   `specs/`, `.specify/`.
4. Use grep aggressively to find patterns:
   - Routes: `@app.route`, `router.get`, `@GetMapping`, `get '/'`, etc.
   - Models: `class.*Model`, `@Entity`, `Schema(`, `create_table`, etc.
   - Config: `database`, `redis`, `kafka`, `queue`, `cron`, etc.
   - Errors: `throw new`, `raise`, `Error(`, `Exception`, `error_code`, etc.
   - Auth: `jwt`, `bearer`, `session`, `passport`, `auth`, `guard`, `middleware`.
   - Tests: `describe(`, `test(`, `it(`, `def test_`, `@Test`, `assert`.
   - Public API: `module.exports`, `export`, `__all__`, `pub use`, `func main`, `bin` entries.
5. Read key files in full when they're central (entry points, configs, schemas).
6. Use glob to find files by pattern (`**/*.proto`, `**/migrations/**`, `**/*schema*`).

Default depth for documentation generation is **very thorough**: scan everything, read key files,
grep for patterns across the entire codebase.

## Output format (per brief)

- **Summary** at the top (2–3 sentences).
- **Inventory tables** for lists (endpoints, models, services, …) — consistent columns so generator
  agents can parse them reliably.
- **File references** with exact paths.
- **Mermaid diagram suggestions** where applicable (write the actual ```mermaid block).
- **Gaps & uncertainties** section noting anything you couldn't determine.

Example table shapes:

```markdown
| Item | Location | Details |
|------|----------|---------|
| User model | src/models/user.ts:5 | fields: id, email, name, role |

| Term | Definition | Found in |
|------|-----------|----------|
| Wrap | Annual video summary for a user | src/models/wrap.ts, src/services/wrap-generator.ts |

| Error | Code/Status | Thrown in | Handling |
|-------|------------|-----------|----------|
| InvalidTokenError | 401 | src/middleware/auth.ts:34 | Returns JSON error, logs warning |
```

---

## The 8 exploration briefs

### Brief 1 — Project Overview, Tech Stack & Applicability

Scan the entire repo. Identify:
- Programming languages and their relative usage.
- Frameworks and libraries (check package.json, requirements.txt, go.mod, Cargo.toml, Gemfile,
  pom.xml, build.gradle, etc.).
- Build tools, bundlers, test frameworks, linters, formatters.
- Monorepo vs single-repo structure.
- Environment/config management (.env, config files, docker-compose, k8s manifests).
- CI/CD pipeline files (.github/workflows, Jenkinsfile, .gitlab-ci.yml, etc.).
- README, CONTRIBUTING, LICENSE presence.
- Existing AGENTS.md, .cursorrules, .windsurfrules presence.
- Existing `.opencode/context/` tree: summarize `CONTEXT.md` design decisions, module map, and
  glossary, plus each `topics/*.md` it references — this feeds the generated docs.
- Existing docs/ or specs/ directories and their contents.
- **Project profile** — one of: web app, backend service/API, library/SDK, CLI, desktop/mobile app,
  data/ML project, infrastructure/config repo, monorepo, other. A repo can mix profiles.
- **Surfaces present** (yes/no with evidence): HTTP API, GraphQL, gRPC, WebSocket, CLI, public
  library exports, database/ORM/migrations, frontend app, background jobs/queues, CI/CD/deploy.
- **Applicability table** — for each doc below, `Generate` or `N/A` with a one-line reason.

Output a structured markdown summary that starts with the project profile and applicability table.

#### Doc applicability matrix

| Doc | Generate when |
|-----|---------------|
| `README.md` | Always |
| `architecture.md` | Always (any non-trivial codebase) |
| `tech-stack.md` | Always in `auto`/`full`; omitted in `small` |
| `api-reference.md` | HTTP/GraphQL/gRPC/WebSocket surface, CLI commands, or a public library API |
| `database-schema.md` | Datastore, ORM models, migrations, or a persistent schema exists |
| `frontend-backend.md` | A frontend and a backend communicate (API client, auth flow, real-time) |
| `services.md` | More than one deployable, package, or module boundary worth mapping |
| `workflows-and-triggers.md` | Background jobs, cron, queues, webhooks, or event handlers exist |
| `devops.md` | CI/CD, containers, IaC, deployment, environments, or monitoring exist |
| `glossary.md` | Always |
| `error-catalog.md` | Custom errors, error codes, or centralized error handling exist |
| `testing-strategy.md` | A test suite or test config exists |
| `environment-setup.md` | Always |
| `coding-conventions.md` | Always |
| `security.md` | Auth/authz, validation, secret management, CORS, or rate limiting exists |

`small` profile = `README`, `architecture`, `environment-setup`, `glossary`, `coding-conventions`
(plus `api-reference` when an API/CLI/public API surface exists). `full` profile = every applicable
doc, including optional docs even when thin. `auto` = core plus clearly applicable docs.

### Brief 2 — Architecture & Service Boundaries

Identify the high-level architecture:
- Monolith, microservices, serverless, or hybrid?
- Every distinct service/module/package and its purpose.
- Entry points (main files, index files, server bootstrap).
- Directory structure → architectural components mapping.
- Shared libraries or common packages.
- Service mesh, API gateway, or message queue configurations.
- Architecture decision records (ADRs) if any.

Output a structured summary with a Mermaid diagram suggestion for the service map.

### Brief 3 — API Surface

Find ALL API endpoints, routes, and handlers:
- REST endpoints (Express, FastAPI, Spring, Rails, etc.).
- GraphQL schemas and resolvers.
- gRPC proto files and service definitions.
- WebSocket handlers.
- CLI command definitions and flags.
- Public library exports (functions, classes, types, subpath exports).
- For each: HTTP method or command name, path/signature, handler location, auth requirements if
  visible.
- OpenAPI/Swagger specs, Postman collections.
- Request/response shapes where type definitions exist.
- Rate limiting, pagination, versioning patterns.

Output a structured inventory as markdown.

### Brief 4 — Database & Data Layer

Find ALL database-related code:
- ORM models, schemas, entities (Prisma, SQLAlchemy, TypeORM, ActiveRecord, etc.).
- Migration files and their chronology.
- Database configuration and connection setup.
- Seed files and fixtures.
- Stored procedures, views, triggers if referenced.
- Cache layer (Redis, Memcached configs).
- Message queues (RabbitMQ, Kafka, SQS configs).
- For each model/table: fields, types, relationships, indexes if visible.

Output a structured inventory with a Mermaid ER diagram suggestion. If no datastore exists, say so
explicitly and mark `database-schema.md` N/A.

### Brief 5 — Frontend–Backend Communication

Map how the frontend talks to the backend:
- API client setup (axios, fetch wrappers, tRPC, GraphQL clients).
- State management that interfaces with APIs (Redux thunks, React Query, SWR, Vuex actions).
- Authentication flow (token storage, refresh logic, OAuth redirects).
- Real-time communication (WebSocket, SSE, polling).
- File upload/download mechanisms.
- Client-side error handling and retry patterns.
- Shared types or contracts between frontend and backend.

Output a structured summary as markdown. If the repo has no frontend or no backend communication,
mark `frontend-backend.md` N/A.

### Brief 6 — Workflows, Triggers & DevOps

Identify operational and workflow patterns:
- Background job processors (Sidekiq, Celery, Bull, etc.).
- Scheduled tasks / cron jobs.
- Event-driven triggers (webhooks, pub/sub, event emitters).
- Deployment config (Docker, Kubernetes, Terraform, serverless.yml).
- Monitoring and logging setup (Datadog, Sentry, CloudWatch, etc.).
- Feature flags, A/B testing infrastructure.
- Environment management (staging, production, dev).
- Infrastructure-as-code files.

Output a structured summary as markdown. Mark workflow/devops docs N/A when neither exists.

### Brief 7 — Domain Terminology & Error Handling

Extract domain-specific knowledge, in TWO sections:
1. **Glossary** — business domain terms used in code (variable/class names, comments that reveal
   concepts), abbreviations/acronyms and what they stand for, domain entities and relationships
   (business concepts, not just DB models), domain-specific enums/constants with business meaning.
   Include definitions inferred from code context.
2. **Error catalog** — custom error types/classes, error codes, HTTP status mappings, where thrown,
   handling patterns, error response formats, logging patterns and levels. Mark the error catalog
   N/A when errors are ad-hoc with no reusable catalog.

### Brief 8 — Testing, Security & Conventions

Cover three areas:
- **Testing**: framework(s) (Jest, pytest, RSpec, JUnit, …), test directory structure and naming,
  test types (unit/integration/e2e/snapshot/contract), utilities/factories/fixtures/mocks, coverage
  config and thresholds, how to run tests (commands, flags, env). Mark testing-strategy N/A when no
  tests exist.
- **Security**: auth mechanism (JWT, sessions, OAuth, API keys), authorization model (RBAC, ABAC,
  guards), input validation patterns/libraries, CORS config, rate limiting, secret management
  (.env, vault, AWS secrets), security-related middleware chain. Mark security N/A when there is no
  security surface.
- **Conventions**: code style (functional vs OOP, naming conventions), common design patterns
  (repository, service layer, factory, …), import/export conventions, file/directory naming,
  in-code documentation patterns (JSDoc, docstrings, …).

Output a structured summary covering all three areas.

---

## Domain-specific search hints

**Domain terminology** — class/variable/enum names encode concepts; comments and docstrings explain
business terms; constants files define business values; README/CONTRIBUTING/existing docs may have a
glossary; URL paths and DB column names carry domain vocabulary.

**Error handling** — grep for custom error/exception class definitions, error-code enums/constants,
error-handling middleware, API response formatting for error shapes, try/catch patterns.

**Testing** — find test config (jest.config, pytest.ini, .rspec), test directory structure and
naming, test utilities/factories/fixtures/mocking, coverage config (nyc, istanbul, coverage.py), CI
test commands.

**Security** — auth middleware and guards, CORS config, rate limiting, input validation libs (Joi,
Zod, class-validator), secret/env management patterns.

**Conventions** — import patterns (barrel exports, relative vs absolute), naming conventions,
design patterns, linter/formatter configs (.eslintrc, .prettierrc, rubocop.yml), how existing code
is structured.
