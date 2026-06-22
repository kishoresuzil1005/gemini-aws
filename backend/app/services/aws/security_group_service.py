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
