"""Render Markdown content to HTML using markdown-it-py."""

from markdown_it import MarkdownIt


class MarkdownRenderer:
    """Convert Markdown text into HTML with HTML tags disabled by default."""

    def __init__(self) -> None:
        # CommonMark provides predictable Markdown syntax without enabling raw HTML.
        self._parser = MarkdownIt("commonmark", {"html": False, "linkify": False})

    def render(self, markdown_text: str) -> str:
        """Render a Markdown string into HTML."""
        return self._parser.render(markdown_text)
