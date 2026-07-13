import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class ALBDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('elbv2', region_name=region)
            paginator = client.get_paginator('describe_load_balancers')
            lbs = []
            
            for page in paginator.paginate():
                for lb in page.get('LoadBalancers', []):
                    lb_arn = lb['LoadBalancerArn']
                    
                    tags = {}
                    try:
                        tags_resp = client.describe_tags(ResourceArns=[lb_arn])
                        if tags_resp.get('TagDescriptions'):
                            tags = {t['Key']: t['Value'] for t in tags_resp['TagDescriptions'][0].get('Tags', [])}
                    except Exception: pass
                    
                    dependencies = []
                    vpc_id = lb.get('VpcId')
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                        
                    for az in lb.get('AvailabilityZones', []):
                        if az.get('SubnetId'):
                            dependencies.append(ResourceDependency(type='Subnet', id=az['SubnetId']))
                            
                    security_groups = lb.get('SecurityGroups', [])
                    for sg in security_groups:
                        dependencies.append(ResourceDependency(type='SecurityGroup', id=sg))

                    listeners = []
                    try:
                        listener_paginator = client.get_paginator('describe_listeners')
                        for l_page in listener_paginator.paginate(LoadBalancerArn=lb_arn):
                            for listener in l_page.get('Listeners', []):
                                listeners.append({
                                    'port': listener.get('Port'),
                                    'protocol': listener.get('Protocol'),
                                    'default_actions': listener.get('DefaultActions', [])
                                })
                    except Exception: pass

                    attributes = {}
                    try:
                        attr_resp = client.describe_load_balancer_attributes(LoadBalancerArn=lb_arn)
                        attributes = {a['Key']: a['Value'] for a in attr_resp.get('Attributes', [])}
                    except Exception: pass

                    print("=" * 80)
                    print("RAW ALB")
                    print("vpc_id:", vpc_id)
                    print("subnets:", [az.get("SubnetId") for az in lb.get("AvailabilityZones", [])])
                    print("security_groups:", security_groups)
                    print("=" * 80)

                    res = NormalizedResource(
                        resource_id=lb_arn,
                        resource_type='ALB',
                        region=region,
                        name=lb['LoadBalancerName'],
                        status=lb.get('State', {}).get('Code', 'Unknown'),
                        metadata={
                            "dns_name": lb.get("DNSName"),
                            "scheme": lb.get("Scheme"),
                            "type": lb.get("Type"),
                            "ip_address_type": lb.get("IpAddressType"),
                            
                            "vpc_id": vpc_id,
                            
                            "subnets": [
                                az.get("SubnetId")
                                for az in lb.get("AvailabilityZones", [])
                                if az.get("SubnetId")
                            ],
                            
                            "security_groups": security_groups
                        },
                        security={
                            'security_groups': security_groups
                        },
                        configuration={
                            'vpc_id': vpc_id,
                            'availability_zones': [az.get('ZoneName') for az in lb.get('AvailabilityZones', [])],
                            'subnets': [az.get('SubnetId') for az in lb.get('AvailabilityZones', []) if az.get('SubnetId')],
                            'listeners': listeners,
                            'attributes': attributes
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    print("=" * 80)
                    print("ALB RAW RESOURCE")
                    print(res.dict())
                    print("=" * 80)
                    
                    lbs.append(res.dict())
                    
            return lbs
        except Exception:
            logger.exception('ALB discovery failed for region %s', region)
            return []