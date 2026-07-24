# knowledge/catalog/catalog_models.py
"""The central CanonicalResource schema."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CanonicalResource(BaseModel):
    """The authoritative universal representation of a cloud resource in the Catalog."""
    
    # Core Identity
    resource_id: str
    canonical_name: str
    display_name: str
    
    # Taxonomy
    provider: str
    provider_resource_name: str
    service: str
    category: str
    resource_type: str
    
    # Content
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    supported_operations: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationships (static pointers)
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    
    # Metadata
    documentation: List[str] = Field(default_factory=list)
    tags: Dict[str, str] = Field(default_factory=dict)
    aliases: List[str] = Field(default_factory=list)
    
    # Lifecycle
    version: str = "1.0"
    status: str = "ACTIVE"
    creation_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    update_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
