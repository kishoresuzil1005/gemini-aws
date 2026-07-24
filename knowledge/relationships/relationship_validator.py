# knowledge/relationships/relationship_validator.py
"""Detects cycles and enforces relationship schema logic."""

import logging
from typing import List, Dict, Set

from .relationship_models import CanonicalRelationship
from .relationship_exceptions import CircularDependencyError

logger = logging.getLogger(__name__)

class RelationshipValidator:
    """Validates edges for cycles and completeness."""

    def validate(self, relationships: List[CanonicalRelationship]) -> List[CanonicalRelationship]:
        """Runs the validation suite."""
        self._detect_cycles(relationships)
        return relationships

    def _detect_cycles(self, relationships: List[CanonicalRelationship]) -> None:
        """Runs a Depth-First Search (DFS) to detect catastrophic circular dependencies."""
        
        # Build a quick directional graph mapping
        graph: Dict[str, List[str]] = {}
        for rel in relationships:
            # We only care about DEPENDS_ON or hierarchical edges for cycle detection
            if rel.relationship_type in ("DEPENDS_ON", "PART_OF", "CONTAINS"):
                graph.setdefault(rel.source_resource_id, []).append(rel.target_resource_id)
                
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True # Cycle detected!
                    
            recursion_stack.remove(node)
            return False
            
        for node in graph:
            if node not in visited:
                if dfs(node):
                    logger.error("Circular dependency detected in graph traversal!")
                    raise CircularDependencyError("A cycle was detected in the relationship hierarchy.")
                    
        logger.debug("No circular dependencies detected.")
