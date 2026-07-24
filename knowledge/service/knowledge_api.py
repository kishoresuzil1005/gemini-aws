# knowledge/service/knowledge_api.py
"""The public contract definition for the Knowledge Service."""

import abc
from typing import Dict, Any

from .knowledge_models import KnowledgeResponse
from .knowledge_query import KnowledgeQuery

class KnowledgeAPI(abc.ABC):
    """The stable public interface required by the M12 specification."""
    
    # Resources
    @abc.abstractmethod
    def get_resource(self, resource_id: str) -> KnowledgeResponse: pass
    
    @abc.abstractmethod
    def find_resource(self, name: str) -> KnowledgeResponse: pass
    
    @abc.abstractmethod
    def list_resources(self, query: KnowledgeQuery) -> KnowledgeResponse: pass

    # Relationships
    @abc.abstractmethod
    def get_relationship(self, relationship_id: str) -> KnowledgeResponse: pass
    
    @abc.abstractmethod
    def find_relationships(self, resource_id: str) -> KnowledgeResponse: pass
    
    @abc.abstractmethod
    def find_dependencies(self, resource_id: str) -> KnowledgeResponse: pass

    # Rules
    @abc.abstractmethod
    def get_rule(self, rule_id: str) -> KnowledgeResponse: pass

    @abc.abstractmethod
    def list_rules(self, query: KnowledgeQuery) -> KnowledgeResponse: pass

    # Graph
    @abc.abstractmethod
    def get_node(self, node_id: str) -> KnowledgeResponse: pass

    @abc.abstractmethod
    def find_shortest_path(self, source_id: str, target_id: str) -> KnowledgeResponse: pass

    @abc.abstractmethod
    def find_blast_radius(self, resource_id: str) -> KnowledgeResponse: pass

    # Search
    @abc.abstractmethod
    def search(self, search_term: str, query: KnowledgeQuery) -> KnowledgeResponse: pass

    # Health
    @abc.abstractmethod
    def health(self) -> Dict[str, Any]: pass
