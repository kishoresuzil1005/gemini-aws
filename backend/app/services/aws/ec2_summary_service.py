import boto3


class EC2SummaryService:

    def __init__(self, region: str):

        self.region = region

        self.ec2 = boto3.client(
            "ec2",
            region_name=region
        )

    def get_summary(self):

        running_instances = 0
        total_instances = 0

        reservations = self.ec2.describe_instances()

        for reservation in reservations["Reservations"]:

            instances = reservation["Instances"]

            total_instances += len(instances)

            for instance in instances:

                if (
                    instance["State"]["Name"]
                    == "running"
                ):
                    running_instances += 1

        instance_types = len(
            self.ec2.describe_instance_types()[
                "InstanceTypes"
            ]
        )

        security_groups = len(
            self.ec2.describe_security_groups()[
                "SecurityGroups"
            ]
        )

        elastic_ips = len(
            self.ec2.describe_addresses()[
                "Addresses"
            ]
        )

        volumes = len(
            self.ec2.describe_volumes()[
                "Volumes"
            ]
        )

        snapshots = len(
            self.ec2.describe_snapshots(
                OwnerIds=["self"]
            )["Snapshots"]
        )

        return {

            "running_instances":
                running_instances,

            "total_instances":
                total_instances,

            "instance_types":
                instance_types,

            "security_groups":
                security_groups,

            "elastic_ips":
                elastic_ips,

            "volumes":
                volumes,

            "snapshots":
                snapshots
        }
