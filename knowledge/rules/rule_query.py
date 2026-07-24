# knowledge/rules/rule_query.py
"""API Boundary definitions for querying the Rule Catalog."""

from typing import List
import abc

from .rule_models import CanonicalRule

class RuleQueryAPI(abc.ABC):
    """Abstract interface defining the strict query contract for downstream consumers."""

    @abc.abstractmethod
    def get_rule(self, rule_id: str) -> CanonicalRule:
        pass

    @abc.abstractmethod
    def list_rules(self, include_drafts: bool = False) -> List[CanonicalRule]:
        pass

    @abc.abstractmethod
    def list_rules_by_category(self, category: str, include_drafts: bool = False) -> List[CanonicalRule]:
        pass

    @abc.abstractmethod
    def list_rules_by_severity(self, severity: str, include_drafts: bool = False) -> List[CanonicalRule]:
        pass

    @abc.abstractmethod
    def list_rules_by_resource(self, resource_type: str, include_drafts: bool = False) -> List[CanonicalRule]:
        pass
        
    @abc.abstractmethod
    def search_rules_by_tag(self, key: str, value: str, include_drafts: bool = False) -> List[CanonicalRule]:
        pass
