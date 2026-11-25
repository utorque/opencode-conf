---
description: Build or validate the single-page offline HTML docs at docs/dist/index.html from generated Markdown docs, using the canonical make-docs skill script. Supports --check, --all, --only/--skip, --mermaid, and --no-secret-scan.
agent: build
---

Build the docs dist with the canonical script from the `make-docs` skill. Do not copy or fork the
script into the project.

Resolve the script from the opencode config:

```bash
SKILL_DIR="${OPENCODE_CONFIG:-$HOME/.config/opencode}/skills/make-docs"
SCRIPT="${MAKE_DOCS_SCRIPT:-$SKILL_DIR/scripts/build_docs.py}"
```

`MAKE_DOCS_SCRIPT` is an escape hatch for a project that intentionally vendors the script, e.g.
`MAKE_DOCS_SCRIPT="$PWD/docs/script/build_docs.py"`; the default is always the canonical skill
script.

Run it from the current project root, passing the user's arguments through:

```bash
uv run --with 'pypandoc-binary==1.17' python "$SCRIPT" --project "$PWD" $ARGUMENTS
```

If `uv` is unavailable, use:

```bash
python3 "$SCRIPT" --project "$PWD" $ARGUMENTS
```

Behavior and flags:

- Default: publish only `docs/*.md` carrying `<!-- make-docs:generated -->`; output
  `docs/dist/index.html`; run the high-confidence secret scan.
- `--check` — validate pages, generated markers, secret scan, links, and counts without writing
  HTML or downloading Mermaid.
- `--all` — include unmarked/legacy docs too.
- `--only a,b` / `--skip c,d` — scope pages by slug.
- `--mermaid PATH` — use a local pinned Mermaid JS file when offline.
- `--no-secret-scan` — explicit escape hatch only.
- `--title TEXT` / `--lede TEXT` — branding overrides.
- `--docs-dir DIR` / `--output PATH` — non-default docs location/output.

If the script or `docs/` is missing, stop and report the exact path. If no generated docs exist,
tell the user to run `/make-docs` first (or pass `--all` for legacy docs). The command
`make-docs --dist` runs generation and this build together.

After a successful build: report the output path, doc count, Mermaid count, and size; run the
smoke checks from `skills/make-docs/references/dist-build.md`. If an image-inspection subagent is
available, delegate a screenshot check of the page; otherwise tell the user what to eyeball.

Do not commit unless the user asked.
