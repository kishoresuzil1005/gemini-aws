from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.graph_metadata_helper import GraphMetadataHelper
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class TargetGroupGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "TargetGroup"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # TargetGroup -> VPC
        vpc_id = GraphMetadataHelper.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="TargetGroup",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # TargetGroup -> ALB (Actually ALB -> TargetGroup is more common, but let's do both or just TG -> ALB based on ALB dependency)
        for alb_id in GraphMetadataHelper.get_load_balancers(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=alb_id,
                relationship=RelationshipType.ATTACHED_TO,
                source_type="TargetGroup",
                target_type="ALB"
            )
            if edge: edges.append(edge)
            
        # TargetGroup -> Targets (EC2 or Lambda)
        for target in GraphMetadataHelper.get_targets(resource):
            target_id = target.get("id")
            if target_id:
                # We can deduce type somewhat heuristically, or default to generic DEPENDS_ON / TARGETS
                # For now let's just make it TARGETS Generic
                edge = GraphRelationship.create(
                    source=resource.resource_id,
                    target=target_id,
                    relationship=RelationshipType.TARGETS,
                    source_type="TargetGroup",
                    target_type="EC2" if target_id.startswith("i-") else "Lambda"
                )
                if edge: edges.append(edge)
                
        return edges
