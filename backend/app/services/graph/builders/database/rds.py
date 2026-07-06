from typing import List, Dict, Any
from app.models import ResourceDB

class RDSGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "RDS" and res.resource_metadata:
                metadata = res.resource_metadata
                
                subnet_group = metadata.get("subnet_group", {})
                
                # RDS -> VPC
                vpc_id = subnet_group.get("VpcId")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "RDS",
                        "target_type": "VPC"
                    })
                
                # RDS -> Subnet
                for subnet in subnet_group.get("Subnets", []):
                    subnet_id = subnet.get("SubnetIdentifier")
                    if subnet_id:
                        relationships.append({
                            "from": res.resource_id,
                            "to": subnet_id,
                            "type": "IN_SUBNET",
                            "source_type": "RDS",
                            "target_type": "Subnet"
                        })
                
                # RDS -> SecurityGroup
                for sg in metadata.get("vpc_security_groups", []):
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
