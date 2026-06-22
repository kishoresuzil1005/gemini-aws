import boto3

from app.core.region_validator import (
    validate_region
)
from app.core.aws_logger import log_aws_call


class EC2InstancesService:

    def __init__(self, region: str):

        self.region = validate_region(
            "ec2",
            region
        )

        self.ec2 = boto3.client(
            "ec2",
            region_name=self.region
        )

    def get_instances(self):

        log_aws_call("ec2", "describe_instances", self.region, "SUCCESS", "Fetch all regional instances")

        response = self.ec2.describe_instances()

        instances = []

        for reservation in response["Reservations"]:

            for instance in reservation["Instances"]:

                instances.append({

                    "instance_id":
                        instance["InstanceId"],

                    "instance_type":
                        instance.get(
                            "InstanceType",
                            "unknown"
                        ),

                    "state":
                        instance["State"]["Name"],

                    "region":
                        self.region,

                    "public_ip":
                        instance.get(
                            "PublicIpAddress"
                        ),

                    "private_ip":
                        instance.get(
                            "PrivateIpAddress"
                        )
                })

        return instances
