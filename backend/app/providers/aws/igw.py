import boto3
from app.providers.aws.models import NormalizedResource, ResourceDependency

class IGWDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_internet_gateways()
            igws = []
            
            for igw in response.get('InternetGateways', []):
                tags = {t['Key']: t['Value'] for t in igw.get('Tags', [])}
                name = tags.get('Name', igw['InternetGatewayId'])
                
                dependencies = []
                attachments = igw.get('Attachments', [])
                vpc_id = None
                for attachment in attachments:
                    if attachment.get('VpcId'):
                        vpc_id = attachment['VpcId']
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                        
                res = NormalizedResource(
                    resource_id=igw['InternetGatewayId'],
                    resource_type='InternetGateway',
                    region=region,
                    name=name,
                    status='Active',
                    metadata={},
                    configuration={
                        'attachments': attachments,
                        'vpc_id': vpc_id
                    },
                    tags=tags,
                    dependencies=dependencies
                )
                igws.append(res.dict())
                
            return igws
        except Exception as e:
            print(f"Error in IGWDiscovery: {e}")
            return []