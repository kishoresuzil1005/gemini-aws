# knowledge/service/knowledge_search.py
"""Unified search across all underlying catalogs."""

import logging
from typing import List, Any
from .knowledge_query import KnowledgeQuery

logger = logging.getLogger(__name__)

class KnowledgeSearch:
    """Executes full-text/field searches by delegating to the appropriate sub-catalogs."""
    
    def __init__(self, resource_catalog, relationship_catalog, rule_catalog):
        self.resources = resource_catalog
        self.relationships = relationship_catalog
        self.rules = rule_catalog

    def search_all(self, query: str) -> List[Any]:
        """A naive full-text search simulation across resources and rules."""
        q = query.lower()
        results = []
        
        # Search Resources
        for res in self.resources.list_resources():
            if (q in res.canonical_name.lower() or 
                q in res.display_name.lower() or 
                (res.description and q in res.description.lower())):
                results.append(res)
                
        # Search Rules
        for rule in self.rules.list_rules():
            if (q in rule.canonical_name.lower() or 
                q in rule.description.lower() or 
                q in rule.purpose.lower()):
                results.append(rule)
                
        return results

    def _apply_pagination(self, data: List[Any], q: KnowledgeQuery) -> List[Any]:
        """Slices the array based on limit/offset."""
        return data[q.offset : q.offset + q.limit]
