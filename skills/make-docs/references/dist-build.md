# Dist Build — single-page HTML documentation handoff (Phase 5, optional)

Run this phase when the user asked for a distributable documentation page (e.g. "build the docs
dist", "single-page HTML docs"). It packages the Markdown docs in `docs/` into **one
self-contained, committed HTML page** at `docs/dist/index.html`.

If the implementation already exists in the target repo, verify it against this spec and rebuild;
do not create a second script or a second output path.

## Goal

Turn the project's public Markdown documentation into one page that works when opened directly
from disk (`file://`), with no server and no external assets. It must be easy to regenerate
whenever the Markdown changes.

## Locked decisions

- All public docs (`docs/*.md`) are concatenated into one long page, in a stable order.
- The project-root `README.md` is **not** embedded; links to it point to the local file, relative
  to the generated page.
- Internal working reports `docs/_*.md` are excluded.
- `AGENTS.md` is **not** embedded (it is agent-facing). Links to it point to the local file,
  relative to the generated page — never a forge (GitLab/GitHub) URL.
- Mermaid JavaScript is inlined (pinned version, SHA-256-verified, cached) so diagrams render
  offline.
- There is a navigable table of contents at the top of the page and a sticky sidebar. Every
  heading gets a visible `#` anchor link.
- The generated HTML is committed to git.
- The Markdown files remain the source of truth; no doc format changes are required. Never
  hand-edit generated HTML.
- Use `uv` for Python; do not add a docs dependency to the project's lockfile unless explicitly
  requested.

## Script

The build script lives in this skill at
[`../scripts/build_docs.py`](../scripts/build_docs.py), with the HTML/CSS/JS shell
([`../scripts/docs_template.html`](../scripts/docs_template.html)) next to it. It is
project-agnostic — run it **from the project you are documenting**:

```bash
uv run --with 'pypandoc-binary==1.17' python /path/to/skills/make-docs/scripts/build_docs.py
```

Interface:

- `--project ROOT` — project root (default: current working directory).
- `--docs-dir DIR` — docs directory (default: `<project>/docs`).
- `--output PATH` — output HTML (default: `<docs-dir>/dist/index.html`).
- `--title TEXT` / `--lede TEXT` — branding overrides; defaults derive from the project README's
  first `#` heading (else the folder name).

Dependencies:

- `pypandoc-binary==1.17` bundles Pandoc 3.9. A system Pandoc (3.1+) also works; the script
  prefers pypandoc and falls back to `pandoc`.
- First run downloads Mermaid to `~/.cache/make-docs/`; later builds are offline. Mermaid is
  pinned to `11.12.2` with SHA-256
  `d0830a6c05546e9edb8fe20a8f545f3e0dc7c4c3134d584bad9c13a99d7a71e0`.
- Build time is a few seconds. Output is a few MiB because Mermaid is inline.

## Page discovery and order

No per-project page list is maintained. The script auto-discovers `docs/*.md`:

1. Files beginning with `_` are internal working files — excluded.
2. `README.md` or `index.md` (docs index) comes first.
3. Remaining pages follow alphabetically by filename.
4. Slug = filename stem; nav label = the page's first `#` heading, else a prettified stem.

Because discovery is automatic, every non-`_` Markdown file in `docs/` is part of the published
page — there is no list to fall out of sync.

## Build pipeline (what the script does)

For each page:

1. Render with Pandoc GFM:
   `pandoc -f gfm -t html5 --wrap=none --highlight-style=tango`.
2. Prefix every generated `id` with `<slug>-` so headings like `Overview` repeated in many docs
   do not collide.
3. Rewrite in-page links (in the rendered HTML, **not** the Markdown) so code blocks containing
   links are never corrupted:
   - `href="#foo"` -> `href="#<slug>-foo"`.
   - `href="foo.md"` -> `href="#foo"`.
   - `href="foo.md#bar"` -> `href="#foo-bar"`.
   - `href="../README.md"` -> the local project-root `README.md`, relative to the generated page,
     plus `#bar` if present. The root README is not a page section.
   - `href="AGENTS.md"` and `href="../AGENTS.md"` -> relative local path from the output file to
     the project-root `AGENTS.md`.
   - External `http(s)`/`mailto` links are left alone.
   - Any other relative link: if it resolves to an existing repo file, rewrite it to a path
     relative to the output page; if it resolves to the output HTML itself, use `#top`; otherwise
     **fail the build**.
4. Collect H1/H2 headings for navigation before adding `#` anchor links. Exclude H2s whose
   unprefixed slug is `table-of-contents`, `related-docs`, or `last-updated` from both the top
   contents and sidebar.
5. Add a `#` anchor link after every H1–H4:
   `<a class="anchor" href="#ID" aria-label="Link to this section">#</a>`.
6. Wrap each `<table>` in `<div class="table-wrap">…</div>` so wide tables scroll instead of
   escaping the content column.
7. Wrap each page in `<section class="doc" id="SLUG" data-doc="SLUG">…</section>`.

Then assemble into the template shell: `{{HIGHLIGHT_CSS}}` (Pandoc's highlighting CSS from a tiny
standalone render), `{{CONTENTS}}` (top two-column contents), `{{SIDEBAR}}` (same tree for the
sticky sidebar), `{{BODY}}` (all sections in order), `{{MERMAID_JS}}` (pinned inline build),
`{{TITLE}}`/`{{PROJECT_NAME}}`/`{{LEDE}}` (branding), `{{AGENTS_NOTE}}` (local AGENTS.md link, or
omitted when the file does not exist), `{{BUILD_DATE}}` (ISO date).

The template provides the page header, footer, responsive CSS, print CSS, sidebar scrollspy,
back-to-top link, Mermaid initialization, and the click-to-enlarge diagram overlay.

## Front-end behavior

- Sticky left sidebar with doc links and H2 links; scrollspy highlights the current section and
  scrolls the active link into view.
- Top `Contents` block at the start of the page, two columns on desktop and one on mobile.
- Every heading has a subtle `#` link; hover makes it prominent.
- Mermaid diagrams render inline at content width; wide diagrams can be clicked to open a
  full-size overlay. The overlay supports drag/scroll/arrow panning and closes with the X button
  or `Esc`.
- Tables use responsive wrappers; long code tokens wrap rather than clipping.
- Print CSS hides the sidebar/overlay and starts each doc on a new page.
- Mobile stacks the layout, limits the sidebar height, and makes the contents one column.

## Required validation

The build must fail, not silently write, when:

- the docs directory is missing or contains no public Markdown;
- a relative link cannot be resolved;
- any generated `href="#..."` has no matching `id`;
- the number of doc sections differs from the discovered page count;
- the rendered Mermaid block count differs from the source `mermaid` fence count;
- a template marker is missing.

After a successful build, smoke-check:

```bash
test -f docs/dist/index.html
grep -c '<section class="doc"' docs/dist/index.html     # == number of public docs
grep -c '<pre class="mermaid">' docs/dist/index.html    # == number of ```mermaid fences
```

Then open the page in a browser and check:

1. Top `Contents` block is present and links jump correctly.
2. Sidebar highlights the active section and can reach the last doc.
3. Every doc H1 and H2 has a `#` anchor.
4. Tables fit or scroll; no page-level horizontal overflow.
5. Mermaid diagrams render; click one to verify the overlay and close.
6. Mobile width (~390 px) stacks cleanly and the contents is one column.
7. Browser console has no errors.

A quick headless check with Chrome/Puppeteer is fine; do not add it as a repo dependency. In a
text-only harness, delegate the visual check to an image-inspection subagent on a screenshot, or
ask the user to eyeball the page.

## README requirement

The target project's README should document the build so future agents can rebuild without this
skill. A `## Documentation build` section should state:

- output path `docs/dist/index.html`;
- the exact build command;
- the generated HTML is committed and must be rebuilt with any docs change;
- never hand-edit the generated HTML;
- `docs/_*.md` are excluded;
- `AGENTS.md` links stay local; the root `README.md` is not embedded;
- Mermaid is pinned/cached, first build needs network;
- docs content must stay synthetic/PII-free (no real secrets, no real user data).

## Change loop

When editing documentation in the target project:

```bash
# 1. Edit Markdown
$EDITOR docs/*.md README.md

# 2. Rebuild the committed page
uv run --with 'pypandoc-binary==1.17' python /path/to/skills/make-docs/scripts/build_docs.py

# 3. Inspect / smoke-test
#    open docs/dist/index.html

# 4. Commit Markdown + generated HTML together
git add docs/*.md README.md docs/dist/index.html
git commit -m "docs: update single-page HTML"
```

## Pitfalls

- Do not run Pandoc on all docs in one invocation. Duplicate headings across docs (`Overview`,
  `Related Docs`, `Last Updated`) create ambiguous IDs and relative `.md` links break.
- Do not rewrite Markdown links before Pandoc. Rewriting the rendered HTML `href` values avoids
  corrupting link-like text inside code blocks.
- Do not include `AGENTS.md` as a page section; it is agent-facing. Link to the local file only.
- Do not use forge (GitLab/GitHub) URLs for `AGENTS.md`; keep local links.
- Do not add images without updating the build to inline them; the page must stay self-contained.
- Do not commit `.env`, certs, credentials, or real user data via the docs.
- Do not change Mermaid/Pandoc versions without updating the checksum/version in the script and
  this file.
- Pandoc 3.9 prints a deprecation warning for `--highlight-style`; the build filters only that
  known warning. Do not silence other warnings.
- The sidebar/contents intentionally skip per-doc TOCs, `Related Docs`, and `Last Updated`
  headings; keep that behavior to avoid a noisy nav.

## Acceptance summary

Done when:

- `docs/dist/index.html` exists, is committed, and opens offline;
- the page starts with a header, the two-column `Contents`, then all public docs in discovery
  order;
- all Mermaid diagrams render without external requests;
- all in-page links resolve;
- the sidebar, `#` anchors, tables, print styles, and mobile layout work;
- the target README documents the command and rules (when the project keeps one);
- this file still matches the script's actual behavior.
