# knowledge/relationships/relationship_query.py
"""API Boundary definitions for traversing relationships."""

from typing import List
import abc

from .relationship_models import CanonicalRelationship

class RelationshipQueryAPI(abc.ABC):
    """Abstract interface defining the strict query contract for downstream consumers."""

    @abc.abstractmethod
    def get_relationship(self, relationship_id: str) -> CanonicalRelationship:
        pass

    @abc.abstractmethod
    def find_relationships(self, resource_id: str) -> List[CanonicalRelationship]:
        pass

    @abc.abstractmethod
    def find_dependencies(self, resource_id: str) -> List[CanonicalRelationship]:
        pass

    @abc.abstractmethod
    def find_dependents(self, resource_id: str) -> List[CanonicalRelationship]:
        pass

    @abc.abstractmethod
    def find_network_path(self, source_id: str, target_id: str) -> List[CanonicalRelationship]:
        """Executes a multi-hop pathfinding query between two nodes."""
        pass
        
    @abc.abstractmethod
    def find_security_relationships(self, resource_id: str) -> List[CanonicalRelationship]:
        pass
