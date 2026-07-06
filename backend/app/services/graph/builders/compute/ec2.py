from typing import List
from app.models import ResourceDB

class EC2GraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[dict]:
        relationships = []
        for res in resources:
            if res.resource_type == "EC2" and res.resource_metadata:
                metadata = res.resource_metadata
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
                # EC2 -> SecurityGroups
                for sg_id in metadata.get("security_groups", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": sg_id,
                        "type": "USES_SG",
                        "source_type": "EC2",
                        "target_type": "SecurityGroup"
                    })

                # EC2 -> IAM
                iam_arn = metadata.get("iam_instance_profile")
                if iam_arn:
                    relationships.append({
                        "from": res.resource_id,
                        "to": iam_arn,
                        "type": "USES_ROLE",
                        "source_type": "EC2",
                        "target_type": "IAM_ROLE"
                    })

                # EC2 -> EBS
                for vol in metadata.get("ebs_volumes", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": vol,
                        "type": "ATTACHED_TO",
                        "source_type": "EC2",
                        "target_type": "EBS"
                    })

        return relationships
