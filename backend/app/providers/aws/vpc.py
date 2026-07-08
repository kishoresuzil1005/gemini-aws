import boto3
from app.providers.aws.models import NormalizedResource, ResourceDependency

class VPCDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_vpcs()
            vpcs = []
            
            for vpc in response.get('Vpcs', []):
                tags = {t['Key']: t['Value'] for t in vpc.get('Tags', [])}
                name = tags.get('Name', vpc['VpcId'])
                
                res = NormalizedResource(
                    resource_id=vpc['VpcId'],
                    resource_type='VPC',
                    region=region,
                    name=name,
                    status=vpc.get('State', 'Unknown'),
                    metadata={
                        'cidr_block': vpc.get('CidrBlock'),
                        'is_default': vpc.get('IsDefault', False),
                        'instance_tenancy': vpc.get('InstanceTenancy')
                    },
                    configuration={
                        'dhcp_options_id': vpc.get('DhcpOptionsId')
                    },
                    tags=tags,
                    dependencies=[]
                )
                vpcs.append(res.dict())
                
            return vpcs
        except Exception as e:
            print(f"Error in VPCDiscovery: {e}")
            return []