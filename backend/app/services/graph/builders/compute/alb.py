from typing import List, Dict, Any
from app.models import ResourceDB

class ALBGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "ALB" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # ALB -> VPC
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "ALB",
                        "target_type": "VPC"
                    })

        return relationships
