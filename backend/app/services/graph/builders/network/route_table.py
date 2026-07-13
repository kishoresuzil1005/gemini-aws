from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.metadata.network_metadata import NetworkMetadata
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class RouteTableGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "RouteTable"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # RouteTable -> VPC
        vpc_id = NetworkMetadata.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="RouteTable",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # RouteTable -> Subnets (Associations)
        for subnet_id in NetworkMetadata.get_route_table_subnets(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=subnet_id,
                relationship=RelationshipType.ASSOCIATED_WITH,
                source_type="RouteTable",
                target_type="Subnet"
            )
            if edge: edges.append(edge)
            
        # RouteTable -> IGW (Routes)
        for igw_id in NetworkMetadata.get_route_table_igws(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=igw_id,
                relationship=RelationshipType.ROUTES_TO,
                source_type="RouteTable",
                target_type="InternetGateway"
            )
            if edge: edges.append(edge)
            
        # RouteTable -> NAT Gateway (Routes)
        for nat_id in NetworkMetadata.get_route_table_nat_gateways(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=nat_id,
                relationship=RelationshipType.ROUTES_TO,
                source_type="RouteTable",
                target_type="NatGateway"
            )
            if edge: edges.append(edge)
            
        return edge