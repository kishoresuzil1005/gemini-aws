import boto3
import logging
import json
from app.providers.aws.models import NormalizedResource, ResourceDependency

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
                    
                    tags = {}
                    try:
                        tags_resp = client.list_queue_tags(QueueUrl=queue_url)
                        tags = {k: v for k, v in tags_resp.get('Tags', {}).items()}
                    except Exception: pass
                    
                    attrs = {}
                    try:
                        attrs_resp = client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
                        attrs = attrs_resp.get('Attributes', {})
                    except Exception:
                        pass
                        
                    dependencies = []
                    kms_key = attrs.get('KmsMasterKeyId')
                    if kms_key:
                        dependencies.append(ResourceDependency(type='KMSKey', id=kms_key))
                        
                    dlq_arn = _extract_dlq_arn(attrs)
                    if dlq_arn:
                        dependencies.append(ResourceDependency(type='SQSQueue', id=dlq_arn))
                        
                    res = NormalizedResource(
                        resource_id=attrs.get('QueueArn', queue_url),
                        resource_type='SQSQueue',
                        region=region,
                        name=queue_name,
                        status='Active',
                        metadata={
                            'arn': attrs.get('QueueArn', ''),
                            'url': queue_url,
                            'is_fifo': queue_name.endswith('.fifo'),
                            'approximate_messages': int(attrs.get('ApproximateNumberOfMessages', 0)),
                            'approximate_inflight': int(attrs.get('ApproximateNumberOfMessagesNotVisible', 0))
                        },
                        security={
                            'kms_key_id': kms_key,
                            'policy': attrs.get('Policy', '')
                        },
                        configuration={
                            'visibility_timeout': int(attrs.get('VisibilityTimeout', 30)),
                            'message_retention_seconds': int(attrs.get('MessageRetentionPeriod', 345600)),
                            'max_message_size': int(attrs.get('MaximumMessageSize', 262144)),
                            'delay_seconds': int(attrs.get('DelaySeconds', 0)),
                            'receive_wait_time': int(attrs.get('ReceiveMessageWaitTimeSeconds', 0)),
                            'dlq_arn': dlq_arn
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
        except Exception:
            logger.exception('SQS discovery failed for region %s', region)
        return resources

def _extract_dlq_arn(attrs: dict) -> str:
    try:
        policy = json.loads(attrs.get('RedrivePolicy', '{}'))
        return policy.get('deadLetterTargetArn', '')
    except Exception:
        return ''