# knowledge/catalog/catalog_metadata.py
"""Metadata structures tracking the state of the catalog."""

from pydantic import BaseModel, Field
from datetime import datetime

class CatalogMetadata(BaseModel):
    """Metadata tracking catalog versioning, size, and timestamps."""
    catalog_version: str = "1.0.0"
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    total_resources: int = 0
    total_providers: int = 0
    total_services: int = 0
