import boto3
import logging
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
                    resources.append({'resource_id': secret_arn, 'resource_type': 'Secret', 'region': region, 'name': secret.get('Name'), 'provider': 'AWS', 'metadata': {'arn': secret_arn, 'description': secret.get('Description', ''), 'rotation_enabled': rotation_enabled, 'rotation_lambda_arn': secret.get('RotationLambdaARN', ''), 'rotation_rules': secret.get('RotationRules', {}), 'last_rotated': last_rotated, 'last_accessed': str(secret.get('LastAccessedDate', '')), 'last_changed': str(secret.get('LastChangedDate', '')), 'kms_key_id': secret.get('KmsKeyId', ''), 'tags': {t['Key']: t['Value'] for t in secret.get('Tags', [])}, 'owning_service': secret.get('OwningService', '')}, 'dependencies': []})
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
                    resources.append({'resource_id': param['Name'], 'resource_type': 'SSMParameter', 'region': region, 'name': param['Name'], 'provider': 'AWS', 'metadata': {'type': param.get('Type'), 'data_type': param.get('DataType', 'text'), 'version': param.get('Version'), 'tier': param.get('Tier', 'Standard'), 'last_modified': str(param.get('LastModifiedDate', '')), 'last_modified_user': param.get('LastModifiedUser', ''), 'kms_key_id': param.get('KeyId', ''), 'policies': param.get('Policies', [])}, 'dependencies': []})
        except Exception:
            logger.exception('SSM discovery failed for region %s', region)
        return resources