import boto3

from app.services.aws.region_service import (
    AWSRegionService
)


class SubnetInventoryService:

    @staticmethod
    def get_all_subnets():

        results = []

        regions = (
            AWSRegionService
            .get_all_regions()
        )

        for region in regions:

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                response = (
                    ec2.describe_subnets()
                )

                for subnet in response["Subnets"]:

                    results.append({

                        "subnet_id":
                            subnet["SubnetId"],

                        "vpc_id":
                            subnet["VpcId"],

                        "cidr":
                            subnet["CidrBlock"],

                        "availability_zone":
                            subnet["AvailabilityZone"],

                        "available_ips":
                            subnet["AvailableIpAddressCount"],

                        "state":
                            subnet["State"],

                        "region":
                            region
                    })

            except Exception as e:

                print(
                    f"[SUBNET ERROR] "
                    f"{region}: {e}"
                )

        return results
