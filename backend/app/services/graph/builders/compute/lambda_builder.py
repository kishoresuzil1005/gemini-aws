from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.builders.common import RELATIONSHIP_MAP

class LambdaGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type != "Lambda":
                continue
            metadata = res.resource_metadata or {}
            for dep in metadata.get("dependencies", []):
                dep_type = dep.get("type", "").upper()
                relationships.append({
                    "from": res.resource_id,
                    "to": dep["id"],
                    "type": RELATIONSHIP_MAP.get(dep_type, "DEPENDS_ON"),
                    "source_type": "Lambda",
                    "target_type": dep.get("type", "")
                })
        return relationships
