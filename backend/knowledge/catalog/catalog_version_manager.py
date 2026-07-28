# knowledge/catalog/catalog_version_manager.py
"""Tracks historical state and schema versions."""

import logging

logger = logging.getLogger(__name__)

class CatalogVersionManager:
    """Manages the version lifecycle of the catalog data."""

    def __init__(self):
        self.current_version = "1.0.0"

    def increment_version(self) -> str:
        """Bump the catalog version for a new snapshot/build."""
        # Simplified: just append a minor patch
        major, minor, patch = map(int, self.current_version.split('.'))
        self.current_version = f"{major}.{minor}.{patch + 1}"
        logger.info(f"Catalog version incremented to {self.current_version}")
        return self.current_version
