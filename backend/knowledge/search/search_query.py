# knowledge/search/search_query.py
"""Definition of the search query object used across the Search Engine."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SearchQuery(BaseModel):
    """Encapsulates common search parameters.

    Attributes
    ----------
    limit: int
        Maximum number of results to return (default 50).
    offset: int
        Pagination offset (default 0).
    filters: Optional[Dict[str, Any]]
        Key‑value filters for exact matches, e.g. {"provider": "aws"}.
    sort_by: Optional[str]
        Field name to sort on. Prefix with '-' for descending.
    facets: Optional[list[str]]
        List of fields to compute facet counts on.
    """

    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    facets: Optional[list[str]] = None
