import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

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
                            
                            tags = {}
                            try:
                                tags_resp = client.list_tags_for_resource(ResourceARN=acl_arn)
                                tags = {t['Key']: t['Value'] for t in tags_resp.get('TagInfoForResource', {}).get('TagList', [])}
                            except Exception: pass
                            
                            rule_count = 0
                            capacity = 0
                            managed_by = False
                            default_action = {}
                            try:
                                detail = client.get_web_acl(Name=acl_name, Scope=scope, Id=acl_id)
                                web_acl = detail.get('WebACL', {})
                                rule_count = len(web_acl.get('Rules', []))
                                capacity = web_acl.get('Capacity', 0)
                                managed_by = web_acl.get('ManagedByFirewallManager', False)
                                default_action = web_acl.get('DefaultAction', {})
                            except Exception:
                                pass
                                
                            associations = []
                            dependencies = []
                            try:
                                assoc_resp = client.list_resources_for_web_acl(WebACLArn=acl_arn, ResourceType='APPLICATION_LOAD_BALANCER')
                                for r in assoc_resp.get('ResourceArns', []):
                                    associations.append(r)
                                    dependencies.append(ResourceDependency(type='ALB', id=r))
                                    
                                assoc_resp_cf = client.list_resources_for_web_acl(WebACLArn=acl_arn, ResourceType='API_GATEWAY')
                                for r in assoc_resp_cf.get('ResourceArns', []):
                                    associations.append(r)
                                    dependencies.append(ResourceDependency(type='ApiGateway', id=r))
                            except Exception:
                                pass
                                
                            res = NormalizedResource(
                                resource_id=acl_arn,
                                resource_type='WAFWebACL',
                                region='global' if scope == 'CLOUDFRONT' else region,
                                name=acl_name,
                                status='Active',
                                metadata={
                                    'arn': acl_arn,
                                    'scope': scope,
                                    'rule_count': rule_count,
                                    'capacity': capacity,
                                    'managed_by_firewall_manager': managed_by,
                                    'default_action': default_action
                                },
                                configuration={
                                    'associated_resources': associations
                                },
                                tags=tags,
                                dependencies=dependencies
                            )
                            resources.append(res.dict())
                            
                        next_marker = response.get('NextMarker')
                        if not next_marker:
                            break
                except Exception:
                    logger.exception('WAFv2 %s scope discovery failed for region %s', scope, region)
        except Exception:
            logger.exception('WAFv2 discovery failed for region %s', region)
        return resources