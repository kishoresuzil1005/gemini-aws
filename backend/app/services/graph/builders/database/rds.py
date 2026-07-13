from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.metadata.rds_metadata import RDSMetadata
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class RDSGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "RDS"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        print("=" * 60)
        print("Building RDS:", resource.resource_id)
        print(resource.resource_metadata)
        
        # RDS -> VPC
        vpc_id = RDSMetadata.get_vpc_id(resource)
        print("VPC:", vpc_id)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="RDS",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # RDS -> Security Groups
        sgs = RDSMetadata.get_security_groups(resource)
        print("Security Groups:", sgs)
        for sg_id in sgs:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=sg_id,
                relationship=RelationshipType.USES_SG,
                source_type="RDS",
                target_type="SecurityGroup"
            )
            if edge: edges.append(edge)
            
        print("Edges Created:", len(edges))
        for edge in edges:
            print(edge)
            
        return edges