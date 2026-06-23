# opencode config

My personal [opencode](https://opencode.ai) configuration. Tuned for token-efficient, plan-first agentic coding.

## Setup

### 1. Clone

```bash
git clone <repo-url> ~/.config/opencode
cd ~/.config/opencode
```

### 2. Install plugins

```bash
./install_plugins.sh
```

This installs:
- **[bun](https://bun.sh)** — JS runtime
- **cc-safety-net** — opencode plugin
- **caveman** — terse-mode plugin (compresses model output ~65-75%)
- **context-mode** — auto-installs itself via opencode on first launch

### 3. Install deps

```bash
bun install
```

Restores `@opencode-ai/plugin` from the tracked `package.json`.

### 4. Launch

```bash
opencode
```

## Plugins

| Plugin | What it does |
|--------|--------------|
| **caveman** (`./plugins/caveman/plugin.js`) | Compresses model responses to caveman-style prose. Drops articles/filler, keeps all technical substance. Six intensity levels (`lite`/`full`/`ultra`/`wenyan-*`). Toggle via `/caveman`. |
| **cc-safety-net** | Safety rails for destructive ops. |
| **context-mode** | Protects context window: routes large outputs through a sandbox, auto-indexes to a searchable knowledge base (FTS5). Run `ctx stats` / `ctx doctor` / `ctx purge`. |

## Workflow

Plan-first agentic flow, inspired by [mattpocock/skills](https://github.com/mattpocock/skills):

1. **Align** — `/grill` interview to stress-test a feature design until shared understanding.
2. **Plan** — synthesize alignment into a PRD at `.opencode/plans/NNN_PRD_<name>.md`.
3. **Decompose** — break PRD into tracer-bullet issues at `.opencode/plans/issues/NNN_Issue_<name>.md` (each new-feature issue starts with a failing test — TDD, red→green→refactor).
4. **Build** — pick an issue in `automode`, implement against acceptance criteria, move `Status: TODO → DOING → DONE`.

### Agents

| Agent | Role |
|-------|------|
| `planner` | Read-only (outside `.opencode/plans/**`). Aligns & plans. |
| `build` | Implements one issue. |
| `automode` | Autonomous multi-step execution. All permissions allow. |
| `multimodal` | Visual inspection (screenshots, UI, diagrams). |

### Skills

Custom slash commands + specialized workflows under `skills/`:
- **caveman** family — `/caveman`, `/caveman-commit`, `/caveman-review`, `/caveman-stats`, `/caveman-compress`, `/caveman-help`
- **planning** — `/grilling`, `/to-prd`, `/to-issues`
- **tdd** — red-green-refactor
- **pdf** — PDF read/write/merge/split/OCR

### Context hygiene

Living project-context tree at `.opencode/context/` (`CONTEXT.md` lean overview + `topics/*.md` deep dives). Updated in the same change as code when architecture/API/data model shifts. Run `/refresh-context-md` periodically to catch drift.

## License

Personal config. No license granted — use at your own risk.
