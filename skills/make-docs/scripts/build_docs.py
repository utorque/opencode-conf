#!/usr/bin/env python3
"""Build a single-page HTML documentation set from a project's Markdown docs.

Run from the project you are documenting (any project, no install needed):

    uv run --with 'pypandoc-binary==1.17' python /path/to/this/build_docs.py

Defaults:
    --docs-dir  ./docs
    --output    ./docs/dist/index.html

Only docs carrying the ``<!-- make-docs:generated -->`` marker are published by
default. Pass ``--all`` to include hand-written or legacy docs too.

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
import functools
import hashlib
import html
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

if sys.version_info < (3, 10):
    sys.exit("build_docs.py requires Python 3.10 or newer")

SCRIPT = pathlib.Path(__file__).resolve()
TEMPLATE = SCRIPT.parent / "docs_template.html"

GENERATED_MARKER = "<!-- make-docs:generated -->"
ALLOW_SECRET = "make-docs:allow-secret"

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

# Anchors that stay page-global instead of being scoped to one document.
GLOBAL_ANCHORS = {"top", "contents-heading", "page-title"}

# High-confidence secret shapes. Inline ``make-docs:allow-secret`` exempts a
# line, e.g. for documentation examples.
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    (
        "GitHub token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})\b"),
    ),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Stripe live key", re.compile(r"\bsk_live_[0-9A-Za-z]{20,}\b")),
    (
        "OpenAI-style key",
        re.compile(r"\bsk-(?:proj-|live-)?[A-Za-z0-9_-]{32,}\b"),
    ),
)


class LinkError(Exception):
    """Raised when a relative link cannot be resolved."""


def plain_heading(text: str) -> str:
    """Strip inline Markdown so toc/sidebar labels are readable text."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"`+([^`]*)`+", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"~~([^~]+)~~", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", text)
    return html.unescape(text).strip()


def first_heading(md_path: pathlib.Path) -> str | None:
    """Return the first ``# `` heading text, skipping frontmatter and fences."""
    lines = md_path.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                lines = lines[index + 1 :]
                break

    fence: str | None = None
    for line in lines:
        stripped = line.lstrip()
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            continue
        opener = re.match(r"^(```+|~~~+)", stripped)
        if opener:
            fence = opener.group(1)[:3]
            continue
        match = re.match(r"^\s{0,3}#\s+(.+?)(?:\s+#+)?\s*$", line)
        if match:
            return plain_heading(match.group(1))
    return None


def has_generated_marker(md_path: pathlib.Path) -> bool:
    """True when the doc carries the make-docs generated-file marker."""
    return GENERATED_MARKER in md_path.read_text(encoding="utf-8")[:2000]


def project_name(project: pathlib.Path) -> str:
    """Derive a display name: README H1, else the project folder name."""
    for candidate in (project / "README.md", project / "readme.md"):
        if candidate.is_file():
            heading = first_heading(candidate)
            if heading:
                return heading
    return project.name or "Project"


def pretty_slug(slug: str) -> str:
    return " ".join(
        part.capitalize() for part in re.split(r"[-_]+", slug) if part
    )


def normalize_page_set(value: str | None) -> set[str] | None:
    if not value:
        return None
    pages = {
        re.sub(r"\.md$", "", part.strip().lower()).replace("_", "-")
        for part in value.split(",")
        if part.strip()
    }
    return pages or None


def discover_pages(
    docs_dir: pathlib.Path,
    *,
    generated_only: bool = True,
    only: set[str] | None = None,
    skip: set[str] | None = None,
) -> list[tuple[str, pathlib.Path, str]]:
    """Auto-discover public pages: README/index first, then alphabetical."""
    files = sorted(
        (p for p in docs_dir.glob("*.md") if not p.name.startswith("_")),
        key=lambda p: (
            0 if p.name.lower() in ("readme.md", "index.md") else 1,
            p.name.lower(),
        ),
    )
    pages: list[tuple[str, pathlib.Path, str]] = []
    seen: dict[str, pathlib.Path] = {}
    for path in files:
        slug = path.stem.lower().replace("_", "-")
        if only is not None and slug not in only:
            continue
        if skip is not None and slug in skip:
            continue
        if generated_only and not has_generated_marker(path):
            continue
        if slug in seen:
            raise ValueError(
                f"duplicate page slug {slug!r}: {seen[slug]} and {path}"
            )
        seen[slug] = path
        label = first_heading(path) or pretty_slug(slug)
        pages.append((slug, path, label))
    return pages


@functools.lru_cache(maxsize=1)
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


def mermaid_js(explicit: pathlib.Path | None = None) -> str:
    """Return a pinned, checksum-verified Mermaid build from a local source."""
    if explicit is not None:
        source = explicit.expanduser().resolve()
        if not source.is_file():
            sys.exit(f"Mermaid file not found: {source}")
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != MERMAID_SHA256:
            sys.exit(f"Mermaid SHA-256 mismatch: {source}")
        return data.decode("utf-8")

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
            f"Place the pinned file at {path} and rerun, or pass --mermaid PATH."
        )
    if hashlib.sha256(data).hexdigest() != MERMAID_SHA256:
        sys.exit("Mermaid download failed the SHA-256 check")

    # Atomic cache write: concurrent builds must not read a partial file.
    temp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    try:
        temp.write_bytes(data)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()
    return data.decode("utf-8")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).strip()


def rewrite_links(
    frag: str,
    slug: str,
    source: pathlib.Path,
    files: dict[str, pathlib.Path],
    agents_link: str | None,
    output: pathlib.Path,
    project: pathlib.Path,
) -> str:
    """Make heading IDs page-local and rewrite links for the single page."""
    # 1. Make every id unique to this document.
    frag = re.sub(r'id="([^"]+)"', lambda m: f'id="{slug}-{m.group(1)}"', frag)

    # 2. In-page links are local to this document now.
    def local_anchor(m: re.Match[str]) -> str:
        anchor = urllib.parse.unquote(m.group(1))
        if not anchor or anchor in GLOBAL_ANCHORS or anchor.startswith(f"{slug}-"):
            return m.group(0)
        return f'href="#{slug}-{anchor}"'

    frag = re.sub(r'href="#([^"]+)"', local_anchor, frag)

    # 3. Cross-file links become page anchors, or local repo files for docs
    #    that deliberately stay outside the published page (AGENTS.md, root
    #    README, nested docs, non-Markdown assets).
    unresolved: list[str] = []

    def cross_file(m: re.Match[str]) -> str:
        raw = html.unescape(m.group(1))
        if (
            raw.startswith("#")
            or raw.startswith("//")
            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", raw)
        ):
            return m.group(0)

        path_part, _, anchor_part = raw.partition("#")
        path = urllib.parse.unquote(path_part).split("?", 1)[0]
        anchor = urllib.parse.unquote(anchor_part)
        if not path:
            return m.group(0)

        if path.startswith("/"):
            candidate = (project / path.lstrip("/")).resolve()
        else:
            candidate = (source.parent / path).resolve()

        if candidate == output.resolve():
            return 'href="#top"'

        if candidate == (project / "AGENTS.md").resolve():
            if agents_link is None:
                unresolved.append(f"{slug}: {raw} (AGENTS.md not found)")
                return m.group(0)
            return f'href="{agents_link}"'

        target_slug = next(
            (
                page_slug
                for page_slug, page_path in files.items()
                if page_path == candidate
            ),
            None,
        )
        if target_slug is not None:
            if not anchor:
                return f'href="#{target_slug}"'
            if anchor.startswith(f"{target_slug}-"):
                return f'href="#{anchor}"'
            return f'href="#{target_slug}-{anchor}"'

        # Existing files that are not embedded stay local links instead of
        # failing the build. This covers the root README, nested docs, images,
        # and other repo assets.
        if candidate.is_file():
            rel = os.path.relpath(candidate, output.parent).replace(os.sep, "/")
            suffix = f"#{anchor}" if anchor else ""
            return f'href="{rel}{suffix}"'

        unresolved.append(f"{slug}: {raw}")
        return m.group(0)

    frag = re.sub(r'href="([^"]+)"', cross_file, frag)
    if unresolved:
        raise LinkError("unresolved relative links:\n  " + "\n  ".join(unresolved))
    return frag


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
        check=False,
    )
    if proc.returncode != 0:
        sys.exit(f"pandoc failed for {source}:\n{proc.stderr.strip()}")
    warnings = [
        line
        for line in proc.stderr.splitlines()
        if line.strip() and "Deprecated: --highlight-style" not in line
    ]
    if warnings:
        print(f"pandoc [{slug}]: " + "\n".join(warnings))
    frag = rewrite_links(
        proc.stdout, slug, source, files, agents_link, output, project
    )

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


def nav_html(
    pages: list[tuple[str, str, list[tuple[int, str, str]]]], *, contents: bool
) -> str:
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


def scan_secrets(paths: list[pathlib.Path]) -> list[tuple[pathlib.Path, int, str]]:
    """Return high-confidence secret hits in the selected docs."""
    hits: list[tuple[pathlib.Path, int, str]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if ALLOW_SECRET in line:
                continue
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append((path, lineno, name))
    return hits


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
    parser.add_argument(
        "--all",
        action="store_true",
        help=f"include docs without the {GENERATED_MARKER} marker",
    )
    parser.add_argument(
        "--only",
        default=None,
        help="comma-separated page slugs to include",
    )
    parser.add_argument(
        "--skip",
        default=None,
        help="comma-separated page slugs to exclude",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate pages and links without writing the HTML file",
    )
    parser.add_argument(
        "--mermaid",
        type=pathlib.Path,
        default=None,
        help="local Mermaid JS file to use instead of the cache/CDN",
    )
    parser.add_argument(
        "--no-secret-scan",
        action="store_true",
        help="skip the high-confidence secret scan",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    docs_dir = (args.docs_dir or project / "docs").resolve()
    output = (args.output or docs_dir / "dist" / "index.html").resolve()

    if not docs_dir.is_dir():
        sys.exit(f"docs directory not found: {docs_dir}")
    if not TEMPLATE.is_file():
        sys.exit(f"template not found next to the script: {TEMPLATE}")

    try:
        pages = discover_pages(
            docs_dir,
            generated_only=not args.all,
            only=normalize_page_set(args.only),
            skip=normalize_page_set(args.skip),
        )
    except ValueError as exc:
        sys.exit(str(exc))
    if not pages:
        hint = (
            "No docs found."
            if args.all
            else f"No docs with {GENERATED_MARKER} found. "
            "Run /make-docs first, or pass --all for legacy hand-written docs."
        )
        sys.exit(f"{hint}\nDocs directory: {docs_dir}")

    if not args.no_secret_scan:
        secret_hits = scan_secrets([path for _, path, _ in pages])
        if secret_hits:
            details = "\n".join(
                f"  {path}:{lineno}: possible {name}"
                for path, lineno, name in secret_hits
            )
            sys.exit(
                "secret scan failed; remove the value, add a safe example, or "
                f"exempt the line with {ALLOW_SECRET}:\n{details}"
            )

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
        try:
            fragment, heads = render(
                text, slug, path, files, agents_link, output, project
            )
        except LinkError as exc:
            sys.exit(str(exc))
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
        check=False,
    )
    if sample.returncode != 0:
        sys.exit(f"pandoc failed to render highlighting CSS:\n{sample.stderr.strip()}")
    highlight_css = re.search(r"<style>(.*?)</style>", sample.stdout, re.S)
    if highlight_css is None:
        sys.exit("pandoc output is missing the highlighting style block")

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
        "{{HIGHLIGHT_CSS}}": highlight_css.group(1),
        "{{CONTENTS}}": contents,
        "{{SIDEBAR}}": sidebar,
        "{{BODY}}": body,
        # --check validates links/markers without downloading Mermaid.
        "{{MERMAID_JS}}": "" if args.check else mermaid_js(args.mermaid),
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
        sys.exit("broken in-page links:\n  " + "\n  ".join(missing))
    if page.count('<section class="doc"') != len(pages):
        sys.exit("not every page produced a document section")
    if page.count('<pre class="mermaid">') != mermaid_blocks:
        sys.exit("Mermaid block count changed during conversion")

    if args.check:
        print(
            f"check ok: {len(pages)} docs, {mermaid_blocks} Mermaid diagrams, "
            f"{len(hrefs)} in-page links, no write"
        )
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(f"{output.name}.tmp-{os.getpid()}")
    try:
        temp.write_text(page, encoding="utf-8")
        os.replace(temp, output)
    finally:
        if temp.exists():
            temp.unlink()

    table_count = page.count('<div class="table-wrap">')
    print(
        f"wrote {output} "
        f"({output.stat().st_size / 1024 / 1024:.2f} MiB, "
        f"{len(pages)} docs, {table_count} tables, "
        f"{mermaid_blocks} Mermaid diagrams, {len(hrefs)} in-page links)"
    )


if __name__ == "__main__":
    main()
