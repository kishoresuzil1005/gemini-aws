import boto3
import logging
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
                    resources.append({'resource_id': zone_id, 'resource_type': 'Route53HostedZone', 'region': 'global', 'name': zone_name, 'provider': 'AWS', 'metadata': {'private': zone.get('Config', {}).get('PrivateZone', False), 'record_count': zone.get('ResourceRecordSetCount', 0), 'comment': zone.get('Config', {}).get('Comment', '')}, 'dependencies': []})
                    try:
                        record_paginator = client.get_paginator('list_resource_record_sets')
                        for record_page in record_paginator.paginate(HostedZoneId=zone_id):
                            for record in record_page.get('ResourceRecordSets', []):
                                record_name = record.get('Name', '').rstrip('.')
                                record_type = record.get('Type')
                                alias_target = record.get('AliasTarget', {})
                                alias_dns = alias_target.get('DNSName', '')
                                values = [r.get('Value', '') for r in record.get('ResourceRecords', [])]
                                resources.append({'resource_id': f'{zone_id}/{record_name}/{record_type}', 'resource_type': 'Route53Record', 'region': 'global', 'name': record_name, 'provider': 'AWS', 'metadata': {'zone_id': zone_id, 'zone_name': zone_name, 'record_type': record_type, 'ttl': record.get('TTL'), 'is_alias': bool(alias_target), 'alias_dns': alias_dns.rstrip('.'), 'values': values, 'set_identifier': record.get('SetIdentifier', ''), 'routing_policy': record.get('Failover', record.get('Region', ''))}, 'dependencies': []})
                    except Exception:
                        logger.exception('Route53 record set scan failed for zone %s', zone_id)
        except Exception:
            logger.exception('Route53 discovery failed')
        return resources