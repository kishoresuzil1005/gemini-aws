# knowledge/snapshot/release_manager.py
"""Manages the lifecycle of snapshot promotions (DEV -> PROD)."""

import uuid
import logging
from typing import Dict
from .snapshot_models import Release

logger = logging.getLogger(__name__)

class ReleaseManager:
    def __init__(self):
        self.releases: Dict[str, Release] = {}

    def promote(self, snapshot_id: str, environment: str, notes: str) -> Release:
        release = Release(
            release_id=str(uuid.uuid4()),
            snapshot_id=snapshot_id,
            environment=environment,
            approval_status="APPROVED",
            release_notes=notes
        )
        self.releases[release.release_id] = release
        logger.info(f"Snapshot {snapshot_id} promoted to {environment}")
        return release
