from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.metadata.network_metadata import NetworkMetadata
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class ElasticIPGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "ElasticIP"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        edges = []
        
        # ElasticIP -> ENI
        eni_id = NetworkMetadata.get_eni_id(resource)
        if eni_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=eni_id,
                relationship=RelationshipType.ATTACHED_TO,
                source_type="ElasticIP",
                target_type="NetworkInterface"
            )
            if edge: edges.append(edge)
            if edge: edges.append(edge)
            
        # ElasticIP -> EC2
        instance_id = NetworkMetadata.get_instance_id(resource)
        if instance_id:
            edge = GraphRelationship.create(
                source=resource.resource_id,
                target=instance_id,
                relationship=RelationshipType.ATTACHED_TO,
                source_type="ElasticIP",
                target_type="EC2"
            )
            if edge: edges.append(edge)
            
        return edge