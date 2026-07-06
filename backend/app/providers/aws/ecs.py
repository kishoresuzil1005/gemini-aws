import boto3

class ECSDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ecs', region_name=region)
            response = client.list_clusters()
            clusters = []
            for arn in response.get('clusterArns', []):
                name = arn.split('/')[-1]
                clusters.append({'resource_id': name, 'resource_type': 'ECS', 'region': region, 'provider': 'AWS', 'metadata': {'arn': arn}, 'dependencies': []})
            return clusters
        except Exception:
            return []