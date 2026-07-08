import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class ElasticIPDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_addresses()
            elastic_ips = []
            
            for address in response.get('Addresses', []):
                tags = {t['Key']: t['Value'] for t in address.get('Tags', [])}
                resource_id = address.get('AllocationId') or address.get('PublicIp')
                name = tags.get('Name', address.get('PublicIp'))
                
                dependencies = []
                eni_id = address.get('NetworkInterfaceId')
                if eni_id:
                    dependencies.append(ResourceDependency(type='NetworkInterface', id=eni_id))
                instance_id = address.get('InstanceId')
                if instance_id:
                    dependencies.append(ResourceDependency(type='EC2', id=instance_id))
                    
                res = NormalizedResource(
                    resource_id=resource_id,
                    resource_type='ElasticIP',
                    region=region,
                    name=name,
                    status='InUse' if address.get('AssociationId') else 'Unassociated',
                    metadata={
                        'public_ip': address.get('PublicIp'),
                        'private_ip': address.get('PrivateIpAddress'),
                        'allocation_id': address.get('AllocationId'),
                        'association_id': address.get('AssociationId'),
                        'domain': address.get('Domain')
                    },
                    configuration={
                        'instance_id': instance_id,
                        'network_interface_id': eni_id,
                        'network_interface_owner': address.get('NetworkInterfaceOwnerId'),
                        'public_ipv4_pool': address.get('PublicIpv4Pool')
                    },
                    tags=tags,
                    dependencies=dependencies
                )
                elastic_ips.append(res.dict())
                
            return elastic_ips
        except Exception:
            logger.exception('Elastic IP discovery failed for region %s', region)
            return []