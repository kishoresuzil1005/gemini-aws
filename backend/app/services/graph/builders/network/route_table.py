from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.graph_metadata_helper import GraphMetadataHelper
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class RouteTableGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "RouteTable"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # RouteTable -> VPC
        vpc_id = GraphMetadataHelper.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="RouteTable",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        # RouteTable -> Subnets
        for subnet_id in GraphMetadataHelper.get_route_table_subnets(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=subnet_id,
                relationship=RelationshipType.IN_SUBNET,
                source_type="RouteTable",
                target_type="Subnet"
            )
            if edge: edges.append(edge)
            
        # RouteTable -> InternetGateways
        for igw_id in GraphMetadataHelper.get_route_table_igws(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=igw_id,
                relationship=RelationshipType.ROUTES_TO,
                source_type="RouteTable",
                target_type="InternetGateway"
            )
            if edge: edges.append(edge)
            
        # RouteTable -> NATGateways
        for nat_id in GraphMetadataHelper.get_route_table_nat_gateways(resource):
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=nat_id,
                relationship=RelationshipType.ROUTES_TO,
                source_type="RouteTable",
                target_type="NatGateway"
            )
            if edge: edges.append(edge)
            
        return edges
