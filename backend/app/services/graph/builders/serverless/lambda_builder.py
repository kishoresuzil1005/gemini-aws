from typing import List, Dict, Any
from app.models import ResourceDB

class LambdaGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "Lambda" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # Lambda -> IAM
                role_arn = metadata.get("role")
                if role_arn:
                    relationships.append({
                        "from": res.resource_id,
                        "to": role_arn,
                        "type": "USES_ROLE",
                        "source_type": "Lambda",
                        "target_type": "IAM_ROLE"
                    })
                
                # Lambda -> VPC & Subnets & Security Groups
                vpc_config = metadata.get("vpc_config", {})
                if isinstance(vpc_config, dict):
                    vpc_id = vpc_config.get("VpcId")
                    if vpc_id:
                        relationships.append({
                            "from": res.resource_id,
                            "to": vpc_id,
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
