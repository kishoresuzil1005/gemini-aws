from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.base_builder import BaseGraphBuilder

class VPCGraphBuilder(BaseGraphBuilder):
    RESOURCE_TYPE = "VPC"

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        # VPCs are top-level constructs, usually Subnets connect TO VPCs.
        # But if we need VPC -> DHCP or Peering, it goes here.
        return []