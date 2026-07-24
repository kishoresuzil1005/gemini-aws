# knowledge/snapshot/snapshot_storage.py
"""Disk I/O and compression for snapshots."""

import os
import gzip
import logging

logger = logging.getLogger(__name__)

class SnapshotStorage:
    def __init__(self, storage_dir: str = ".snapshots"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save(self, snapshot_id: str, raw_data: str) -> str:
        filepath = os.path.join(self.storage_dir, f"{snapshot_id}.json.gz")
        with gzip.open(filepath, 'wt', encoding='utf-8') as f:
            f.write(raw_data)
        logger.info(f"Snapshot {snapshot_id} saved to {filepath}")
        return filepath

    def load(self, snapshot_id: str) -> str:
        filepath = os.path.join(self.storage_dir, f"{snapshot_id}.json.gz")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found at {filepath}")
            
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            return f.read()
