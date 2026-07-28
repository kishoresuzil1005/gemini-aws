# knowledge/rules/rule_manager.py
"""Orchestrates rule catalog lifecycle and state transitions."""

import logging
from typing import List

from .rule_models import CanonicalRule
from .rule_builder import RuleBuilder
from .rule_index import RuleIndex
from .rule_version_manager import RuleVersionManager
from .rule_metadata import RuleCatalogMetadata

logger = logging.getLogger(__name__)

class RuleManager:
    """Controls the rebuilding and indexing lifecycle."""

    def __init__(self, index: RuleIndex, version_manager: RuleVersionManager):
        self.index = index
        self.version_manager = version_manager
        self.builder = RuleBuilder()
        
        self.current_rules: List[CanonicalRule] = []
        self.metadata: RuleCatalogMetadata = RuleCatalogMetadata()

    def update_rules(self, raw_rules: List[CanonicalRule]) -> None:
        """Validates new rules and rebuilds the catalog."""
        
        valid_rules = self.builder.build(raw_rules)
        self.current_rules = valid_rules
        
        # Metadata and Versioning
        self.metadata.catalog_version = self.version_manager.increment_version()
        self.metadata.total_rules = len(self.current_rules)
        self.metadata.published_rules = sum(1 for r in self.current_rules if r.status == "PUBLISHED")
        
        # Rebuild Indexes
        self.index.build_indexes(self.current_rules)
        
        logger.info(f"Rule Catalog updated. Total Rules: {self.metadata.total_rules}")
