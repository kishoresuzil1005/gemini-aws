# knowledge/snapshot/snapshot_exporter.py
"""Serializes the comprehensive snapshot payload."""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SnapshotExporter:
    @staticmethod
    def export(payload: Dict[str, Any]) -> str:
        """Serializes the payload to a JSON string."""
        return json.dumps(payload, sort_keys=True)
