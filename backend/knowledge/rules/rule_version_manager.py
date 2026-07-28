# knowledge/rules/rule_version_manager.py
"""Tracks historical state and schema versions for rules."""

import logging

logger = logging.getLogger(__name__)

class RuleVersionManager:
    """Manages the version lifecycle of the rules payload."""

    def __init__(self):
        self.current_version = "1.0.0"

    def increment_version(self) -> str:
        """Bump the version for a new rule snapshot/build."""
        major, minor, patch = map(int, self.current_version.split('.'))
        self.current_version = f"{major}.{minor}.{patch + 1}"
        logger.info(f"Rule Catalog version incremented to {self.current_version}")
        return self.current_version
