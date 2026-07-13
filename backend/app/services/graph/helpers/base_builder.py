from typing import List, Dict, Any
from app.models import ResourceDB

class BaseGraphBuilder:
    RESOURCE_TYPE = None

    @classmethod
    def build(cls, resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        edges = []
        for res in resources:
            if res.resource_type == cls.RESOURCE_TYPE:
                edges.extend(cls.build_resource_edges(res))
        return edges

    @classmethod
    def build_resource_edges(cls, resource: ResourceDB) -> List[Dict[str, Any]]:
        raise NotImplementedError("Each builder must implement build_resource_edges")