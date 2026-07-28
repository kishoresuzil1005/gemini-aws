# knowledge/snapshot/snapshot_metadata.py
"""Metadata definitions for a captured snapshot."""

from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class SnapshotMetadata(BaseModel):
    author: str = "System"
    reason: str = "Automated Backup"
    schema_version: str = "1.0.0"
    tags: Dict[str, str] = Field(default_factory=dict)
    created_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
