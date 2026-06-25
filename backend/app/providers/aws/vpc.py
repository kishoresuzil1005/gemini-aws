import boto3

class VPCDiscovery:
    @staticmethod
    def discover(region):
        try:
            client = boto3.client("ec2", region_name=region)
            response = client.describe_vpcs()
            vpcs = []
            for vpc in response.get("Vpcs", []):
                # Fetch route tables or subnets count if needed
                vpcs.append({
                    "resource_id": vpc["VpcId"],
                    "resource_type": "VPC",
                    "region": region,
                    "cidr_block": vpc.get("CidrBlock"),
                    "state": vpc.get("State"),
                    "is_default": vpc.get("IsDefault", False)
                })
            return vpcs
        except Exception:
            return []
