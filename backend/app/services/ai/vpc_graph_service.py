import boto3

from app.services.aws.aws_regions import (
    get_all_regions
)


class VPCGraphService:

    def get_vpc_graph(
        self,
        vpc_id: str
    ):

        ec2_resources = []
        subnet_resources = []
        security_group_resources = []
        rds_resources = []

        for region in get_all_regions():

            try:

                ec2 = boto3.client(
                    "ec2",
                    region_name=region
                )

                rds = boto3.client(
                    "rds",
                    region_name=region
                )

                # -------------------
                # EC2 Instances
                # -------------------

                reservations = ec2.describe_instances()[
                    "Reservations"
                ]

                for reservation in reservations:

                    for instance in reservation[
                        "Instances"
                    ]:

                        if (
                            instance.get(
                                "VpcId"
                            ) != vpc_id
                        ):
                            continue

                        name = ""

                        for tag in instance.get(
                            "Tags",
                            []
                        ):

                            if (
                                tag["Key"]
                                == "Name"
                            ):
                                name = tag[
                                    "Value"
                                ]

                        ec2_resources.append({

                            "instance_id":
                                instance[
                                    "InstanceId"
                                ],

                            "name":
                                name,

                            "state":
                                instance[
                                    "State"
                                ][
                                    "Name"
                                ],

                            "instance_type":
                                instance[
                                    "InstanceType"
                                ],

                            "region":
                                region
                        })

                # -------------------
                # Subnets
                # -------------------

                subnets = ec2.describe_subnets()[
                    "Subnets"
                ]

                for subnet in subnets:

                    if (
                        subnet[
                            "VpcId"
                        ]
                        != vpc_id
                    ):
                        continue

                    subnet_resources.append({

                        "subnet_id":
                            subnet[
                                "SubnetId"
                            ],

                        "cidr":
                            subnet[
                                "CidrBlock"
                            ],

                        "availability_zone":
                            subnet[
                                "AvailabilityZone"
                            ],

                        "region":
                            region
                    })

                # -------------------
                # Security Groups
                # -------------------

                groups = ec2.describe_security_groups()[
                    "SecurityGroups"
                ]

                for sg in groups:

                    if (
                        sg[
                            "VpcId"
                        ]
                        != vpc_id
                    ):
                        continue

                    security_group_resources.append({

                        "group_id":
                            sg[
                                "GroupId"
                            ],

                        "group_name":
                            sg[
                                "GroupName"
                            ],

                        "description":
                            sg[
                                "Description"
                            ],

                        "region":
                            region
                    })

                # -------------------
                # RDS
                # -------------------

                databases = rds.describe_db_instances()[
                    "DBInstances"
                ]

                for db in databases:

                    db_vpc = (
                        db.get(
                            "DBSubnetGroup",
                            {}
                        ).get(
                            "VpcId"
                        )
                    )

                    if db_vpc != vpc_id:
                        continue

                    rds_resources.append({

                        "db_identifier":
                            db[
                                "DBInstanceIdentifier"
                            ],

                        "engine":
                            db[
                                "Engine"
                            ],

                        "status":
                            db[
                                "DBInstanceStatus"
                            ],

                        "region":
                            region
                    })

            except Exception:
                continue

        return {

            "vpc_id":
                vpc_id,

            "summary": {

                "instances":
                    len(
                        ec2_resources
                    ),

                "subnets":
                    len(
                        subnet_resources
                    ),

                "security_groups":
                    len(
                        security_group_resources
                    ),

                "rds":
                    len(
                        rds_resources
                    )
            },

            "resources": {

                "ec2":
                    ec2_resources,

                "subnets":
                    subnet_resources,

                "security_groups":
                    security_group_resources,

                "rds":
                    rds_resources
            }
        }
