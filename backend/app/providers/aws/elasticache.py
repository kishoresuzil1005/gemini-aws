import boto3
import logging
logger = logging.getLogger(__name__)

class ElastiCacheDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('elasticache', region_name=region)
            try:
                paginator = client.get_paginator('describe_replication_groups')
                for page in paginator.paginate():
                    for group in page.get('ReplicationGroups', []):
                        rg_id = group['ReplicationGroupId']
                        node_groups = group.get('NodeGroups', [])
                        primary_endpoint = ''
                        reader_endpoint = ''
                        for ng in node_groups:
                            primary_endpoint = ng.get('PrimaryEndpoint', {}).get('Address', '')
                            reader_endpoint = ng.get('ReaderEndpoint', {}).get('Address', '')
                        resources.append({'resource_id': rg_id, 'resource_type': 'ElastiCacheRedis', 'region': region, 'name': rg_id, 'status': group.get('Status'), 'provider': 'AWS', 'metadata': {'arn': group.get('ARN', ''), 'description': group.get('Description', ''), 'engine': 'Redis', 'engine_version': group.get('CacheNodeType', ''), 'node_type': group.get('CacheNodeType', ''), 'num_shards': len(node_groups), 'num_replicas': group.get('AutomaticFailover', 'disabled'), 'multi_az': group.get('MultiAZ', 'disabled'), 'primary_endpoint': primary_endpoint, 'reader_endpoint': reader_endpoint, 'at_rest_encryption': group.get('AtRestEncryptionEnabled', False), 'in_transit_encryption': group.get('TransitEncryptionEnabled', False), 'auth_token_enabled': group.get('AuthTokenEnabled', False), 'kms_key_id': group.get('KmsKeyId', '')}, 'dependencies': []})
            except Exception:
                logger.exception('ElastiCache Replication Groups failed for region %s', region)
            try:
                paginator = client.get_paginator('describe_cache_clusters')
                for page in paginator.paginate(ShowCacheNodeInfo=True):
                    for cluster in page.get('CacheClusters', []):
                        cluster_id = cluster['CacheClusterId']
                        engine = cluster.get('Engine', '')
                        if cluster.get('ReplicationGroupId'):
                            continue
                        resources.append({'resource_id': cluster_id, 'resource_type': 'ElastiCacheMemcached' if engine == 'memcached' else 'ElastiCacheCluster', 'region': region, 'name': cluster_id, 'status': cluster.get('CacheClusterStatus'), 'provider': 'AWS', 'metadata': {'arn': cluster.get('ARN', ''), 'engine': engine, 'engine_version': cluster.get('EngineVersion', ''), 'node_type': cluster.get('CacheNodeType', ''), 'num_nodes': cluster.get('NumCacheNodes', 0), 'endpoint': cluster.get('ConfigurationEndpoint', {}).get('Address', ''), 'port': cluster.get('ConfigurationEndpoint', {}).get('Port', 11211), 'subnet_group': cluster.get('CacheSubnetGroupName', ''), 'security_groups': [sg.get('SecurityGroupId') for sg in cluster.get('SecurityGroups', [])]}, 'dependencies': []})
            except Exception:
                logger.exception('ElastiCache Cache Clusters failed for region %s', region)
        except Exception:
            logger.exception('ElastiCache discovery failed for region %s', region)
        return resources