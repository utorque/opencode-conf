# Plugins

> Runtime plugins registered in `opencode.jsonc`'s `plugin:` array.

## `cc-safety-net` (external)

Safety rails for destructive ops. Installed via `opencode plugin -g cc-safety-net` in `install_plugins.sh`.

## `@opencode-ai/plugin` (npm dep)

Pinned `1.17.9` in `package.json`. RESTORED via `bun install` (lockfiles `bun.lock`/`package-lock.json` are gitignored — regen per machine). The only runtime dependency.
