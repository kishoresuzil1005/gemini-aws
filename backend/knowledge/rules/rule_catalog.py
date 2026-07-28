# knowledge/rules/rule_catalog.py
"""Unified facade exposing the complete Rule Catalog functionality."""

from typing import List

from .rule_models import CanonicalRule
from .rule_index import RuleIndex
from .rule_query import RuleQueryAPI
from .rule_manager import RuleManager
from .rule_version_manager import RuleVersionManager
from .rule_loader import RuleLoader
from .rule_exceptions import RuleNotFoundError

class RuleCatalog(RuleQueryAPI):
    """The central authoritative registry for Canonical Rules.
    
    Implements the RuleQueryAPI to serve as the unified API boundary for
    all downstream Policy Engines and AI Analyzers.
    """

    def __init__(self):
        self.index = RuleIndex()
        self.version_manager = RuleVersionManager()
        self.manager = RuleManager(self.index, self.version_manager)
        self.loader = RuleLoader()

    # Lifecycle Methods
    
    def ingest(self, raw_rules: List[CanonicalRule]) -> None:
        """Ingest new rules into the catalog."""
        self.manager.update_rules(raw_rules)

    def load_from_disk(self, filepath: str) -> None:
        """Load and index a rule catalog from disk."""
        rules = self.loader.load(filepath)
        if rules:
            self.manager.update_rules(rules)

    def save_to_disk(self, filepath: str) -> None:
        """Persist the current rule catalog to disk."""
        self.loader.save(filepath, self.manager.current_rules)

    # Internal Helpers
    
    def _resolve_ids(self, ids: set, include_drafts: bool = False) -> List[CanonicalRule]:
        rules = [self.index.id_index[rid] for rid in ids if rid in self.index.id_index]
        if not include_drafts:
            rules = [r for r in rules if r.status == "PUBLISHED"]
        return rules

    # Query API Implementation

    def get_rule(self, rule_id: str) -> CanonicalRule:
        rule = self.index.id_index.get(rule_id)
        if not rule:
            raise RuleNotFoundError(f"Rule {rule_id} not found.")
        return rule

    def list_rules(self, include_drafts: bool = False) -> List[CanonicalRule]:
        all_ids = set(self.index.id_index.keys())
        return self._resolve_ids(all_ids, include_drafts)

    def list_rules_by_category(self, category: str, include_drafts: bool = False) -> List[CanonicalRule]:
        ids = self.index.category_index.get(category.lower(), set())
        return self._resolve_ids(ids, include_drafts)

    def list_rules_by_severity(self, severity: str, include_drafts: bool = False) -> List[CanonicalRule]:
        ids = self.index.severity_index.get(severity.upper(), set())
        return self._resolve_ids(ids, include_drafts)

    def list_rules_by_resource(self, resource_type: str, include_drafts: bool = False) -> List[CanonicalRule]:
        ids = self.index.resource_index.get(resource_type.lower(), set())
        return self._resolve_ids(ids, include_drafts)
        
    def search_rules_by_tag(self, key: str, value: str, include_drafts: bool = False) -> List[CanonicalRule]:
        tag_key = f"{key}:{value}".lower()
        ids = self.index.tag_index.get(tag_key, set())
        return self._resolve_ids(ids, include_drafts)
