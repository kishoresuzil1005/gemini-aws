# knowledge/snapshot/snapshot_models.py
"""Core schemas for snapshots and releases."""

from pydantic import BaseModel, Field
from datetime import datetime

class SnapshotManifest(BaseModel):
    snapshot_id: str
    version: str
    checksum: str
    resource_count: int
    relationship_count: int
    rule_count: int
    created_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class Release(BaseModel):
    release_id: str
    snapshot_id: str
    environment: str   # DEV, TEST, RC, PROD
    approval_status: str
    release_notes: str
    released_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
