import boto3
import logging
logger = logging.getLogger(__name__)

class SQSDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('sqs', region_name=region)
            paginator = client.get_paginator('list_queues')
            for page in paginator.paginate():
                for queue_url in page.get('QueueUrls', []):
                    queue_name = queue_url.split('/')[-1]
                    attrs = {}
                    try:
                        attrs_resp = client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
                        attrs = attrs_resp.get('Attributes', {})
                    except Exception:
                        pass
                    resources.append({'resource_id': attrs.get('QueueArn', queue_url), 'resource_type': 'SQSQueue', 'region': region, 'name': queue_name, 'provider': 'AWS', 'metadata': {'arn': attrs.get('QueueArn', ''), 'url': queue_url, 'is_fifo': queue_name.endswith('.fifo'), 'visibility_timeout': int(attrs.get('VisibilityTimeout', 30)), 'message_retention_seconds': int(attrs.get('MessageRetentionPeriod', 345600)), 'max_message_size': int(attrs.get('MaximumMessageSize', 262144)), 'delay_seconds': int(attrs.get('DelaySeconds', 0)), 'receive_wait_time': int(attrs.get('ReceiveMessageWaitTimeSeconds', 0)), 'kms_key_id': attrs.get('KmsMasterKeyId', ''), 'dlq_arn': _extract_dlq_arn(attrs), 'approximate_messages': int(attrs.get('ApproximateNumberOfMessages', 0)), 'approximate_inflight': int(attrs.get('ApproximateNumberOfMessagesNotVisible', 0))}, 'dependencies': []})
        except Exception:
            logger.exception('SQS discovery failed for region %s', region)
        return resources

def _extract_dlq_arn(attrs: dict) -> str:
    import json
    try:
        policy = json.loads(attrs.get('RedrivePolicy', '{}'))
        return policy.get('deadLetterTargetArn', '')
    except Exception:
        return ''