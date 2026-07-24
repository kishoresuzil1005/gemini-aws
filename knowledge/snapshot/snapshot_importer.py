# knowledge/snapshot/snapshot_importer.py
"""Deserializes the comprehensive snapshot payload."""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SnapshotImporter:
    @staticmethod
    def parse(raw_data: str) -> Dict[str, Any]:
        """Deserializes the JSON string back into the payload dictionary."""
        return json.loads(raw_data)
