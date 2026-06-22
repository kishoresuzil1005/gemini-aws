import boto3


class InventoryAIService:

    @staticmethod
    def get_all_regions():

        ec2 = boto3.client(
            "ec2",
            region_name="us-east-1"
        )

        response = ec2.describe_regions(
            AllRegions=False
        )

        return sorted([
            r["RegionName"]
            for r in response["Regions"]
        ])

    @staticmethod
    def get_name_tag(instance):
        for tag in instance.get("Tags", []):
            if tag["Key"] == "Name":
                return tag["Value"]
        return "-"

    @staticmethod
    def get_all_ec2_instances():

        results = []

        regions = (
            InventoryAIService
            .get_all_regions()
        )

        for region in regions:

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                response = ec2.describe_instances()

                for reservation in response["Reservations"]:

                    for instance in reservation["Instances"]:

                        results.append({
                            "instance_id":
                                instance["InstanceId"],
                            "name":
                                InventoryAIService.get_name_tag(
                                    instance
                                ),
                            "instance_type":
                                instance.get(
                                    "InstanceType"
                                ),
                            "state":
                                instance["State"]["Name"],
                            "region":
                                region,
                            "private_ip":
                                instance.get(
                                    "PrivateIpAddress"
                                ),
                            "public_ip":
                                instance.get(
                                    "PublicIpAddress"
                                ),
                            "launch_time":
                                str(
                                    instance.get(
                                        "LaunchTime"
                                    )
                                )
                        })

            except Exception as e:

                print(
                    f"Skipping {region}: {e}"
                )

        return results
