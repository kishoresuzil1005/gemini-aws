from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.metadata.network_metadata import NetworkMetadata
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class SubnetGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "Subnet"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # Subnet -> VPC
        vpc_id = NetworkMetadata.get_vpc_id(resource)
        if vpc_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=vpc_id,
                relationship=RelationshipType.IN_VPC,
                source_type="Subnet",
                target_type="VPC"
            )
            if edge: edges.append(edge)
            
        return edges