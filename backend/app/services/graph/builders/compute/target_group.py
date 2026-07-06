from typing import List, Dict, Any
from app.models import ResourceDB

class TargetGroupGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "TargetGroup" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # TargetGroup -> VPC
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "TargetGroup",
                        "target_type": "VPC"
                    })
                
                # TargetGroup -> ALB (TargetGroup is attached to ALB)
                # Technically the route is usually ALB -> TargetGroup
                # We map it as ALB -> TargetGroup because the ALB distributes traffic to the TargetGroup.
                for lb_arn in metadata.get("load_balancers", []):
                    relationships.append({
                        "from": lb_arn,
                        "to": res.resource_id,
                        "type": "ROUTES_TO",
                        "source_type": "ALB",
                        "target_type": "TargetGroup"
                    })

        return relationships
