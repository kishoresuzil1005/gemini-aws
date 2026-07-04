from typing import List
from app.models import ResourceDB

class EC2GraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[dict]:
        relationships = []
        for res in resources:
            if res.resource_type == "EC2" and res.metadata:
                metadata = res.metadata
                # EC2 -> VPC
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "EC2",
                        "target_type": "VPC"
                    })
                # EC2 -> Subnet
                subnet_id = metadata.get("subnet_id")
                if subnet_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": subnet_id,
                        "type": "IN_SUBNET",
                        "source_type": "EC2",
                        "target_type": "Subnet"
                    })
        return relationships
