# knowledge/graph/graph_builder.py
"""Synthesizes Catalogs into unified Graph Nodes and Edges."""

import logging
import uuid
from typing import List, Tuple

from .graph_models import GraphNode, GraphEdge
from .graph_validator import GraphValidator
from ..catalog.catalog_models import CanonicalResource
from ..relationships.relationship_models import CanonicalRelationship
from ..rules.rule_models import CanonicalRule

logger = logging.getLogger(__name__)

class GraphBuilder:
    """Transforms disparate Catalogs into the unified Graph Schema."""

    def __init__(self):
        self.validator = GraphValidator()

    def build(self, resources: List[CanonicalResource], relationships: List[CanonicalRelationship], rules: List[CanonicalRule]) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Parses M8, M9, M10 outputs and stitches them into a cohesive Graph."""
        
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        
        # 1. Process Resources -> Nodes
        for res in resources:
            nodes.append(GraphNode(
                node_id=res.resource_id,
                node_type="RESOURCE",
                entity=res,
                labels=[res.category, res.service, res.provider.upper()]
            ))
            
        # 2. Process Relationships -> Edges
        for rel in relationships:
            edges.append(GraphEdge(
                edge_id=rel.relationship_id,
                source_id=rel.source_resource_id,
                target_id=rel.target_resource_id,
                relationship_type=rel.relationship_type,
                entity=rel
            ))
            
        # 3. Process Rules -> Nodes + Virtual Edges
        for rule in rules:
            rule_node_id = f"RULE::{rule.rule_id}"
            nodes.append(GraphNode(
                node_id=rule_node_id,
                node_type="RULE",
                entity=rule,
                labels=[rule.category, "RULE", rule.severity.upper()]
            ))
            
            # Virtual Edges connecting Rule to supported Resources
            # (In a real scenario, this might connect to specific resource IDs via query, 
            # but we simulate the topology mapping here)
            for res_type in rule.supported_resources:
                # Find all resources matching this type and bind the rule to them
                for res in resources:
                    if res.resource_type.lower() == res_type.lower():
                        edges.append(GraphEdge(
                            edge_id=str(uuid.uuid4()),
                            source_id=rule_node_id,
                            target_id=res.resource_id,
                            relationship_type="GOVERNS",
                            entity=None
                        ))
                        
        # 4. Validate
        valid_edges = self.validator.validate(nodes, edges)
        
        logger.info(f"Graph Builder constructed {len(nodes)} nodes and {len(valid_edges)} edges.")
        return nodes, valid_edges
