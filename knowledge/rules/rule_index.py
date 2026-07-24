# knowledge/rules/rule_index.py
"""In-memory indexing engine for O(1) rule lookups."""

import logging
from typing import Dict, List, Set

from .rule_models import CanonicalRule

logger = logging.getLogger(__name__)

class RuleIndex:
    """Maintains highly optimized reverse-indexes for rapid rule querying."""

    def __init__(self):
        # Primary lookup
        self.id_index: Dict[str, CanonicalRule] = {}
        
        # Categorical indexes
        self.category_index: Dict[str, Set[str]] = {}
        self.severity_index: Dict[str, Set[str]] = {}
        self.provider_index: Dict[str, Set[str]] = {}
        self.resource_index: Dict[str, Set[str]] = {}
        self.status_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}

    def build_indexes(self, rules: List[CanonicalRule]) -> None:
        """Rebuilds all indexes from a fresh list of rules."""
        self.clear()
        
        for rule in rules:
            rid = rule.rule_id
            self.id_index[rid] = rule
            
            # Status
            self.status_index.setdefault(rule.status, set()).add(rid)
            
            # Category
            self.category_index.setdefault(rule.category.lower(), set()).add(rid)
            
            # Severity
            self.severity_index.setdefault(rule.severity.upper(), set()).add(rid)
            
            # Provider
            self.provider_index.setdefault(rule.provider.lower(), set()).add(rid)
            
            # Resources
            for res in rule.supported_resources:
                self.resource_index.setdefault(res.lower(), set()).add(rid)
            
            # Tags
            for tk, tv in rule.tags.items():
                tag_key = f"{tk}:{tv}".lower()
                self.tag_index.setdefault(tag_key, set()).add(rid)
                
        logger.info("Rule indexes built successfully.")

    def clear(self) -> None:
        """Flush all indexes."""
        self.id_index.clear()
        self.category_index.clear()
        self.severity_index.clear()
        self.provider_index.clear()
        self.resource_index.clear()
        self.status_index.clear()
        self.tag_index.clear()
