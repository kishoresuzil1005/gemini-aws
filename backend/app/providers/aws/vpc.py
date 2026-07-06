import boto3

class VPCDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_vpcs()
            vpcs = []
            for vpc in response.get('Vpcs', []):
                vpcs.append({'resource_id': vpc['VpcId'], 'resource_type': 'VPC', 'region': region, 'status': vpc.get('State'), 'provider': 'AWS', 'metadata': {'cidr_block': vpc.get('CidrBlock'), 'is_default': vpc.get('IsDefault', False)}, 'dependencies': []})
            return vpcs
        except Exception:
            return []