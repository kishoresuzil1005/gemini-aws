import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class EKSDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('eks', region_name=region)
            response = client.list_clusters()
            clusters = []
            
            for name in response.get('clusters', []):
                try:
                    desc = client.describe_cluster(name=name)
                    cluster = desc.get('cluster', {})
                    
                    arn = cluster.get('arn')
                    version = cluster.get('version')
                    status = cluster.get('status')
                    endpoint = cluster.get('endpoint')
                    role_arn = cluster.get('roleArn')
                    
                    tags = cluster.get('tags', {})
                    
                    dependencies = []
                    if role_arn:
                        dependencies.append(ResourceDependency(type='IAMRole', id=role_arn))
                        
                    vpc_config = cluster.get('resourcesVpcConfig', {})
                    vpc_id = vpc_config.get('vpcId')
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                        
                    subnets = vpc_config.get('subnetIds', [])
                    for subnet in subnets:
                        dependencies.append(ResourceDependency(type='Subnet', id=subnet))
                        
                    security_groups = vpc_config.get('securityGroupIds', [])
                    if vpc_config.get('clusterSecurityGroupId'):
                        security_groups.append(vpc_config['clusterSecurityGroupId'])
                    for sg in set(security_groups):
                        dependencies.append(ResourceDependency(type='SecurityGroup', id=sg))

                    res = NormalizedResource(
                        resource_id=arn,
                        resource_type='EKSCluster',
                        region=region,
                        name=name,
                        status=status,
                        metadata={
                            'arn': arn,
                            'version': version,
                            'endpoint': endpoint,
                            'platform_version': cluster.get('platformVersion')
                        },
                        security={
                            'role_arn': role_arn,
                            'cluster_security_group_id': vpc_config.get('clusterSecurityGroupId'),
                            'endpoint_public_access': vpc_config.get('endpointPublicAccess', True),
                            'endpoint_private_access': vpc_config.get('endpointPrivateAccess', False)
                        },
                        configuration={
                            'vpc_id': vpc_id,
                            'subnets': subnets,
                            'security_groups': security_groups,
                            'logging': cluster.get('logging', {}),
                            'oidc_issuer': cluster.get('identity', {}).get('oidc', {}).get('issuer')
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    clusters.append(res.dict())
                except Exception:
                    logger.exception('Failed to describe EKS cluster %s', name)
                    
            return clusters
        except Exception:
            logger.exception('EKS discovery failed for region %s', region)
            return []