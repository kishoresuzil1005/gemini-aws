from typing import List, Dict, Any
from app.models import ResourceDB

class AutoScalingGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "AutoScalingGroup" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # AutoScalingGroup -> EC2
                for instance_id in metadata.get("instances", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": instance_id,
                        "type": "MANAGES",
                        "source_type": "AutoScalingGroup",
                        "target_type": "EC2"
                    })
                
                # AutoScalingGroup -> TargetGroup
                for tg_arn in metadata.get("target_groups", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": tg_arn,
                        "type": "ATTACHED_TO",
                        "source_type": "AutoScalingGroup",
                        "target_type": "TargetGroup"
                    })

        return relationships
