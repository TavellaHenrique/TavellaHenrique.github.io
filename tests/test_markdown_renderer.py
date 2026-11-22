"""Tests for Markdown-to-HTML conversion."""

from app.services.markdown_renderer import MarkdownRenderer


def test_renderer_converts_commonmark_content() -> None:
    renderer = MarkdownRenderer()

    html = renderer.render("# Title\n\n- First\n- Second\n\n`inline code`")

    assert "<h1>Title</h1>" in html
    assert "<li>First</li>" in html
    assert "<code>inline code</code>" in html


def test_renderer_does_not_allow_raw_html() -> None:
    renderer = MarkdownRenderer()

    html = renderer.render("<script>alert('x')</script>")

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
