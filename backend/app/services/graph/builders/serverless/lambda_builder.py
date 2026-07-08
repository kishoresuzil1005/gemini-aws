from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.graph_metadata_helper import GraphMetadataHelper
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class LambdaGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "Lambda"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # Lambda -> IAM Role
        role = GraphMetadataHelper.get_iam_profile_or_role(resource)
        if role:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=role,
                relationship=RelationshipType.USES_ROLE,
                source_type="Lambda",
                target_type="IAM"
            )
            if edge: edges.append(edge)
            
        # Lambda -> VPC
        vpc_id = GraphMetadataHelper.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="Lambda",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # Lambda -> Subnets
        for subnet_id in GraphMetadataHelper.get_subnet_ids(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=subnet_id,
                relationship=RelationshipType.IN_SUBNET,
                source_type="Lambda",
                target_type="Subnet"
            )
            if edge: edges.append(edge)
            
        # Lambda -> Security Groups
        for sg_id in GraphMetadataHelper.get_security_groups(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=sg_id,
                relationship=RelationshipType.USES_SG,
                source_type="Lambda",
                target_type="SecurityGroup"
            )
            if edge: edges.append(edge)
            
        return edges
