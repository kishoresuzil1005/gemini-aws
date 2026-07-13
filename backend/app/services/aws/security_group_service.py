import boto3


class SecurityGroupService:

    @staticmethod
    def get_all_regions():

        ec2 = boto3.client("ec2", region_name="us-east-1")

        regions = ec2.describe_regions()["Regions"]

        return [
            r["RegionName"]
            for r in regions
        ]

    @classmethod
    def get_all_security_groups(cls):

        groups = []

        for region in cls.get_all_regions():

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                response = ec2.describe_security_groups()

                for sg in response["SecurityGroups"]:

                    groups.append({
                        "group_id": sg["GroupId"],
                        "group_name": sg["GroupName"],
                        "description": sg.get("Description"),
                        "vpc_id": sg.get("VpcId"),
                        "region": region,
                        "inbound_rules":
                            len(
                                sg.get(
                                    "IpPermissions",
                                    []
                                )
                            ),
                        "outbound_rules":
                            len(
                                sg.get(
                                    "IpPermissionsEgress",
                                    []
                                )
                            )
                    })

            except Exception:
                continue

        return groups

    @classmethod
    def get_security_group_details(
        cls,
        group_id: str
    ):

        for region in cls.get_all_regions():

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                response = ec2.describe_security_groups(
                    GroupIds=[group_id]
                )

                if not response["SecurityGroups"]:
                    continue

                sg = response["SecurityGroups"][0]

                inbound_rules = []

                for rule in sg.get(
                    "IpPermissions",
                    []
                ):

                    for ip in rule.get(
                        "IpRanges",
                        []
                    ):

                        inbound_rules.append({
                            "protocol":
                                rule.get(
                                    "IpProtocol"
                                ),
                            "from_port":
                                rule.get(
                                    "FromPort"
                                ),
                            "to_port":
                                rule.get(
                                    "ToPort"
                                ),
                            "source":
                                ip.get(
                                    "CidrIp"
                                )
                        })

                outbound_rules = []

                for rule in sg.get(
                    "IpPermissionsEgress",
                    []
                ):

                    for ip in rule.get(
                        "IpRanges",
                        []
                    ):

                        outbound_rules.append({
                            "protocol":
                                rule.get(
                                    "IpProtocol"
                                ),
                            "from_port":
                                rule.get(
                                    "FromPort"
                                ),
                            "to_port":
                                rule.get(
                                    "ToPort"
                                ),
                            "destination":
                                ip.get(
                                    "CidrIp"
                                )
                        })

                return {

                    "group_id":
                        sg["GroupId"],

                    "group_name":
                        sg["GroupName"],

                    "description":
                        sg.get(
                            "Description"
                        ),

                    "vpc_id":
                        sg.get(
                            "VpcId"
                        ),

                    "region":
                        region,

                    "inbound_rules":
                        inbound_rules,

                    "outbound_rules":
                        outbound_rules
                }

            except Exception:
                continue

        return None

    @classmethod
    def handle(cls, msg: str):
        message = msg.lower()

        # ----------------------------------
        # SECURITY GROUP COUNT
        # ----------------------------------

        if (
            "security group" in message
            and "how many" in message
        ):
            groups = cls.get_all_security_groups()
            return {
                "success": True,
                "response": f"You have {len(groups)} security groups."
            }

        # ----------------------------------
        # LIST SECURITY GROUPS
        # ----------------------------------

        if (
            "list" in message
            and "security group" in message
        ):
            groups = cls.get_all_security_groups()
            return {
                "success": True,
                "total": len(groups),
                "security_groups": groups
            }

        # ----------------------------------
        # SECURITY GROUP DETAILS
        # ----------------------------------

        if (
            "security group" in message
            and "sg-" in message
        ):
            import re

            match = re.search(
                r"(sg-[a-zA-Z0-9]+)",
                msg,
                re.IGNORECASE
            )

            if match:
                group_id = match.group(1)
                details = cls.get_security_group_details(group_id)

                if details:
                    return {
                        "success": True,
                        "security_group": details
                    }

                return {
                    "success": False,
                    "message": "Security group not found"
                }

        # ----------------------------------
        # EC2 SECURITY GROUP MAPPING BY ID
        # ----------------------------------

        if (
            "security group" in message
            and "i-" in message
        ):
            import re
            from app.services.aws.ec2_security_mapping_service import (
                EC2SecurityMappingService
            )

            match = re.search(
                r"(i-[a-zA-Z0-9]+)",
                msg,
                re.IGNORECASE
            )

            if match:
                instance_id = match.group(1)
                result = (
                    EC2SecurityMappingService
                    .get_instance_security_groups(instance_id)
                )

                if result:
                    return {
                        "success": True,
                        "instance": result
                    }

                return {
                    "success": False,
                    "message": "Instance not found"
                }

        # ----------------------------------
        # EC2 SECURITY GROUP MAPPING BY NAME
        # ----------------------------------

        if (
            "security group" in message
            or "network security" in message
        ):
            from app.services.aws.ec2_security_mapping_service import (
                EC2SecurityMappingService
            )

            skip_words = [
                "show",
                "security",
                "groups",
                "group",
                "for",
                "describe",
                "network",
                "attached",
                "instance",
                "to"
            ]

            words = msg.split()
            filtered = []

            for word in words:
                clean = (
                    word
                    .replace("?", "")
                    .replace(",", "")
                )

                if clean.lower() not in skip_words:
                    filtered.append(clean)

            if filtered:
                instance_name = filtered[-1]
                result = (
                    EC2SecurityMappingService
                    .get_instance_by_name(instance_name)
                )

                if result:
                    return {
                        "success": True,
                        "instance": result
                    }

        return None
