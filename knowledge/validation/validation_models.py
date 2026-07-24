# knowledge/validation/validation_models.py
"""Internal models representing the state and context of validation."""

from pydantic import BaseModel
from typing import Any, Dict


class SnapshotContext(BaseModel):
    """Encapsulates all necessary data about the snapshot being validated."""
    snapshot_path: str
    connector_name: str
    provider: str
    metadata: Dict[str, Any]
    manifest: Dict[str, Any]
    raw_content: bytes
    parsed_content: Any = None
