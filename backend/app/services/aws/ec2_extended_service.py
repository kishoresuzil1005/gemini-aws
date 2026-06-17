import boto3
import time
from concurrent.futures import ThreadPoolExecutor


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

    def get_launch_templates(self):
        try:
            return len(
                self.ec2.describe_launch_templates()[
                    "LaunchTemplates"
                ]
            )
        except Exception:
            return 0

    def get_spot_requests(self):
        try:
            return len(
                self.ec2
                .describe_spot_instance_requests()[
                    "SpotInstanceRequests"
                ]
            )
        except Exception:
            return 0

    def get_reserved_instances(self):
        try:
            return len(
                self.ec2
                .describe_reserved_instances()[
                    "ReservedInstances"
                ]
            )
        except Exception:
            return 0

    def get_dedicated_hosts(self):
        try:
            return len(
                self.ec2.describe_hosts()[
                    "Hosts"
                ]
            )
        except Exception:
            return 0

    def get_amis(self):
        try:
            return len(
                self.ec2.describe_images(
                    Owners=["self"]
                )["Images"]
            )
        except Exception:
            return 0

    def get_ami_catalog(self):
        try:
            return len(
                self.ec2.describe_images(
                    Owners=["amazon"]
                )["Images"]
            )
        except Exception:
            return 0

    def get_savings_plans(self):
        try:
            return len(
                self.savingsplans
                .describe_savings_plans()[
                    "savingsPlans"
                ]
            )
        except Exception:
            return 0

    def get_extended_summary(self):
        start = time.time()

        with ThreadPoolExecutor(max_workers=8) as executor:
            launch_templates_future = executor.submit(self.get_launch_templates)
            spot_requests_future = executor.submit(self.get_spot_requests)
            reserved_future = executor.submit(self.get_reserved_instances)
            hosts_future = executor.submit(self.get_dedicated_hosts)
            amis_future = executor.submit(self.get_amis)
            ami_catalog_future = executor.submit(self.get_ami_catalog)
            savings_future = executor.submit(self.get_savings_plans)

            res = {
                "launch_templates": launch_templates_future.result(),
                "spot_requests": spot_requests_future.result(),
                "reserved_instances": reserved_future.result(),
                "dedicated_hosts": hosts_future.result(),
                "amis": amis_future.result(),
                "ami_catalog": ami_catalog_future.result(),
                "savings_plans": savings_future.result()
            }

        print(f"[EC2 EXTENDED] {round(time.time() - start, 2)}s")
        return res
