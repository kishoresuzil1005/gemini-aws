import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class SNSDiscovery:
    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('sns', region_name=region)
            paginator = client.get_paginator('list_topics')
            for page in paginator.paginate():
                for topic in page.get('Topics', []):
                    topic_arn = topic['TopicArn']
                    topic_name = topic_arn.split(':')[-1]
                    
                    tags = {}
                    try:
                        tags_resp = client.list_tags_for_resource(ResourceArn=topic_arn)
                        tags = {t['Key']: t['Value'] for t in tags_resp.get('Tags', [])}
                    except Exception: pass
                    
                    attrs = {}
                    try:
                        attrs_resp = client.get_topic_attributes(TopicArn=topic_arn)
                        attrs = attrs_resp.get('Attributes', {})
                    except Exception:
                        pass
                        
                    dependencies = []
                    kms_key = attrs.get('KmsMasterKeyId')
                    if kms_key:
                        dependencies.append(ResourceDependency(type='KMSKey', id=kms_key))
                        
                    res = NormalizedResource(
                        resource_id=topic_arn,
                        resource_type='SNSTopic',
                        region=region,
                        name=topic_name,
                        status='Active',
                        metadata={
                            'arn': topic_arn,
                            'display_name': attrs.get('DisplayName', ''),
                            'subscription_count': int(attrs.get('SubscriptionsConfirmed', 0)),
                            'pending_subscription_count': int(attrs.get('SubscriptionsPending', 0))
                        },
                        security={
                            'kms_key_id': kms_key,
                            'policy': attrs.get('Policy')
                        },
                        configuration={
                            'fifo': topic_name.endswith('.fifo'),
                            'content_deduplication': attrs.get('ContentBasedDeduplication', 'false') == 'true'
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
                    
                    try:
                        sub_paginator = client.get_paginator('list_subscriptions_by_topic')
                        for sub_page in sub_paginator.paginate(TopicArn=topic_arn):
                            for sub in sub_page.get('Subscriptions', []):
                                if sub.get('SubscriptionArn') in ('PendingConfirmation', 'Deleted'):
                                    continue
                                    
                                sub_arn = sub['SubscriptionArn']
                                protocol = sub.get('Protocol')
                                endpoint = sub.get('Endpoint', '')
                                
                                sub_dependencies = [ResourceDependency(type='SNSTopic', id=topic_arn)]
                                if protocol == 'lambda':
                                    sub_dependencies.append(ResourceDependency(type='Lambda', id=endpoint))
                                elif protocol == 'sqs':
                                    sub_dependencies.append(ResourceDependency(type='SQSQueue', id=endpoint))
                                    
                                sub_res = NormalizedResource(
                                    resource_id=sub_arn,
                                    resource_type='SNSSubscription',
                                    region=region,
                                    name=f"{topic_name}-{protocol}",
                                    status='Active',
                                    metadata={
                                        'arn': sub_arn,
                                        'topic_arn': topic_arn,
                                        'protocol': protocol,
                                        'endpoint': endpoint
                                    },
                                    configuration={},
                                    tags={},
                                    dependencies=sub_dependencies
                                )
                                resources.append(sub_res.dict())
                    except Exception:
                        pass
        except Exception:
            logger.exception('SNS discovery failed for region %s', region)
        return resources