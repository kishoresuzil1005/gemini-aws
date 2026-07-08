import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class NetworkInterfaceDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_network_interfaces')
            interfaces = []
            
            for page in paginator.paginate():
                for eni in page.get('NetworkInterfaces', []):
                    tags = {t['Key']: t['Value'] for t in eni.get('TagSet', [])}
                    name = tags.get('Name', eni['NetworkInterfaceId'])
                    
                    dependencies = []
                    security_groups = [sg['GroupId'] for sg in eni.get('Groups', []) if sg.get('GroupId')]
                    attachment = eni.get('Attachment', {})
                    
                    vpc_id = eni.get('VpcId')
                    subnet_id = eni.get('SubnetId')
                    
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                    if subnet_id:
                        dependencies.append(ResourceDependency(type='Subnet', id=subnet_id))
                    for sg in security_groups:
                        dependencies.append(ResourceDependency(type='SecurityGroup', id=sg))
                        
                    res = NormalizedResource(
                        resource_id=eni['NetworkInterfaceId'],
                        resource_type='NetworkInterface',
                        region=region,
                        name=name,
                        status=eni.get('Status', 'Unknown'),
                        metadata={
                            'description': eni.get('Description'),
                            'interface_type': eni.get('InterfaceType'),
                            'private_ip': eni.get('PrivateIpAddress'),
                            'mac_address': eni.get('MacAddress'),
                            'owner_id': eni.get('OwnerId'),
                            'requester_id': eni.get('RequesterId'),
                            'requester_managed': eni.get('RequesterManaged')
                        },
                        security={
                            'security_groups': security_groups
                        },
                        configuration={
                            'vpc_id': vpc_id,
                            'subnet_id': subnet_id,
                            'attachment': attachment,
                            'source_dest_check': eni.get('SourceDestCheck', True)
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    interfaces.append(res.dict())
                    
            return interfaces
        except Exception:
            logger.exception('Network Interface discovery failed for region %s', region)
            return []