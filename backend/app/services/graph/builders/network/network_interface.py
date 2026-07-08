from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.metadata.network_metadata import NetworkMetadata
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class NetworkInterfaceGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "NetworkInterface"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # NetworkInterface -> VPC
        vpc_id = NetworkMetadata.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="NetworkInterface",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # NetworkInterface -> Subnet
        subnet_id = NetworkMetadata.get_subnet_id(resource)
        if subnet_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=subnet_id,
                relationship=RelationshipType.IN_SUBNET,
                source_type="NetworkInterface",
                target_type="Subnet"
            )
            if edge: edges.append(edge)
            
        # NetworkInterface -> Security Groups
        for sg_id in NetworkMetadata.get_security_groups(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=sg_id,
                relationship=RelationshipType.USES_SG,
                source_type="NetworkInterface",
                target_type="SecurityGroup"
            )
            if edge: edges.append(edge)
            
        return edges
