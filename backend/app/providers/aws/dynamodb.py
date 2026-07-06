import boto3
import logging
logger = logging.getLogger(__name__)

class DynamoDBDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('dynamodb', region_name=region)
            paginator = client.get_paginator('list_tables')
            for page in paginator.paginate():
                for table_name in page.get('TableNames', []):
                    try:
                        desc = client.describe_table(TableName=table_name)
                        table = desc['Table']
                        table_arn = table['TableArn']
                        gsis = [{'name': idx['IndexName'], 'status': idx['IndexStatus'], 'item_count': idx.get('ItemCount', 0)} for idx in table.get('GlobalSecondaryIndexes', [])]
                        lsis = [{'name': idx['IndexName']} for idx in table.get('LocalSecondaryIndexes', [])]
                        stream_arn = table.get('LatestStreamArn', '')
                        billing = table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
                        encryption = table.get('SSEDescription', {}).get('Status', 'DISABLED')
                        resources.append({'resource_id': table_arn, 'resource_type': 'DynamoDBTable', 'region': region, 'name': table_name, 'status': table.get('TableStatus'), 'provider': 'AWS', 'metadata': {'arn': table_arn, 'item_count': table.get('ItemCount', 0), 'size_bytes': table.get('TableSizeBytes', 0), 'billing_mode': billing, 'read_capacity': table.get('ProvisionedThroughput', {}).get('ReadCapacityUnits', 0), 'write_capacity': table.get('ProvisionedThroughput', {}).get('WriteCapacityUnits', 0), 'global_secondary_indexes': gsis, 'local_secondary_indexes': lsis, 'stream_enabled': bool(stream_arn), 'stream_arn': stream_arn, 'encryption_status': encryption, 'kms_key_arn': table.get('SSEDescription', {}).get('KMSMasterKeyArn', ''), 'point_in_time_recovery': _get_pitr(client, table_name)}, 'dependencies': []})
                    except Exception:
                        logger.exception('DynamoDB table describe failed: %s', table_name)
        except Exception:
            logger.exception('DynamoDB discovery failed for region %s', region)
        return resources

def _get_pitr(client, table_name: str) -> bool:
    try:
        resp = client.describe_continuous_backups(TableName=table_name)
        pitr = resp.get('ContinuousBackupsDescription', {}).get('PointInTimeRecoveryDescription', {})
        return pitr.get('PointInTimeRecoveryStatus') == 'ENABLED'
    except Exception:
        return False