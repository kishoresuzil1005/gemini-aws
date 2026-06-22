import boto3

from app.services.aws.region_service import (
    AWSRegionService
)


class VPCInventoryService:

    @staticmethod
    def get_all_vpcs():

        results = []

        regions = AWSRegionService.get_all_regions()

        for region in regions:

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                response = ec2.describe_vpcs()

                for vpc in response["Vpcs"]:

                    results.append({

                        "vpc_id":
                            vpc["VpcId"],

                        "cidr":
                            vpc["CidrBlock"],

                        "state":
                            vpc["State"],

                        "region":
                            region,

                        "is_default":
                            vpc.get(
                                "IsDefault",
                                False
                            )
                    })

            except Exception:
                pass

        return results
