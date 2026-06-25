import boto3
<<<<<<< HEAD
import logging
=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc

from app.core.region_validator import (
    validate_region
)
from app.core.aws_logger import log_aws_call

<<<<<<< HEAD
logger = logging.getLogger(__name__)

=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc

class EC2InstancesService:

    def __init__(self, region: str):

        self.region = validate_region(
            "ec2",
            region
        )

<<<<<<< HEAD
        try:
            self.ec2 = boto3.client(
                "ec2",
                region_name=self.region
            )
            self.has_credentials = True
        except Exception:
            self.has_credentials = False

    def get_instances(self):
        if not self.has_credentials:
            return self.get_mock_instances()

        try:
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
        except Exception as e:
            logger.warning(f"Failed to query EC2 instances: {e}, falling back to mock.")
            return self.get_mock_instances()

    def get_mock_instances(self):
        return [
            {
                "instance_id": "i-06d74665d9c16da17",
                "instance_type": "t2.medium",
                "state": "running",
                "region": self.region,
                "public_ip": "54.205.123.215",
                "private_ip": "10.0.1.53"
            },
            {
                "instance_id": "i-0f8a927a4d531a7bc",
                "instance_type": "t3.large",
                "state": "stopped",
                "region": self.region,
                "public_ip": "34.210.44.12",
                "private_ip": "10.0.2.14"
            }
        ]
=======
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
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
