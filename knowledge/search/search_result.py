# knowledge/search/search_result.py
"""Result wrapper for the Search Engine.

The ``SearchResult`` model defined in ``search_models.py`` already captures the
core data structure (total, took_ms, items, facets).  This module provides a
lightweight helper that can be instantiated from raw dictionaries and that
adds a convenient ``to_dict`` method for serialisation.
"""

from .search_models import SearchResult

class SearchResultWrapper(SearchResult):
    """Extends ``SearchResult`` with utility methods."""

    def to_dict(self) -> dict:
        """Return a JSON‑serialisable ``dict`` of the result."""
        return self.dict()
