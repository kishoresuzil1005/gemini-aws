from typing import List, Dict, Any
from app.models import ResourceDB


class LambdaGraphBuilder:

    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:

        relationships = []

        for res in resources:

            if res.resource_type != "Lambda":
                continue

            metadata = res.resource_metadata or {}

            # ------------------------
            # Lambda -> IAM Role
            # ------------------------

            role = metadata.get("role")

            if role:
                relationships.append({
                    "from": res.resource_id,
                    "to": role,
                    "type": "USES_ROLE",
                    "source_type": "Lambda",
                    "target_type": "IAM"
                })

            # ------------------------
            # Lambda -> Networking
            # ------------------------

            vpc_config = metadata.get("vpc_config", {})

            if not isinstance(vpc_config, dict):
                continue

            vpc_id = (
                vpc_config.get("VpcId")
                or vpc_config.get("VpcID")
                or vpc_config.get("vpc_id")
            )

            if vpc_id:

                relationships.append({
                    "from": res.resource_id,
                    "to": vpc_id,
                    "type": "IN_VPC",
                    "source_type": "Lambda",
                    "target_type": "VPC"
                })

            for subnet in (
                vpc_config.get("SubnetIds")
                or vpc_config.get("subnet_ids")
                or []
            ):

                relationships.append({
                    "from": res.resource_id,
                    "to": subnet,
                    "type": "IN_SUBNET",
                    "source_type": "Lambda",
                    "target_type": "Subnet"
                })

            for sg in (
                vpc_config.get("SecurityGroupIds")
                or vpc_config.get("security_group_ids")
                or []
            ):

                relationships.append({
                    "from": res.resource_id,
                    "to": sg,
                    "type": "USES_SG",
                    "source_type": "Lambda",
                    "target_type": "SecurityGroup"
                })

        return relationships
