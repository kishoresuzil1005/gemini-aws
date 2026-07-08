from typing import List, Dict, Any
from app.models import ResourceDB

class EC2GraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        
        for res in resources:
            if res.resource_type != "EC2":
                continue
                
            metadata = res.resource_metadata or {}
            config = metadata.get("configuration", {})
            security = metadata.get("security", {})
            
            # EC2 -> VPC
            vpc_id = config.get("vpc_id")
            if vpc_id:
                relationships.append({
                    "from": res.resource_id,
                    "to": vpc_id,
                    "type": "IN_VPC",
                    "source_type": "EC2",
                    "target_type": "VPC"
                })
                
            # EC2 -> Subnet
            subnet_id = config.get("subnet_id")
            if subnet_id:
                relationships.append({
                    "from": res.resource_id,
                    "to": subnet_id,
                    "type": "IN_SUBNET",
                    "source_type": "EC2",
                    "target_type": "Subnet"
                })
                
            # EC2 -> EBS Volumes
            for ebs_id in config.get("ebs_volumes", []):
                if ebs_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": ebs_id,
                        "type": "ATTACHED_TO",
                        "source_type": "EC2",
                        "target_type": "EBS"
                    })
                    
            # EC2 -> Security Groups
            for sg_id in security.get("security_groups", []):
                if sg_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": sg_id,
                        "type": "USES_SG",
                        "source_type": "EC2",
                        "target_type": "SecurityGroup"
                    })
                    
            # EC2 -> IAM Role / Instance Profile
            iam_profile = security.get("iam_instance_profile")
            if iam_profile:
                relationships.append({
                    "from": res.resource_id,
                    "to": iam_profile,
                    "type": "USES_ROLE",
                    "source_type": "EC2",
                    "target_type": "IAM"
                })
                
        return relationships
