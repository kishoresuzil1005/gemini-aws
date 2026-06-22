import boto3


class RDSInventoryService:

    @staticmethod
    def get_all_regions():

        ec2 = boto3.client(
            "ec2",
            region_name="us-east-1"
        )

        response = ec2.describe_regions()

        return [
            r["RegionName"]
            for r in response["Regions"]
        ]

    @staticmethod
    def get_all_rds():

        databases = []

        for region in (
            RDSInventoryService
            .get_all_regions()
        ):

            try:

                rds = boto3.client(
                    "rds",
                    region_name=region
                )

                response = (
                    rds.describe_db_instances()
                )

                for db in (
                    response["DBInstances"]
                ):

                    databases.append({

                        "db_identifier":
                            db["DBInstanceIdentifier"],

                        "engine":
                            db["Engine"],

                        "engine_version":
                            db["EngineVersion"],

                        "status":
                            db["DBInstanceStatus"],

                        "instance_class":
                            db["DBInstanceClass"],

                        "region":
                            region,

                        "endpoint":
                            (
                                db.get(
                                    "Endpoint",
                                    {}
                                ).get(
                                    "Address"
                                )
                            )
                    })

            except Exception:
                pass

        return databases
