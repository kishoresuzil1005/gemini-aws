from typing import Dict, Any, List
from ..ec2_service import EC2Service
from ..vpc_service import VPCService
from ..iam_service import IAMService
from ..rds_service import RDSService
from ..s3_service import S3Service

class ResourceDiscovery:
    """
    Crawls AWS APIs to pull raw resource definitions across all supported services.
    """
    def __init__(self, client_manager):
        self.ec2 = EC2Service(client_manager)
        self.vpc = VPCService(client_manager)
        self.iam = IAMService(client_manager)
        self.rds = RDSService(client_manager)
        self.s3 = S3Service(client_manager)

    def discover_all(self) -> Dict[str, List[Any]]:
        print("[ResourceDiscovery] Fetching resources from AWS APIs...")
        
        inventory = {
            "ec2_instances": self.ec2.describe_instances(),
            "vpcs": self.vpc.describe_vpcs(),
            "subnets": self.vpc.describe_subnets(),
            "security_groups": self.vpc.describe_security_groups(),
            "iam_roles": self.iam.list_roles(),
            "rds_instances": self.rds.describe_db_instances(),
            "s3_buckets": self.s3.list_buckets()
        }
        
        print(f"[ResourceDiscovery] Found {len(inventory['ec2_instances'])} EC2 instances.")
        return inventory
