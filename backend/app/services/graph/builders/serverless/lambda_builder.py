from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.builders.common import GraphBuilderHelper

class LambdaGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        edges = []
        resource_lookup = {r.resource_id: r.resource_type for r in resources}
        
        for res in resources:
                            "type": "IN_VPC",
                            "source_type": "Lambda",
                            "target_type": "VPC"
                        })
                    
                    for subnet_id in vpc_config.get("SubnetIds", []):
                        relationships.append({
                            "from": res.resource_id,
                            "to": subnet_id,
                            "type": "IN_SUBNET",
                            "source_type": "Lambda",
                            "target_type": "Subnet"
                        })
                    
                    for sg_id in vpc_config.get("SecurityGroupIds", []):
                        relationships.append({
                            "from": res.resource_id,
                            "to": sg_id,
                            "type": "USES_SG",
                            "source_type": "Lambda",
                            "target_type": "SecurityGroup"
                        })

        return relationships
