import boto3


class EC2SecurityMappingService:

    @staticmethod
    def get_all_regions():

        ec2 = boto3.client(
            "ec2",
            region_name="us-east-1"
        )

        return [
            r["RegionName"]
            for r in ec2.describe_regions()["Regions"]
        ]

    @classmethod
    def get_instance_security_groups(
        cls,
        instance_id
    ):

        for region in cls.get_all_regions():

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                response = ec2.describe_instances(
                    InstanceIds=[
                        instance_id
                    ]
                )

                reservations = response.get(
                    "Reservations",
                    []
                )

                if not reservations:
                    continue

                instance = (
                    reservations[0]
                    ["Instances"][0]
                )

                name = ""

                for tag in instance.get(
                    "Tags",
                    []
                ):
                    if tag["Key"] == "Name":
                        name = tag["Value"]

                return {

                    "instance_id":
                        instance["InstanceId"],

                    "instance_name":
                        name,

                    "instance_type":
                        instance.get(
                            "InstanceType"
                        ),

                    "state":
                        instance["State"][
                            "Name"
                        ],

                    "region":
                        region,

                    "security_groups": [
                        {
                            "group_id":
                                sg["GroupId"],

                            "group_name":
                                sg["GroupName"]
                        }
                        for sg in instance.get(
                            "SecurityGroups",
                            []
                        )
                    ]
                }

            except Exception:
                continue

        return None
