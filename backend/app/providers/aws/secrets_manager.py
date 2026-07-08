import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class SecretsManagerDiscovery:
    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('secretsmanager', region_name=region)
            paginator = client.get_paginator('list_secrets')
            for page in paginator.paginate():
                for secret in page.get('SecretList', []):
                    secret_arn = secret['ARN']
                    rotation_enabled = secret.get('RotationEnabled', False)
                    last_rotated = str(secret.get('LastRotatedDate', ''))
                    
                    tags = {t['Key']: t['Value'] for t in secret.get('Tags', [])}
                    
                    dependencies = []
                    kms_key = secret.get('KmsKeyId')
                    if kms_key:
                        dependencies.append(ResourceDependency(type='KMSKey', id=kms_key))
                    rot_lambda = secret.get('RotationLambdaARN')
                    if rot_lambda:
                        dependencies.append(ResourceDependency(type='Lambda', id=rot_lambda))
                        
                    res = NormalizedResource(
                        resource_id=secret_arn,
                        resource_type='Secret',
                        region=region,
                        name=secret.get('Name'),
                        status='Active',
                        metadata={
                            'arn': secret_arn,
                            'description': secret.get('Description', ''),
                            'last_accessed': str(secret.get('LastAccessedDate', '')),
                            'last_changed': str(secret.get('LastChangedDate', '')),
                            'owning_service': secret.get('OwningService', '')
                        },
                        security={
                            'kms_key_id': kms_key
                        },
                        configuration={
                            'rotation_enabled': rotation_enabled,
                            'rotation_lambda_arn': rot_lambda,
                            'rotation_rules': secret.get('RotationRules', {}),
                            'last_rotated': last_rotated
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
        except Exception:
            logger.exception('SecretsManager discovery failed for region %s', region)
        return resources

class SSMDiscovery:
    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('ssm', region_name=region)
            paginator = client.get_paginator('describe_parameters')
            for page in paginator.paginate():
                for param in page.get('Parameters', []):
                    dependencies = []
                    kms_key = param.get('KeyId')
                    if kms_key:
                        dependencies.append(ResourceDependency(type='KMSKey', id=kms_key))
                        
                    res = NormalizedResource(
                        resource_id=param['Name'],
                        resource_type='SSMParameter',
                        region=region,
                        name=param['Name'],
                        status='Active',
                        metadata={
                            'type': param.get('Type'),
                            'data_type': param.get('DataType', 'text'),
                            'version': param.get('Version'),
                            'tier': param.get('Tier', 'Standard'),
                            'last_modified': str(param.get('LastModifiedDate', '')),
                            'last_modified_user': param.get('LastModifiedUser', '')
                        },
                        security={
                            'kms_key_id': kms_key,
                            'policies': param.get('Policies', [])
                        },
                        configuration={},
                        tags={},
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
        except Exception:
            logger.exception('SSM discovery failed for region %s', region)
        return resources