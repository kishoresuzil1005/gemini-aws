from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.metadata.alb_metadata import ALBMetadata
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class ALBGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "ALB"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # ALB -> VPC
        vpc_id = ALBMetadata.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="ALB",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # ALB -> Subnets
        for subnet_id in ALBMetadata.get_subnet_ids(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=subnet_id,
                relationship=RelationshipType.IN_SUBNET,
                source_type="ALB",
                target_type="Subnet"
            )
            if edge: edges.append(edge)
            
        # ALB -> Security Groups
        for sg_id in ALBMetadata.get_security_groups(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=sg_id,
                relationship=RelationshipType.USES_SG,
                source_type="ALB",
                target_type="SecurityGroup"
            )
            if edge: edges.append(edge)
            
        return edges
