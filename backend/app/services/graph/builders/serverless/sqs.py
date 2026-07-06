from typing import List, Dict, Any
from app.models import ResourceDB

class SQSGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        # SQS -> Lambda triggers are typically defined via Lambda Event Source Mappings.
        # This acts as a placeholder for when that discovery is integrated,
        # or if the metadata includes 'lambda_triggers' in the future.
        for res in resources:
            if res.resource_type == "SQSQueue" and res.resource_metadata:
                metadata = res.resource_metadata
                
                for function_arn in metadata.get("lambda_triggers", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": function_arn,
                        "type": "TRIGGERS",
                        "source_type": "SQSQueue",
                        "target_type": "Lambda"
                    })

        return relationships
