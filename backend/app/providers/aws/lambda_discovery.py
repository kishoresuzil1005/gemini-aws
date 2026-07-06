import boto3

class LambdaDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('lambda', region_name=region)
            response = client.list_functions()
            functions = []
            for f in response.get('Functions', []):
                functions.append({'resource_id': f['FunctionName'], 'resource_type': 'Lambda', 'region': region, 'provider': 'AWS', 'metadata': {'runtime': f.get('Runtime'), 'handler': f.get('Handler'), 'timeout': f.get('Timeout'), 'memory_size': f.get('MemorySize'), 'role': f.get('Role'), 'vpc_config': f.get('VpcConfig', {})}, 'dependencies': ([{'type': 'VPC', 'id': fn.get('VpcConfig', {}).get('VpcId')}] if fn.get('VpcConfig', {}).get('VpcId') else [])})
            return functions
        except Exception:
            return []