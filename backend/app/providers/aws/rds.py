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
                    "multi_az": db.get("MultiAZ", False),
                    "vpc_security_groups": db.get("VpcSecurityGroups", []),
                    "subnet_group": db.get("DBSubnetGroup", {})
                })
            return rds_instances
        except Exception:
            return []
