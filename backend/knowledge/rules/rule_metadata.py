# knowledge/rules/rule_metadata.py
"""Metadata structures tracking the state of the Rule Catalog."""

from pydantic import BaseModel, Field
from datetime import datetime

class RuleCatalogMetadata(BaseModel):
    """Metadata tracking rule catalog versioning, size, and timestamps."""
    catalog_version: str = "1.0.0"
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    total_rules: int = 0
    published_rules: int = 0
    deprecated_rules: int = 0
