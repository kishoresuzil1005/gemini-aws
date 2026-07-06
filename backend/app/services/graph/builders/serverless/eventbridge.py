from typing import List, Dict, Any
from app.models import ResourceDB

class EventBridgeGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "EventBridgeRule" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # EventBridge Rule -> Lambda
                target_arns = metadata.get("target_arns", [])
                for target_arn in target_arns:
                    if ":lambda:" in target_arn:
                        relationships.append({
                            "from": metadata.get("bus_arn", res.resource_id),
                            "to": target_arn,
                            "type": "TRIGGERS",
                            "source_type": "EventBridgeBus",
                            "target_type": "Lambda"
                        })
                    
        return relationships
