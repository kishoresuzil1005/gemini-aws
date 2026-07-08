import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class Route53Discovery:
    @staticmethod
    def discover(region: str='us-east-1') -> list[dict]:
        """Route53 is a global service."""
        resources = []
        try:
            client = boto3.client('route53', region_name='us-east-1')
            paginator = client.get_paginator('list_hosted_zones')
            for page in paginator.paginate():
                for zone in page.get('HostedZones', []):
                    zone_id = zone['Id'].split('/')[-1]
                    zone_name = zone.get('Name', '').rstrip('.')
                    
                    is_private = zone.get('Config', {}).get('PrivateZone', False)
                    vpc_dependencies = []
                    if is_private:
                        try:
                            # Fetch VPCs for private hosted zones if possible
                            hz_resp = client.get_hosted_zone(Id=zone_id)
                            for vpc in hz_resp.get('VPCs', []):
                                if vpc.get('VPCId'):
                                    vpc_dependencies.append(ResourceDependency(type='VPC', id=vpc['VPCId']))
                        except Exception:
                            pass
                    
                    hz_res = NormalizedResource(
                        resource_id=zone_id,
                        resource_type='Route53HostedZone',
                        region='global',
                        name=zone_name,
                        status='Active',
                        metadata={
                            'private': is_private,
                            'record_count': zone.get('ResourceRecordSetCount', 0),
                            'comment': zone.get('Config', {}).get('Comment', '')
                        },
                        configuration={},
                        dependencies=vpc_dependencies
                    )
                    resources.append(hz_res.dict())
                    
                    try:
                        record_paginator = client.get_paginator('list_resource_record_sets')
                        for record_page in record_paginator.paginate(HostedZoneId=zone_id):
                            for record in record_page.get('ResourceRecordSets', []):
                                record_name = record.get('Name', '').rstrip('.')
                                record_type = record.get('Type')
                                alias_target = record.get('AliasTarget', {})
                                alias_dns = alias_target.get('DNSName', '')
                                values = [r.get('Value', '') for r in record.get('ResourceRecords', [])]
                                
                                rec_dependencies = [ResourceDependency(type='Route53HostedZone', id=zone_id)]
                                
                                rec_res = NormalizedResource(
                                    resource_id=f'{zone_id}/{record_name}/{record_type}',
                                    resource_type='Route53Record',
                                    region='global',
                                    name=record_name,
                                    status='Active',
                                    metadata={
                                        'zone_id': zone_id,
                                        'zone_name': zone_name,
                                        'record_type': record_type,
                                        'ttl': record.get('TTL'),
                                        'is_alias': bool(alias_target),
                                        'alias_dns': alias_dns.rstrip('.'),
                                        'values': values,
                                        'set_identifier': record.get('SetIdentifier', ''),
                                        'routing_policy': record.get('Failover', record.get('Region', ''))
                                    },
                                    configuration={
                                        'alias_target': alias_target
                                    },
                                    dependencies=rec_dependencies
                                )
                                resources.append(rec_res.dict())
                    except Exception:
                        logger.exception('Route53 record set scan failed for zone %s', zone_id)
        except Exception:
            logger.exception('Route53 discovery failed')
        return resources