import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class TargetGroupDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('elbv2', region_name=region)
            paginator = client.get_paginator('describe_target_groups')
            target_groups = []
            
            for page in paginator.paginate():
                for tg in page.get('TargetGroups', []):
                    tg_arn = tg['TargetGroupArn']
                    
                    tags = {}
                    try:
                        tags_resp = client.describe_tags(ResourceArns=[tg_arn])
                        if tags_resp.get('TagDescriptions'):
                            tags = {t['Key']: t['Value'] for t in tags_resp['TagDescriptions'][0].get('Tags', [])}
                    except Exception: pass
                    
                    dependencies = []
                    vpc_id = tg.get('VpcId')
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                        
                    load_balancers = list(tg.get('LoadBalancerArns', []))
                    for lb in load_balancers:
                        dependencies.append(ResourceDependency(type='ALB', id=lb))

                    targets = []
                    try:
                        health_resp = client.describe_target_health(TargetGroupArn=tg_arn)
                        for t in health_resp.get('TargetHealthDescriptions', []):
                            target_id = t.get('Target', {}).get('Id')
                            target_port = t.get('Target', {}).get('Port')
                            health_state = t.get('TargetHealth', {}).get('State')
                            targets.append({
                                'id': target_id,
                                'port': target_port,
                                'health': health_state
                            })
                            if target_id and tg.get('TargetType') == 'instance':
                                dependencies.append(ResourceDependency(type='EC2', id=target_id))
                            elif target_id and tg.get('TargetType') == 'lambda':
                                dependencies.append(ResourceDependency(type='Lambda', id=target_id))
                    except Exception: pass

                    res = NormalizedResource(
                        resource_id=tg_arn,
                        resource_type='TargetGroup',
                        region=region,
                        name=tg.get('TargetGroupName'),
                        status='Active',
                        metadata={
                            'protocol': tg.get('Protocol'),
                            'port': tg.get('Port'),
                            'target_type': tg.get('TargetType'),
                            'health_check_protocol': tg.get('HealthCheckProtocol'),
                            'health_check_port': tg.get('HealthCheckPort'),
                            'health_check_path': tg.get('HealthCheckPath')
                        },
                        configuration={
                            'vpc_id': vpc_id,
                            'load_balancers': load_balancers,
                            'targets': targets
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    target_groups.append(res.dict())
                    
            return target_groups
        except Exception:
            logger.exception('Target Group discovery failed for region %s', region)
            return []