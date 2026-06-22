import boto3

from app.services.aws.aws_regions import (
    get_all_regions
)


class AccountTopologyService:

    def get_topology(self):

        regions = get_all_regions()

        total_ec2 = 0
        total_rds = 0
        total_vpcs = 0
        total_subnets = 0
        total_security_groups = 0

        regional_breakdown = {}

        for region in regions:

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                rds = boto3.client(
                    "rds",
                    region_name=region
                )

                reservations = ec2.describe_instances()[
                    "Reservations"
                ]

                ec2_count = sum(
                    len(r["Instances"])
                    for r in reservations
                )

                vpc_count = len(
                    ec2.describe_vpcs()[
                        "Vpcs"
                    ]
                )

                subnet_count = len(
                    ec2.describe_subnets()[
                        "Subnets"
                    ]
                )

                sg_count = len(
                    ec2.describe_security_groups()[
                        "SecurityGroups"
                    ]
                )

                rds_count = len(
                    rds.describe_db_instances()[
                        "DBInstances"
                    ]
                )

                total_ec2 += ec2_count
                total_vpcs += vpc_count
                total_subnets += subnet_count
                total_security_groups += sg_count
                total_rds += rds_count

                regional_breakdown[
                    region
                ] = {

                    "ec2":
                        ec2_count,

                    "rds":
                        rds_count,

                    "vpcs":
                        vpc_count,

                    "subnets":
                        subnet_count,

                    "security_groups":
                        sg_count
                }

            except Exception:
                continue

        # -------------------
        # S3
        # -------------------

        try:

            s3 = boto3.client(
                "s3"
            )

            total_s3 = len(
                s3.list_buckets()[
                    "Buckets"
                ]
            )

        except Exception:

            total_s3 = 0

        return {

            "regions":
                len(
                    regional_breakdown
                ),

            "resources": {

                "ec2":
                    total_ec2,

                "rds":
                    total_rds,

                "s3":
                    total_s3,

                "vpcs":
                    total_vpcs,

                "subnets":
                    total_subnets,

                "security_groups":
                    total_security_groups
            },

            "regional_breakdown":
                regional_breakdown
        }
