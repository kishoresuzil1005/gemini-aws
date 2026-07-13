import boto3

class ExposureService:

    @staticmethod
    def get_all_regions():

        ec2 = boto3.client(
            "ec2",
            region_name="us-east-1"
        )

        response = ec2.describe_regions()

        return [
            region["RegionName"]
            for region in response["Regions"]
        ]

    @staticmethod
    def get_public_instances():

        exposed = []

        for region in ExposureService.get_all_regions():

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                reservations = ec2.describe_instances()[
                    "Reservations"
                ]

                for reservation in reservations:

                    for instance in reservation["Instances"]:

                        public_ip = instance.get(
                            "PublicIpAddress"
                        )

                        if public_ip:

                            exposed.append({
                                "instance_id":
                                    instance["InstanceId"],

                                "name":
                                    next(
                                        (
                                            tag["Value"]
                                            for tag in instance.get(
                                                "Tags", []
                                            )
                                            if tag["Key"] == "Name"
                                        ),
                                        "Unknown"
                                    ),

                                "state":
                                    instance["State"]["Name"],

                                "region":
                                    region,

                                "public_ip":
                                    public_ip,

                                "private_ip":
                                    instance.get(
                                        "PrivateIpAddress"
                                    ),

                                "instance_type":
                                    instance[
                                        "InstanceType"
                                    ],

                                "risk":
                                    "PUBLICLY_ACCESSIBLE"
                            })

            except Exception as e:
                print(region, e)

        return expose