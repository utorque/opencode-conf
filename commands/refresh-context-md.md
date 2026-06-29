---
description: Bootstrap or refresh the .opencode/context/ tree (CONTEXT.md, topics/) by scanning repo + recent commits. Edits in place, preserving curated content. Mirrors /init but for project context, not AGENTS.md rules. The keep-updated hygiene rule lives in the global AGENTS.md, not here.
agent: build
---

You are regenerating the project's living context tree at `.opencode/context/` (sibling of `.opencode/plans/`). This is the *descriptive* project context (what the project IS, who uses it, architecture, module map, domain glossary) — NOT rules (those live in `AGENTS.md`, owned by `/init`) and NOT the roadmap (that lives in `.opencode/plans/`).

Goal: every opencode session in this repo should auto-load an accurate, lean CONTEXT.md so primary agents start with project knowledge instead of blind. Deep material lives in `topics/*.md` loaded on demand via `@` refs.

## Phase 1 — Ensure the tree exists

Make sure these exist (mkdir -p, drop a `.gitkeep` in empty dirs):
```
.opencode/context/
.opencode/context/topics/
```
Skip paths that already exist.

## Phase 2 — Bootstrap missing files

If `.opencode/context/CONTEXT.md` does NOT exist, write it from the template below, then fill the placeholders from the repo (Phase 3). If it DOES exist, skip to Phase 4.

The keep-updated hygiene rule is **not** bootstrapped here — it lives in the global `~/.config/opencode/AGENTS.md` ("Project context hygiene" section), auto-loaded by every project. Do not create a per-project `_hygiene.md`.

### CONTEXT.md template (write on bootstrap, fill in Phase 3)

```markdown
# Project Context

> Lean always-on overview. Deep material lives in `topics/` (loaded on demand via the `@` refs below) and the roadmap lives in `.opencode/plans/`. Rules live in `AGENTS.md`. Keep this file lean enough to load every session, but long enough to convey the project's overall context — a fresh agent reading only this file should grasp what the project is, how it's shaped, and the key domain terms.

- **Product**: <one line — what this is, who it's for>
- **Actors**: <end-users, services, integrators>
- **Tech stack**: <language, framework, datastore, deploy target>

## Architecture

<one paragraph: top-level shape, data flow, key boundaries>

Module map:
- `path/to/module` — <one-line responsibility>
- `path/to/other` — <one-line responsibility>

### Deep dives (loaded on demand — read with the Read tool when the task touches them)
- @.opencode/context/topics/data-model.md
- @.opencode/context/topics/auth-module.md

## Domain glossary

<8-12 hard terms the codebase assumes; one line each>
- **Term**: meaning
- **Term**: meaning

## Conventions pointer

- Rules (style, commands, gotchas): `AGENTS.md` (managed by `/init`)
- Roadmap (PRDs, issues): `.opencode/plans/` (managed by `/plan`, `to-prd`, `to-issues`)
- This overview: you are here (managed by `/refresh-context-md`)

## Current focus

<rotate as focus shifts — active epic, open decisions, in-flight refactor>
```

### _hygiene.md — NOT bootstrapped here

The keep-updated rule lives in the global `~/.config/opencode/AGENTS.md` ("Project context hygiene" section) and auto-loads in every project. Do not create `.opencode/context/_hygiene.md`. If a legacy per-project `_hygiene.md` exists from a previous version of this command, leave it untouched (it is harmless) unless the user explicitly asks to remove it.

## Phase 3 — Fill placeholders (bootstrap path only)

Scan the repo to fill the CONTEXT.md template placeholders. Use the `Read`/`Glob`/`Grep` tools (NOT raw shell). Look at:

- `package.json` / `go.mod` / `Cargo.toml` / `pyproject.toml` / `mix.exs` / etc. for product name, deps, scripts (build/test/lint).
- Top-level directory structure for the module map.
- `README.md` / `docs/` for product purpose and actors.
- Existing `AGENTS.md` / `.cursor/rules/` / `CONTRIBUTING.md` for any stated conventions or domain terms (do NOT duplicate — just reference).
- `.opencode/plans/` PRDs for current focus / active epic.

Fill every `<...>` placeholder. Keep CONTEXT.md lean — terseness over padding — but complete enough that a fresh agent reading only this file grasps the project's overall context (product, actors, architecture, module map, domain terms). When in doubt, favor completeness over brevity; this file is the session's only always-loaded map of the project. If a section has no real content from the repo, leave the placeholder with a short `TODO: <what's missing>` note rather than inventing.

For each major concern discovered (data model, auth module, a big feature) that warrants its own deep doc, create `topics/<concern>.md` with a one-line purpose statement + the detail you gathered, and make sure CONTEXT.md's "Deep dives" section has an `@.opencode/context/topics/<concern>.md` ref for it.

If the repo cannot answer a key question (e.g. "who is the primary user?", "what is the deploy target?"), ask the user ONE targeted question with your best-guess answer recommended. Do not bulk-interrogate.

## Phase 4 — Drift patch (existing tree path)

If `.opencode/context/CONTEXT.md` already existed, do NOT rewrite it. Instead:

1. Read the existing `CONTEXT.md` and every `topics/*.md`.
2. Run `git log --oneline -30` (or equivalent) and scan recent commits for shifts in: architecture, public API, data model, domain terms, module responsibilities, new features.
3. Read the current repo state (`package.json`, top-level dirs, `README.md`, any new modules since last refresh).
4. Diff what the docs claim against what the repo now shows. Apply TARGETED patches with the Edit tool — preserve all manually curated prose, only update what drifted. If a topic file's concern has grown stale (module removed, feature shipped), update its content; only delete a topic file if the user confirms (suggest it; don't do it silently).
5. If recent work clearly introduced a new deep concern (new big feature, new data-model area) that lacks a topic file, create one and add the `@` ref to CONTEXT.md's "Deep dives".
6. Update the "Current focus" section to match the latest `.opencode/plans/` state (active PRD/epic).

The keep-updated hygiene rule lives in the global `~/.config/opencode/AGENTS.md`, not in this tree — nothing to patch here for policy.

## Phase 5 — Summary

Print a concise summary:
- Files created (with one-line purpose each).
- Files patched (with a one-line `what changed` per file).
- Topic files: count + names.
- Any questions you asked the user + their answers.
- Any drift you noticed but did not patch (and why).
- Final line: `Review changes: git diff .opencode/context/` — prompt the user to inspect before committing. Do NOT commit yourself unless the user asked.
