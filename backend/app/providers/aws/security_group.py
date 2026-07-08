import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class SecurityGroupDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_security_groups')
            security_groups = []
            
            for page in paginator.paginate():
                for sg in page.get('SecurityGroups', []):
                    tags = {t['Key']: t['Value'] for t in sg.get('Tags', [])}
                    name = tags.get('Name', sg.get('GroupName'))
                    
                    dependencies = []
                    vpc_id = sg.get('VpcId')
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                        
                    ingress_rules = []
                    for perm in sg.get('IpPermissions', []):
                        ingress_rules.append(perm)
                        for pair in perm.get('UserIdGroupPairs', []):
                            if pair.get('GroupId'):
                                dependencies.append(ResourceDependency(type='SecurityGroup', id=pair['GroupId']))
                                
                    egress_rules = []
                    for perm in sg.get('IpPermissionsEgress', []):
                        egress_rules.append(perm)
                        for pair in perm.get('UserIdGroupPairs', []):
                            if pair.get('GroupId'):
                                dependencies.append(ResourceDependency(type='SecurityGroup', id=pair['GroupId']))

                    res = NormalizedResource(
                        resource_id=sg['GroupId'],
                        resource_type='SecurityGroup',
                        region=region,
                        name=name,
                        status='Active',
                        metadata={
                            'description': sg.get('Description'),
                            'owner_id': sg.get('OwnerId'),
                            'ingress_rule_count': len(ingress_rules),
                            'egress_rule_count': len(egress_rules)
                        },
                        security={
                            'ingress_rules': ingress_rules,
                            'egress_rules': egress_rules
                        },
                        configuration={
                            'vpc_id': vpc_id
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    security_groups.append(res.dict())
                    
            return security_groups
        except Exception:
            logger.exception('Security Group discovery failed for region %s', region)
            return []