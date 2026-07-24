# knowledge/snapshot/checksum_manager.py
"""Cryptographic integrity for snapshots."""

import hashlib
import json
from typing import Dict, Any

class ChecksumManager:
    @staticmethod
    def generate(payload: Dict[str, Any]) -> str:
        """Generates a SHA-256 hash of the serialized payload."""
        serialized = json.dumps(payload, sort_keys=True).encode('utf-8')
        return hashlib.sha256(serialized).hexdigest()

    @staticmethod
    def verify(payload: Dict[str, Any], expected_checksum: str) -> bool:
        """Verifies if the payload matches the expected checksum."""
        actual = ChecksumManager.generate(payload)
        return actual == expected_checksum
