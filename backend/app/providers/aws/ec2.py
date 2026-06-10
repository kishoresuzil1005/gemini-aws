from .auth import get_aws_client
import boto3

class EC2Discovery:

    @staticmethod
    def discover(region):

        client = boto3.client(
            "ec2",
            region_name=region
        )

        response = client.describe_instances()

        instances = []

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:

                instances.append({
                    "resource_id": instance["InstanceId"],
                    "resource_type": "EC2",
                    "region": region,
                    "instance_type": instance.get("InstanceType"),
                    "state": instance["State"]["Name"],
                    "launch_time": str(
                        instance.get("LaunchTime")
                    ),
                    "subnet_id": instance.get("SubnetId"),
                    "vpc_id": instance.get("VpcId"),
                    "security_groups": [sg.get("GroupId") for sg in instance.get("SecurityGroups", [])]
                })

        return instances