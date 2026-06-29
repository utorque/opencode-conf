# Project Context

> Lean always-on overview. Deep material lives in `topics/` (loaded on demand via the `@` refs below) and the roadmap lives in `.opencode/plans/` (managed by `to-prd` / `to-issues`). Rules live in `AGENTS.md` (managed by `/init`). Keep this file lean enough to load every session, but long enough to convey the project's overall context — a fresh agent reading only this file should grasp what the project is, how it's shaped, and the key domain terms.

- **Product**: A personal [opencode](https://opencode.ai) configuration repo (`~/.config/opencode`), git-synced across machines and treated as a reusable reference. Tuned for token-efficient, plan-first agentic coding: protect the context window, plan before build, parallel by default, living context.
- **Actors**: the single user (owner); the opencode CLI/runtime (primary consumer of this config); four agents — `planner` (read-only planning, primary), `build` (one-issue implementer, primary), `automode` (autonomous, primary), `multimodal` (visual inspection subagent). MCP tools from the `context-mode` plugin. External plugins: `cc-safety-net`.
- **Tech stack**: opencode config (JSON / JSONC / Markdown). JS plugins run on [Bun](https://bun.sh); only runtime dep is `@opencode-ai/plugin` (pinned `1.17.9`). No datastore: context-mode uses a local SQLite FTS5 knowledge base under `context-mode/sessions/`. No deploy target — this IS the deploy artifact (consumed in place by opencode).

## Architecture

`opencode.jsonc` is the single source of truth: it registers the plugin array, the always-on `instructions:` array (loaded in order), the permission matrix, and agent overrides (`plan` agent disabled in favor of the custom `planner` agent). The `instructions:` array loads, in order: `AGENTS.md` (index) → `instructions/caveman.md` → `instructions/context-mode.md` → `instructions/context-hygiene.md` → this file. Rules are always-on; agents are thin orchestrators that **reference** skills rather than paraphrase them — skill bodies under `skills/*/SKILL.md` are the single source of truth for workflow detail. The planning + context trees (`.opencode/plans/`, `.opencode/context/`) are runtime-edited by skills and the `refresh-context-md` command, not hand-curated rules.

Module map:
- `opencode.jsonc` — single source of truth: plugins, always-on instructions order, permission matrix, agent overrides.
- `AGENTS.md` — entry-point index; points at rule files + planning/context trees. Loaded first.
- `instructions/` — always-on rule files (`caveman.md`, `context-mode.md`, `context-hygiene.md`).
- `agents/*.md` — per-agent role/phase/permission definitions (`planner`, `build`, `automode`, `multimodal`).
- `skills/*/SKILL.md` — workflow single-source-of-truth bodies (`caveman*`, `grilling`, `tdd`, `pdf`, `to-prd`, `to-issues`). Brief `README.md` in caveman-family skills.
- `commands/*.md` — slash-command definitions (`refresh-context-md`, `project-status`).
- `plugins/caveman/` — runtime caveman-mode tracker plugin (gitignored; installed by `install_plugins.sh`).
- `install_plugins.sh` — bootstrap: bun, `cc-safety-net`, caveman; prunes caveman agent/command shims (keeps only skills).
- `.opencode/plans/` — roadmap: `NNN_PRD_<slug>.md` + `issues/NNN_Issue_<slug>.md` (+ `archive/`).
- `.opencode/context/` — this living project-context tree (you are here).
- `context-mode/` — MCP server runtime data (sessions); gitignored.

### Deep dives (loaded on demand — read with the Read tool when the task touches them)
- @.opencode/context/topics/agents-and-skills.md
- @.opencode/context/topics/plan-lifecycle.md
- @.opencode/context/topics/plugins.md

## Domain glossary

- **opencode**: the agentic-coding CLI/runtime this repo configures.
- **Agent**: a named role/phase/permission profile (`planner`, `build`, `automode`, `multimodal`). Primary agents run top-level; `multimodal` is a hidden subagent.
- **Skill**: a workflow body under `skills/*/SKILL.md` (single source of truth). Agents reference skill bodies; they do not paraphrase them.
- **Instruction**: an always-on rule file loaded by the `opencode.jsonc` `instructions:` array (caveman, context-mode, context-hygiene).
- **PRD**: Product Requirements Document at `.opencode/plans/NNN_PRD_<slug>.md`. Lifecycle state machine: `Draft → Aligned → Done` (managed by `to-prd` skill).
- **Issue**: a tracer-bullet vertical slice at `.opencode/plans/issues/NNN_Issue_<slug>.md`. Lifecycle: `TODO → DOING → DONE → BLOCKED|CANCELLED` (managed by `to-issues` skill).
- **Tracer bullet / vertical slice**: a single end-to-end slice of a feature, independently grabbable by one agent.
- **Grilling**: the alignment interview (`/grilling`) that stress-tests a feature design before a PRD exists.
- **Done-gate** (PRD 001): an issue may not move `→ DONE` until `.opencode/context/` has been refreshed for any architecture/API/data-model shift.
- **Caveman mode**: terse-model-output compression (drops articles/filler, keeps technical substance). Six intensity levels. Tracked by the plugin + ruleset.
- **context-mode**: MCP tool layer that protects the context window — large outputs routed through a sandbox and indexed to an FTS5 knowledge base; raw bytes never enter the conversation.
- **Parallel close-out**: when a launcher fans out multiple issues as concurrent subagents, the launcher owns close-out and flips the PRD `→ Done` once no non-archived issue siblings remain.

## Conventions pointer

- Rules (style, routing, gotchas): `AGENTS.md` + `instructions/` (managed by `/init`).
- Roadmap (PRDs, issues): `.opencode/plans/` (managed by `/plan`, `to-prd`, `to-issues`).
- This overview: you are here (managed by `/refresh-context-md`). Hygiene rule (keep `.opencode/context/` updated in the same change as code when architecture/API/data model shifts) lives in the global `AGENTS.md` "Project context hygiene" section.

## Current focus

Both shipped PRDs are archived and Done: [000 config reconciliation](./.opencode/plans/archive/000_PRD_config-reconciliation.md) (split rules into `instructions/`, agents into thin orchestrators) and [001 context DONE-gate](./.opencode/plans/archive/001_PRD_context-done-gate.md) (issue cannot flip to DONE without refreshing `.opencode/context/`). `TODO.md` is empty of open work. No active PRD/epic in flight. The `planner` agent's `plan` builtin is disabled in `opencode.jsonc` (`agent.plan.disable: true`) — use the custom `planner` agent instead. Next focus TBD by the user.
