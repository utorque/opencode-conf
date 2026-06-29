# Plugins

> Runtime plugins registered in `opencode.jsonc`'s `plugin:` array.

## `plugins/caveman/plugin.js` (local)

Runtime mode tracker. Gitignored; installed by `install_plugins.sh` (clones JuliusBrussee/caveman, runs its `bin/install.js --only opencode`, then prunes the dropped `cavecrew-*.md` agents + `caveman-*.md` commands — keeping only skills).

Responsibilities (dynamic state only — ruleset is separate, in `instructions/caveman.md`):
- Writes mode flag at session init (`.caveman-active`, gitignored).
- Parses user messages for `/caveman` commands + natural-language toggles ("talk like caveman", "less tokens", "be brief").
- Injects per-turn reinforcement into the system prompt.

Hook mapping (opencode >= 1.15.x): `event` (`session.created` type), `chat.message`, `experimental.chat.system.transform`.

Layout:
```
plugins/caveman/
├── package.json        (name: caveman-opencode-plugin, ESM, private)
├── plugin.js           (hook handlers)
└── caveman-config.cjs   (symlink-safe flag-write helpers)
```

Six intensity levels: `lite` | `full` (default) | `ultra` | `wenyan-lite` | `wenyan-full` | `wenyan-ultra`. Toggle: `/caveman <level>` or `stop caveman` / `normal mode`.

## `cc-safety-net` (external)

Safety rails for destructive ops. Installed via `opencode plugin -g cc-safety-net` in `install_plugins.sh`.

## `context-mode` (external MCP server)

Context-window protection layer. Auto-installs itself via opencode on first launch (not handled in `install_plugins.sh`). Runtime data lands in `context-mode/sessions/` (gitignored).

Service: a local SQLite FTS5 knowledge base. Tools exposed: `ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_fetch_and_index`, `ctx_index`, `ctx_search`, `ctx_stats`, `ctx_purge`, `ctx_doctor`, `ctx_insight`, `ctx_upgrade`.

Routing rules: `instructions/context-mode.md` (BLOCKED list: shell `curl/wget`, inline HTTP, direct web fetch — all redirected through indexed sandbox tools). Sub-session memory (decisions, errors, blockers, plans) is auto-captured + searchable via `ctx_search(sort: "timeline")`.

User commands: `ctx stats`, `ctx doctor`, `ctx upgrade`, `ctx purge`. After `/clear` or `/compact`, knowledge base + session stats persist; use `ctx purge` to start fresh.

## `@opencode-ai/plugin` (npm dep)

Pinned `1.17.9` in `package.json`. RESTORED via `bun install` (lockfiles `bun.lock`/`package-lock.json` are gitignored — regen per machine). The only runtime dependency.
