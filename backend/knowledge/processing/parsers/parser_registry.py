# knowledge/processing/parsers/parser_registry.py
"""Central registry for discovering and instantiating format parsers."""

from typing import Dict, Type

from .base_parser import BaseParser
from .json_parser import JsonParser
from .yaml_parser import YamlParser
from .xml_parser import XmlParser
from .html_parser import HtmlParser
from .markdown_parser import MarkdownParser


class ParserRegistry:
    """Manages the mapping of content types / file extensions to Parsers."""

    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {
            "json": JsonParser,
            "yaml": YamlParser,
            "xml": XmlParser,
            "html": HtmlParser,
            "markdown": MarkdownParser,
            "md": MarkdownParser
        }

    def get_parser(self, format_name: str) -> BaseParser:
        """Returns an instantiated parser for the given format."""
        parser_cls = self._parsers.get(format_name.lower())
        if not parser_cls:
            raise ValueError(f"No parser registered for format: {format_name}")
        return parser_cls()
