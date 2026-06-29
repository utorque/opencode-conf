# Plugins

> Runtime plugins registered in `opencode.jsonc`'s `plugin:` array.

## `cc-safety-net` (external)

Safety rails for destructive ops. Installed via `opencode plugin -g cc-safety-net` in `install_plugins.sh`.

## `context-mode` (external MCP server)

Context-window protection layer. Auto-installs itself via opencode on first launch (not handled in `install_plugins.sh`). Runtime data lands in `context-mode/sessions/` (gitignored).

Service: a local SQLite FTS5 knowledge base. Tools exposed: `ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_fetch_and_index`, `ctx_index`, `ctx_search`, `ctx_stats`, `ctx_purge`, `ctx_doctor`, `ctx_insight`, `ctx_upgrade`.

Routing rules: `instructions/context-mode.md` (BLOCKED list: shell `curl/wget`, inline HTTP, direct web fetch — all redirected through indexed sandbox tools). Sub-session memory (decisions, errors, blockers, plans) is auto-captured + searchable via `ctx_search(sort: "timeline")`.

User commands: `ctx stats`, `ctx doctor`, `ctx upgrade`, `ctx purge`. After `/clear` or `/compact`, knowledge base + session stats persist; use `ctx purge` to start fresh.

## `@opencode-ai/plugin` (npm dep)

Pinned `1.17.9` in `package.json`. RESTORED via `bun install` (lockfiles `bun.lock`/`package-lock.json` are gitignored — regen per machine). The only runtime dependency.
