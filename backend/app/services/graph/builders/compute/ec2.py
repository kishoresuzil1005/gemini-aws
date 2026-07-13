from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.metadata.ec2_metadata import EC2Metadata
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class EC2GraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "EC2"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # EC2 -> VPC
        vpc_id = EC2Metadata.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="EC2",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # EC2 -> Subnet
        subnet_id = EC2Metadata.get_subnet_id(resource)
        if subnet_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=subnet_id,
                relationship=RelationshipType.IN_SUBNET,
                source_type="EC2",
                target_type="Subnet"
            )
            if edge: edges.append(edge)
            
        # EC2 -> EBS Volumes
        for ebs_id in EC2Metadata.get_ebs_volumes(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=ebs_id,
                relationship=RelationshipType.ATTACHED_TO,
                source_type="EC2",
                target_type="EBS"
            )
            if edge: edges.append(edge)
                
        # EC2 -> Security Groups
        for sg_id in EC2Metadata.get_security_groups(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=sg_id,
                relationship=RelationshipType.USES_SG,
                source_type="EC2",
                target_type="SecurityGroup"
            )
            if edge: edges.append(edge)
                
        # EC2 -> IAM Role / Instance Profile
        iam_profile = EC2Metadata.get_iam_instance_profile(resource)
        if iam_profile:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=iam_profile,
                relationship=RelationshipType.USES_ROLE,
                source_type="EC2",
                target_type="IAM"
            )
            if edge: edges.append(edge)
            
        return edges