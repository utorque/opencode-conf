<!-- caveman-begin -->
Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.
<!-- caveman-end -->
<!-- context-mode-begin -->
# context-mode — MANDATORY routing rules

context-mode MCP tools available. Rules protect context window from flooding. One unrouted command dumps 56 KB into context.

## Think in Code — MANDATORY

Analyze/count/filter/compare/search/parse/transform data: **write code** via `context-mode_ctx_execute(language, code)`, `console.log()` only the answer. Do NOT read raw data into context. PROGRAM the analysis, not COMPUTE it. Pure JavaScript — Node.js built-ins only (`fs`, `path`, `child_process`). `try/catch`, handle `null`/`undefined`. One script replaces ten tool calls.

## BLOCKED — do NOT attempt

### curl / wget — BLOCKED
Shell `curl`/`wget` intercepted and blocked. Do NOT retry.
Use: `context-mode_ctx_fetch_and_index(url, source)` or `context-mode_ctx_execute(language: "javascript", code: "const r = await fetch(...)")`

### Inline HTTP — BLOCKED
`fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, `http.request(` — intercepted. Do NOT retry.
Use: `context-mode_ctx_execute(language, code)` — only stdout enters context

### Direct web fetching — BLOCKED
Use: `context-mode_ctx_fetch_and_index(url, source)` then `context-mode_ctx_search(queries)`

## REDIRECTED — use sandbox

### Shell (>20 lines output)
Shell ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`.
Otherwise: `context-mode_ctx_batch_execute(commands, queries)` or `context-mode_ctx_execute(language: "javascript", code: "...")`. Use `language: "shell"` only when code matches the host shell.

### File reading (for analysis)
Reading to **edit** → reading correct. Reading to **analyze/explore/summarize** → `context-mode_ctx_execute_file(path, language, code)`.

### grep / search (large results)
Use `context-mode_ctx_execute(language: "javascript", code: "...")` in sandbox for portable filtering/counting.

## Tool selection

0. **MEMORY**: `context-mode_ctx_search(sort: "timeline")` — after resume, check prior context before asking user.
1. **GATHER**: `context-mode_ctx_batch_execute(commands, queries)` — runs all commands, auto-indexes, returns search. ONE call replaces 30+. Each command: `{label: "header", command: "..."}`.
2. **FOLLOW-UP**: `context-mode_ctx_search(queries: ["q1", "q2", ...])` — all questions as array, ONE call (default relevance mode).
3. **PROCESSING**: `context-mode_ctx_execute(language, code)` | `context-mode_ctx_execute_file(path, language, code)` — sandbox, only stdout enters context.
4. **WEB**: `context-mode_ctx_fetch_and_index(url, source)` then `context-mode_ctx_search(queries)` — raw HTML never enters context.
5. **INDEX**: `context-mode_ctx_index(content, source)` — store in FTS5 for later search.

## Parallel I/O batches

For multi-URL fetches or multi-API calls, **always** include `concurrency: N` (1-8):

- `context-mode_ctx_batch_execute(commands: [3+ network commands], concurrency: 5)` — gh, curl, dig, docker inspect, multi-region cloud queries
- `context-mode_ctx_fetch_and_index(requests: [{url, source}, ...], concurrency: 5)` — multi-URL batch fetch

**Use concurrency 4-8** for I/O-bound work (network calls, API queries). **Keep concurrency 1** for CPU-bound (npm test, build, lint) or commands sharing state (ports, lock files, same-repo writes).

GitHub API rate-limit: cap at 4 for `gh` calls.

## Output

Write artifacts to FILES — never inline. Return: file path + 1-line description.
Descriptive source labels for `search(source: "label")`.

## Session Continuity

Skills, roles, and decisions persist for the entire session. Do not abandon them as the conversation grows.

## Memory

Session history is persistent and searchable. On resume, search BEFORE asking the user:

| Need | Command |
|------|---------|
| What did we decide? | `context-mode_ctx_search(queries: ["decision"], source: "decision", sort: "timeline")` |
| What constraints exist? | `context-mode_ctx_search(queries: ["constraint"], source: "constraint")` |

DO NOT ask "what were we working on?" — SEARCH FIRST.
If search returns 0 results, proceed as a fresh session.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call `stats` MCP tool, display full output verbatim |
| `ctx doctor` | Call `doctor` MCP tool, run returned shell command, display as checklist |
| `ctx upgrade` | Call `upgrade` MCP tool, run returned shell command, display as checklist |
| `ctx purge` | Call `purge` MCP tool with confirm: true. Warns before wiping knowledge base. |

After /clear or /compact: knowledge base and session stats preserved. Use `ctx purge` to start fresh.
<!-- context-mode-end -->

<!-- context-hygiene-begin -->
## Project context hygiene

This project keeps a living project-context tree under `.opencode/context/` (sibling of `.opencode/plans/`). The lean `CONTEXT.md` overview loads every session via the global `opencode.json` `instructions:` array; deeper material lives in `.opencode/context/topics/*.md`, loaded on demand via `@` path refs in CONTEXT.md.

### You MUST update context docs

In the SAME change (commit/PR) as your code edit, update the matching `.opencode/context/` doc when your change touches any of:

- **Architecture** — top-level module add/remove/rename, data-flow shift, new service boundary -> edit `CONTEXT.md` Architecture section.
- **Public API** — new/removed/renamed public interface (REST route, RPC method, exported library API, CLI flag) -> edit `CONTEXT.md` module map or a topic file.
- **Data model** — schema change, new table/collection, migration altering shape -> edit/create `topics/data-model.md`.
- **Domain terms** — new ubiquitous-language term, renamed concept -> edit `CONTEXT.md` glossary.
- **Module responsibilities** — a module's purpose shifts -> edit `CONTEXT.md` module map.
- **Big feature** — work spanning multiple sessions warrants its own deep context -> create `topics/<feature>.md` and add an `@` ref in CONTEXT.md.

### When you need NOT update

Cosmetic refactor, internal rename, test additions, dependency bumps, formatting, docs-only changes — no context edit needed.

### Topic file rules

- One concern per file: `topics/<concern>.md` (e.g. `auth-module.md`, `data-model.md`, `checkout-feature.md`).
- ~1 page max. If it grows beyond that, split into two topics.
- Lazy-loaded: NEVER put a topic file in `opencode.json` `instructions:`. Agents read it only when their task triggers its `@` ref in CONTEXT.md.
- Each topic starts with a one-line purpose statement.

### Plan-mode agents

Plan agent is read-only for everything outside `.opencode/plans/**`. It MUST NOT edit `.opencode/context/` docs directly. Instead, when a plan introduces architecture/API/data-model shifts, it flags the needed context updates in the PRD's `## Further Notes` section as: `- Context update needed: .opencode/context/<file>.md — <what changed>`. The `build`/`automode` agent picks this up during implementation.

### Periodic regen

Run `/refresh-context-md` periodically (or after large refactors) to catch drift the hygiene rule missed. The command edits in place, preserving curated content; review via `git diff .opencode/context/`.
<!-- context-hygiene-end -->