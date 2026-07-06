import boto3
import logging
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
                    origins = []
                    for o in dist.get('Origins', {}).get('Items', []):
                        origins.append({'provider': 'AWS', 'metadata': {'id': o.get('Id'), 'domain': o.get('DomainName'), 'path': o.get('OriginPath', '')}, 'dependencies': [{'type': 'WAF', 'id': dist.get('WebACLId')}] if dist.get('WebACLId') else []})
                    aliases = dist.get('Aliases', {}).get('Items', [])
                    cert = dist.get('ViewerCertificate', {})
                    resources.append({'resource_id': dist_id, 'resource_type': 'CloudFront', 'region': 'global', 'name': aliases[0] if aliases else dist.get('DomainName'), 'status': dist.get('Status'), 'provider': 'AWS', 'metadata': {'arn': dist_arn, 'domain_name': dist.get('DomainName'), 'aliases': aliases, 'enabled': dist.get('Enabled', False), 'http_version': dist.get('HttpVersion', ''), 'is_ipv6_enabled': dist.get('IsIPV6Enabled', False), 'price_class': dist.get('PriceClass', ''), 'origins': origins, 'certificate_source': cert.get('CertificateSource', 'cloudfront'), 'acm_certificate_arn': cert.get('ACMCertificateArn', ''), 'web_acl_id': dist.get('WebACLId', '')}, 'dependencies': [{'type': 'WAF', 'id': dist.get('WebACLId')}] if dist.get('WebACLId') else []})
                    for behavior in dist.get('CacheBehaviors', {}).get('Items', []):
                        resources.append({'resource_id': f"{dist_id}-{behavior.get('PathPattern')}", 'resource_type': 'CloudFrontBehavior', 'region': 'global', 'name': f"{dist_id}:{behavior.get('PathPattern')}", 'provider': 'AWS', 'metadata': {'distribution_id': dist_id, 'path_pattern': behavior.get('PathPattern'), 'target_origin_id': behavior.get('TargetOriginId'), 'viewer_protocol': behavior.get('ViewerProtocolPolicy', ''), 'compress': behavior.get('Compress', False)}, 'dependencies': [{'type': 'WAF', 'id': dist.get('WebACLId')}] if dist.get('WebACLId') else []})
        except Exception:
            logger.exception('CloudFront discovery failed')
        return resources