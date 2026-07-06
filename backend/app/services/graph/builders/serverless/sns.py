from typing import List, Dict, Any
from app.models import ResourceDB

class SNSGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "SNSSubscription" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # SNS -> Lambda
                protocol = metadata.get("protocol")
                endpoint = metadata.get("endpoint", "")
                topic_arn = metadata.get("topic_arn")
                
                if protocol == "lambda" and topic_arn and endpoint:
                    # Endpoint is the Lambda ARN
                    relationships.append({
                        "from": topic_arn,
                        "to": endpoint,
                        "type": "TRIGGERS",
                        "source_type": "SNSTopic",
                        "target_type": "Lambda"
                    })

        return relationships
