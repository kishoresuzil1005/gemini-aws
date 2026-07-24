# knowledge/snapshot/version_manager.py
"""Semantic versioning logic for Snapshots."""

import logging

logger = logging.getLogger(__name__)

class VersionManager:
    def __init__(self):
        self.current_version = "1.0.0"

    def increment(self, update_type: str = "patch") -> str:
        major, minor, patch = map(int, self.current_version.split('.'))
        
        if update_type == "major":
            major += 1
            minor, patch = 0, 0
        elif update_type == "minor":
            minor += 1
            patch = 0
        else:
            patch += 1
            
        self.current_version = f"{major}.{minor}.{patch}"
        logger.info(f"Platform version bumped to {self.current_version}")
        return self.current_version
