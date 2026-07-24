# knowledge/search/search_models.py
"""Data models for the Search Engine."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Highlight(BaseModel):
    field: str
    snippet: str

class SearchResultItem(BaseModel):
    id: str
    type: str  # resource|relationship|rule|doc|snapshot|version
    score: float
    payload: Dict[str, Any]
    highlights: List[Highlight] = []

class SearchResult(BaseModel):
    total: int
    took_ms: int
    items: List[SearchResultItem]
    facets: Optional[Dict[str, Dict[str, int]]] = None  # e.g., tag -> count
