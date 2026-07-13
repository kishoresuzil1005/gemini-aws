import boto3
from app.providers.aws.models import NormalizedResource, ResourceDependency

class LambdaDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('lambda', region_name=region)
            response = client.list_functions()
            functions = []
            
            for f in response.get('Functions', []):
                tags_resp = client.list_tags(Resource=f['FunctionArn']) if 'FunctionArn' in f else {}
                tags = tags_resp.get('Tags', {})
                
                vpc_config = f.get('VpcConfig', {})
                
                dependencies = []
                if vpc_config.get('VpcId'):
                    dependencies.append(ResourceDependency(type='VPC', id=vpc_config['VpcId']))
                for sub in vpc_config.get('SubnetIds', []):
                    dependencies.append(ResourceDependency(type='Subnet', id=sub))
                for sg in vpc_config.get('SecurityGroupIds', []):
                    dependencies.append(ResourceDependency(type='SecurityGroup', id=sg))
                if f.get('Role'):
                    dependencies.append(ResourceDependency(type='IAM', id=f['Role']))
                for layer in f.get('Layers', []):
                    dependencies.append(ResourceDependency(type='LambdaLayer', id=layer.get('Arn')))

                res = NormalizedResource(
                    resource_id=f['FunctionName'],
                    resource_type='Lambda',
                    region=region,
                    name=f['FunctionName'],
                    status=f.get('State', 'Active'),
                    metadata={
                        'runtime': f.get('Runtime'),
                        'handler': f.get('Handler'),
                        'architectures': f.get('Architectures', []),
                        'memory_size': f.get('MemorySize'),
                        'timeout': f.get('Timeout'),
                        'ephemeral_storage': f.get('EphemeralStorage', {}).get('Size'),
                        'code_size': f.get('CodeSize'),
                        'package_type': f.get('PackageType'),
                        'last_modified': f.get('LastModified'),
                        'version': f.get('Version'),
                        'description': f.get('Description'),
                        'environment_variables': list(f.get('Environment', {}).get('Variables', {}).keys()),
                        
                        # Needed by Graph Builder
                        'role': f.get('Role'),
                        'vpc_config': vpc_config
                    },
                    security={
                        'role': f.get('Role'),
                        'kms_key_arn': f.get('KMSKeyArn')
                    },
                    configuration={
                        'vpc_config': vpc_config,
                        'layers': [layer.get('Arn') for layer in f.get('Layers', [])],
                        'snap_start': f.get('SnapStart', {})
                    },
                    monitoring={
                        'tracing_config': f.get('TracingConfig', {}),
                        'logging_config': f.get('LoggingConfig', {})
                    },
                    tags=tags,
                    dependencies=dependencies
                )
                functions.append(res.dict())
                
            return functions
        except Exception as e:
            print(f"Error in LambdaDiscovery: {e}")
            return []