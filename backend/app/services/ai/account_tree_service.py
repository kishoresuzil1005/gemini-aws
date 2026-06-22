import boto3

from app.services.aws.aws_regions import get_all_regions


class AccountTreeService:

    def generate_tree(self):

        tree = []

        tree.append("AWS ACCOUNT")

        regions = get_all_regions()

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

                instances = []

                for reservation in reservations:

                    for instance in reservation["Instances"]:

                        name = instance["InstanceId"]

                        for tag in instance.get(
                            "Tags",
                            []
                        ):

                            if tag["Key"] == "Name":

                                name = tag["Value"]

                        instances.append(name)

                databases = []

                for db in rds.describe_db_instances()[
                    "DBInstances"
                ]:

                    databases.append(
                        db["DBInstanceIdentifier"]
                    )

                if not instances and not databases:
                    continue

                tree.append(f"├── {region}")

                if instances:

                    tree.append(
                        f"│   ├── EC2 ({len(instances)})"
                    )

                    for instance in instances:

                        tree.append(
                            f"│   │   ├── {instance}"
                        )

                if databases:

                    tree.append(
                        f"│   ├── RDS ({len(databases)})"
                    )

                    for db in databases:

                        tree.append(
                            f"│   │   ├── {db}"
                        )

            except Exception:
                continue

        return "\n".join(tree)
