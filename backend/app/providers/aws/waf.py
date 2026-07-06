import boto3
import logging
logger = logging.getLogger(__name__)

class WAFDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('wafv2', region_name=region)
            for scope in ('REGIONAL', 'CLOUDFRONT') if region == 'us-east-1' else ('REGIONAL',):
                try:
                    next_marker = None
                    while True:
                        kwargs = {'Scope': scope, 'Limit': 50}
                        if next_marker:
                            kwargs['NextMarker'] = next_marker
                        response = client.list_web_acls(**kwargs)
                        for acl in response.get('WebACLs', []):
                            acl_id = acl['Id']
                            acl_arn = acl['ARN']
                            acl_name = acl['Name']
                            rule_count = 0
                            try:
                                detail = client.get_web_acl(Name=acl_name, Scope=scope, Id=acl_id)
                                rule_count = len(detail.get('WebACL', {}).get('Rules', []))
                                capacity = detail.get('WebACL', {}).get('Capacity', 0)
                                managed_by = detail.get('WebACL', {}).get('ManagedByFirewallManager', False)
                            except Exception:
                                capacity = 0
                                managed_by = False
                            associations = []
                            try:
                                assoc_resp = client.list_resources_for_web_acl(WebACLArn=acl_arn, ResourceType='APPLICATION_LOAD_BALANCER')
                                associations.extend(assoc_resp.get('ResourceArns', []))
                                assoc_resp_cf = client.list_resources_for_web_acl(WebACLArn=acl_arn, ResourceType='API_GATEWAY')
                                associations.extend(assoc_resp_cf.get('ResourceArns', []))
                            except Exception:
                                pass
                            resources.append({'resource_id': acl_arn, 'resource_type': 'WAFWebACL', 'region': 'global' if scope == 'CLOUDFRONT' else region, 'name': acl_name, 'provider': 'AWS', 'metadata': {'arn': acl_arn, 'scope': scope, 'rule_count': rule_count, 'capacity': capacity, 'managed_by_firewall_manager': managed_by, 'associated_resources': associations}, 'dependencies': []})
                        next_marker = response.get('NextMarker')
                        if not next_marker:
                            break
                except Exception:
                    logger.exception('WAFv2 %s scope discovery failed for region %s', scope, region)
        except Exception:
            logger.exception('WAFv2 discovery failed for region %s', region)
        return resources