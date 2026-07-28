# knowledge/processing/parsers/markdown_parser.py
"""Markdown Parser implementation."""

try:
    import markdown
except ImportError:
    markdown = None

from typing import Any

from .base_parser import BaseParser
# We could reuse HtmlParser if we convert Markdown to HTML first
from .html_parser import HtmlParser


class MarkdownParser(BaseParser):
    """Parses Markdown format into a structured document representation."""

    def parse(self, raw_data: bytes, **kwargs) -> Any:
        if markdown is None:
            raise ImportError("markdown package is required to parse Markdown documents")
            
        try:
            md_text = raw_data.decode("utf-8")
            
            # For intermediate representation, one strategy is to convert MD to HTML
            # and use the HtmlParser to extract standard structural elements.
            html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
            
            html_parser = HtmlParser()
            return html_parser.parse(html_content.encode("utf-8"))
        except Exception as exc:
            raise ValueError(f"Failed to parse Markdown: {exc}")
