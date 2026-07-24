# knowledge/snapshot/snapshot_validator.py
"""Validates snapshots prior to restoration."""

import logging
from typing import Dict, Any

from .checksum_manager import ChecksumManager
from .snapshot_exceptions import IntegrityError

logger = logging.getLogger(__name__)

class SnapshotValidator:
    def validate_for_restore(self, payload: Dict[str, Any]) -> bool:
        """Ensures the manifest and checksums are intact before rolling back."""
        manifest = payload.get("manifest")
        if not manifest:
            raise IntegrityError("Snapshot is missing manifest.")
            
        expected_checksum = manifest.get("checksum")
        
        # We must verify the checksum of the data portion
        data_payload = payload.get("data", {})
        if not ChecksumManager.verify(data_payload, expected_checksum):
            raise IntegrityError("Snapshot checksum verification failed. Payload may be corrupted.")
            
        logger.info(f"Snapshot {manifest.get('snapshot_id')} passed integrity validation.")
        return True
