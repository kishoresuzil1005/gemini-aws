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

