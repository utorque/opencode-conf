#!/usr/bin/env python3
"""Build a single-page HTML documentation set from a project's Markdown docs.

Run from the project you are documenting (any project, no install needed):

    uv run --with 'pypandoc-binary==1.17' python /path/to/this/build_docs.py

Defaults:
    --docs-dir  ./docs
    --output    ./docs/dist/index.html

The Markdown files are the source of truth. This script renders each public
page with Pandoc, makes heading IDs unique per document, rewrites links to
in-page anchors, and assembles one self-contained HTML file (meant to be
committed to the repository).

Internal ``docs/_*.md`` reports are deliberately excluded. Pages are
auto-discovered: ``README.md``/``index.md`` first, then the rest
alphabetically. No per-project configuration is required; pass ``--title``
and ``--lede`` to override the branding derived from the project README.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

SCRIPT = pathlib.Path(__file__).resolve()
TEMPLATE = SCRIPT.parent / "docs_template.html"

MERMAID_VERSION = "11.12.2"
MERMAID_URL = (
    f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}"
    "/dist/mermaid.min.js"
)
MERMAID_SHA256 = (
    "d0830a6c05546e9edb8fe20a8f545f3e0dc7c4c3134d584bad9c13a99d7a71e0"
)

# Headings that are redundant with the generated navigation.
SKIP_NAV = {"table-of-contents", "related-docs", "last-updated"}


def first_heading(md_path: pathlib.Path) -> str | None:
    """Return the first ``# `` heading text, skipping YAML frontmatter."""
    text = md_path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1)
    return None


def project_name(project: pathlib.Path) -> str:
    """Derive a display name: README H1, else the project folder name."""
    for candidate in (project / "README.md", project / "readme.md"):
        if candidate.is_file():
            heading = first_heading(candidate)
            if heading:
                return heading
    return project.name or "Project"


def pretty_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").strip().capitalize()


def discover_pages(docs_dir: pathlib.Path) -> list[tuple[str, pathlib.Path, str]]:
    """Auto-discover public pages: README/index first, then alphabetical."""
    files = sorted(
        (p for p in docs_dir.glob("*.md") if not p.name.startswith("_")),
        key=lambda p: (
            0 if p.name.lower() in ("readme.md", "index.md") else 1,
            p.name.lower(),
        ),
    )
    pages = []
    for path in files:
        slug = path.stem.lower().replace("_", "-")
        label = first_heading(path) or pretty_slug(slug)
        pages.append((slug, path, label))
    return pages


def pandoc_path() -> str:
    """Prefer the Pandoc bundled with pypandoc; fall back to PATH."""
    try:
        import pypandoc  # type: ignore

        return pypandoc.get_pandoc_path()
    except Exception:
        found = shutil.which("pandoc")
        if found:
            return found
    sys.exit(
        "Pandoc not found. Run with:\n"
        f"  uv run --with 'pypandoc-binary==1.17' python {SCRIPT}"
    )


def mermaid_js() -> str:
    """Return a pinned, checksum-verified Mermaid build from the local cache."""
    cache = pathlib.Path(
        os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache")
    ) / "make-docs"
    path = cache / f"mermaid-{MERMAID_VERSION}.min.js"
    if path.exists():
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() == MERMAID_SHA256:
            return data.decode("utf-8")
        path.unlink()

    cache.mkdir(parents=True, exist_ok=True)
    print(f"downloading Mermaid {MERMAID_VERSION} to {path} ...")
    try:
        with urllib.request.urlopen(MERMAID_URL, timeout=60) as response:
            data = response.read()
    except Exception as exc:
        sys.exit(
            f"could not download Mermaid: {exc}\n"
            f"Place the pinned file at {path} and rerun."
        )
    if hashlib.sha256(data).hexdigest() != MERMAID_SHA256:
        sys.exit("Mermaid download failed the SHA-256 check")
    path.write_bytes(data)
    return data.decode("utf-8")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).strip()


def render(
    md: str,
    slug: str,
    source: pathlib.Path,
    files: dict[str, pathlib.Path],
    agents_link: str | None,
    output: pathlib.Path,
    project: pathlib.Path,
) -> tuple[str, list[tuple[int, str, str]]]:
    """Render one Markdown file and make its IDs/links page-local."""
    proc = subprocess.run(
        [
            pandoc_path(),
            "-f",
            "gfm",
            "-t",
            "html5",
            "--wrap=none",
            "--highlight-style=tango",
        ],
        input=md,
        text=True,
        capture_output=True,
        check=True,
    )
    warnings = [
        line
        for line in proc.stderr.splitlines()
        if line.strip() and 'Deprecated: --highlight-style' not in line
    ]
    if warnings:
        print(f"pandoc [{slug}]: " + "\n".join(warnings))
    frag = proc.stdout

    # 1. Make every id unique to this document.
    frag = re.sub(r'id="([^"]+)"', lambda m: f'id="{slug}-{m.group(1)}"', frag)

    # 2. In-page links are local to this document now.
    frag = re.sub(
        r'href="#([^"]+)"',
        lambda m: m.group(0)
        if m.group(1).startswith(f"{slug}-")
        else f'href="#{slug}-{m.group(1)}"',
        frag,
    )

    # 3. Cross-file links become page anchors, or local repo files for docs
    #    that deliberately stay outside the published page (AGENTS.md, README.md).
    unresolved: list[str] = []

    def cross_file(m: re.Match[str]) -> str:
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        path, _, anchor = target.partition("#")
        candidate = (source.parent / path).resolve()
        if not path.endswith(".md"):
            if candidate == output:
                return 'href="#top"'
            if candidate.is_file():
                rel = os.path.relpath(candidate, output.parent).replace(os.sep, "/")
                suffix = f"#{anchor}" if anchor else ""
                return f'href="{rel}{suffix}"'
            unresolved.append(f"{slug}: {target}")
            return m.group(0)
        if candidate == (project / "AGENTS.md").resolve():
            if agents_link is None:
                unresolved.append(f"{slug}: {target} (AGENTS.md not found)")
            return f'href="{agents_link}"'
        target_slug = next(
            (
                page_slug
                for page_slug, page_path in files.items()
                if page_path == candidate
            ),
            None,
        )
        if target_slug is None:
            # The project-root README is not embedded; link to the local file.
            if candidate == (project / "README.md").resolve() or candidate == (
                project / "readme.md"
            ).resolve():
                rel = os.path.relpath(candidate, output.parent).replace(os.sep, "/")
                suffix = f"#{anchor}" if anchor else ""
                return f'href="{rel}{suffix}"'
            unresolved.append(f"{slug}: {target}")
            return m.group(0)
        suffix = f"-{anchor}" if anchor else ""
        return f'href="#{target_slug}{suffix}"'

    frag = re.sub(r'href="([^"]+)"', cross_file, frag)
    if unresolved:
        sys.exit("unresolved relative links:\n  " + "\n  ".join(unresolved))

    # 4. Collect headings for the top contents block and the sidebar.
    heads: list[tuple[int, str, str]] = []
    for match in re.finditer(
        r'<h([12]) id="([^"]+)">(.*?)</h\1>', frag, flags=re.S
    ):
        heads.append(
            (int(match.group(1)), match.group(2), clean_text(match.group(3)))
        )

    # 5. Give every heading a visible "#" anchor link.
    def heading_anchor(match: re.Match[str]) -> str:
        level, hid, inner = match.groups()
        return (
            f'<h{level} id="{hid}">{inner} '
            f'<a class="anchor" href="#{hid}" '
            f'aria-label="Link to this section">#</a></h{level}>'
        )

    frag = re.sub(
        r'<h([1-4]) id="([^"]+)">(.*?)</h\1>',
        heading_anchor,
        frag,
        flags=re.S,
    )

    # 6. Responsive tables need a scroll container in the static page.
    frag = re.sub(
        r'<table(\s[^>]*)?>',
        lambda m: f'<div class="table-wrap"><table{m.group(1) or ""}>',
        frag,
    )
    frag = frag.replace("</table>", "</table></div>")

    return (
        f'<section class="doc" id="{slug}" data-doc="{slug}">\n{frag}\n</section>',
        heads,
    )


def nav_html(pages: list[tuple[str, str, list[tuple[int, str, str]]]], *, contents: bool) -> str:
    """Build the contents block or the sidebar tree."""
    items: list[str] = []
    for slug, label, heads in pages:
        subheads = [
            (hid, text)
            for level, hid, text in heads
            if level == 2 and hid.removeprefix(f"{slug}-") not in SKIP_NAV
        ]
        if contents:
            items.append(
                f'<li class="toc-doc"><a href="#{slug}">{html.escape(label)}</a>'
            )
            if subheads:
                items.append("<ul>")
                items.extend(
                    f'<li class="toc-sub"><a href="#{hid}">{html.escape(text)}</a></li>'
                    for hid, text in subheads
                )
                items.append("</ul>")
            items.append("</li>")
        else:
            items.append(
                f'<li class="nav-doc"><a href="#{slug}">{html.escape(label)}</a>'
            )
            if subheads:
                items.append("<ul>")
                items.extend(
                    f'<li><a href="#{hid}">{html.escape(text)}</a></li>'
                    for hid, text in subheads
                )
                items.append("</ul>")
            items.append("</li>")

    if contents:
        return (
            '<nav id="contents" aria-labelledby="contents-heading">'
            '<h2 id="contents-heading">Contents <a class="anchor" href="#contents-heading" aria-label="Link to this section">#</a></h2>'
            '<div class="contents-grid"><ol>'
            + "".join(items)
            + "</ol></div></nav>"
        )
    return "<ul>" + "".join(items) + "</ul>"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help="project root (default: current working directory)",
    )
    parser.add_argument(
        "--docs-dir",
        type=pathlib.Path,
        default=None,
        help="docs directory (default: <project>/docs)",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=None,
        help="output HTML path (default: <docs-dir>/dist/index.html)",
    )
    parser.add_argument("--title", default=None, help="page title override")
    parser.add_argument(
        "--lede",
        default=None,
        help="one-line description shown in the page header",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    docs_dir = (args.docs_dir or project / "docs").resolve()
    output = (args.output or docs_dir / "dist" / "index.html").resolve()

    if not docs_dir.is_dir():
        sys.exit(f"docs directory not found: {docs_dir}")
    if not TEMPLATE.is_file():
        sys.exit(f"template not found next to the script: {TEMPLATE}")

    pages = discover_pages(docs_dir)
    if not pages:
        sys.exit(f"no public Markdown pages found in {docs_dir}")
    files = {slug: path.resolve() for slug, path, _ in pages}

    # AGENTS.md stays agent-facing: link to the local file, never embed it.
    agents_link: str | None = None
    if (project / "AGENTS.md").is_file():
        agents_link = pathlib.PurePosixPath(
            os.path.relpath(project / "AGENTS.md", output.parent).replace(os.sep, "/")
        ).as_posix()

    name = project_name(project)
    title = args.title or f"{name} — Documentation"
    lede = args.lede or "All project documentation on one page."

    rendered: dict[str, str] = {}
    metadata: list[tuple[str, str, list[tuple[int, str, str]]]] = []
    mermaid_blocks = 0
    for slug, path, label in pages:
        text = path.read_text(encoding="utf-8")
        mermaid_blocks += len(re.findall(r"^```mermaid\b", text, flags=re.M))
        fragment, heads = render(text, slug, path, files, agents_link, output, project)
        rendered[slug] = fragment
        metadata.append((slug, label, heads))

    body = "\n".join(rendered[slug] for slug, _, _ in pages)
    contents = nav_html(metadata, contents=True)
    sidebar = nav_html(metadata, contents=False)

    # Pandoc's generated Pygments/skylighting CSS keeps code blocks readable.
    sample = subprocess.run(
        [
            pandoc_path(),
            "-f",
            "gfm",
            "-t",
            "html5",
            "--standalone",
            "--highlight-style=tango",
        ],
        input="```python\nx = 1\n```\n",
        text=True,
        capture_output=True,
        check=True,
    )
    highlight_css = re.search(r"<style>(.*?)</style>", sample.stdout, re.S).group(1)

    agents_note = (
        f'Internal <code>docs/_*.md</code> reports are excluded. '
        f'<a href="{agents_link}">AGENTS.md</a> (local) contains repo rules for agents.'
        if agents_link
        else "Internal <code>docs/_*.md</code> reports are excluded."
    )

    template = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{TITLE}}": html.escape(title),
        "{{PROJECT_NAME}}": html.escape(name),
        "{{LEDE}}": html.escape(lede),
        "{{BUILD_DATE}}": dt.date.today().isoformat(),
        "{{HIGHLIGHT_CSS}}": highlight_css,
        "{{CONTENTS}}": contents,
        "{{SIDEBAR}}": sidebar,
        "{{BODY}}": body,
        "{{MERMAID_JS}}": mermaid_js(),
        "{{AGENTS_NOTE}}": agents_note,
    }
    for marker in replacements:
        if marker not in template:
            sys.exit(f"template is missing {marker}")
    page = template
    for marker, value in replacements.items():
        page = page.replace(marker, value)

    # Fail before writing if any in-page link is broken.
    ids = set(re.findall(r'id="([^"]+)"', page))
    hrefs = re.findall(r'href="#([^"]+)"', page)
    missing = sorted({href for href in hrefs if href not in ids})
    if missing:
        sys.exit(
            "broken in-page links:\n  " + "\n  ".join(missing)
        )
    if page.count('<section class="doc"') != len(pages):
        sys.exit("not every page produced a document section")
    if page.count('<pre class="mermaid">') != mermaid_blocks:
        sys.exit("Mermaid block count changed during conversion")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    table_count = page.count('<div class="table-wrap">')
    print(
        f"wrote {output} "
        f"({output.stat().st_size / 1024 / 1024:.2f} MiB, "
        f"{len(pages)} docs, {table_count} tables, "
        f"{mermaid_blocks} Mermaid diagrams, {len(hrefs)} in-page links)"
    )


if __name__ == "__main__":
    main()
