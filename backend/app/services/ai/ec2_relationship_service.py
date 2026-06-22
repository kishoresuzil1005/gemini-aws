import boto3


class EC2RelationshipService:

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

    def find_instance(
        self,
        search_value: str
    ):

        regions = self.get_all_regions()

        for region in regions:

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                reservations = ec2.describe_instances()[
                    "Reservations"
                ]

                for reservation in reservations:

                    for instance in reservation[
                        "Instances"
                    ]:

                        instance_id = instance[
                            "InstanceId"
                        ]

                        name = ""

                        for tag in instance.get(
                            "Tags",
                            []
                        ):

                            if tag["Key"] == "Name":

                                name = tag[
                                    "Value"
                                ]

                        if (
                            search_value.lower()
                            ==
                            instance_id.lower()
                        ):

                            return (
                                instance,
                                region,
                                name
                            )

                        if (
                            search_value.lower()
                            ==
                            name.lower()
                        ):

                            return (
                                instance,
                                region,
                                name
                            )

            except Exception:
                continue

        return None

    def get_instance_vpc(
        self,
        search_value: str
    ):

        result = self.find_instance(
            search_value
        )

        if not result:
            return None

        instance, region, name = result

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
