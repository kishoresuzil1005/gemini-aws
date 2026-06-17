import boto3


class EC2ExtendedService:

    def __init__(self, region: str):

        self.region = region

        self.ec2 = boto3.client(
            "ec2",
            region_name=region
        )

        self.savingsplans = boto3.client(
            "savingsplans",
            region_name=region
        )

    def get_extended_summary(self):

        try:

            launch_templates = len(
                self.ec2.describe_launch_templates()[
                    "LaunchTemplates"
                ]
            )

        except Exception:
            launch_templates = 0

        try:

            spot_requests = len(
                self.ec2
                .describe_spot_instance_requests()[
                    "SpotInstanceRequests"
                ]
            )

        except Exception:
            spot_requests = 0

        try:

            reserved_instances = len(
                self.ec2
                .describe_reserved_instances()[
                    "ReservedInstances"
                ]
            )

        except Exception:
            reserved_instances = 0

        try:

            dedicated_hosts = len(
                self.ec2.describe_hosts()[
                    "Hosts"
                ]
            )

        except Exception:
            dedicated_hosts = 0

        try:

            amis = len(
                self.ec2.describe_images(
                    Owners=["self"]
                )["Images"]
            )

        except Exception:
            amis = 0

        try:

            ami_catalog = len(
                self.ec2.describe_images(
                    Owners=["amazon"]
                )["Images"]
            )

        except Exception:
            ami_catalog = 0

        try:

            savings_plans = len(
                self.savingsplans
                .describe_savings_plans()[
                    "savingsPlans"
                ]
            )

        except Exception:
            savings_plans = 0

        return {

            "launch_templates":
                launch_templates,

            "spot_requests":
                spot_requests,

            "reserved_instances":
                reserved_instances,

            "dedicated_hosts":
                dedicated_hosts,

            "amis":
                amis,

            "ami_catalog":
                ami_catalog,

            "savings_plans":
                savings_plans
        }
