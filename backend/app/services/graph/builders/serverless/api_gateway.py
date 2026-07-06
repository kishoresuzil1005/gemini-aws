from typing import List, Dict, Any
from app.models import ResourceDB

class APIGatewayGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "APIGatewayIntegration" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # APIGateway -> Lambda
                # Integration URI typically looks like arn:aws:apigateway:...:lambda:path/2015-03-31/functions/arn:aws:lambda:region:account:function:FunctionName/invocations
                integration_uri = metadata.get("integration_uri", "")
                if "lambda" in integration_uri and "function:" in integration_uri:
                    # Extract the function ARN or name
                    parts = integration_uri.split("function:")
                    if len(parts) > 1:
                        function_arn = parts[1].split("/")[0]
                        relationships.append({
                            "from": metadata.get("api_id", res.resource_id),
                            "to": function_arn,
                            "type": "INVOKES",
                            "source_type": "APIGateway",
                            "target_type": "Lambda"
                        })

        return relationships
