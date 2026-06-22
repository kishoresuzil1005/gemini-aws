import boto3


class EC2VPCService:

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

    def get_instance_vpc(
        self,
        instance_id: str
    ):

        regions = self.get_all_regions()

        for region in regions:

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                response = ec2.describe_instances(
                    InstanceIds=[instance_id]
                )

                for reservation in response["Reservations"]:

                    for instance in reservation["Instances"]:

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

                            "vpc_id":
                                instance.get(
                                    "VpcId"
                                ),

                            "region":
                                region
                        }

            except Exception:
                continue

        return None
