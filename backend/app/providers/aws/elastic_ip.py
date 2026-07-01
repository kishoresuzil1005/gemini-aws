import boto3
import logging

logger = logging.getLogger(__name__)


class ElasticIPDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client("ec2", region_name=region)
            response = client.describe_addresses()
            elastic_ips = []
            for address in response.get("Addresses", []):
                # AllocationId only exists for VPC EIPs; fall back to PublicIp for EC2-Classic
                resource_id = address.get("AllocationId") or address.get("PublicIp")
                elastic_ips.append({
                    "resource_id": resource_id,
                    "resource_type": "ElasticIP",
                    "region": region,
                    "name": address.get("PublicIp"),
                    "public_ip": address.get("PublicIp"),
                    "private_ip": address.get("PrivateIpAddress"),
                    "allocation_id": address.get("AllocationId"),
                    "association_id": address.get("AssociationId"),
                    "instance_id": address.get("InstanceId"),
                    "network_interface_id": address.get("NetworkInterfaceId"),
                    "network_interface_owner": address.get("NetworkInterfaceOwnerId"),
                    "domain": address.get("Domain")
                })
            return elastic_ips
        except Exception:
            logger.exception("Elastic IP discovery failed for region %s", region)
            return []
