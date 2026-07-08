import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class CloudFrontDiscovery:
    @staticmethod
    def discover(region: str='us-east-1') -> list[dict]:
        """CloudFront is a global service — always queried from us-east-1."""
        resources = []
        try:
            client = boto3.client('cloudfront', region_name='us-east-1')
            paginator = client.get_paginator('list_distributions')
            for page in paginator.paginate():
                dist_list = page.get('DistributionList', {})
                for dist in dist_list.get('Items', []):
                    dist_id = dist['Id']
                    dist_arn = dist.get('ARN', '')
                    
                    tags = {}
                    try:
                        tags_resp = client.list_tags_for_resource(Resource=dist_arn)
                        tags = {t['Key']: t['Value'] for t in tags_resp.get('Tags', {}).get('Items', [])}
                    except Exception: pass
                    
                    dependencies = []
                    web_acl_id = dist.get('WebACLId')
                    if web_acl_id:
                        dependencies.append(ResourceDependency(type='WAFWebACL', id=web_acl_id))
                        
                    origins = []
                    for o in dist.get('Origins', {}).get('Items', []):
                        domain = o.get('DomainName')
                        origins.append({
                            'id': o.get('Id'),
                            'domain': domain,
                            'path': o.get('OriginPath', '')
                        })
                        if domain:
                            if '.s3.' in domain:
                                dependencies.append(ResourceDependency(type='S3Bucket', id=domain.split('.')[0]))
                            elif '.elb.' in domain:
                                dependencies.append(ResourceDependency(type='ALB', id=domain.split('.')[0]))
                                
                    aliases = dist.get('Aliases', {}).get('Items', [])
                    cert = dist.get('ViewerCertificate', {})
                    acm_arn = cert.get('ACMCertificateArn')
                    if acm_arn:
                        dependencies.append(ResourceDependency(type='ACMCertificate', id=acm_arn))

                    res = NormalizedResource(
                        resource_id=dist_id,
                        resource_type='CloudFrontDistribution',
                        region='global',
                        name=aliases[0] if aliases else dist.get('DomainName'),
                        status=dist.get('Status', 'Unknown'),
                        metadata={
                            'arn': dist_arn,
                            'domain_name': dist.get('DomainName'),
                            'aliases': aliases,
                            'enabled': dist.get('Enabled', False),
                            'http_version': dist.get('HttpVersion', ''),
                            'is_ipv6_enabled': dist.get('IsIPV6Enabled', False),
                            'price_class': dist.get('PriceClass', '')
                        },
                        security={
                            'web_acl_id': web_acl_id,
                            'certificate_source': cert.get('CertificateSource', 'cloudfront'),
                            'acm_certificate_arn': acm_arn
                        },
                        configuration={
                            'origins': origins
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
                    
                    for behavior in dist.get('CacheBehaviors', {}).get('Items', []):
                        b_dependencies = [ResourceDependency(type='CloudFrontDistribution', id=dist_id)]
                        
                        b_res = NormalizedResource(
                            resource_id=f"{dist_id}-{behavior.get('PathPattern')}",
                            resource_type='CloudFrontBehavior',
                            region='global',
                            name=f"{dist_id}:{behavior.get('PathPattern')}",
                            status='Active',
                            metadata={
                                'distribution_id': dist_id,
                                'path_pattern': behavior.get('PathPattern'),
                                'target_origin_id': behavior.get('TargetOriginId')
                            },
                            configuration={
                                'viewer_protocol': behavior.get('ViewerProtocolPolicy', ''),
                                'compress': behavior.get('Compress', False)
                            },
                            tags={},
                            dependencies=b_dependencies
                        )
                        resources.append(b_res.dict())
        except Exception:
            logger.exception('CloudFront discovery failed')
        return resources