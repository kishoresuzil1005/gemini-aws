from app.services.ai.inventory_ai import InventoryAIService
from app.services.ai.rds_inventory import RDSInventoryService
from app.services.ai.s3_inventory import S3InventoryService
from app.services.ai.vpc_inventory import VPCInventoryService
from app.services.ai.subnet_inventory import SubnetInventoryService
from app.services.aws.security_group_service import SecurityGroupService


class AccountTopologyService:

    @classmethod
    def get_account_topology(cls):
        # 1. EC2 Count
        try:
            instances = InventoryAIService.get_all_ec2_instances()
        except Exception:
            instances = []
        
        total_ec2 = len(instances)
        running_ec2 = len([i for i in instances if i.get("state") == "running"])
        stopped_ec2 = len([i for i in instances if i.get("state") == "stopped"])

        # 2. RDS Count
        try:
            databases = RDSInventoryService.get_all_rds()
        except Exception:
            databases = []
        
        # 3. VPC Count
        try:
            vpcs = VPCInventoryService.get_all_vpcs()
        except Exception:
            vpcs = []
        
        # 4. Security Groups
        try:
            security_groups = SecurityGroupService.get_all_security_groups()
        except Exception:
            security_groups = []

        # 5. Subnets
        try:
            subnets = SubnetInventoryService.get_all_subnets()
        except Exception:
            subnets = []

        # 6. S3 Buckets
        try:
            buckets = S3InventoryService.get_all_buckets()
        except Exception:
            buckets = []

        return {
            "success": True,
            "topology": {
                "ec2": {
                    "total": total_ec2,
                    "running": running_ec2,
                    "stopped": stopped_ec2,
                    "instances_list": [
                        {
                            "instance_id": i.get("instance_id"),
                            "name": i.get("name"),
                            "state": i.get("state"),
                            "region": i.get("region")
                        } for i in instances
                    ]
                },
                "rds": {
                    "total": len(databases),
                    "databases_list": [
                        {
                            "db_identifier": d.get("db_identifier"),
                            "engine": d.get("engine"),
                            "status": d.get("status"),
                            "region": d.get("region")
                        } for d in databases
                    ]
                },
                "vpc": {
                    "total": len(vpcs),
                    "vpcs_list": [
                        {
                            "vpc_id": v.get("vpc_id"),
                            "cidr": v.get("cidr"),
                            "state": v.get("state"),
                            "region": v.get("region")
                        } for v in vpcs
                    ]
                },
                "security_groups": {
                    "total": len(security_groups),
                    "groups_list": [
                        {
                            "group_id": s.get("group_id"),
                            "group_name": s.get("group_name"),
                            "vpc_id": s.get("vpc_id"),
                            "region": s.get("region")
                        } for s in security_groups
                    ]
                },
                "subnets": {
                    "total": len(subnets),
                    "subnets_list": [
                        {
                            "subnet_id": s.get("subnet_id"),
                            "vpc_id": s.get("vpc_id"),
                            "cidr": s.get("cidr") or s.get("cidr_block"),
                            "region": s.get("region")
                        } for s in subnets
                    ]
                },
                "s3": {
                    "total": len(buckets),
                    "buckets_list": [
                        {
                            "bucket_name": b.get("bucket_name"),
                            "region": b.get("region")
                        } for b in buckets
                    ]
                }
            }
        }
