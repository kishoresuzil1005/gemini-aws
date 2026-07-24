# knowledge/processing/parsers/html_parser.py
"""HTML Parser implementation."""

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from typing import Any

from .base_parser import BaseParser


class HtmlParser(BaseParser):
    """Parses HTML format into a structured document representation."""

    def parse(self, raw_data: bytes, **kwargs) -> Any:
        if BeautifulSoup is None:
            raise ImportError("beautifulsoup4 is required to parse HTML documents")
            
        try:
            soup = BeautifulSoup(raw_data.decode("utf-8"), "html.parser")
            
            # As a basic intermediate representation, we extract standard structural elements
            return {
                "title": soup.title.string if soup.title else None,
                "headings": [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
                "paragraphs": [p.get_text(strip=True) for p in soup.find_all('p')],
                "links": [{"text": a.get_text(strip=True), "href": a.get('href')} for a in soup.find_all('a', href=True)],
                # Raw text can also be preserved if needed
                "raw_text": soup.get_text(separator="\n", strip=True)
            }
        except Exception as exc:
            raise ValueError(f"Failed to parse HTML: {exc}")
