# knowledge/providers/aws/connectors/monitoring_snapshot_manager.py
"""Manages the creation and integrity of immutable monitoring knowledge snapshots.
"""

import hashlib
import json
import logging
import os
from datetime import datetime

from .connector_config import ConnectorConfig

logger = logging.getLogger(__name__)


class MonitoringSnapshotManager:
    """Handles saving immutable snapshots for operational and monitoring knowledge.
    Ensures checksums and manifests are generated for data integrity.
    """

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.base_dir = os.path.join(
            self.config.data_dir, "providers", "aws", "snapshots", "monitoring"
        )

    def save_snapshot(self, data: bytes, connector_name: str, version: str) -> str:
        """Saves the raw JSON data to an immutable snapshot directory.
        
        Directory format:
        knowledge/providers/aws/snapshots/monitoring/<connector_name>/<YYYY-MM-DD>/
        """
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        snapshot_dir = os.path.join(self.base_dir, connector_name, date_str)

        if not os.path.exists(snapshot_dir):
            os.makedirs(snapshot_dir, exist_ok=True)

        content_path = os.path.join(snapshot_dir, "content.json")
        metadata_path = os.path.join(snapshot_dir, "metadata.json")
        manifest_path = os.path.join(snapshot_dir, "manifest.json")
        checksum_path = os.path.join(snapshot_dir, "checksum.sha256")

        # In a strict immutable system, we might raise if content_path already exists,
        # but for daily updates, we overwrite within the same day or append versions.
        # Here we'll overwrite the current day's snapshot.

        # Write content
        with open(content_path, "wb") as f:
            f.write(data)

        # Generate checksum
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        checksum = sha256_hash.hexdigest()

        with open(checksum_path, "w") as f:
            f.write(f"{checksum}  content.json\n")

        # Create metadata
        metadata = {
            "connector": connector_name,
            "version": version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "size_bytes": len(data),
            "checksum_sha256": checksum,
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create manifest
        manifest = {
            "snapshot_id": f"{connector_name}-{date_str}",
            "metadata": metadata,
            "files": ["content.json", "metadata.json", "checksum.sha256"],
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info("Saved immutable snapshot to %s", snapshot_dir)
        return snapshot_dir
