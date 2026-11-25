"""Unit tests for the make-docs dist builder.

Run from the skill directory:

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "make_docs_build_docs", ROOT / "scripts" / "build_docs.py"
)
assert SPEC and SPEC.loader
build_docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_docs)

MARKER = build_docs.GENERATED_MARKER


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class PlainHeadingTests(unittest.TestCase):
    def test_strips_inline_markdown(self) -> None:
        self.assertEqual(
            build_docs.plain_heading("**Bold** *Title* `code`"),
            "Bold Title code",
        )

    def test_keeps_identifiers_with_underscores(self) -> None:
        self.assertEqual(
            build_docs.plain_heading("user_id and snake_case"),
            "user_id and snake_case",
        )

    def test_strips_links_images_and_html(self) -> None:
        self.assertEqual(
            build_docs.plain_heading("[Link](x.md) ![Alt](y.png) <b>HTML</b>"),
            "Link Alt HTML",
        )


class FirstHeadingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)

    def test_plain_heading(self) -> None:
        path = write(self.root / "a.md", "# Hello\n\nBody\n")
        self.assertEqual(build_docs.first_heading(path), "Hello")

    def test_skips_frontmatter(self) -> None:
        path = write(
            self.root / "a.md",
            "---\ntitle: Ignored\n---\n\n# Real Heading\n",
        )
        self.assertEqual(build_docs.first_heading(path), "Real Heading")

    def test_ignores_heading_inside_fence(self) -> None:
        path = write(
            self.root / "a.md",
            "```bash\n# not a heading\n```\n\n# Real Heading\n",
        )
        self.assertEqual(build_docs.first_heading(path), "Real Heading")

    def test_strips_inline_markdown_from_label(self) -> None:
        path = write(self.root / "a.md", "# **Bold** *Title* `code`\n")
        self.assertEqual(build_docs.first_heading(path), "Bold Title code")

    def test_keeps_trailing_hash_when_not_a_closing_marker(self) -> None:
        path = write(self.root / "a.md", "# C#\n")
        self.assertEqual(build_docs.first_heading(path), "C#")

    def test_removes_closing_hashes(self) -> None:
        path = write(self.root / "a.md", "# Title ###\n")
        self.assertEqual(build_docs.first_heading(path), "Title")

    def test_returns_none_without_heading(self) -> None:
        path = write(self.root / "a.md", "No heading here.\n")
        self.assertIsNone(build_docs.first_heading(path))


class DiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.docs = pathlib.Path(self.tmp.name) / "docs"
        write(self.docs / "README.md", f"{MARKER}\n# Home\n")
        write(self.docs / "architecture.md", f"{MARKER}\n# Architecture\n")
        write(self.docs / "notes.md", "# Hand-written notes\n")
        write(self.docs / "_report.md", f"{MARKER}\n# Internal\n")

    def test_generated_only_is_default(self) -> None:
        slugs = [
            slug
            for slug, _, _ in build_docs.discover_pages(self.docs, generated_only=True)
        ]
        self.assertEqual(slugs, ["readme", "architecture"])

    def test_all_includes_unmarked_docs(self) -> None:
        slugs = [
            slug
            for slug, _, _ in build_docs.discover_pages(self.docs, generated_only=False)
        ]
        self.assertEqual(slugs, ["readme", "architecture", "notes"])

    def test_only_and_skip(self) -> None:
        slugs = [
            slug
            for slug, _, _ in build_docs.discover_pages(
                self.docs,
                generated_only=True,
                only={"architecture"},
            )
        ]
        self.assertEqual(slugs, ["architecture"])
        slugs = [
            slug
            for slug, _, _ in build_docs.discover_pages(
                self.docs,
                generated_only=True,
                skip={"readme"},
            )
        ]
        self.assertEqual(slugs, ["architecture"])

    def test_duplicate_slug_fails(self) -> None:
        write(self.docs / "api_reference.md", f"{MARKER}\n# A\n")
        write(self.docs / "api-reference.md", f"{MARKER}\n# B\n")
        with self.assertRaises(ValueError):
            build_docs.discover_pages(self.docs, generated_only=True)


class RewriteLinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = pathlib.Path(self.tmp.name)
        self.docs = self.project / "docs"
        self.output = self.docs / "dist" / "index.html"
        write(self.docs / "architecture.md", f"{MARKER}\n# Architecture\n")
        write(self.docs / "api-reference.md", f"{MARKER}\n# API\n")
        write(self.project / "README.md", "# Project\n")
        write(self.project / "AGENTS.md", "# Rules\n")
        write(self.docs / "guides" / "nested.md", "# Nested\n")
        write(self.docs / "image one.png", "not really an image\n")
        self.files = {
            "architecture": (self.docs / "architecture.md").resolve(),
            "api-reference": (self.docs / "api-reference.md").resolve(),
        }

    def rewrite(self, html_fragment: str, source: pathlib.Path, slug: str) -> str:
        return build_docs.rewrite_links(
            html_fragment,
            slug,
            source,
            self.files,
            "../../AGENTS.md",
            self.output,
            self.project,
        )

    def test_prefixes_ids_and_local_anchors(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<h1 id="overview">Overview</h1><a href="#overview">jump</a>',
            source,
            "architecture",
        )
        self.assertIn('id="architecture-overview"', result)
        self.assertIn('href="#architecture-overview"', result)

    def test_keeps_global_top_anchor(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite('<a href="#top">top</a>', source, "architecture")
        self.assertIn('href="#top"', result)

    def test_empty_anchor_is_untouched(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite('<a href="#">top</a>', source, "architecture")
        self.assertIn('href="#"', result)

    def test_cross_doc_link_becomes_anchor(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="api-reference.md#routes">api</a>',
            source,
            "architecture",
        )
        self.assertIn('href="#api-reference-routes"', result)

    def test_cross_doc_link_with_prefixed_anchor_is_not_doubled(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="api-reference.md#api-reference-routes">api</a>',
            source,
            "architecture",
        )
        self.assertIn('href="#api-reference-routes"', result)

    def test_root_readme_stays_local(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="../README.md#intro">readme</a>',
            source,
            "architecture",
        )
        self.assertIn('href="../../README.md#intro"', result)

    def test_nested_markdown_stays_local(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="guides/nested.md">nested</a>',
            source,
            "architecture",
        )
        self.assertIn('href="../guides/nested.md"', result)

    def test_percent_encoded_path_is_decoded(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="image%20one.png">image</a>',
            source,
            "architecture",
        )
        self.assertIn('href="../image one.png"', result)

    def test_absolute_repo_path_is_resolved(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="/docs/api-reference.md">api</a>',
            source,
            "architecture",
        )
        self.assertIn('href="#api-reference"', result)

    def test_agents_link_is_local(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="../AGENTS.md">rules</a>',
            source,
            "architecture",
        )
        self.assertIn('href="../../AGENTS.md"', result)

    def test_external_links_are_untouched(self) -> None:
        source = self.docs / "architecture.md"
        result = self.rewrite(
            '<a href="https://example.com">site</a>',
            source,
            "architecture",
        )
        self.assertIn('href="https://example.com"', result)

    def test_missing_link_raises(self) -> None:
        source = self.docs / "architecture.md"
        with self.assertRaises(build_docs.LinkError):
            self.rewrite('<a href="missing.md">missing</a>', source, "architecture")


class SecretScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)

    def test_detects_aws_key(self) -> None:
        path = write(self.root / "a.md", "key AKIAIOSFODNN7EXAMPLE\n")
        self.assertEqual(
            build_docs.scan_secrets([path]),
            [(path, 1, "AWS access key")],
        )

    def test_allow_marker_exempts_line(self) -> None:
        path = write(
            self.root / "a.md",
            "key AKIAIOSFODNN7EXAMPLE make-docs:allow-secret\n",
        )
        self.assertEqual(build_docs.scan_secrets([path]), [])

    def test_clean_file_has_no_hits(self) -> None:
        path = write(self.root / "a.md", "nothing sensitive here\n")
        self.assertEqual(build_docs.scan_secrets([path]), [])


if __name__ == "__main__":
    unittest.main()
