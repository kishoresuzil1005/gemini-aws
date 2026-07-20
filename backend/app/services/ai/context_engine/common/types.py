"""Shared type aliases and typed dicts used across the Context Engine."""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class ProviderMetadataDict(TypedDict, total=False):
    """Shape of the ``metadata`` block inside every provider response."""
    provider: str
    version: str
    generated_at: str
    cache_ttl: Optional[int]
    status: str          # "ok" | "not_implemented" | "error"
    enabled: bool
    execution_time_ms: float
    source: str          # e.g. "neo4j", "postgres", "cloudwatch"


class StandardProviderResponse(TypedDict):
    """Standardized provider response.  Every provider **must** return this shape."""
    metadata: ProviderMetadataDict
    data: Dict[str, Any]


ProviderPayloads = Dict[str, StandardProviderResponse]
"""Mapping from provider name to its standardized response."""
