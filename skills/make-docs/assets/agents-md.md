<!--
Template for the AGENTS.md written to the project root (Phase 4, Step 4a). Canonical agent context
file for opencode and other tools. Plain relative Markdown links only — no tool-specific `@`
imports. Replace {placeholders}. Keep under 120 lines. Manage only the marked section; preserve
human-written content outside it. Keep only rows for docs that were actually generated; delete
N/A and --skip rows.
-->

# {Project Name}

{One-line description}

<!-- BEGIN AUTO-GENERATED DOCS SECTION — regenerate with make-docs -->

## Project Structure
{top-level directory → purpose mapping, max 8 lines, e.g.:}
src/api/        → API route handlers and middleware
src/models/     → Database models and schemas
src/services/   → Business logic layer
src/workers/    → Background job processors
src/utils/      → Shared utilities
tests/          → Test suites (unit, integration, e2e)
docs/           → Project documentation (auto-generated)

## Commands
{build, test, dev, lint — extracted from package.json / Makefile / etc., max 6 lines}

## Architecture
{2-3 sentence summary from architecture.md}
Full details: [docs/architecture.md](docs/architecture.md)

## Key Documentation

Read the relevant doc before making changes in that area. Delete rows for docs that were not
generated (N/A or `--skip`).

<!-- Add this row to the table below only if .opencode/context/ exists:
| Context tree | [.opencode/context/CONTEXT.md](.opencode/context/CONTEXT.md) | Project intent, design decisions, glossary |
-->

| Area | File | Read when... |
|------|------|--------------|
| Architecture | [docs/architecture.md](docs/architecture.md) | Modifying system structure or adding services |
| API Reference | [docs/api-reference.md](docs/api-reference.md) | Adding or modifying endpoints |
| Database | [docs/database-schema.md](docs/database-schema.md) | Working with models, migrations, schemas |
| Services | [docs/services.md](docs/services.md) | Changing inter-service communication |
| Frontend-Backend | [docs/frontend-backend.md](docs/frontend-backend.md) | Changing data fetching or auth flow |
| Workflows | [docs/workflows-and-triggers.md](docs/workflows-and-triggers.md) | Adding jobs, cron, events, webhooks |
| Security | [docs/security.md](docs/security.md) | Modifying auth, permissions, validation |
| Glossary | [docs/glossary.md](docs/glossary.md) | Encountering domain terms, naming entities |
| Errors | [docs/error-catalog.md](docs/error-catalog.md) | Adding error handling or custom errors |
| Conventions | [docs/coding-conventions.md](docs/coding-conventions.md) | Unsure about patterns or naming |
| Testing | [docs/testing-strategy.md](docs/testing-strategy.md) | Writing or modifying tests |
| Environment | [docs/environment-setup.md](docs/environment-setup.md) | Setting up local dev or troubleshooting |
| DevOps | [docs/devops.md](docs/devops.md) | Modifying CI/CD or deployment |
| Tech Stack | [docs/tech-stack.md](docs/tech-stack.md) | Evaluating or checking dependencies |

## Conventions
{Top 5 most critical rules extracted from coding-conventions.md}

## Terminology
{Top 10 most important domain terms extracted from glossary.md}

## Constraints
- Verify endpoints and models against docs before creating new ones
- Follow patterns documented in [docs/coding-conventions.md](docs/coding-conventions.md)
- Use terminology from [docs/glossary.md](docs/glossary.md)
- Rebuild `docs/dist/index.html` with `/build-docs` after docs changes; never hand-edit it

<!-- END AUTO-GENERATED DOCS SECTION -->
