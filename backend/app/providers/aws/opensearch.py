import boto3
import logging
logger = logging.getLogger(__name__)

class OpenSearchDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('opensearch', region_name=region)
            response = client.list_domain_names()
            domain_names = [d['DomainName'] for d in response.get('DomainNames', [])]
            if not domain_names:
                return resources
            for i in range(0, len(domain_names), 5):
                chunk = domain_names[i:i + 5]
                try:
                    desc_resp = client.describe_domains(DomainNames=chunk)
                    for domain in desc_resp.get('DomainStatusList', []):
                        domain_arn = domain.get('ARN', '')
                        domain_name = domain['DomainName']
                        ep = domain.get('Endpoints', {}) or {}
                        endpoint = ep.get('vpc', domain.get('Endpoint', ''))
                        vpc_options = domain.get('VPCOptions', {})
                        resources.append({'resource_id': domain_arn or domain_name, 'resource_type': 'OpenSearchDomain', 'region': region, 'name': domain_name, 'status': 'Active' if domain.get('Created') else 'Creating', 'provider': 'AWS', 'metadata': {'arn': domain_arn, 'engine_version': domain.get('EngineVersion', ''), 'endpoint': endpoint, 'instance_type': domain.get('ClusterConfig', {}).get('InstanceType', ''), 'instance_count': domain.get('ClusterConfig', {}).get('InstanceCount', 1), 'dedicated_master': domain.get('ClusterConfig', {}).get('DedicatedMasterEnabled', False), 'multi_az': domain.get('ClusterConfig', {}).get('ZoneAwarenessEnabled', False), 'vpc_id': vpc_options.get('VPCId', ''), 'subnet_ids': vpc_options.get('SubnetIds', []), 'security_groups': vpc_options.get('SecurityGroupIds', []), 'ebs_enabled': domain.get('EBSOptions', {}).get('EBSEnabled', False), 'volume_type': domain.get('EBSOptions', {}).get('VolumeType', ''), 'volume_size_gb': domain.get('EBSOptions', {}).get('VolumeSize', 0), 'encryption_at_rest': domain.get('EncryptionAtRestOptions', {}).get('Enabled', False), 'node_to_node_encryption': domain.get('NodeToNodeEncryptionOptions', {}).get('Enabled', False)}, 'dependencies': []})
                except Exception:
                    logger.exception('OpenSearch describe failed for chunk %s region %s', chunk, region)
        except Exception:
            logger.exception('OpenSearch discovery failed for region %s', region)
        return resources