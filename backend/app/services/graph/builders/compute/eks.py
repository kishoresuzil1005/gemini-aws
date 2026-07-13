from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.builders.common import GraphBuilderHelper

class EKSGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        edges = []
        resource_lookup = {r.resource_id: r.resource_type for r in resources}
        
        for res in resources:
            if res.resource_type == "EKSCluster":
                edges.extend(GraphBuilderHelper.build_edges(res, resource_lookup))
                
        return edges