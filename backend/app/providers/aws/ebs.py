import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class EBSDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_volumes')
            volumes = []
            
            for page in paginator.paginate():
                for vol in page.get('Volumes', []):
                    tags = {t['Key']: t['Value'] for t in vol.get('Tags', [])}
                    name = tags.get('Name', vol['VolumeId'])
                    
                    dependencies = []
                    attachments_list = []
                    for att in vol.get('Attachments', []):
                        if 'InstanceId' in att:
                            attachments_list.append(att['InstanceId'])
                            dependencies.append(ResourceDependency(type='EC2', id=att['InstanceId']))
                            
                    kms_key = vol.get('KmsKeyId')
                    if kms_key:
                        dependencies.append(ResourceDependency(type='KMSKey', id=kms_key))

                    res = NormalizedResource(
                        resource_id=vol['VolumeId'],
                        resource_type='EBSVolume',
                        region=region,
                        name=name,
                        status=vol.get('State', 'Unknown'),
                        metadata={
                            'size_gb': vol.get('Size'),
                            'volume_type': vol.get('VolumeType'),
                            'iops': vol.get('Iops'),
                            'throughput': vol.get('Throughput'),
                            'snapshot_id': vol.get('SnapshotId'),
                            'availability_zone': vol.get('AvailabilityZone')
                        },
                        security={
                            'encrypted': vol.get('Encrypted', False),
                            'kms_key_id': kms_key
                        },
                        configuration={
                            'multi_attach_enabled': vol.get('MultiAttachEnabled', False),
                            'fast_restored': vol.get('FastRestored', False),
                            'attachments': attachments_list
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    volumes.append(res.dict())
                    
            return volumes
        except Exception:
            logger.exception('EBS discovery failed for region %s', region)
            return []