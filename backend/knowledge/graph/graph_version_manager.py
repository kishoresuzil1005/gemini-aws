# knowledge/graph/graph_version_manager.py
"""Tracks historical state and schema versions for the Knowledge Graph."""

import logging

logger = logging.getLogger(__name__)

class GraphVersionManager:
    """Manages the version lifecycle of the graph payload."""

    def __init__(self):
        self.current_version = "1.0.0"

    def increment_version(self) -> str:
        """Bump the version for a new graph snapshot/build."""
        major, minor, patch = map(int, self.current_version.split('.'))
        self.current_version = f"{major}.{minor}.{patch + 1}"
        logger.info(f"Knowledge Graph version incremented to {self.current_version}")
        return self.current_version
