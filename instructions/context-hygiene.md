# Project context hygiene

This project keeps a living project-context tree under `.opencode/context/` (sibling of `.opencode/plans/`). The lean `CONTEXT.md` overview loads every session via the global `opencode.json` `instructions:` array; deeper material lives in `.opencode/context/topics/*.md`, loaded on demand via `@` path refs in CONTEXT.md. Keep CONTEXT.md lean enough to load every session, but long enough to convey the project's overall context — a fresh agent reading only this file should grasp what the project is, how it's shaped, and the key domain terms. Favor completeness over brevity when the two conflict; this file is the session's only always-loaded map.

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

### Links must be clickable

Any `.md` file (CONTEXT.md, topics, PRDs, issues, AGENTS.md) MUST use clickable links. Rules:

- External references: `[text](https://...)` — never a bare URL.
- Local paths/refs: `[label](./relative/path.md)` or `[label](path/to/file)` — never a bare `path/to/file.md` or backtick'd path standing alone as a reference.
- `@` path refs in CONTEXT.md (for lazy-loaded topics) stay as-is — they are machine directives, not human links.
- If a path appears in prose for the user to follow, wrap it: see `[topics/data-model.md](./topics/data-model.md)`.

Bare paths inside code blocks or inline code (`` `opencode.jsonc` ``) are fine — they are not navigation links.

### Periodic regen

Run `/refresh-context-md` periodically (or after large refactors) to catch drift the hygiene rule missed. The command edits in place, preserving curated content; review via `git diff .opencode/context/`.
