from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.builders.common import GraphBuilderHelper

class RDSGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        edges = []
        resource_lookup = {r.resource_id: r.resource_type for r in resources}
        
        for res in resources:
                    sg_id = sg.get("VpcSecurityGroupId")
                    if sg_id:
                        relationships.append({
                            "from": res.resource_id,
                            "to": sg_id,
                            "type": "USES_SG",
                            "source_type": "RDS",
                            "target_type": "SecurityGroup"
                        })

        return relationships
