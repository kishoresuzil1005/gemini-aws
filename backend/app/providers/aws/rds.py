import boto3

class RDSDiscovery:
    @staticmethod
    def discover(region):
        try:
            client = boto3.client("rds", region_name=region)
            response = client.describe_db_instances()
            rds_instances = []
            for db in response.get("DBInstances", []):
                rds_instances.append({
                    "resource_id": db["DBInstanceIdentifier"],
                    "resource_type": "RDS",
                    "region": region,
                    "engine": db.get("Engine"),
                    "class": db.get("DBInstanceClass"),
                    "status": db.get("DBInstanceStatus"),
                    "multi_az": db.get("MultiAZ", False)
                })
            return rds_instances
        except Exception:
            return []
