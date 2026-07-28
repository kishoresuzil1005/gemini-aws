# knowledge/snapshot/snapshot_manager.py
"""Master orchestrator for the Snapshot subsystem."""

import uuid
import logging
from typing import Dict, Any, List

from .snapshot_builder import SnapshotBuilder
from .snapshot_statistics import SnapshotStatistics
from .checksum_manager import ChecksumManager
from .manifest_generator import ManifestGenerator
from .snapshot_exporter import SnapshotExporter
from .snapshot_importer import SnapshotImporter
from .snapshot_storage import SnapshotStorage
from .version_manager import VersionManager
from .audit_manager import AuditManager
from .rollback_manager import RollbackManager
from .snapshot_diff import SnapshotDiff
from .snapshot_metadata import SnapshotMetadata

logger = logging.getLogger(__name__)

class SnapshotManager:
    """The central orchestrator wrapping all snapshot logic."""

    def __init__(self, resource_cat, rel_cat, rule_cat, graph):
        self.builder = SnapshotBuilder(resource_cat, rel_cat, rule_cat, graph)
        self.storage = SnapshotStorage()
        self.version = VersionManager()
        self.audit = AuditManager()
        self.rollback_mgr = RollbackManager(resource_cat, rel_cat, rule_cat, graph)
        self.diff_engine = SnapshotDiff()
        
    def create_snapshot(self, author: str, reason: str, update_type: str = "patch") -> str:
        """Takes a full state dump, calculates checksum, saves to disk."""
        snapshot_id = str(uuid.uuid4())
        
        # 1. Build Payload Data
        data_payload = self.builder.build_payload()
        
        # 2. Stats & Checksum
        stats = SnapshotStatistics.compute(data_payload)
        checksum = ChecksumManager.generate(data_payload)
        
        # 3. Version & Manifest
        ver = self.version.increment(update_type)
        manifest = ManifestGenerator.generate(snapshot_id, ver, checksum, stats)
        meta = SnapshotMetadata(author=author, reason=reason)
        
        # 4. Final Enveloped Payload
        full_payload = {
            "manifest": manifest.dict(),
            "metadata": meta.dict(),
            "data": data_payload
        }
        
        # 5. Export and Save
        raw_json = SnapshotExporter.export(full_payload)
        self.storage.save(snapshot_id, raw_json)
        
        # 6. Audit
        self.audit.record_action("CREATE", snapshot_id, author, reason)
        
        return snapshot_id

    def restore_snapshot(self, snapshot_id: str, author: str) -> None:
        """Loads and verifies a snapshot before committing a rollback."""
        raw_json = self.storage.load(snapshot_id)
        payload = SnapshotImporter.parse(raw_json)
        
        self.rollback_mgr.rollback(payload)
        self.audit.record_action("RESTORE", snapshot_id, author, "Rollback invoked")

    def compare(self, snapshot_id_a: str, snapshot_id_b: str) -> Dict[str, Any]:
        """Calculates diff between two stored snapshots."""
        raw_a = self.storage.load(snapshot_id_a)
        raw_b = self.storage.load(snapshot_id_b)
        
        payload_a = SnapshotImporter.parse(raw_a)
        payload_b = SnapshotImporter.parse(raw_b)
        
        return self.diff_engine.compare(payload_a, payload_b)
